import logging
import time

from src.moodle import MoodleNotificationHandler
from src.notification import NotificationProcessor
from src.ui import animate_logo, logo_lines, setup_logging
from src.utils import Config


def main() -> None:
    """Main entry point of the application."""
    setup_logging()
    animate_logo(logo_lines)
    logging.info("Starting Moodle Mate...")

    try:
        # Load configuration
        config = Config()

        # Initialize handlers
        moodle_handler = MoodleNotificationHandler(config)
        notification_processor = NotificationProcessor(config)

        # Main loop
        while True:
            try:
                # Fetch latest notification
                notification = moodle_handler.fetch_newest_notification()
                if notification:
                    # Process and send notification
                    notification_processor.process_notification(notification)

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
