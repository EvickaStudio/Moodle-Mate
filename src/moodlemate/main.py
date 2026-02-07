import argparse
import logging
import sys

from moodlemate.ai.chat import GPT
from moodlemate.app import MoodleMateApp
from moodlemate.config import Settings
from moodlemate.core.state_manager import StateManager
from moodlemate.infrastructure.http.request_manager import request_manager
from moodlemate.infrastructure.logging.setup import setup_logging
from moodlemate.moodle.api import MoodleAPI
from moodlemate.moodle.notification_handler import MoodleNotificationHandler
from moodlemate.notifications.processor import NotificationProcessor
from moodlemate.notifications.summarizer import NotificationSummarizer
from moodlemate.providers.notification import initialize_providers
from moodlemate.ui.cli.screen import print_logo


def main() -> None:
    """Entry point for the package. Initializes and starts the application."""
    parser = argparse.ArgumentParser(
        description="Moodle Mate - Your Smart Moodle Notification Assistant"
    )
    parser.add_argument(
        "--test-notification",
        action="store_true",
        help="Send a test notification to all configured providers",
    )
    args = parser.parse_args()

    # Initialize logging and print the Moodle Mate logo.
    setup_logging()
    print_logo()
    logging.info("Starting Moodle Mate...")

    # Initialize settings for all components and services.
    try:
        settings = Settings()
    except Exception as e:
        logging.critical(f"Failed to load configuration: {e}")
        logging.critical(
            "Please ensure .env file exists or environment variables are set."
        )
        sys.exit(1)

    try:
        initialize_and_run_app(settings, args)
    except Exception as e:
        logging.critical(f"Fatal error during startup: {e}", exc_info=True)
        sys.exit(1)


def initialize_and_run_app(settings: Settings, args: argparse.Namespace) -> None:
    # Apply network defaults
    request_manager.configure(
        connect_timeout=settings.notification.connect_timeout,
        read_timeout=settings.notification.read_timeout,
        retry_total=settings.notification.retry_total,
        backoff_factor=settings.notification.retry_backoff_factor,
    )

    # State Manager
    state_manager = StateManager()

    # Moodle API
    moodle_api = MoodleAPI(
        url=settings.moodle.url,
        username=settings.moodle.username,
        password=settings.moodle.password,
        session_encryption_key=settings.session_encryption_key,
    )

    # AI / Summarization
    summarizer = None
    if settings.ai.enabled:
        gpt = GPT()
        gpt.api_key = settings.ai.api_key
        if settings.ai.endpoint:
            gpt.endpoint = settings.ai.endpoint

        summarizer = NotificationSummarizer(settings, gpt)

    # Notification Providers
    providers = initialize_providers(settings)

    # Notification Processor
    notification_processor = NotificationProcessor(
        settings, providers, state_manager, summarizer
    )

    # Moodle Handler
    moodle_handler = MoodleNotificationHandler(settings, moodle_api, state_manager)

    # App
    app = MoodleMateApp(
        settings=settings,
        notification_processor=notification_processor,
        moodle_handler=moodle_handler,
        moodle_api=moodle_api,
        state_manager=state_manager,
    )

    if args.test_notification:
        app.send_test_notification()
    else:
        app.run()


if __name__ == "__main__":
    main()
