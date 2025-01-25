import logging
import time
from typing import Optional, TypedDict

from src.core.config import Config

from .api import MoodleAPI

logger = logging.getLogger(__name__)


class NotificationData(TypedDict):
    """Type definition for Moodle notification data."""

    id: int
    useridfrom: int
    subject: str
    fullmessagehtml: str


class UserData(TypedDict):
    """Type definition for Moodle user data."""

    id: int
    fullname: str
    profileimageurl: str


class MoodleError(Exception):
    """Base exception for Moodle-related errors."""

    pass


class MoodleConnectionError(MoodleError):
    """Raised when connection to Moodle fails."""

    pass


class MoodleAuthenticationError(MoodleError):
    """Raised when authentication to Moodle fails."""

    pass


class MoodleNotificationHandler:
    """
    Handles fetching and processing of Moodle notifications.

    This class manages the connection to Moodle, authentication,
    and retrieval of notifications and user information.
    """

    def __init__(self, config: Config) -> None:
        """
        Initialize the notification handler.

        Args:
            config: Application configuration

        Raises:
            MoodleConnectionError: If connection to Moodle fails
            MoodleAuthenticationError: If authentication fails
            ValueError: If required configuration is missing
        """
        try:
            # Access Moodle config directly from the new structure
            self.moodle_config = config.moodle

            if not self.moodle_config.url:
                raise ValueError("Moodle URL is required")
            if not self.moodle_config.username:
                raise ValueError("Moodle username is required")
            if not self.moodle_config.password:
                raise ValueError("Moodle password is required")

            self.api = MoodleAPI(self.moodle_config.url)
            self._authenticate()

            # Get and store the authenticated user's ID
            self.moodle_user_id = self.api.get_user_id()
            if not self.moodle_user_id:
                raise MoodleAuthenticationError("Failed to get user ID after login")

            self.last_notification_id: Optional[int] = None

        except Exception as e:
            raise MoodleConnectionError(
                f"Failed to initialize Moodle connection: {str(e)}"
            ) from e

    def _authenticate(self) -> None:
        """
        Authenticate with Moodle.

        Raises:
            MoodleAuthenticationError: If authentication fails
        """
        try:
            if not self.api.login(
                username=self.moodle_config.username,
                password=self.moodle_config.password,
            ):
                raise MoodleAuthenticationError("Login returned false")
        except Exception as e:
            raise MoodleAuthenticationError(f"Authentication failed: {str(e)}") from e

    def fetch_latest_notification(self) -> Optional[NotificationData]:
        """
        Fetch the most recent notification from Moodle.

        Returns:
            The latest notification if available, None otherwise

        Raises:
            MoodleConnectionError: If connection fails repeatedly
        """
        retry_delay = 60  # Initial delay in seconds
        max_delay = 300  # Maximum delay of 5 minutes
        max_retries = 5  # Maximum number of retries
        retries = 0

        while retries < max_retries:
            try:
                logger.info("Fetching notifications from Moodle")
                response = self.api.get_popup_notifications(self.moodle_user_id)

                if not isinstance(response, dict):
                    logger.error(f"Unexpected response type: {type(response)}")
                    return None

                notifications = response.get("notifications", [])
                if not notifications:
                    logger.info("No notifications found")
                    return None

                # Validate notification format
                notification = notifications[0]
                if any(k not in notification for k in NotificationData.__annotations__):
                    logger.error("Notification missing required fields")
                    return None

                logger.debug(f"Latest notification: {notification}")
                return NotificationData(**notification)

            except Exception as e:
                retries += 1
                if retries >= max_retries:
                    raise MoodleConnectionError(
                        f"Failed to fetch notifications after {max_retries} attempts"
                    ) from e

                logger.warning(
                    f"Failed to fetch notifications (attempt {retries}/{max_retries}): {str(e)}"
                )
                logger.info(f"Retrying in {retry_delay} seconds...")

                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_delay)  # Exponential backoff

    def fetch_newest_notification(self) -> Optional[NotificationData]:
        """
        Fetch only notifications newer than the last processed one.

        Returns:
            The newest unprocessed notification if available, None otherwise

        Raises:
            MoodleConnectionError: If fetching notifications fails
        """
        try:
            notification = self.fetch_latest_notification()
            if not notification:
                return None

            current_id = notification["id"]

            # First run or new notification
            if self.last_notification_id is None:
                return self._handle_new_notification(
                    "First notification fetched: ID ", current_id, notification
                )
            if current_id > self.last_notification_id:
                return self._handle_new_notification(
                    "New notification found: ID ", current_id, notification
                )
            logger.debug(
                f"No new notifications. Current ID: {current_id}, Last ID: {self.last_notification_id}"
            )
            return None

        except Exception as e:
            raise MoodleConnectionError(
                f"Failed to fetch new notifications: {str(e)}"
            ) from e

    def _handle_new_notification(self, arg0, current_id, notification):
        logger.info(f"{arg0}{current_id}")
        self.last_notification_id = current_id
        return notification

    def user_id_from(self, user_id: int) -> Optional[UserData]:
        """
        Fetch user information by ID.

        Args:
            user_id: The Moodle user ID to look up

        Returns:
            User information if found, None otherwise

        Raises:
            MoodleConnectionError: If the API call fails
        """
        try:
            logger.debug(f"Fetching user with ID {user_id}")
            response = self.api.core_user_get_users_by_field("id", str(user_id))

            if not response:
                logger.info(f"No user found with ID {user_id}")
                return None

            user_data = response[0]
            if not all(k in user_data for k in UserData.__annotations__):
                logger.error("User data missing required fields")
                return None

            logger.debug(f"User data fetched: {user_data}")
            return UserData(**user_data)

        except Exception as e:
            raise MoodleConnectionError(
                f"Failed to fetch user {user_id}: {str(e)}"
            ) from e
