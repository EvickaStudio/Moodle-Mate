import logging
from typing import Optional

from src.core.notification.base import NotificationProvider
from src.infrastructure.http.request_manager import request_manager

logger = logging.getLogger(__name__)


class TemplateNotificationProvider(NotificationProvider):
    """Template for creating new notification providers.

    Why: Provides a minimal, production-ready skeleton that matches Moodle-Mate's
    discovery, configuration, and HTTP practices so you can add providers quickly.

    Usage:
        1) Copy this file to: src/providers/notification/your_service_name/provider.py
        2) Rename the class to: YourServiceNameProvider
        3) Implement request logic inside send()
        4) Run: python main.py --gen-config to generate config.ini prompts

    Example config.ini section (auto-generated from __init__ parameters):
        [your_service_name]
        enabled = 1
        api_key = your_api_key
        endpoint = https://api.yourservice.com
    """

    def __init__(
        self, api_key: str, endpoint: str = "https://api.example.com", **kwargs
    ) -> None:
        """Initialize the provider with configuration.

        Args:
            api_key: API key for authentication. Must be non-empty.
            endpoint: Base API endpoint URL. Must start with http(s) and not end with '/'.
            **kwargs: Optional additional parameters from config.ini (strings).

        Raises:
            ValueError: If required parameters are invalid.
        """
        if not api_key:
            raise ValueError("api_key must not be empty")
        if not endpoint.startswith(("http://", "https://")):
            raise ValueError("endpoint must start with http:// or https://")

        self.api_key = api_key
        self.endpoint = endpoint.rstrip("/")
        self.session = request_manager.session
        self.config = kwargs  # All extra values from config.ini arrive as strings

    def send(self, subject: str, message: str, summary: Optional[str] = None) -> bool:
        """Send a notification through your service.

        Args:
            subject: Message subject/title.
            message: Message content in Markdown format.
            summary: Optional AI-generated summary in Markdown.

        Returns:
            True if sent successfully; False otherwise.

        Notes:
            - Prefer request_manager.update_headers(...) for per-request headers.
            - Validate and normalize inputs; never log secrets.
        """
        if not subject or not subject.strip():
            logger.error("Cannot send notification: subject is empty")
            return False
        if not message or not message.strip():
            logger.error("Cannot send notification: message is empty")
            return False

        try:
            # Example (uncomment and adapt):
            # request_manager.update_headers({
            #     "Authorization": f"Bearer {self.api_key}",
            #     "Content-Type": "application/json",
            # })
            # payload = {"title": subject, "body": message}
            # if summary:
            #     payload["summary"] = summary
            # response = self.session.post(f"{self.endpoint}/send", json=payload)
            # if 200 <= response.status_code < 300:
            #     logger.info("Template provider: notification sent successfully")
            #     return True
            # logger.error("Template provider HTTP %d: %s", response.status_code, response.text)
            # return False

            # For the template, just log and simulate success
            logger.info("Template provider would send: %s", subject)
            return True
        except Exception as exc:
            logger.error("Template provider failed: %s", str(exc))
            return False
