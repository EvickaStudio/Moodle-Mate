from src.moodle.moodle_notification_handler import MoodleNotificationHandler
from src.notification.notification_processor import NotificationProcessor
from src.notification.notification_sender import NotificationSender
from src.notification.notification_summarizer import NotificationSummarizer
from src.ui.screen import clear_screen, logo
from src.ui.setup_logging import setup_logging
from src.utils.load_config import Config

# Constants
SLEEP_DURATION_SECONDS = 60  # Sleep duration between each loop iteration
MAX_RETRIES = 3  # Max retries for fetching and processing notifications

if __name__ == "__main__":
    # Clear the screen and print the logo
    clear_screen()
    print(logo)

    # Set up logging
    setup_logging()

    # Initialize Config object
    config = Config("config.ini")

    # Read configurations
    summary = int(config.get_config("moodle", "summary") or 0)
    botname = config.get_config("moodle", "botname") or "MoodleMate"
    thumbnail = (
        config.get_config("moodle", "thumbnailURL")
        or "https://raw.githubusercontent.com/EvickaStudio/Moodle-Mate/main/assets/logo.png"
    )

    # Initialize other classes with the Config object
    moodle_handler = MoodleNotificationHandler(config)
    summarizer = NotificationSummarizer(config)
    sender = NotificationSender(config, botname, thumbnail)

    # Start the notification processor
    processor = NotificationProcessor(
        handler=moodle_handler,
        summarizer=summarizer,
        sender=sender,
        summary_setting=summary,
        sleep_duration=SLEEP_DURATION_SECONDS,
        max_retries=MAX_RETRIES,
    )
    processor.run()
