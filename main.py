import argparse
import logging
import sys
import time

from src.core.config.generator import ConfigGenerator
from src.core.config.loader import Config
from src.core.notification.processor import NotificationProcessor
from src.core.service_locator import ServiceLocator
from src.core.services import initialize_services
from src.core.utils.retry import with_retry
from src.infrastructure.logging.setup import setup_logging
from src.services.moodle.notification_handler import MoodleNotificationHandler
from src.ui.cli.screen import animate_logo, logo_lines


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Moodle Mate - Your Smart Moodle Notification Assistant"
    )
    parser.add_argument(
        "--gen-config", action="store_true", help="Generate a new configuration file"
    )
    parser.add_argument("--config", default="config.ini", help="Path to config file")
    return parser.parse_args()


@with_retry(max_retries=3, base_delay=5.0, max_delay=30.0)
def fetch_and_process(moodle_handler, notification_processor):
    """Fetch and process notifications with retry logic."""
    if notification := moodle_handler.fetch_newest_notification():
        notification_processor.process(notification)
    return True


def handle_config_generation(generator: ConfigGenerator) -> None:
    """Handle configuration file generation."""
    if generator.generate_config():
        logging.info("Configuration file generated successfully!")
        sys.exit(0)
    else:
        logging.error("Failed to generate configuration file.")
        sys.exit(1)


def initialize_app_services() -> tuple:
    """Initialize and return required services."""
    initialize_services()
    locator = ServiceLocator()

    config = locator.get("config", Config)
    notification_processor = locator.get(
        "notification_processor", NotificationProcessor
    )
    moodle_handler = locator.get("moodle_handler", MoodleNotificationHandler)

    return config, notification_processor, moodle_handler


def handle_error(
    consecutive_errors: int, error: Exception, config
) -> tuple[int, float]:
    """Handle error and return updated error count and sleep time."""
    consecutive_errors += 1
    logging.error(
        f"Error during execution (attempt {consecutive_errors}): {str(error)}"
    )

    if consecutive_errors >= config.notification.max_retries:
        logging.critical("Too many consecutive errors. Restarting main loop...")
        consecutive_errors = 0

    error_sleep = min(30 * (2 ** (consecutive_errors - 1)), 300)
    logging.info(f"Waiting {error_sleep} seconds before retry...")

    return consecutive_errors, error_sleep


def calculate_sleep_time(consecutive_errors: int, base_interval: int) -> float:
    """Calculate adaptive sleep time based on error state."""
    if consecutive_errors > 0:
        return min(base_interval * (2**consecutive_errors), 300)
    return base_interval


def run_main_loop(config, moodle_handler, notification_processor) -> None:
    """Run the main application loop."""
    consecutive_errors = 0

    while True:
        try:
            success = fetch_and_process(moodle_handler, notification_processor)
            if success:
                consecutive_errors = 0

            sleep_time = calculate_sleep_time(
                consecutive_errors, config.notification.fetch_interval
            )
            time.sleep(sleep_time)

        except Exception as e:
            consecutive_errors, error_sleep = handle_error(
                consecutive_errors, e, config
            )
            time.sleep(error_sleep)


def main() -> None:
    """Main entry point of the application."""
    setup_logging()
    args = parse_args()

    if args.gen_config:
        handle_config_generation(ConfigGenerator())

    animate_logo(logo_lines)
    logging.info("Starting Moodle Mate...")

    try:
        config, notification_processor, moodle_handler = initialize_app_services()
        run_main_loop(config, moodle_handler, notification_processor)
    except KeyboardInterrupt:
        logging.info("Shutting down gracefully...")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        raise


if __name__ == "__main__":
    main()
