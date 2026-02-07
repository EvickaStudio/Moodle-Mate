import logging

from moodlemate.infrastructure.http.request_manager import request_manager
from moodlemate.notifications.base import NotificationProvider

logger = logging.getLogger(__name__)


class PushbulletProvider(NotificationProvider):
    """
    Pushbullet notification provider for sending notifications to devices.

    This provider sends the notification formatted as Markdown, this is a byproduct
    of the html to markdown conversion for Moodle. The Markdown could be theoretically
    be converted to a more readable format like plain text for the Pushbullet notification,
    but in my testing, it looked more unreadable than the Markdown.
    """

    def __init__(self, api_key: str, include_summary: bool = True) -> None:
        """Initialize Pushbullet provider.

        Args:
            api_key: Pushbullet API key for authentication
            include_summary: Whether to include AI summary in the notification
        """
        self.api_key = api_key
        self.include_summary = include_summary
        self.base_url = "https://api.pushbullet.com/v2"
        self.session = request_manager.get_session("provider_pushbullet")

    def send(self, subject: str, message: str, summary: str | None = None) -> bool:
        """Send a notification via Pushbullet.

        Args:
            subject: Notification subject/title
            message: Main notification content
            summary: Optional summary text

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create the notification payload
            payload = {"type": "note", "title": subject, "body": message}

            # Add summary to the body if available and configured
            if summary and self.include_summary:
                payload["body"] += f"\n\n**Summary:**\n{summary}"

            # Set up headers with API key
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            # Send the request with per-request headers to avoid cross-provider leakage.
            response = self.session.post(
                f"{self.base_url}/pushes",
                json=payload,
                headers=headers,
            )

            if 200 <= response.status_code < 300:
                logger.info("Successfully sent Pushbullet notification")
                return True

            logger.error(
                "Pushbullet API returned unexpected status code: %d, Response: %s",
                response.status_code,
                response.text,
            )
            return False

        except Exception as e:
            logger.error("Failed to send Pushbullet notification: %s", str(e))
            return False
