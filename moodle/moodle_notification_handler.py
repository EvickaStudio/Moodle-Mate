# Copyright 2024 EvickaStudio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Moodle notification handler.

Author: EvickaStudio
Data: 29.12.2023
Github: @EvickaStudio
"""

import logging

from moodle.api import MoodleAPI
from moodle.load_config import Config

logger = logging.getLogger(__name__)


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

    def __init__(self, config: Config):
        """Loads the configuration file and initializes the MoodleNotificationHandler."""
        try:
            self.url = config.get_config("moodle", "moodleUrl")
            self.api = MoodleAPI(self.url)
            self.config = config
            self.login()
            self.moodle_user_id = self.api.get_user_id()
            self.stalk_count = 0
            self.last_notification_id = 0
        except Exception as e:
            logger.exception("Initialization failed")
            raise e

    def login(self) -> None:
        """
        Logs in to Moodle using the username and password.

        Raises:
            Exception: If the login fails.
        """
        try:
            self.username = self.config.get_config("moodle", "username")
            self.password = self.config.get_config("moodle", "password")
            self.api.login(username=self.username, password=self.password)
        except Exception as e:
            logger.exception("Failed to log in to Moodle")
            raise e

    def fetch_latest_notification(self) -> dict | None:
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
            return None

    def fetch_newest_notification(self) -> dict | None:
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
                    logger.info(
                        f"No new notification ID found: {notification_id}"
                    )
                    return None

                logging.info(
                    f"Getting newest notification from Moodle: {notification_id}"
                )
                # If there is, return the notification and update the last notification ID
                self.last_notification_id = notification_id
                # logger.info(f"New notification found: {notification}")
                return notification
        except Exception as e:
            logging.exception("Failed to fetch newest Moodle notification")
            return None

    def user_id_from(self, useridfrom: int) -> dict | None:
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
            logger.debug(f"Fetching user ID {useridfrom} from Moodle")
            if response := self.api.core_user_get_users_by_field(useridfrom):
                return response[0]
        except Exception as e:
            logger.exception(f"Failed to fetch user {useridfrom} from Moodle")

        return None
