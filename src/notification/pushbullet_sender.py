import logging

from pushbullet import Pushbullet

logger = logging.getLogger(__name__)


class PushbulletSender:
    """Handles sending notifications via Pushbullet."""

    def __init__(self, api_key: str):
        """Initialize Pushbullet sender.

        Args:
            api_key: Pushbullet API key

        Raises:
            ValueError: If API key is missing
        """
        if not api_key:
            raise ValueError("Pushbullet API key is required")

        self.pb = Pushbullet(api_key)

    def send(self, subject: str, message: str) -> None:
        """Send a notification via Pushbullet.

        Args:
            subject: Message subject/title
            message: Message content

        Raises:
            Exception: If sending fails
        """
        self.pb.push_note(subject, message)
