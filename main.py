import logging
import time

from src.core.config.loader import Config
from src.core.notification.processor import NotificationProcessor
from src.core.service_locator import ServiceLocator
from src.core.services import initialize_services
from src.infrastructure.logging.setup import setup_logging
from src.services.moodle.notification_handler import MoodleNotificationHandler
from src.ui.cli.screen import animate_logo, logo_lines


def main() -> None:
    """Main entry point of the application."""
    setup_logging()
    animate_logo(logo_lines)
    logging.info("Starting Moodle Mate...")

    try:
        # Initialize all services
        initialize_services()

        # Get required services from locator
        locator = ServiceLocator()
        config = locator.get("config", Config)
        notification_processor = locator.get(
            "notification_processor", NotificationProcessor
        )
        moodle_handler = locator.get("moodle_handler", MoodleNotificationHandler)

        # Main loop
        while True:
            try:
                if notification := moodle_handler.fetch_newest_notification():
                    notification_processor.process(notification)

                time.sleep(config.notification.fetch_interval)

            except Exception as e:
                logging.error(f"Error during execution: {str(e)}")
                time.sleep(10)

    except KeyboardInterrupt:
        logging.info("Shutting down gracefully...")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        raise


if __name__ == "__main__":
    main()
