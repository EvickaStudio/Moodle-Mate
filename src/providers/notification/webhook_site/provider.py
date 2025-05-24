import logging

import requests

from src.core.notification.base import NotificationProvider
from src.infrastructure.http.request_manager import request_manager

logger = logging.getLogger(__name__)


class WebhookSiteProvider(NotificationProvider):
    """Webhook.site notification provider for testing and debugging."""

    def __init__(self, webhook_url: str, include_summary: bool = True) -> None:
        """Initialize Webhook.site provider.

        Args:
            webhook_url: Webhook.site URL to send notifications to
            include_summary: Whether to include summary as a separate field
        """
        self.webhook_url = webhook_url
        self.include_summary = include_summary
        self.session = request_manager.session

    def send(self, subject: str, message: str, summary: str | None = None) -> bool:
        """Send a notification to Webhook.site.

        Args:
            subject: Notification subject/title
            message: Main notification content
            summary: Optional summary text

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create the payload
            payload = {
                "subject": subject,
                "message": message,
            }

            # Include summary if available and configured to include it
            if summary and self.include_summary:
                payload["summary"] = summary

            # Send the request
            request_manager.update_headers({"Content-Type": "application/json"})
            response = self.session.post(self.webhook_url, json=payload)

            if 200 <= response.status_code < 300:
                logger.info("Successfully sent Webhook.site notification")
                return True

            logger.error(
                "Webhook.site API returned unexpected status code: %d, Response: %s",
                response.status_code,
                response.text,
            )
            return False

        except requests.exceptions.RequestException as req_e:
            logger.error(f"Failed to send Webhook.site message: {req_e!s}")
            return False
        except Exception as e:
            logger.error(f"Failed to send Webhook.site message: {e!s}", exc_info=True)
            return False
