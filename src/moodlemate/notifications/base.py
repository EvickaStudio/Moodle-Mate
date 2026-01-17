from abc import ABC, abstractmethod


class NotificationProvider(ABC):
    """Base class for notification providers."""

    provider_name: str = ""

    @abstractmethod
    def send(self, subject: str, message: str, summary: str | None = None) -> bool:
        """Send a notification.

        Args:
            subject: Message subject/title
            message: Message content
            summary: Optional AI-generated summary

        Returns:
            bool: True if sent successfully, False otherwise
        """
        pass
