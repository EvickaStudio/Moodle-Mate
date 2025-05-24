from abc import ABC, abstractmethod


class NotificationProvider(ABC):
    """
    Abstract base class for all notification provider implementations.

    This class defines the common interface that all notification providers
    (e.g., Discord, Pushbullet, Slack) must adhere to. It ensures that the
    `NotificationProcessor` can interact with any provider polymorphically.

    Subclasses must implement the `send` method.

    The primary purpose of this abstraction is to decouple the core notification
    processing logic from the specific details of how notifications are sent to
    different services or platforms.
    """

    @abstractmethod
    def send(self, subject: str, message: str, summary: str | None = None) -> bool:
        """
        Send a notification with the given subject, message, and optional summary.

        This method must be implemented by concrete provider subclasses. It should
        handle all aspects of formatting the notification appropriately for the
        target service and dispatching it.

        Args:
            subject (str): The subject or title of the notification.
            message (str): The main content of the notification. This is typically
                Markdown formatted.
            summary (str | None, optional): An optional AI-generated summary of the
                message. Providers can choose to use this summary, the full message,
                or both. Defaults to None.

        Returns:
            bool: True if the notification was sent successfully to the provider's API
                  or service, False otherwise (e.g., due to API errors, network issues,
                  or invalid configuration for that provider).

        Raises:
            NotImplementedError: If a subclass does not implement this method (though
                this is enforced by @abstractmethod at class instantiation time).
            Potentially other exceptions specific to the provider's SDK or API interactions,
            which should ideally be caught and handled within the `send` method to return
            True/False, or logged appropriately.
        """
        pass
