import logging
from typing import Optional

from src.utils.load_config import Config

from .api import MoodleAPI

logger = logging.getLogger(__name__)


class MoodleNotificationHandler:
    """
    Handles the fetching of Moodle notifications for a specific user.
    """

    def __init__(self, config: Config):
        """
        Loads the configuration and initializes the MoodleNotificationHandler.
        """
        try:
            self.url = config.get_config("moodle", "moodleUrl")
            self.api = MoodleAPI(self.url)
            self.config = config
            self.login()
            self.moodle_user_id = self.api.get_user_id()
            self.last_notification_id = None  # Initialize to None
        except Exception as e:
            logger.exception("Initialization failed")
            raise e

    def login(self) -> None:
        """
        Logs in to Moodle using the username and password.
        """
        try:
            self.username = self.config.get_config("moodle", "username")
            self.password = self.config.get_config("moodle", "password")
            self.api.login(username=self.username, password=self.password)
        except Exception as e:
            logger.exception("Failed to log in to Moodle")
            raise e

    def fetch_latest_notification(self) -> Optional[dict]:
        """
        Fetches the latest notification from Moodle.
        """
        try:
            logging.info("Fetching notifications from Moodle")
            response = self.api.get_popup_notifications(self.moodle_user_id)
            if (
                response
                and "notifications" in response
                and response["notifications"]
            ):
                return response["notifications"][0]
            logging.info("No notifications found.")
            return None
        except Exception as e:
            logging.exception("Failed to fetch Moodle notification")
            return None

    def fetch_newest_notification(self) -> Optional[dict]:
        """
        Fetches the newest notification from Moodle by comparing the ID of the last notification fetched.
        """
        try:
            if notification := self.fetch_latest_notification():
                notification_id = notification["id"]

                if self.last_notification_id is None:
                    # First run, send the notification and set last_notification_id
                    self.last_notification_id = notification_id
                    logger.info(
                        f"First notification fetched: {notification_id}"
                    )
                    return notification

                elif notification_id > self.last_notification_id:
                    # New notification
                    logger.info(f"New notification found: {notification_id}")
                    self.last_notification_id = notification_id
                    return notification
                else:
                    # No new notification
                    logger.info(
                        f"No new notification. Current ID: {notification_id}, Last ID: {self.last_notification_id}"
                    )
                    return None
            else:
                logging.info("No notifications fetched.")
                return None
        except Exception as e:
            logger.exception("Failed to fetch newest Moodle notification")
            return None

    def user_id_from(self, useridfrom: int) -> Optional[dict]:
        """
        Fetches the user information from Moodle based on user ID.
        """
        if not isinstance(useridfrom, int):
            raise TypeError("useridfrom must be an integer")

        try:
            logger.debug(f"Fetching user ID {useridfrom} from Moodle")
            if response := self.api.core_user_get_users_by_field(
                "id", str(useridfrom)
            ):
                return response[0]
            logger.info(f"No user found with ID {useridfrom}")
            return None
        except Exception as e:
            logger.exception(f"Failed to fetch user {useridfrom} from Moodle")
            return None
