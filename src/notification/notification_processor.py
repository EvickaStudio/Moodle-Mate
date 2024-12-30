import logging

from src.filters import convert
from src.moodle.moodle_notification_handler import NotificationData
from src.notification.notification_sender import NotificationSender
from src.notification.notification_summarizer import NotificationSummarizer
from src.utils import Config

logger = logging.getLogger(__name__)


class NotificationProcessor:
    """Processes and sends notifications."""

    def __init__(self, config: Config) -> None:
        """Initialize the notification processor.

        Args:
            config: Application configuration
        """
        self.config = config

        # Initialize components
        self.summarizer = NotificationSummarizer(config)
        self.sender = NotificationSender(config)

        # Get notification settings
        self.max_retries = config.notification.max_retries
        self.fetch_interval = config.notification.fetch_interval

    def process_notification(self, notification: NotificationData) -> None:
        """Process and send a notification.

        Args:
            notification: The notification to process
        """
        try:
            # Extract notification content
            html_content = notification.get("fullmessagehtml", "")
            subject = notification.get("subject", "No subject")

            if not html_content:
                logger.warning("Empty notification content received")
                return

            # Convert HTML to Markdown
            markdown_content = convert(html_content)

            # Initialize summary as None
            summary = None

            # Summarize if enabled
            if self.config.ai.enabled:
                try:
                    summary = self.summarizer.summarize(markdown_content)
                except Exception as e:
                    logger.error(f"Failed to summarize notification: {str(e)}")

            # Send notification with both markdown content and summary
            self.sender.send(subject=subject, message=markdown_content, summary=summary)

        except Exception as e:
            logger.error(f"Failed to process notification: {str(e)}")
