import logging
import time

from src.services.moodle.notification_handler import MoodleNotificationHandler
from src.core.notification.processor import NotificationProcessor
from src.ui.cli.screen import animate_logo, logo_lines
from src.core.config.loader import Config
from src.infrastructure.logging.setup import setup_logging
from src.providers.notification import initialize_providers


def main() -> None:
    """Main entry point of the application."""
    setup_logging()
    animate_logo(logo_lines)
    logging.info("Starting Moodle Mate...")

    try:
        # Load configuration
        config = Config()

        # Initialize notification providers
        providers = initialize_providers(config)

        # Create notification processor with providers
        notification_processor = NotificationProcessor(config, providers)

        # Initialize handlers
        moodle_handler = MoodleNotificationHandler(config)

        # Main loop
        while True:
            try:
                # Fetch latest notification
                notification = moodle_handler.fetch_newest_notification()
                if notification:
                    # Process and send notification
                    notification_processor.process(notification)

                # Sleep for configured interval
                time.sleep(config.notification.fetch_interval)

            except Exception as e:
                logging.error(f"Error during execution: {str(e)}")
                # Sleep for a bit before retrying
                time.sleep(10)

    except KeyboardInterrupt:
        logging.info("Shutting down gracefully...")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        raise


if __name__ == "__main__":
    main()
