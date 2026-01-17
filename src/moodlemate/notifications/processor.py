import logging
from typing import TYPE_CHECKING

from moodlemate.core.security import InputValidator
from moodlemate.core.state_manager import StateManager
from moodlemate.markdown import convert
from moodlemate.notifications.base import NotificationProvider
from moodlemate.notifications.summarizer import NotificationSummarizer

if TYPE_CHECKING:
    from moodlemate.config import Settings

logger = logging.getLogger(__name__)


class NotificationProcessor:
    """Processes and sends notifications."""

    def __init__(
        self,
        settings: "Settings",
        providers: list[NotificationProvider],
        state_manager: StateManager,
        summarizer: NotificationSummarizer | None = None,
    ):
        self.settings = settings
        self.providers = providers
        self.state_manager = state_manager
        self.summarizer = summarizer

    def process(self, notification: dict) -> None:
        """Process and send a notification through all enabled providers."""
        try:
            # Security: Sanitize notification data first
            sanitized_notification = InputValidator.sanitize_notification_data(
                notification
            )

            # Extract notification data
            subject = self._get_notification_subject(sanitized_notification)
            message = self._get_notification_message(sanitized_notification)

            # Apply filters
            if self._should_ignore_notification(subject, sanitized_notification):
                logger.info(f"Notification with subject '{subject}' ignored by filter.")
                return

            # Generate summary if enabled
            summary = self._generate_summary(message) if self.summarizer else None

            # Enforce payload limits
            max_bytes = getattr(self.settings.notification, "max_payload_bytes", 65536)
            message, message_trimmed = self._trim_to_limit(message, max_bytes)
            summary, summary_trimmed = self._trim_to_limit(summary, max_bytes)
            if message_trimmed or summary_trimmed:
                logger.warning(
                    "Notification payload trimmed to %d bytes (message_trimmed=%s, summary_trimmed=%s)",
                    max_bytes,
                    message_trimmed,
                    summary_trimmed,
                )

            # Send through providers and record history
            providers_sent = self._send_to_providers(subject, message, summary)

            # Add to history with message context
            self.state_manager.add_notification_to_history(
                sanitized_notification,
                providers_sent,
                message=message,
                summary=summary,
            )

        except Exception as e:
            logging.error(f"Failed to process notification: {e!s}", exc_info=True)

    def _should_ignore_notification(self, subject: str, notification: dict) -> bool:
        """Checks if a notification should be ignored based on configured filters."""
        lowered_subject = subject.lower()
        return any(
            phrase.lower() in lowered_subject
            for phrase in self.settings.filters.ignore_subjects_containing
        )

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
            return (
                None if self.summarizer is None else self.summarizer.summarize(message)
            )
        except Exception as e:
            logging.error(f"Failed to generate summary: {e!s}")
            return None

    def _trim_to_limit(
        self, text: str | None, max_bytes: int
    ) -> tuple[str | None, bool]:
        """Trim text to a byte limit, returning the trimmed text and whether trimming occurred."""
        if text is None:
            return None, False
        encoded = text.encode("utf-8")
        if len(encoded) <= max_bytes:
            return text, False
        trimmed = encoded[:max_bytes].decode("utf-8", errors="ignore")
        return trimmed, True

    def _send_to_providers(
        self, subject: str, message: str, summary: str | None
    ) -> list[str]:
        """Send notification through all providers."""
        sent_to = []
        for provider in self.providers:
            try:
                name = (
                    getattr(provider, "provider_name", None)
                    or provider.__class__.__name__
                )
                if provider.send(subject, message, summary):
                    sent_to.append(name)
                else:
                    logging.error(f"Failed to send via {name}")
            except Exception as e:
                logging.error(f"Error with {name}: {e!s}", exc_info=True)
        return sent_to
