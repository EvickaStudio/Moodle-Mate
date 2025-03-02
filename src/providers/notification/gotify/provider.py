import logging
from typing import Any, Dict, Optional

from src.core.notification.base import NotificationProvider
from src.infrastructure.http.request_manager import request_manager

logger = logging.getLogger(__name__)


class GotifyProvider(NotificationProvider):
    """Gotify notification provider for sending notifications to a self-hosted Gotify server."""

    def __init__(
        self,
        server_url: str,
        app_token: str,
        priority: int = 5,
        include_summary: bool = True,
        use_markdown: bool = True,
    ) -> None:
        """Initialize Gotify provider.

        Args:
            server_url: URL of the Gotify server (e.g., https://gotify.example.com)
            app_token: Application token for authentication
            priority: Message priority (0-10, default: 5)
            include_summary: Whether to include AI summary in the notification
            use_markdown: Whether to send messages as markdown
        """
        self.server_url = server_url.rstrip("/")
        self.app_token = app_token
        self.priority = priority
        self.include_summary = include_summary
        self.use_markdown = use_markdown
        self.session = request_manager.session

    def send(self, subject: str, message: str, summary: Optional[str] = None) -> bool:
        """Send a notification via Gotify.

        Args:
            subject: Notification subject/title
            message: Main notification content
            summary: Optional summary text

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create the notification payload
            payload: Dict[str, Any] = {
                "title": subject,
                "message": message,
                "priority": self.priority,
            }

            # Add summary to the message if available and configured
            if summary and self.include_summary:
                payload["message"] += f"\n\n**Summary:**\n{summary}"

            # Add extras for markdown support if enabled
            if self.use_markdown:
                payload["extras"] = {
                    "client::display": {"contentType": "text/markdown"}
                }

            # Send the request
            url = f"{self.server_url}/message?token={self.app_token}"
            response = self.session.post(url, json=payload)

            if 200 <= response.status_code < 300:
                logger.info("Successfully sent Gotify notification")
                return True

            logger.error(
                "Gotify API returned unexpected status code: %d, Response: %s",
                response.status_code,
                response.text,
            )
            return False

        except Exception as e:
            logger.error("Failed to send Gotify notification: %s", str(e))
            return False
