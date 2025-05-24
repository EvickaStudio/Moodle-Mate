import argparse
import logging
import sys
import time

import requests

from src.core.config.generator import ConfigGenerator
from src.core.config.loader import Config
from src.core.notification.processor import NotificationProcessor
from src.core.service_locator import ServiceLocator
from src.core.services import initialize_services
from src.core.utils.retry import with_retry
from src.infrastructure.http.request_manager import request_manager
from src.infrastructure.logging.setup import setup_logging
from src.services.moodle.api import MoodleAPI
from src.services.moodle.notification_handler import MoodleNotificationHandler
from src.ui.cli.screen import LOGO_LINES, animate_logo


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for the Moodle-Mate application.

    This function sets up and parses arguments such as `--gen-config` for
    generating a new configuration file and `--config` to specify a custom
    path to the configuration file.

    Returns:
        argparse.Namespace: An object containing the parsed command-line arguments.
                            Attributes include 'gen_config' (bool) and 'config' (str).
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Moodle Mate - Your Smart Moodle Notification Assistant",
    )
    parser.add_argument(
        "--gen-config",
        action="store_true",
        help="Generate a new configuration file",
    )
    parser.add_argument("--config", default="config.ini", help="Path to config file")
    return parser.parse_args()


@with_retry(max_retries=3, base_delay=5.0, max_delay=30.0)
def fetch_and_process(
    moodle_handler: MoodleNotificationHandler,
    notification_processor: NotificationProcessor,
) -> bool:
    """
    Fetch the newest Moodle notification and process it.

    This function attempts to retrieve the latest notification using the
    provided `moodle_handler`. If a notification is found, it's passed
    to the `notification_processor`. The operation is wrapped with retry logic
    defined by the `@with_retry` decorator.

    Args:
        moodle_handler (MoodleNotificationHandler): An instance responsible for
            fetching notifications from Moodle.
        notification_processor (NotificationProcessor): An instance responsible for
            processing and dispatching notifications.

    Returns:
        bool: True if a notification was fetched and processed (or if no new
              notification was found, effectively a successful check), or if a
              retry attempt was made. The retry decorator handles exceptions,
              so this function typically returns True unless a non-retriable
              error occurs within the decorator itself, which is unlikely for
              this simple pass-through.
    """
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


def initialize_app_services() -> tuple[Config, NotificationProcessor, MoodleNotificationHandler]:
    """Initialize and return required services."""
    initialize_services()
    locator = ServiceLocator()

    config = locator.get("config", Config)
    notification_processor = locator.get(
        "notification_processor",
        NotificationProcessor,
    )
    moodle_handler = locator.get("moodle_handler", MoodleNotificationHandler)

    return config, notification_processor, moodle_handler


def handle_error(
    consecutive_errors: int,
    error: Exception,
    config: Config,
) -> tuple[int, float]:
    """Handle error and return updated error count and sleep time."""
    consecutive_errors += 1
    logging.error(
        f"Error during execution (attempt {consecutive_errors}): {error!s}",
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


def run_main_loop(
    config: Config,
    moodle_handler: MoodleNotificationHandler,
    notification_processor: NotificationProcessor,
) -> None:
    """Run the main application loop with provided services."""
    consecutive_errors = 0
    session_refresh_interval = 24.0
    locator = ServiceLocator()
    moodle_api = locator.get("moodle_api", MoodleAPI)

    while True:
        try:
            if request_manager.session_age_hours >= session_refresh_interval:
                logging.info(
                    f"Session is {request_manager.session_age_hours:.2f} hours old. Refreshing...",
                )
                if moodle_api.refresh_session():
                    logging.info("Session successfully refreshed")
                else:
                    logging.error(
                        "Failed to refresh session. Continuing with existing session.",
                    )

            success = fetch_and_process(moodle_handler, notification_processor)
            if success:
                consecutive_errors = 0

            sleep_time = calculate_sleep_time(
                consecutive_errors,
                config.notification.fetch_interval,
            )
            time.sleep(sleep_time)

        except requests.exceptions.RequestException as req_e:
            logging.warning(f"A network request failed: {req_e}")
            consecutive_errors, error_sleep = handle_error(
                consecutive_errors,
                req_e,
                config,
            )
            time.sleep(error_sleep)
        except KeyboardInterrupt:
            logging.info("Main loop interrupted. Shutting down...")
            break
        except (TypeError, ValueError, AttributeError) as e:
            logging.error(f"An unexpected error occurred in the main loop: {e!s}", exc_info=True)
            consecutive_errors, error_sleep = handle_error(
                consecutive_errors,
                e,
                config,
            )
            time.sleep(error_sleep)


def main() -> None:
    """Main entry point of the application."""
    setup_logging()
    args = parse_args()

    if args.gen_config:
        handle_config_generation(ConfigGenerator())

    animate_logo(LOGO_LINES)
    logging.info("Starting Moodle Mate...")

    try:
        config, notification_processor, moodle_handler = initialize_app_services()
        run_main_loop(config, moodle_handler, notification_processor)
    except KeyboardInterrupt:
        logging.info("Shutting down gracefully...")
    except Exception as e:
        logging.critical(f"An critical unexpected error occurred: {e!s}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
