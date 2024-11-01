import logging

from src.moodle import MoodleNotificationHandler
from src.notification import (
    NotificationProcessor,
    NotificationSender,
    NotificationSummarizer,
)
from src.ui import animate_logo, clear_screen, logo_lines, setup_logging
from src.utils import Config


def get_int_config(
    config: Config, section: str, option: str, default: int
) -> int:
    """
    Retrieves an integer value from the configuration.
    If the value is missing or invalid, returns the default.
    """
    value = config.get_config(section, option)
    try:
        return int(value)
    except (TypeError, ValueError):
        logging.warning(
            f"Invalid or missing integer for [{section}] {option}, using default {default}."
        )
        return default


def get_str_config(
    config: Config, section: str, option: str, default: str
) -> str:
    """
    Retrieves a string value from the configuration.
    If the value is missing, returns the default.
    """
    value = config.get_config(section, option)
    if value is None:
        logging.warning(
            f"Missing string for [{section}] {option}, using default '{default}'."
        )
        return default
    return value


def main() -> None:
    try:
        # Clear the screen and print the logo
        clear_screen()
        animate_logo(logo_lines)

        # Set up logging
        setup_logging()

        # Initialize Config object
        config = Config("config.ini")

        # Read configurations with error handling
        sleep_duration_seconds: int = get_int_config(
            config, "settings", "FETCH_INTERVAL", 60
        )
        max_retries: int = get_int_config(config, "settings", "MAX_RETRIES", 3)
        summary: int = get_int_config(config, "summary", "SUMMARIZE", 0)
        bot_name: str = get_str_config(
            config, "discord", "BOT_NAME", "Moodle Mate"
        )
        thumbnail: str = get_str_config(
            config,
            "discord",
            "THUMBNAIL_URL",
            "https://raw.githubusercontent.com/EvickaStudio/Moodle-Mate/main/assets/logo.png",
        )

        # Initialize other classes with the Config object
        moodle_handler = MoodleNotificationHandler(config)
        summarizer = NotificationSummarizer(config)
        sender = NotificationSender(config, bot_name, thumbnail)

        # Start the notification processor
        processor = NotificationProcessor(
            handler=moodle_handler,
            summarizer=summarizer,
            sender=sender,
            summary_setting=summary,
            sleep_duration=sleep_duration_seconds,
            max_retries=max_retries,
        )
        processor.run()

    except Exception as e:
        logging.exception("An unexpected error occurred during execution.")
        exit(1)


if __name__ == "__main__":
    main()
