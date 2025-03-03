import logging
from typing import Optional

from src.infrastructure.database.models import Notification, db

logger = logging.getLogger(__name__)


class NotificationStorage:
    """Service for storing and retrieving notifications."""

    def __init__(self):
        """Initialize the notification storage service."""
        self.db = db
        self.app = None

    def set_app(self, app):
        """Set the Flask application instance."""
        self.app = app

    def store_notification(
        self,
        notification_data: dict,
        markdown_content: str,
        summary: Optional[str] = None,
    ) -> bool:
        """Store a notification in the database.

        Args:
            notification_data: The raw notification data from Moodle
            markdown_content: The converted markdown content
            summary: Optional AI-generated summary

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.app:
            logger.warning(
                "Flask app not set in NotificationStorage. Skipping database storage."
            )
            return False

        try:
            with self.app.app_context():
                # Check if notification already exists
                existing = Notification.query.filter_by(
                    moodle_id=notification_data["id"]
                ).first()
                if existing:
                    logger.debug(
                        f"Notification {notification_data['id']} already exists in database"
                    )
                    return True

                # Create new notification record
                notification = Notification(
                    moodle_id=notification_data["id"],
                    subject=notification_data["subject"],
                    html_content=notification_data["fullmessagehtml"],
                    markdown_content=markdown_content,
                    summary=summary,
                    user_id_from=notification_data["useridfrom"],
                )

                # Add and commit to database
                self.db.session.add(notification)
                self.db.session.commit()
                logger.info(
                    f"Stored notification {notification_data['id']} in database"
                )
                return True

        except Exception as e:
            logger.error(f"Failed to store notification: {str(e)}")
            if self.app:
                with self.app.app_context():
                    self.db.session.rollback()
            return False

    def get_all_notifications(self):
        """Retrieve all notifications from the database."""
        if not self.app:
            logger.warning(
                "Flask app not set in NotificationStorage. Cannot retrieve notifications."
            )
            return []

        with self.app.app_context():
            return Notification.query.order_by(Notification.timestamp.desc()).all()

    def get_notification_by_id(self, notification_id: int):
        """Retrieve a specific notification by ID."""
        if not self.app:
            logger.warning(
                "Flask app not set in NotificationStorage. Cannot retrieve notification."
            )
            return None

        with self.app.app_context():
            return Notification.query.get(notification_id)
