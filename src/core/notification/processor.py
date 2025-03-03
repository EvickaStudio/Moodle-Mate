import logging
from typing import List, Optional

from src.core.config.loader import Config
from src.core.notification.base import NotificationProvider
from src.core.notification.summarizer import NotificationSummarizer
from src.core.service_locator import ServiceLocator
from src.services.markdown import convert
from src.services.notification.storage import NotificationStorage

logger = logging.getLogger(__name__)


class NotificationProcessor:
    """Processes and sends notifications."""

    _instance = None
    _flask_app = None  # Add a class variable to store the Flask app

    def __new__(cls, config: Config, providers: List[NotificationProvider]):
        if cls._instance is None:
            cls._instance = super(NotificationProcessor, cls).__new__(cls)
            cls._instance._init_processor(config, providers)
        return cls._instance

    def _init_processor(self, config: Config, providers: List[NotificationProvider]):
        """Initialize the notification processor."""
        self.config = config
        self.providers = providers
        self.summarizer = NotificationSummarizer(config) if config.ai.enabled else None

        # Initialize storage service
        try:
            self.storage = ServiceLocator().get(
                "notification_storage", NotificationStorage
            )
        except Exception as e:
            logger.error(f"Failed to initialize notification storage: {str(e)}")
            self.storage = None

    def set_flask_app(self, app):
        """Set the Flask app for database operations."""
        NotificationProcessor._flask_app = app
        # Update the storage service if it exists
        if self.storage:
            self.storage.set_app(app)
            logger.info("Flask app set in notification storage service")

    def process(self, notification: dict) -> None:
        """Process and send a notification through all enabled providers."""
        try:
            # Extract notification data
            subject = self._get_notification_subject(notification)
            message = self._get_notification_message(notification)

            # Generate summary if enabled
            summary = self._generate_summary(message) if self.summarizer else None

            # Store notification in database if storage is available
            if self.storage:
                success = self.storage.store_notification(
                    notification, message, summary
                )
                if success:
                    logger.info(f"Notification {notification['id']} stored in database")
                else:
                    logger.warning(
                        f"Failed to store notification {notification['id']} in database"
                    )

            # Send through providers
            self._send_to_providers(subject, message, summary)

        except Exception as e:
            logging.error(f"Failed to process notification: {str(e)}", exc_info=True)

    def _get_notification_subject(self, notification: dict) -> str:
        """Extract and validate notification subject."""
        if subject := notification.get("subject", "").strip():
            return subject
        else:
            raise ValueError("Notification subject is empty")

    def _get_notification_message(self, notification: dict) -> str:
        """Extract and convert notification message."""
        if message := notification.get("fullmessagehtml", "").strip():
            return convert(message)  # Convert HTML to Markdown
        else:
            raise ValueError("Notification message is empty")

    def _generate_summary(self, message: str) -> Optional[str]:
        """Generate AI summary of message."""
        try:
            return (
                None if self.summarizer is None else self.summarizer.summarize(message)
            )
        except Exception as e:
            logging.error(f"Failed to generate summary: {str(e)}")
            return None

    def _send_to_providers(
        self, subject: str, message: str, summary: Optional[str]
    ) -> None:
        """Send notification through all providers."""
        for provider in self.providers:
            try:
                success = provider.send(subject, message, summary)
                if not success:
                    logging.error(f"Failed to send via {provider.__class__.__name__}")
            except Exception as e:
                logging.error(
                    f"Error with {provider.__class__.__name__}: {str(e)}", exc_info=True
                )
