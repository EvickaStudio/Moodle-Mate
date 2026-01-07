import argparse
import logging
import sys

from src.app import MoodleMateApp
from src.config import Settings
from src.core.notification.processor import NotificationProcessor
from src.core.notification.summarizer import NotificationSummarizer
from src.core.state_manager import StateManager
from src.infrastructure.http.request_manager import request_manager
from src.infrastructure.logging.setup import setup_logging
from src.providers.notification import initialize_providers
from src.services.ai.chat import GPT
from src.services.moodle.api import MoodleAPI
from src.services.moodle.notification_handler import MoodleNotificationHandler
from src.ui.cli.screen import print_logo


def main() -> None:
    """Main entry point of the application."""
    parser = argparse.ArgumentParser(
        description="Moodle Mate - Your Smart Moodle Notification Assistant"
    )
    parser.add_argument(
        "--test-notification",
        action="store_true",
        help="Send a test notification to all configured providers",
    )
    args = parser.parse_args()

    setup_logging()

    # Fast startup - just print the logo
    print_logo()
    logging.info("Starting Moodle Mate...")

    # Initialize Configuration
    try:
        settings = Settings()
    except Exception as e:
        logging.critical(f"Failed to load configuration: {e}")
        logging.critical(
            "Please ensure .env file exists or environment variables are set."
        )
        sys.exit(1)

    # Initialize Services
    try:
        initialize_and_run_app(settings, args)
    except Exception as e:
        logging.critical(f"Fatal error during startup: {e}", exc_info=True)
        sys.exit(1)


def initialize_and_run_app(settings: Settings, args: argparse.Namespace) -> None:
    # Apply network defaults early
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
