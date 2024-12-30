import json
import logging
from typing import Optional

from requests.exceptions import RequestException

from src.utils.request_manager import request_manager

logger = logging.getLogger(__name__)


class DiscordSender:
    """Handles sending notifications to Discord via webhooks."""

    def __init__(
        self,
        webhook_url: str,
        bot_name: str,
        thumbnail_url: Optional[str] = None,
    ):
        """Initialize Discord sender.

        Args:
            webhook_url: Discord webhook URL
            bot_name: Name to display for the bot
            thumbnail_url: URL for the bot's thumbnail image
        """
        if not webhook_url:
            raise ValueError("Discord webhook URL is required")

        self.webhook_url = webhook_url
        self.bot_name = bot_name or "MoodleMate"
        self.thumbnail_url = thumbnail_url
        self.session = request_manager.session
        request_manager.update_headers(
            {
                "Content-Type": "application/json",
            }
        )

    def send(self, subject: str, message: str, summary: Optional[str] = None) -> None:
        """Send a message to Discord.

        Args:
            subject: Message subject/title
            message: Message content in Markdown format
            summary: Optional AI-generated summary

        Raises:
            requests.RequestException: If the request fails
        """
        # Prepare the description with both message and summary
        description = ""
        if summary:
            description = "**TLDR (AI Summary):**\n" + summary + "\n\n"
        description += "**\n\nMessage Content:**\n" + message

        embed = {
            "title": subject,
            "description": description,
            "color": 3447003,  # Blue color
            "footer": {"text": "MoodleMate | Made with ❤️ by EvickaStudio"},
        }

        if self.thumbnail_url:
            embed["thumbnail"] = {"url": self.thumbnail_url}

        payload = {
            "username": self.bot_name,
            "embeds": [embed],
            "avatar_url": self.thumbnail_url,  # Keep the webhook avatar
        }

        response = self.session.post(
            self.webhook_url,
            data=json.dumps(payload),
        )

        if not response.ok:
            raise RequestException(
                f"Failed to send Discord message: {response.status_code} - {response.text}"
            )
