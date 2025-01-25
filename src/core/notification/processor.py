import logging
from typing import List

from src.core.config.loader import Config
from src.core.notification.base import NotificationProvider
from src.core.notification.summarizer import NotificationSummarizer
from src.services.markdown import convert

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
        self.summarizer = NotificationSummarizer(config) if config.ai.enabled else None

    def process(self, notification: dict) -> None:
        """Process and send a notification."""
        try:
            html_content = notification.get("fullmessagehtml", "")
            subject = notification.get("subject", "No subject")

            if not html_content:
                logger.warning(
                    "[NotificationProcessor] Empty notification content received"
                )
                return

            # Convert HTML to Markdown
            try:
                markdown_content = convert(html_content)
                logger.debug("[NotificationProcessor] Converted HTML to Markdown")
            except Exception as e:
                logger.error(
                    "[NotificationProcessor] Failed to convert HTML to Markdown: %s",
                    str(e),
                    exc_info=True,
                )
                return

            # Get AI summary if enabled
            summary = None
            if self.config.ai.enabled and self.summarizer:
                try:
                    summary = self.summarizer.summarize(markdown_content)
                    logger.debug(
                        "[NotificationProcessor] Generated AI summary: %s",
                        summary[:100],
                    )
                except Exception as e:
                    logger.error(
                        "[NotificationProcessor] Failed to generate summary: %s",
                        str(e),
                        exc_info=True,
                    )

            # Send via all providers
            for provider in self.providers:
                try:
                    # Pass both content and summary to provider
                    success = provider.send(
                        subject=subject,
                        content=markdown_content,
                        summary=summary if summary else None,
                    )
                    if success:
                        logger.info(
                            "[NotificationProcessor] Sent via %s",
                            provider.__class__.__name__,
                        )
                    else:
                        logger.error(
                            "[NotificationProcessor] Failed to send via %s",
                            provider.__class__.__name__,
                        )
                except Exception as e:
                    logger.error(
                        "[NotificationProcessor] Error with %s: %s",
                        provider.__class__.__name__,
                        str(e),
                        exc_info=True,
                    )

        except Exception as e:
            logger.error(
                "[NotificationProcessor] Failed to process notification: %s",
                str(e),
                exc_info=True,
            )
