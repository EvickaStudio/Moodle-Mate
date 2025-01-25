import logging
import random
from datetime import datetime
from typing import Optional

from src.core.notification.base import NotificationProvider
from src.core.version import __version__
from src.infrastructure.http.request_manager import request_manager

logger = logging.getLogger(__name__)


class DiscordProvider(NotificationProvider):
    """Discord notification provider with rich embed support."""

    def __init__(self, webhook_url: str, bot_name: str, thumbnail_url: str) -> None:
        self.webhook_url = webhook_url
        self.bot_name = bot_name
        self.thumbnail_url = thumbnail_url
        self.session = request_manager.session

    @staticmethod
    def random_color() -> int:
        return int(
            "#{:02x}{:02x}{:02x}".format(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )[1:],
            16,
        )

    def send(self, subject: str, content: str, summary: Optional[str] = None) -> bool:
        """Send a notification via Discord webhook."""
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            embed = {
                "title": subject,
                "description": content[:2000],  # Discord limit
                "color": self.random_color(),
                "thumbnail": (
                    {"url": self.thumbnail_url} if self.thumbnail_url else None
                ),
                "fields": [] if summary else None,  # Initialize as None if no summary
                "footer": {
                    "text": f"{current_time} - Moodle-Mate v{__version__}",
                    "icon_url": "https://raw.githubusercontent.com/EvickaStudio/Moodle-Mate/main/assets/logo.png",
                },
            }

            if summary:
                embed["fields"] = [  # Directly assign list instead of using append
                    {
                        "name": "TL;DR",
                        "value": summary[:1024],  # Discord limit
                        "inline": False,
                    }
                ]

            # Remove None values
            embed = {k: v for k, v in embed.items() if v is not None}

            payload = {
                "username": self.bot_name,
                "avatar_url": "https://raw.githubusercontent.com/EvickaStudio/Moodle-Mate/main/assets/logo.png",
                "embeds": [embed],
            }

            request_manager.update_headers({"Content-Type": "application/json"})
            response = self.session.post(self.webhook_url, json=payload)

            if response.status_code == 204:
                logger.info("Successfully sent Discord notification")
                return True

            response.raise_for_status()
            logger.error(
                "Discord API returned unexpected status code: %d, Response: %s",
                response.status_code,
                response.text,
            )
            return False

        except Exception as e:
            logger.error("Failed to send Discord message: %s", str(e))
            return False
