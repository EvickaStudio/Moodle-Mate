import logging
from typing import List

from src.core.notification.base import NotificationProvider
from src.core.notification.summarizer import NotificationSummarizer
from src.services.markdown import convert
from src.core.config.loader import Config

logger = logging.getLogger(__name__)


class NotificationProcessor:
    """Processes and sends notifications."""

    def __init__(self, config: Config, providers: List[NotificationProvider]) -> None:
        """Initialize the notification processor.

        Args:
            config: Application configuration
            providers: List of notification providers
        """
        self.config = config
        self.providers = providers
        self.summarizer = NotificationSummarizer(config)

    def process(self, notification: dict) -> None:
        """Process and send a notification."""
        try:
            html_content = notification.get("fullmessagehtml", "")
            subject = notification.get("subject", "No subject")

            if not html_content:
                logger.warning("Empty notification content received")
                return

            # Convert HTML to Markdown
            markdown_content = convert(html_content)

            # Get AI summary if enabled
            summary = None
            if self.config.ai.enabled:
                try:
                    summary = self.summarizer.summarize(markdown_content)
                except Exception as e:
                    logger.error(f"Failed to summarize: {str(e)}")

            # Send via all providers
            for provider in self.providers:
                try:
                    success = provider.send(subject, markdown_content, summary)
                    if success:
                        logger.info(f"Sent via {provider.__class__.__name__}")
                    else:
                        logger.error(f"Failed to send via {provider.__class__.__name__}")
                except Exception as e:
                    logger.error(f"Error with {provider.__class__.__name__}: {str(e)}")

        except Exception as e:
            logger.error(f"Failed to process notification: {str(e)}")
