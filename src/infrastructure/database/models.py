from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db: SQLAlchemy = SQLAlchemy()


class Notification(db.Model):  # type: ignore
    """Model for storing notification history."""

    __tablename__ = "notification"

    id = db.Column(db.Integer, primary_key=True)
    moodle_id = db.Column(db.Integer, unique=True)
    subject = db.Column(db.String(255), nullable=False)
    html_content = db.Column(db.Text, nullable=False)
    markdown_content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_id_from = db.Column(db.Integer)

    def __repr__(self) -> str:
        return f"<Notification {self.id}: {self.subject}>"
