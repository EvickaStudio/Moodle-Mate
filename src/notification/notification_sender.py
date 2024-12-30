import logging
from typing import Optional

from src.notification.discord_sender import DiscordSender
from src.notification.pushbullet_sender import PushbulletSender
from src.utils import Config

logger = logging.getLogger(__name__)


class NotificationSender:
    """Handles sending notifications to configured services."""

    def __init__(self, config: Config) -> None:
        """Initialize notification sender.

        Args:
            config: Application configuration
        """
        self.config = config
        self.senders = []

        # Initialize Discord sender if enabled
        if config.discord.enabled:
            try:
                self.senders.append(
                    DiscordSender(
                        webhook_url=config.discord.webhook_url,
                        bot_name=config.discord.bot_name,
                        thumbnail_url=config.discord.thumbnail_url,
                    )
                )
                logger.info("Discord sender initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Discord sender: {str(e)}")

        # Initialize Pushbullet sender if enabled
        if config.pushbullet.enabled:
            try:
                self.senders.append(PushbulletSender(api_key=config.pushbullet.api_key))
                logger.info("Pushbullet sender initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Pushbullet sender: {str(e)}")

        if not self.senders:
            logger.warning("No notification senders were initialized")

    def send(self, subject: str, message: str, summary: Optional[str] = None) -> None:
        """Send a notification through all configured services.

        Args:
            subject: The notification subject
            message: The notification message in Markdown format
            summary: Optional AI-generated summary
        """
        if not self.senders:
            logger.warning("No notification senders available")
            return

        for sender in self.senders:
            try:
                # For Discord, pass both message and summary
                if isinstance(sender, DiscordSender):
                    sender.send(subject, message, summary)
                # For other senders, combine message and summary if available
                else:
                    full_message = message
                    if summary:
                        full_message += f"\n\nTLDR (AI Summary):\n{summary}"
                    sender.send(subject, full_message)

                logger.info(f"Notification sent via {sender.__class__.__name__}")
            except Exception as e:
                logger.error(
                    f"Failed to send notification via {sender.__class__.__name__}: {str(e)}"
                )
