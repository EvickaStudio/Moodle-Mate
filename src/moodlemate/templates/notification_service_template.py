import logging

from moodlemate.infrastructure.http.request_manager import request_manager
from moodlemate.notifications.base import NotificationProvider

logger = logging.getLogger(__name__)


class TemplateNotificationProvider(NotificationProvider):
    """
    Template for creating new notification providers.

    Usage:
    1. Copy this file to src/moodlemate/providers/notification/<name>/provider.py
    2. Rename the class.
    3. Implement the `send` method.
    4. Add a corresponding Config model in src/moodlemate/config.py.
    5. Add the config field to the Settings class in src/moodlemate/config.py.
    """

    def __init__(self, api_key: str, some_setting: int = 10) -> None:
        """
        Initialize the provider.

        The arguments here must match the fields defined in your Config model
        in src/moodlemate/config.py (excluding 'enabled').

        Args:
            api_key: Passed from Settings.
            some_setting: Passed from Settings.
        """
        self.api_key = api_key
        self.some_setting = some_setting
        self.session = request_manager.get_session("provider_template")

    def send(self, subject: str, message: str, summary: str | None = None) -> bool:
        """
        Send the notification.

        Args:
            subject: The title of the notification.
            message: The main content (Markdown).
            summary: An optional AI-generated summary.

        Returns:
            bool: True if successful, False otherwise.
        """
        # 1. Validate inputs
        if not subject or not message:
            logger.error("Cannot send empty notification")
            return False

        try:
            # 2. Prepare payload
            # payload = {
            #     "title": subject,
            #     "text": message
            # }
            # if summary:
            #     payload["summary"] = summary

            # 3. Send request using a provider-scoped session and per-request headers
            # response = self.session.post(
            #     "https://api.example.com/send",
            #     json=payload,
            #     headers={"Authorization": f"Bearer {self.api_key}"},
            # )

            # 4. Check response
            # if response.status_code == 200:
            #     logger.info("Notification sent successfully")
            #     return True

            # logger.error(f"Failed to send: {response.status_code} - {response.text}")
            # return False

            logger.info(f"Template provider received: {subject}")
            return True

        except Exception as e:
            logger.error(f"Exception in provider: {e}")
            return False
