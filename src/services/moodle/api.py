import logging
import os

from requests.exceptions import RequestException

from src.infrastructure.http.request_manager import request_manager

logger = logging.getLogger(__name__)


class MoodleAPI:
    """
    A wrapper for interacting with the Moodle Web Services API.

    This class provides methods for common Moodle API operations such as logging in,
    retrieving site information, getting user details, and fetching notifications.
    It manages the Moodle API token and uses a shared `requests.Session` from the
    `request_manager` for all HTTP communications. Implemented as a singleton.

    The API token is obtained upon successful login and is automatically included
    in subsequent API calls. The class also supports session refreshing.

    Key public methods:
    - `login(username, password)`: Authenticates and obtains an API token.
    - `refresh_session()`: Re-authenticates using stored credentials to get a new session/token.
    - `get_site_info()`: Fetches general site information and the current user's ID.
    - `get_user_id()`: A convenience method to get the current user's ID.
    - `get_popup_notifications(user_id)`: Fetches popup notifications for a user.
    - `core_user_get_users_by_field(field, value)`: Retrieves user details by a specific field.

    Attributes:
        url (str | None): The base URL of the Moodle instance.
        session (requests.Session): The shared requests session instance.
        token (str | None): The Moodle API authentication token.
        userid (int | None): The user ID of the authenticated user.
        _username (str | None): Stored username for session refresh.
        _password (str | None): Stored password for session refresh.

    Example:
        >>> moodle_client = MoodleAPI(url="https://your.moodle.site")
        >>> try:
        ...     if moodle_client.login("myusername", "mypassword"):
        ...         print("Login successful!")
        ...         site_info = moodle_client.get_site_info()
        ...         if site_info:
        ...             print(f"User ID: {site_info.get('userid')}")
        ...         notifications = moodle_client.get_popup_notifications(site_info['userid'])
        ...         # Process notifications...
        ...     else:
        ...         print("Login failed.")
        ... except ValueError as ve:
        ...     print(f"Input error: {ve}")
        ... except RequestException as re:
        ...     print(f"Network error: {re}")
    """

    _instance = None

    def __new__(cls, url: str | None = None) -> "MoodleAPI":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_api(url)
        return cls._instance

    def _init_api(self, url: str | None = None):
        """Initialize the API with URL and session."""
        if url is not None:
            if not isinstance(url, str):
                raise TypeError("Moodle URL must be a string if provided.")
            if not url:
                raise ValueError("Moodle URL cannot be an empty string if provided.")
        self.url = url or os.getenv("MOODLE_URL")
        if not self.url:
            raise ValueError(
                "Moodle URL is not configured. Provide it in config or as MOODLE_URL env var.",
            )

        self.session = request_manager.session
        request_manager.update_headers(
            {
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        self.token: str | None = None
        self.userid: int | None = None
        self._username: str | None = None
        self._password: str | None = None

    def login(self, username: str, password: str) -> bool:
        """
        Log in to the Moodle instance and obtain an API token.

        This method sends a POST request to Moodle's `/login/token.php` endpoint.
        If successful, it stores the obtained token, username, and password (for
        session refreshing) and returns True. Otherwise, it logs an error and
        returns False.

        Args:
            username (str): The Moodle username.
            password (str): The Moodle password.

        Returns:
            bool: True if login was successful and token was obtained, False otherwise.

        Raises:
            ValueError: If `username` or `password` is empty.
            requests.exceptions.RequestException: If a network error occurs during the
                API call (though this is caught and logged, returning False).
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
                # Store credentials for session refresh
                self._username = username
                self._password = password
                logger.info("Login successful")
                return True

            logger.error("Login failed: Invalid credentials")
            return False

        except RequestException as e:
            logger.error("Request to Moodle failed: %s", e)
            return False

    def refresh_session(self) -> bool:
        """
        Refresh the current Moodle API session.

        This method attempts to re-authenticate with Moodle using previously stored
        credentials (username and password from a successful login). It first resets
        the underlying `requests.Session` via `request_manager.reset_session()`
        and then calls `login()` again.

        This is useful if the API token has expired or the session has become invalid.

        Returns:
            bool: True if the session was successfully refreshed (i.e., re-login was
                  successful), False otherwise (e.g., if no credentials were stored
                  or re-login failed).
        """
        if not self._username or not self._password:
            logger.error("Cannot refresh session: No stored credentials")
            return False

        logger.info("Refreshing Moodle session...")

        # Reset the request manager's session
        request_manager.reset_session()

        # Update our session reference
        self.session = request_manager.session

        # Re-login with stored credentials
        self.token = None
        return self.login(self._username, self._password)

    def get_site_info(self) -> dict | None:
        """
        Retrieve general site information from the Moodle instance.

        This method calls the `core_webservice_get_site_info` Moodle API function.
        It requires a valid API token (obtained via `login`). If successful, it also
        extracts and stores the `userid` from the response.

        Returns:
            dict | None: A dictionary containing site information if the call is
                          successful, None otherwise (e.g., if not logged in or a
                          network error occurs).
                          The dictionary structure is defined by the Moodle API.
                          Example keys: `sitename`, `username`, `firstname`, `lastname`,
                          `userid`, `siteurl`, `userpictureurl`, etc.
        """
        if self.token is None:
            logger.error("Token not set. Please login first.")
            return None

        wsfunction = "core_webservice_get_site_info"
        params = {
            "wstoken": self.token,
            "wsfunction": wsfunction,
            "moodlewsrestformat": "json",
        }

        try:
            response = self.session.post(
                f"{self.url}/webservice/rest/server.php",
                params=params,
            )
            response.raise_for_status()
            self.userid = response.json().get("userid")
            return response.json()
        except RequestException as e:
            logger.error(f"Failed to get site info: {e}")
            return None

    def get_user_id(self) -> int | None:
        """
        Convenience method to retrieve the authenticated user's ID.

        This method calls `get_site_info()` and extracts the `userid` from its
        response. It serves as a direct way to get the user ID after a successful login.

        Returns:
            int | None: The user ID as an integer if available and `get_site_info()`
                        was successful, None otherwise.
        """
        if self.token is None:
            logger.error("Token not set. Please login first.")
            return None

        result = self.get_site_info()
        return result["userid"] if result else None

    def get_popup_notifications(self, user_id: int) -> dict | None:
        """
        Retrieve unread popup notifications for a specific user.

        This method calls the `message_popup_get_popup_notifications` Moodle API function.
        It requires a valid API token and the ID of the user for whom to fetch notifications.

        Args:
            user_id (int): The Moodle user ID for whom to retrieve notifications.

        Returns:
            dict | None: A dictionary containing notification data if successful, None
                          otherwise. The structure includes a 'notifications' list.
                          Each notification object typically has 'id', 'useridfrom',
                          'useridto', 'subject', 'shortenedmessage', 'fullmessagehtml',
                          'timecreated', 'timeread', etc.

        Raises:
            TypeError: If `user_id` is not an integer.
        """
        if not isinstance(user_id, int):
            raise TypeError("user_id must be an integer.")
        return self._post("message_popup_get_popup_notifications", user_id)

    def core_user_get_users_by_field(self, field: str, value: str) -> dict | None:
        """
        Retrieve Moodle user(s) information based on a specified field and its value.

        This method calls the `core_user_get_users_by_field` Moodle API function.
        It allows searching for users by fields like 'id', 'username', 'email', etc.
        Requires a valid API token.

        Args:
            field (str): The user field to search by (e.g., "id", "username", "email").
            value (str): The value to match for the specified field.

        Returns:
            dict | None: A list of user objects matching the criteria if successful,
                          None otherwise. The structure is defined by Moodle API.

        Raises:
            TypeError: If `field` or `value` is not a string.
            ValueError: If `field` or `value` is an empty string.
        """
        if not isinstance(field, str):
            raise TypeError("Search field must be a string.")
        if not field:
            raise ValueError("Search field cannot be empty.")
        if not isinstance(value, str):
            raise TypeError("Search value must be a string.")
        # Allowing empty string for value as some Moodle fields might be searchable that way
        # if not value: # Depending on Moodle API specifics, an empty value might be valid or not.
        #     raise ValueError("Search value cannot be empty.")

        if self.token is None:
            logger.error("Token not set. Please login first.")
            return None

        wsfunction = "core_user_get_users_by_field"
        params = {
            "wstoken": self.token,
            "wsfunction": wsfunction,
            "field": field,
            "values[0]": value,
            "moodlewsrestformat": "json",
        }

        try:
            response = self.session.post(
                f"{self.url}/webservice/rest/server.php",
                params=params,
            )
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.error(f"Failed to get user by field: {e}")
            return None

    def _post(self, wsfunction: str, user_id: int) -> dict | None:
        """
        Sends a POST request to the Moodle API with the given wsfunction and user ID.
        """
        if self.token is None:
            logger.error("Token not set. Please login first.")
            return None

        params = {
            "wstoken": self.token,
            "wsfunction": wsfunction,
            "useridto": user_id,
            "moodlewsrestformat": "json",
        }

        try:
            response = self.session.post(
                f"{self.url}/webservice/rest/server.php",
                params=params,
            )
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.error(f"Request to Moodle failed: {e}")
            return None
