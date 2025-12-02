import logging
from typing import List, Optional, TYPE_CHECKING

from src.core.notification.base import NotificationProvider
from src.core.notification.summarizer import NotificationSummarizer
from src.core.security import InputValidator
from src.services.markdown import convert

if TYPE_CHECKING:
    from src.config import Settings

logger = logging.getLogger(__name__)


class NotificationProcessor:
    """Processes and sends notifications."""

    def __init__(
        self,
        settings: "Settings",
        providers: List[NotificationProvider],
        summarizer: Optional[NotificationSummarizer] = None,
    ):
        self.settings = settings
        self.providers = providers
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

            # Send through providers
            self._send_to_providers(subject, message, summary)

        except Exception as e:
            logging.error(f"Failed to process notification: {str(e)}", exc_info=True)

    def _should_ignore_notification(self, subject: str, notification: dict) -> bool:
        """Checks if a notification should be ignored based on configured filters."""
        # Subject filtering
        for phrase in self.settings.filters.ignore_subjects_containing:
            if phrase.lower() in subject.lower():
                return True

        # Course ID filtering (assuming notification contains 'courseid' or similar)
        # Moodle's message_popup_get_popup_notifications does not return courseid directly.
        # If course ID filtering is needed, MoodleAPI would need to be extended
        # to fetch more detailed notification info or course info.
        # For now, this part is a placeholder or can be removed if not feasible.
        # if 'courseid' in notification and notification['courseid'] in self.settings.filters.ignore_courses_by_id:
        #     return True

        return False

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

    def _generate_summary(self, message: str) -> Optional[str]:
        """Generate AI summary of message."""
        try:
            return (
                None if self.summarizer is None else self.summarizer.summarize(message)
            )
        except Exception as e:
            logging.error(f"Failed to generate summary: {str(e)}")
            return None

    def _send_to_providers(
        self, subject: str, message: str, summary: Optional[str]
    ) -> None:
        """Send notification through all providers."""
        for provider in self.providers:
            try:
                success = provider.send(subject, message, summary)
                if not success:
                    logging.error(f"Failed to send via {provider.__class__.__name__}")
            except Exception as e:
                logging.error(
                    f"Error with {provider.__class__.__name__}: {str(e)}", exc_info=True
                )
