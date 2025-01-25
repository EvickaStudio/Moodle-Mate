import json
import logging
from typing import Optional

from requests.exceptions import RequestException
from src.core.notification.base import NotificationProvider
from src.infrastructure.http.request_manager import request_manager

logger = logging.getLogger(__name__)


class DiscordProvider(NotificationProvider):
    """Discord notification provider implementation."""

    def __init__(
        self,
        webhook_url: str,
        bot_name: str = "MoodleMate",
        thumbnail_url: Optional[str] = None,
    ):
        if not webhook_url:
            raise ValueError("Discord webhook URL is required")

        self.webhook_url = webhook_url
        self.bot_name = bot_name
        self.thumbnail_url = thumbnail_url
        self.session = request_manager.session
        request_manager.update_headers({"Content-Type": "application/json"})

    def send(self, subject: str, message: str, summary: Optional[str] = None) -> bool:
        try:
            description = ""
            if summary:
                description = "**TLDR (AI Summary):**\n" + summary + "\n\n"
            description += "**Message Content:**\n" + message

            embed = {
                "title": subject,
                "description": description,
                "color": 3447003,
                "footer": {"text": "MoodleMate | Made with ❤️ by EvickaStudio"},
            }

            if self.thumbnail_url:
                embed["thumbnail"] = {"url": self.thumbnail_url}

            payload = {
                "username": self.bot_name,
                "embeds": [embed],
                "avatar_url": self.thumbnail_url,
            }

            response = self.session.post(
                self.webhook_url,
                data=json.dumps(payload),
            )
            response.raise_for_status()
            return True

        except RequestException as e:
            logger.error(f"Failed to send Discord message: {str(e)}")
            return False 