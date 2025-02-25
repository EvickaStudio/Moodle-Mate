from typing import Optional

from src.core.notification.base import NotificationProvider
from src.infrastructure.http.request_manager import request_manager


class TemplateNotificationProvider(NotificationProvider):
    """Template for creating new notification providers.

    To create a new provider:
    1. Copy this file to src/providers/notification/your_service_name/provider.py
    2. Rename the class to YourServiceNameProvider
    3. Implement the required methods
    4. Add configuration in the config.ini file

    Configuration in config.ini:
    [your_service_name]
    enabled = 1
    # Add any other configuration parameters your service needs
    api_key = your_api_key
    endpoint = https://api.yourservice.com
    """

    def __init__(
        self, api_key: str, endpoint: str = "https://api.example.com", **kwargs
    ):
        """Initialize the provider with configuration.

        Args:
            api_key: API key for authentication
            endpoint: API endpoint URL
            **kwargs: Additional configuration parameters
        """
        self.api_key = api_key
        self.endpoint = endpoint.rstrip("/")
        self.session = request_manager.session

        # Store any additional configuration parameters
        self.config = kwargs

    def send(self, subject: str, message: str, summary: Optional[str] = None) -> bool:
        """Send a notification through your service.

        Args:
            subject: Message subject/title
            message: Message content in markdown format
            summary: Optional AI-generated summary

        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            # Implement your service-specific logic here
            # Example:
            # headers = {
            #     "Authorization": f"Bearer {self.api_key}",
            #     "Content-Type": "application/json"
            # }
            #
            # payload = {
            #     "title": subject,
            #     "body": message,
            #     "summary": summary
            # }
            #
            # response = self.session.post(
            #     f"{self.endpoint}/send",
            #     json=payload,
            #     headers=headers
            # )
            #
            # return response.status_code == 200

            # For template, just log and return success
            print(f"Would send notification via template provider: {subject}")
            return True

        except Exception as e:
            print(f"Error sending notification: {str(e)}")
            return False
