import logging
from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from moodlemate.core.security import InputValidator
from moodlemate.core.state_manager import StateManager
from moodlemate.markdown import convert
from moodlemate.notifications.base import NotificationProvider
from moodlemate.notifications.summarizer import NotificationSummarizer

if TYPE_CHECKING:
    from moodlemate.config import Settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ProcessingResult:
    """Delivery is complete only when all enabled providers confirm success."""

    delivered: bool
    ignored: bool = False
    providers_sent: tuple[str, ...] = ()

    @property
    def should_checkpoint(self) -> bool:
        return self.delivered or self.ignored


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

    def process(self, notification: Mapping[str, Any]) -> ProcessingResult:
        """Process and send a notification through all enabled providers."""
        try:
            # Security: Sanitize notification data first
            sanitized_notification = InputValidator.sanitize_notification_data(
                dict(notification)
            )

            # Extract notification data
            subject = self._get_notification_subject(sanitized_notification)
            message = self._get_notification_message(sanitized_notification)

            # Apply filters
            if self._should_ignore_notification(subject, sanitized_notification):
                logger.info(f"Notification with subject '{subject}' ignored by filter.")
                return ProcessingResult(delivered=False, ignored=True)

            # Generate summary if enabled
            summary = self._generate_summary(message) if self.summarizer else None

            # Enforce payload limits
            max_bytes = getattr(self.settings.notification, "max_payload_bytes", 65536)
            message, message_trimmed = self._trim_to_limit(message, max_bytes)
            if message is None:
                raise ValueError("Notification message is empty after trimming")
            summary, summary_trimmed = self._trim_to_limit(summary, max_bytes)
            if message_trimmed or summary_trimmed:
                logger.warning(
                    "Notification payload trimmed to %d bytes (message_trimmed=%s, summary_trimmed=%s)",
                    max_bytes,
                    message_trimmed,
                    summary_trimmed,
                )

            # Send through providers and record history
            notification_id = sanitized_notification.get("id")
            # Test notifications (ID 0) and messages without IDs always send anew.
            if not isinstance(notification_id, int) or notification_id <= 0:
                notification_id = None
            result = self._send_to_providers(subject, message, summary, notification_id)

            if not result.delivered:
                logger.error("Notification delivery is incomplete")
                return result

            # Add successfully delivered notifications to history.
            self.state_manager.add_notification_to_history(
                sanitized_notification,
                list(result.providers_sent),
                message=message,
                summary=summary,
            )
            return result

        except Exception as e:
            logging.error(f"Failed to process notification: {e!s}", exc_info=True)
            return ProcessingResult(delivered=False)

    def _should_ignore_notification(
        self, subject: str, notification: Mapping[str, Any]
    ) -> bool:
        """Checks if a notification should be ignored based on configured filters."""
        lowered_subject = subject.lower()
        subject_match = any(
            phrase.lower() in lowered_subject
            for phrase in self.settings.filters.ignore_subjects_containing
        )
        if subject_match:
            return True

        course_id = notification.get("courseid")
        try:
            if course_id is not None and int(course_id) in set(
                self.settings.filters.ignore_courses_by_id
            ):
                return True
        except (TypeError, ValueError):
            logger.debug("Skipping invalid course id in notification: %r", course_id)

        return False

    def _get_notification_subject(self, notification: Mapping[str, Any]) -> str:
        """Extract and validate notification subject."""
        if subject := notification.get("subject", "").strip():
            return subject
        else:
            raise ValueError("Notification subject is empty")

    def _get_notification_message(self, notification: Mapping[str, Any]) -> str:
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
        self,
        subject: str,
        message: str,
        summary: str | None,
        notification_id: int | None,
    ) -> ProcessingResult:
        """Send only to providers that have not yet confirmed delivery."""
        delivered = (
            self.state_manager.get_delivered_providers(notification_id)
            if notification_id is not None
            else set()
        )
        sent_to = []
        for provider in self.providers:
            name = (
                getattr(provider, "provider_name", None) or provider.__class__.__name__
            )
            if name in delivered:
                sent_to.append(name)
                continue
            try:
                if provider.send(subject, message, summary):
                    sent_to.append(name)
                    if notification_id is not None:
                        self.state_manager.mark_provider_delivered(
                            notification_id, name
                        )
                else:
                    logging.error(f"Failed to send via {name}")
            except Exception as e:
                logging.error(f"Error with {name}: {e!s}", exc_info=True)
        return ProcessingResult(
            delivered=bool(self.providers) and len(sent_to) == len(self.providers),
            providers_sent=tuple(sent_to),
        )
