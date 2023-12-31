"""
Simple Moodle API wrapper for Python.

Author: EvickaStudio
Data: 07.10.2023
Github: @EvickaStudio
"""

import logging
import os

import requests
from requests.exceptions import RequestException


class MoodleAPI:
    """
    A simple Moodle API wrapper for Python.

    This class provides methods for interacting with the Moodle API, including
    logging in, retrieving site information, and fetching user data.

    Attributes:
        url (str): Moodle API URL.
        session (requests.Session): A session object for making requests.
        token (str, optional): Authentication token for the Moodle API.
        userid (int, optional): User ID of the logged-in user.
    """

    def __init__(self, url: str = None):
        """
        Initializes the MoodleAPI object with the provided API URL.
        """
        self.url = url or os.getenv("MOODLE_URL")
        self.session = requests.Session()
        self.request_header = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 7.1.1; ...) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.99 Mobile Safari/537.36 MoodleMobile",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        self.session.headers.update(self.request_header)
        self.token = None
        self.userid = None

    def login(self, username: str, password: str) -> bool:
        """
        Logs in to the Moodle instance using the provided username and password.
        Sets the token for the MoodleAPI object.

        Args:
            username (str): Moodle username.
            password (str): Moodle password.

        Returns:
            bool: True if login is successful, False otherwise.

        Raises:
            ValueError: If username or password is not provided.
        """
        if not username:
            raise ValueError("Username is required")
        if not password:
            raise ValueError("Password is required")

        login_data = {
            "username": username,
            "password": password,
            "service": "moodle_mobile_app",
        }
        try:
            response = self.session.post(f"{self.url}/login/token.php", data=login_data)
            response.raise_for_status()
            if "token" in response.json():
                self.token = response.json()["token"]
                logging.info("Login successful")
                return True
            else:
                logging.error("Login failed: Invalid credentials")
                return False
        except RequestException as e:
            logging.error("Request to Moodle failed: %s", e)
            return False

    def get_site_info(self) -> dict:
        """
        Retrieves site information from the Moodle instance.

        Returns:
            dict: A dictionary containing site information.
        """
        if self.token is None:
            logging.error("Token not set. Please login first.")
            return None

        wsfunction = "core_webservice_get_site_info"
        params = {
            "wstoken": self.token,
            "wsfunction": wsfunction,
            "moodlewsrestformat": "json",
        }
        response = self.session.post(
            f"{self.url}/webservice/rest/server.php", params=params
        )
        self.userid = response.json().get("userid")
        return response.json()

    def get_user_id(self) -> int:
        if self.token is None:
            logging.error("Token not set. Please login first.")
            return None
        site_info = self.get_site_info()
        return site_info["userid"]

    def get_popup_notifications(self, user_id: int):
        """
        Retrieves popup notifications for a user.
        """
        return self._post("message_popup_get_popup_notifications", user_id)

    def popup_notification_unread_count(self, user_id: int) -> int:
        """
        Retrieves the number of unread popup notifications for a user.
        """
        return self._post("message_popup_get_unread_popup_notification_count", user_id)

    def core_user_get_users_by_field(self, user_id: int) -> dict:
        """
        Retrieves user information for a user.
        """
        if self.token is None:
            logging.error("Token not set. Please login first.")
            return None
        wsfunction = "core_user_get_users_by_field"
        params = {
            "wstoken": self.token,
            "wsfunction": wsfunction,
            "field": "id",
            "values[0]": user_id,
            "moodlewsrestformat": "json",
        }
        response = self.session.post(
            f"{self.url}webservice/rest/server.php", params=params
        )
        return response.json()

    def _post(self, arg0: str, user_id: str) -> dict:
        """
        Sends a POST request to the Moodle API with an given wsfunction and user ID.
        """
        if self.token is None:
            logging.error("Token not set. Please login first.")
            return None
        wsfunction = arg0
        params = {
            "wstoken": self.token,
            "wsfunction": wsfunction,
            "useridto": user_id,
            "moodlewsrestformat": "json",
        }
        response = self.session.post(
            f"{self.url}webservice/rest/server.php", params=params
        )
        return response.json()
