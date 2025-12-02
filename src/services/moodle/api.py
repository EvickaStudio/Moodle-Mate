import logging
import os
from typing import Optional, Dict, Any

from requests.exceptions import RequestException

from src.infrastructure.http.request_manager import request_manager
from src.core.security import InputValidator, rate_limiter_manager

logger = logging.getLogger(__name__)


class MoodleAPI:
    """
    A simple Moodle API wrapper for Python.
    """

    def __init__(self, url: str, username: str, password: str):
        """Initialize the API with credentials."""
        self.url = url.rstrip("/")
        self.username = username
        self.password = password
        self.session = request_manager.session
        request_manager.update_headers(
            {
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )
        self.token: Optional[str] = None
        self.userid: Optional[int] = None

        # Validate on init (fail fast)
        if not InputValidator.validate_username(username):
            raise ValueError("Invalid username format")
        if not InputValidator.validate_password(password):
            # We don't log the password, just raise error
            raise ValueError("Invalid password format (empty or invalid)")
        if not InputValidator.validate_moodle_url(self.url):
            raise ValueError("Invalid Moodle URL")

    def login(self) -> bool:
        """
        Logs in to the Moodle instance using the stored credentials.
        """
        login_data = {
            "username": self.username,
            "password": self.password,
            "service": "moodle_mobile_app",
        }

        # Rate limiting check
        if not rate_limiter_manager.is_allowed("moodle_api", f"{self.url}_login"):
            remaining = rate_limiter_manager.get_remaining_requests("moodle_api", f"{self.url}_login")
            reset_time = rate_limiter_manager.get_reset_time("moodle_api", f"{self.url}_login")
            logger.warning(f"Login rate limit exceeded for {self.url}. Remaining: {remaining}, Reset: {reset_time}")
            raise ValueError("Too many login attempts. Please try again later.")

        try:
            response = self.session.post(f"{self.url}/login/token.php", data=login_data)
            response.raise_for_status()
            
            json_resp = response.json()
            if "token" in json_resp:
                self.token = json_resp["token"]
                logger.info("Login successful")
                return True
            
            if "error" in json_resp:
                 logger.error(f"Login failed: {json_resp['error']}")
            else:
                 logger.error("Login failed: Invalid credentials or unexpected response")
            
            return False

        except RequestException as e:
            logger.error("Request to Moodle failed: %s", e)
            return False

    def refresh_session(self) -> bool:
        """
        Refreshes the session by creating a new session and re-authenticating.
        """
        logger.info("Refreshing Moodle session...")

        # Reset the request manager's session
        request_manager.reset_session()

        # Update our session reference
        self.session = request_manager.session

        # Re-login with stored credentials
        self.token = None
        return self.login()

    def get_site_info(self) -> Optional[dict]:
        """
        Retrieves site information from the Moodle instance.
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
                f"{self.url}/webservice/rest/server.php", params=params
            )
            response.raise_for_status()
            data = response.json()
            self.userid = data.get("userid")
            return data
        except RequestException as e:
            logger.error(f"Failed to get site info: {e}")
            return None

    def get_user_id(self) -> Optional[int]:
        """
        Retrieve the user ID.
        """
        if self.token is None:
            logger.error("Token not set. Please login first.")
            return None

        result = self.get_site_info()
        return result["userid"] if result else None

    def get_popup_notifications(
        self, user_id: int, limit: Optional[int] = None
    ) -> Optional[dict]:
        """
        Retrieves popup notifications for a user.
        """
        return self._post("message_popup_get_popup_notifications", user_id, limit=limit)

    def core_user_get_users_by_field(self, field: str, value: str) -> Optional[dict]:
        """
        Retrieves user info based on a specific field and value.
        """
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
                f"{self.url}/webservice/rest/server.php", params=params
            )
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.error(f"Failed to get user by field: {e}")
            return None

    def _post(
        self, wsfunction: str, user_id: int, limit: Optional[int] = None
    ) -> Optional[dict]:
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

        if limit is not None:
            params["limit"] = limit

        # Rate limiting check
        if not rate_limiter_manager.is_allowed("moodle_api", f"{self.url}_{wsfunction}"):
            logger.warning(f"API rate limit exceeded for {self.url} - {wsfunction}")
            return None

        try:
            response = self.session.post(
                f"{self.url}/webservice/rest/server.php", params=params
            )
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.error(f"Request to Moodle failed: {e}")
            return None
