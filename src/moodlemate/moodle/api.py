import base64
import hashlib
import json
import logging
import os
from typing import Any

from requests.exceptions import RequestException

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError:  # pragma: no cover - dependency is expected in production
    Fernet = None
    InvalidToken = Exception

from moodlemate.core.security import InputValidator, rate_limiter_manager
from moodlemate.infrastructure.http.request_manager import request_manager

logger = logging.getLogger(__name__)


class MoodleAPI:
    """
    A simple Moodle API wrapper for Python.
    """

    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        session_encryption_key: str | None = None,
    ):
        """Initialize the API with credentials."""
        self.url = url.rstrip("/")
        self.username = username
        self.password = password
        self.session_state_file = os.path.abspath(
            os.getenv("MOODLE_SESSION_FILE", "moodle_session.json")
        )
        self._session_restored_from_disk = False
        self.session = request_manager.get_session("moodle")
        self._session_encryption_key = session_encryption_key
        self._session_fernet = self._build_session_cipher()
        self.token: str | None = None
        self.userid: int | None = None

        # Validate on init (fail fast)
        if not InputValidator.validate_username(username):
            raise ValueError("Invalid username format")
        if not InputValidator.validate_password(password):
            # We don't log the password, just raise error
            raise ValueError("Invalid password format (empty or invalid)")
        if not InputValidator.validate_moodle_url(self.url):
            raise ValueError("Invalid Moodle URL")

        self._session_restored_from_disk = self._restore_session_state()

    def login(self) -> bool:
        """
        Logs in to the Moodle instance using the stored credentials.
        """
        if self.token and self._session_restored_from_disk:
            if self._cached_session_is_valid():
                logger.info("Re-using cached Moodle session from disk.")
                return True

            logger.info("Cached Moodle session invalid. Performing full login.")
            self._clear_session_state()

        login_data = {
            "username": self.username,
            "password": self.password,
            "service": "moodle_mobile_app",
        }

        # Rate limiting check
        if not rate_limiter_manager.is_allowed("moodle_api", f"{self.url}_login"):
            remaining = rate_limiter_manager.get_remaining_requests(
                "moodle_api", f"{self.url}_login"
            )
            reset_time = rate_limiter_manager.get_reset_time(
                "moodle_api", f"{self.url}_login"
            )
            logger.warning(
                f"Login rate limit exceeded for {self.url}. Remaining: {remaining}, Reset: {reset_time}"
            )
            raise ValueError("Too many login attempts. Please try again later.")

        try:
            response = self.session.post(f"{self.url}/login/token.php", data=login_data)
            response.raise_for_status()

            json_resp = response.json()
            if "token" in json_resp:
                self.token = json_resp["token"]
                logger.info("Login successful")
                self._save_session_state()
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
        request_manager.reset_session("moodle")

        # Update our session reference
        self.session = request_manager.get_session("moodle")

        # Re-login with stored credentials
        self._clear_session_state()
        return self.login()

    def get_site_info(self) -> dict | None:
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
            self._save_session_state()
            return data
        except RequestException as e:
            logger.error(f"Failed to get site info: {e}")
            return None

    def get_user_id(self) -> int | None:
        """
        Retrieve the user ID.
        """
        if self.token is None:
            logger.error("Token not set. Please login first.")
            return None

        result = self.get_site_info()
        return result["userid"] if result else None

    def get_popup_notifications(
        self, user_id: int, limit: int | None = None
    ) -> dict | None:
        """
        Retrieves popup notifications for a user.
        """
        return self._post("message_popup_get_popup_notifications", user_id, limit=limit)

    def core_user_get_users_by_field(
        self, field: str, value: str
    ) -> list[dict[str, Any]] | dict[str, Any] | None:
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
            result = response.json()
            self._save_session_state()
            return result
        except RequestException as e:
            logger.error(f"Failed to get user by field: {e}")
            return None

    def _post(
        self, wsfunction: str, user_id: int, limit: int | None = None
    ) -> dict | None:
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
        if not rate_limiter_manager.is_allowed(
            "moodle_api", f"{self.url}_{wsfunction}"
        ):
            logger.warning(f"API rate limit exceeded for {self.url} - {wsfunction}")
            return None

        try:
            response = self.session.post(
                f"{self.url}/webservice/rest/server.php", params=params
            )
            response.raise_for_status()
            result = response.json()
            self._save_session_state()
            return result
        except RequestException as e:
            logger.error(f"Request to Moodle failed: {e}")
            return None

    def _restore_session_state(self) -> bool:
        """Attempt to restore a previously saved encrypted Moodle session."""
        if self._session_fernet is None:
            return False

        if not os.path.exists(self.session_state_file):
            return False

        try:
            with open(self.session_state_file, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning(
                "Failed to read cached Moodle session from %s: %s",
                self.session_state_file,
                exc,
            )
            return False

        ciphertext = data.get("ciphertext")
        if not isinstance(ciphertext, str):
            logger.warning(
                "Ignoring legacy or invalid Moodle session cache at %s.",
                self.session_state_file,
            )
            return False

        try:
            decrypted_data = self._session_fernet.decrypt(ciphertext.encode("utf-8"))
            payload = json.loads(decrypted_data.decode("utf-8"))
        except (InvalidToken, json.JSONDecodeError) as exc:
            logger.warning(
                "Failed to decrypt cached Moodle session from %s: %s",
                self.session_state_file,
                exc,
            )
            return False

        token = payload.get("token")
        userid = payload.get("userid")

        if token:
            self.token = token
        if userid:
            self.userid = userid

        logger.info("Loaded cached Moodle session from disk.")
        return True

    def _cached_session_is_valid(self) -> bool:
        """Validate the cached session by performing a lightweight API call."""
        if not self.token:
            return False
        result = self.get_site_info()
        return result is not None

    def _save_session_state(self) -> None:
        """Persist the current Moodle session token encrypted at rest."""
        if not self.token:
            return

        if self._session_fernet is None:
            return

        state = {
            "token": self.token,
            "userid": self.userid,
        }

        directory = os.path.dirname(self.session_state_file)
        if directory:
            os.makedirs(directory, exist_ok=True)

        encrypted_state = self._session_fernet.encrypt(
            json.dumps(state).encode("utf-8")
        ).decode("utf-8")

        payload = {"version": 1, "ciphertext": encrypted_state}

        try:
            with open(self.session_state_file, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2)
            try:
                os.chmod(self.session_state_file, 0o600)
            except OSError as exc:
                logger.warning(
                    "Unable to set restrictive permissions on %s: %s",
                    self.session_state_file,
                    exc,
                )
            self._session_restored_from_disk = True
        except OSError as exc:
            logger.error(
                "Failed to persist Moodle session to %s: %s",
                self.session_state_file,
                exc,
            )

    def _build_session_cipher(self) -> Any | None:
        """Build a cipher used to encrypt/decrypt cached Moodle session state."""
        if Fernet is None:
            logger.info(
                "cryptography is not installed; Moodle session persistence is disabled."
            )
            return None

        encryption_secret = (self._session_encryption_key or "").strip()
        if not encryption_secret:
            # Backward-compatible fallback for direct MoodleAPI usage.
            encryption_secret = os.getenv(
                "MOODLEMATE_SESSION_ENCRYPTION_KEY", ""
            ).strip()
        if not encryption_secret:
            logger.info(
                "MOODLEMATE_SESSION_ENCRYPTION_KEY is not set; Moodle session persistence is disabled."
            )
            return None

        key_material = hashlib.sha256(encryption_secret.encode("utf-8")).digest()
        fernet_key = base64.urlsafe_b64encode(key_material)
        return Fernet(fernet_key)

    def _clear_session_state(self) -> None:
        """Remove cached session details from memory and disk."""
        self.token = None
        self.userid = None
        self.session.cookies.clear()
        self._session_restored_from_disk = False

        try:
            if os.path.exists(self.session_state_file):
                os.remove(self.session_state_file)
        except OSError as exc:
            logger.warning(
                "Failed to delete cached Moodle session %s: %s",
                self.session_state_file,
                exc,
            )
