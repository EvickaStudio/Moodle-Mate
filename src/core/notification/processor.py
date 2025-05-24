import logging

import requests

from src.core.config.loader import Config
from src.core.notification.base import NotificationProvider
from src.core.notification.summarizer import NotificationSummarizer
from src.services.markdown import convert

logger = logging.getLogger(__name__)


class NotificationProcessor:
    """
    Handles the processing and dispatching of notifications to various providers.

    This class acts as a singleton. It takes a raw Moodle notification (as a dictionary),
    extracts relevant information (subject, message), converts the message from HTML to
    Markdown, optionally generates an AI-powered summary, and then sends the processed
    notification through all configured and enabled notification providers.

    Key responsibilities:
    - Extracting and validating notification content.
    - Converting HTML message content to Markdown.
    - Interfacing with `NotificationSummarizer` for AI summaries (if enabled).
    - Iterating through a list of `NotificationProvider` instances and calling their
      `send` method.
    - Handling errors that may occur during processing or sending.

    Attributes:
        config (Config): The application's configuration object.
        providers (list[NotificationProvider]): A list of initialized and enabled
            notification provider instances.
        summarizer (NotificationSummarizer | None): An instance of the AI summarizer
            if AI features are enabled in the config; otherwise, None.

    Example:
        Assume `app_config` and `active_providers` are already initialized:
        >>> processor = NotificationProcessor(config=app_config, providers=active_providers)
        >>> raw_moodle_notification = {
        ...     'subject': 'New Forum Post',
        ...     'fullmessagehtml': '<p>Check out the new post!</p>'
        ... }
        >>> processor.process(raw_moodle_notification) # This will send the notification
    """

    _instance = None

    def __new__(cls, config: Config, providers: list[NotificationProvider]) -> "NotificationProcessor":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_processor(config, providers)
        return cls._instance

    def _init_processor(self, config: Config, providers: list[NotificationProvider]):
        """Initialize the notification processor."""
        if not isinstance(config, Config):
            raise TypeError("config must be an instance of Config.")
        if not isinstance(providers, list):
            raise TypeError("providers must be a list.")
        if not all(isinstance(p, NotificationProvider) for p in providers):
            raise TypeError(
                "All elements in providers list must be instances of NotificationProvider.",
            )

        self.config = config
        self.providers = providers
        self.summarizer = NotificationSummarizer(config) if config.ai.enabled else None

    def process(self, notification: dict) -> None:
        """
        Process a single raw notification and send it through all enabled providers.

        This is the main public method for this class. It performs the following steps:
        1. Extracts subject and message from the `notification` dictionary.
        2. Converts the HTML message to Markdown.
        3. If AI summarization is enabled, generates a summary of the message.
        4. Calls `_send_to_providers` to dispatch the notification.
        5. Catches and logs errors like `ValueError` (for invalid notification data)
           or other exceptions during processing.

        Args:
            notification (dict): A dictionary representing the raw notification data
                from Moodle. Expected keys include 'subject' and 'fullmessagehtml'.

        Raises:
            TypeError: If `notification` is not a dictionary.

        Side Effects:
            - Logs errors if notification data is invalid or if processing/sending fails.
            - May call external services (AI API via summarizer, provider APIs via `send`).
        """
        if not isinstance(notification, dict):
            raise TypeError("notification must be a dictionary.")

        try:
            # Extract notification data
            subject = self._get_notification_subject(notification)
            message = self._get_notification_message(notification)

            # Generate summary if enabled
            summary = self._generate_summary(message) if self.summarizer else None

            # Send through providers
            self._send_to_providers(subject, message, summary)

        except ValueError as ve:  # Raised by our own validation
            logging.error(f"Invalid notification data: {ve!s}")
        except Exception as e:  # Catch-all for other processing errors
            logging.error(f"Failed to process notification: {e!s}", exc_info=True)

    def _get_notification_subject(self, notification: dict) -> str:
        """Extract and validate notification subject."""
        if subject := notification.get("subject", "").strip():
            return subject
        else:
            raise ValueError("Notification subject is empty")

    def _get_notification_message(self, notification: dict) -> str:
        """Extract and convert notification message."""
        if message := notification.get("fullmessagehtml", "").strip():
            return convert(message)  # Convert HTML to Markdown
        else:
            raise ValueError("Notification message is empty")

    def _generate_summary(self, message: str) -> str | None:
        """Generate AI summary of message."""
        try:
            return None if self.summarizer is None else self.summarizer.summarize(message)
        except requests.exceptions.RequestException as req_e:  # For AI API calls
            logging.error(f"Network error during summary generation: {req_e!s}")
            return None
        except Exception as e:  # Other potential errors from summarizer
            logging.error(f"Failed to generate summary: {e!s}", exc_info=True)
            return None

    def _send_to_providers(
        self,
        subject: str,
        message: str,
        summary: str | None,
    ) -> None:
        """Send notification through all providers."""
        for provider in self.providers:
            try:
                success = provider.send(subject, message, summary)
                if not success:
                    logging.error(f"Failed to send via {provider.__class__.__name__}")
            except Exception as e:
                logging.error(
                    f"Error with {provider.__class__.__name__}: {e!s}",
                    exc_info=True,
                )
