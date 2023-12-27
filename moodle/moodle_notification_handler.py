import logging

from moodle.api import MoodleAPI
from moodle.load_config import Config


class MoodleNotificationHandler:
    """
    The MoodleNotificationHandler class handles the fetching of Moodle notifications for a specific user.

    Args:
        config_file (str): The path to the configuration file.

    Raises:
        Exception: If the initialization fails.

    Example:
        ```python
        handler = MoodleNotificationHandler("config.ini")
        notification = handler.fetch_latest_notification()
        if notification:
            print(notification)
        ```

    Attributes:
        api (MoodleAPI): An instance of the MoodleAPI class.
        username (str): The username of the Moodle user.
        password (str): The password of the Moodle user.
        moodle_user_id (int): The ID of the Moodle user.
        last_notification_id (int): The ID of the last notification fetched.
    """

    def __init__(self, config: Config) -> None:
        """
        Loads the configuration file and initializes the MoodleNotificationHandler.
        """
        try:
            # Initialize the MoodleAPI with the config file
            self.url = config.get_config("moodle", "moodleUrl")
            self.api = MoodleAPI(self.url)
            self.config = config

            # Login to Moodle using the username and password
            self.login()

            # Get the current user ID from Moodle
            self.moodle_user_id = self.api.get_user_id()

            # Initialize the stalk count and last notification ID
            self.stalk_count = 0
            self.last_notification_id = 0
        except Exception as e:
            logging.exception("Initialization failed")
            raise e
            exit(1)

    def login(self) -> None:
        """
        Logs in to Moodle using the username and password.

        Raises:
            Exception: If the login fails.
        """
        try:
            # Login to Moodle using the username and password
            self.username = self.config.get_config("moodle", "username")
            self.password = self.config.get_config("moodle", "password")
            self.api.login(username=self.username, password=self.password)
        except Exception as e:
            logging.exception("Failed to login to Moodle")
            raise e

    def fetch_latest_notification(self) -> str:
        """
        Fetches the latest notification from Moodle.
        Latest notification is defined as the first notification in the list of notifications.
        This notification must not be newer than the last notification fetched, it can be the same
        => fetch_newest checks for this.

        Returns:
            dict: A dictionary containing the latest notification.

        """
        try:
            # Count the number of times this method has been called
            logging.info("Fetching notification from Moodle")
            # Parse the last notification from the Moodle API response and return it
            return self.api.get_popup_notifications(self.moodle_user_id)[
                "notifications"
            ][0]
        except Exception as e:
            logging.exception("Failed to fetch Moodle notification")
            raise e

    def fetch_newest_notification(self) -> str:
        """
        Fetches the newest notification from Moodle by comparing the ID of the last notification fetched.

        Returns:
            dict: A dictionary containing the newest notification.

        """
        try:
            # Check if there is a newer notification than the last one
            if notification := self.fetch_latest_notification():
                notification_id = notification["id"]

                if notification_id <= self.last_notification_id:
                    # If there isn't, return None
                    return None

                logging.info("Getting newest notification from Moodle")
                # If there is, return the notification and update the last notification ID
                self.last_notification_id = notification_id
                return notification
        except Exception as e:
            logging.exception("Failed to fetch newest Moodle notification")
            return None

    def user_id_from(self, useridfrom: int) -> dict:
        """
        Fetches the user ID from Moodle.

        Args:
            useridfrom (int): The ID of the user.

        Returns:
            dict: A dictionary containing the user ID.
        """
        if not isinstance(useridfrom, int):
            raise TypeError("useridfrom must be an integer")

        try:
            # logging.info(f"Fetching user ID {useridfrom} from Moodle")
            return self.api.core_user_get_users_by_field(useridfrom)
        except Exception as e:  # Hier könnten Sie spezifische API-Fehler behandeln
            logging.exception(f"Failed to fetch user {useridfrom} from Moodle")
            return None
