import logging
import time
from typing import TypedDict, TypeVar

from src.core.config import Config
from src.core.service_locator import ServiceLocator
from src.services.moodle.api import MoodleAPI

from .errors import MoodleAuthenticationError, MoodleConnectionError

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


UserDataT = TypeVar("UserDataT", bound=UserData)
NotificationDataT = TypeVar("NotificationDataT", bound=NotificationData)


class MoodleNotificationHandler:
    """
    Handles fetching, processing, and managing Moodle notifications and user data.

    This class is responsible for all direct interactions with the Moodle instance
    related to notifications. It uses the `MoodleAPI` service for raw API calls
    and manages session state, including initial login, session expiry checks,
    and reconnection logic with exponential backoff.

    Key functionalities:
    - Initializing the connection and authenticating with Moodle.
    - Ensuring the Moodle API session remains active and refreshing it when necessary.
    - Fetching the latest popup notifications for the authenticated user.
    - Fetching only notifications newer than the previously processed one to avoid duplicates.
    - Retrieving specific Moodle user details by their ID.
    - Processing raw API responses into structured `NotificationData` and `UserData` typed dictionaries.

    Attributes:
        config (Config): The application's configuration object.
        api (MoodleAPI): An instance of the MoodleAPI service for making API calls.
        moodle_user_id (int | None): The ID of the authenticated Moodle user.
        last_notification_id (int | None): The ID of the last successfully processed notification,
            used to prevent duplicate processing.
        last_successful_connection (float): Timestamp of the last successful interaction
            with the Moodle API, used for session timeout calculations.
        session_timeout (int): Duration in seconds after which the session is considered potentially expired.
        max_reconnect_attempts (int): Maximum number of times to attempt reconnection on failure.
        reconnect_delay (int): Initial delay in seconds for reconnection attempts.

    Raises:
        MoodleConnectionError: During initialization or operations if connection to Moodle
                               fails and cannot be re-established.
        MoodleAuthenticationError: During initialization or operations if Moodle authentication fails.
    """

    def __init__(self, config: Config) -> None:
        """
        Initialize the MoodleNotificationHandler instance.

        This constructor sets up the connection to Moodle by obtaining necessary
        configuration, getting an instance of `MoodleAPI` via the `ServiceLocator`,
        performing an initial login, and fetching the authenticated user's ID.
        It also initializes variables for session management and tracking the last
        processed notification.

        Args:
            config (Config): The application's global configuration object, containing
                Moodle URL, credentials, and other settings.

        Raises:
            MoodleConnectionError: If the initial connection or login to Moodle fails,
                                   or if fetching the initial user ID fails.
            MoodleAuthenticationError: If Moodle authentication fails during the initial login
                                       or if the user ID cannot be retrieved post-login.
            TypeError: If `config` is not an instance of Config.
            ValueError: If essential configuration details (e.g., Moodle URL in `MoodleAPI`)
                        are missing, leading to failures in `MoodleAPI` instantiation or login.
        """
        if not isinstance(config, Config):
            raise TypeError("config must be an instance of Config.")

        try:
            self.config = config
            self.api = ServiceLocator().get("moodle_api", MoodleAPI)
            self._login()

            # Get and store the authenticated user's ID
            self.moodle_user_id = self.api.get_user_id()
            if not self.moodle_user_id:
                raise MoodleAuthenticationError("Failed to get user ID after login")
            self.moodle_user_id = int(self.moodle_user_id)  # Cast to int

            self.last_notification_id: int | None = None

            # Session management variables
            self.last_successful_connection = time.time()
            self.session_timeout = 3600  # Default session timeout of 1 hour
            self.max_reconnect_attempts = 5
            self.reconnect_delay = 60  # Initial delay for reconnection attempts

        except Exception as e:
            raise MoodleConnectionError(
                f"Failed to initialize Moodle connection: {e!s}",
            ) from e

    def _login(self) -> None:
        """
        Authenticate with Moodle.

        Raises:
            MoodleAuthenticationError: If authentication fails
        """
        try:
            if not self.api.login(
                username=self.config.moodle.username,
                password=self.config.moodle.password,
            ):
                raise MoodleAuthenticationError("Login returned false")

            # Update the last successful connection time
            self.last_successful_connection = time.time()
            return None
        except Exception as e:
            raise MoodleAuthenticationError(f"Authentication failed: {e!s}") from e

    def _ensure_connection(self) -> None:
        """
        Ensure connection to Moodle is active, reconnect if necessary.

        This method checks if the session might have expired based on time
        or tries to reconnect if a previous operation failed.

        Raises:
            MoodleConnectionError: If reconnection fails after multiple attempts
        """
        # Check if session might have expired (1 hour default timeout)
        current_time = time.time()
        time_since_last_connection = current_time - self.last_successful_connection

        if time_since_last_connection > self.session_timeout:
            logger.info("Session may have expired. Attempting to reconnect...")
            self._reconnect()
            return

        # If we have a token but no user ID, try to get it
        if self.api.token and not self.moodle_user_id:
            logger.warning(
                "User ID missing but token exists. Attempting to retrieve user ID...",
            )
            try:
                user_id = self.api.get_user_id()
                if user_id:
                    self.moodle_user_id = int(user_id)
                    self.last_successful_connection = time.time()
                    logger.info(
                        f"Successfully retrieved user ID: {self.moodle_user_id}",
                    )
                else:
                    logger.warning(
                        "Failed to retrieve user ID after API call. Attempting reconnection...",
                    )
                    self._reconnect()  # Reconnect if get_user_id returns None
            except MoodleConnectionError as mce:
                logger.warning(f"Connection error while trying to get user ID: {mce!s}. Attempting reconnection.")
                self._reconnect()
            except (ValueError, TypeError, AttributeError) as e:  # Specific errors during user_id processing
                logger.error(f"Error processing user ID: {e!s}. Attempting reconnection.")
                self._reconnect()
            # Removed broad except Exception to let other unexpected errors propagate or be handled by specific Moodle exceptions.

    def _reconnect(self) -> None:
        """
        Attempt to reconnect to Moodle with exponential backoff.

        Raises:
            MoodleConnectionError: If reconnection fails after multiple attempts
        """
        attempts = 0
        current_delay = self.reconnect_delay
        max_delay = 300  # Maximum 5 minutes between attempts

        while attempts < self.max_reconnect_attempts:
            try:
                logger.info(
                    f"Reconnection attempt {attempts + 1}/{self.max_reconnect_attempts}",
                )
                self._login()

                # Get and update user ID
                user_id = self.api.get_user_id()
                if not user_id:
                    raise MoodleAuthenticationError(
                        "Failed to get user ID after reconnection",
                    )

                self.moodle_user_id = int(user_id)
                logger.info(f"Reconnection successful. User ID: {self.moodle_user_id}")
                return
            except (MoodleAuthenticationError, MoodleConnectionError) as e:
                attempts += 1
                if attempts >= self.max_reconnect_attempts:
                    raise MoodleConnectionError(
                        f"Failed to reconnect after {self.max_reconnect_attempts} attempts: {e!s}",
                    ) from e

                logger.warning(
                    f"Reconnection failed (attempt {attempts}/{self.max_reconnect_attempts}): {e!s}",
                )
                logger.info(f"Retrying in {current_delay} seconds...")

                time.sleep(current_delay)
                current_delay = min(
                    current_delay * 2,
                    max_delay,
                )  # Exponential backoff with cap

    def fetch_latest_notification(self) -> NotificationData | None:
        """
        Fetch the most recent notification from Moodle, regardless of whether it has been seen.

        This method ensures the Moodle connection is active, then calls the Moodle API
        to get the latest popup notification for the authenticated user. It processes
        the raw response into a `NotificationData` object.
        Includes retry logic with exponential backoff for transient network or API errors.

        Returns:
            NotificationData | None: A dictionary containing the latest notification's data
                                     if one is found and successfully processed. Returns `None`
                                     if no notifications are found, or if an unrecoverable error
                                     occurs after multiple retries (excluding authentication issues
                                     that trigger reconnection attempts).

        Raises:
            MoodleConnectionError: If fetching fails due to persistent connection issues
                                   after exhausting retries.
            MoodleAuthenticationError: If an authentication error occurs that cannot be
                                       resolved by the internal reconnection logic (this might
                                       indicate invalid credentials or deeper session issues).
        """
        retry_delay = 60  # Initial delay in seconds
        max_delay = 300  # Maximum delay of 5 minutes
        max_retries = 5  # Maximum number of retries
        retries = 0

        while retries < max_retries:
            try:
                # Ensure connection is active before making the request
                self._ensure_connection()

                logger.info("Fetching notifications from Moodle")
                # Ensure moodle_user_id is not None before passing it
                if self.moodle_user_id is None:
                    raise MoodleAuthenticationError("User ID is not available")

                response = self.api.get_popup_notifications(self.moodle_user_id)

                # Update last successful connection time
                self.last_successful_connection = time.time()

                if not isinstance(response, dict):
                    logger.error(f"Unexpected response type: {type(response)}")
                    return None

                notifications = response.get("notifications", [])
                if not notifications:
                    logger.info("No notifications found")
                    return None

                # Validate notification format
                notification = notifications[0]
                processed = self._process_notification(notification)
                return self._log_and_return(
                    processed,
                    "Failed to process notification",
                    "Latest notification: ",
                )

            except MoodleAuthenticationError as e:
                # Authentication issues should trigger a reconnection attempt
                logger.warning(f"Authentication error: {e!s}")
                try:
                    self._reconnect()
                    retries += 1  # Count this as a retry attempt
                except MoodleConnectionError as ce:
                    # If reconnection fails after multiple attempts, propagate the error
                    raise ce

            except Exception as e:
                retries += 1
                if retries >= max_retries:
                    raise MoodleConnectionError(
                        f"Failed to fetch notifications after {max_retries} attempts",
                    ) from e

                logger.warning(
                    f"Failed to fetch notifications (attempt {retries}/{max_retries}): {e!s}",
                )
                logger.info(f"Retrying in {retry_delay} seconds...")

                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_delay)  # Exponential backoff

        return None

    def fetch_newest_notification(self) -> NotificationData | None:
        """
        Fetch only notifications that are newer than the last one processed.

        This method calls `fetch_latest_notification()` to get the current latest
        notification. It then compares the ID of this notification with
        `self.last_notification_id`. If the current notification is newer, or if no
        notifications have been processed yet, it updates `self.last_notification_id`
        and returns the notification data. Otherwise, it logs that no new notifications
        are available and returns `None`.

        This mechanism is designed to prevent processing the same notification multiple times.

        Returns:
            NotificationData | None: The newest unprocessed notification data if available,
                                     otherwise `None`.

        Side Effects:
            - Updates `self.last_notification_id` if a new notification is found.
            - Logs information about new or duplicate notifications.

        Error Handling:
            - Catches `MoodleConnectionError` from underlying fetch operations and logs it,
              returning `None` to allow the application to continue robustly.
            - Catches `TypeError`, `ValueError`, `AttributeError` for unexpected data processing
              issues and logs them, returning `None`.
        """
        try:
            notification = self.fetch_latest_notification()
            if not notification:
                return None

            current_id = notification["id"]

            # First run or new notification
            if self.last_notification_id is None:
                return self._handle_new_notification(
                    "First notification fetched: ID ",
                    current_id,
                    notification,
                )
            if current_id > self.last_notification_id:
                return self._handle_new_notification(
                    "New notification found: ID ",
                    current_id,
                    notification,
                )
            logger.debug(
                f"No new notifications. Current ID: {current_id}, Last ID: {self.last_notification_id}",
            )
            return None

        except MoodleConnectionError as e:
            # For connection errors, we'll log and return None instead of re-raising
            # This allows the application to continue running even with connectivity issues
            logger.error(f"Connection error while fetching new notifications: {e!s}")
            return None
        except (TypeError, ValueError, AttributeError) as e:  # For unexpected data processing issues
            logger.error(f"Unexpected error processing notification data: {e!s}", exc_info=True)
            return None

    def user_id_from(self, user_id: int) -> UserData | None:
        """
        Fetch detailed information for a specific Moodle user by their ID.

        This method ensures the Moodle connection is active, then calls the
        `core_user_get_users_by_field` Moodle API function to retrieve user data.
        It processes the raw API response into a structured `UserData` object.
        Includes retry logic with exponential backoff for transient errors.

        Args:
            user_id (int): The ID of the Moodle user to fetch information for.

        Returns:
            UserData | None: A dictionary containing the user's data (id, fullname,
                              profileimageurl) if found and successfully processed.
                              Returns `None` if the user is not found or an unrecoverable
                              error occurs after retries.

        Raises:
            TypeError: If `user_id` is not an integer.
            MoodleConnectionError: If fetching fails due to persistent connection issues.
            MoodleAuthenticationError: If an authentication error occurs.
        """
        if not isinstance(user_id, int):
            raise TypeError("user_id must be an integer.")
        if user_id <= 0:
            # Moodle user IDs are typically positive. Adjust if system users can have 0 or negative.
            raise ValueError("user_id must be a positive integer.")

        retry_delay = 60  # Initial delay in seconds
        max_delay = 240  # Maximum delay of 4 minutes
        max_retries = 3  # Maximum number of retries
        retries = 0

        while retries < max_retries:
            try:
                # Ensure connection is active before making the request
                self._ensure_connection()

                logger.debug(f"Fetching user with ID {user_id}")
                response = self.api.core_user_get_users_by_field("id", str(user_id))

                # Update last successful connection time
                self.last_successful_connection = time.sleep(retry_delay)

                if not response:
                    logger.info(f"No user found with ID {user_id}")
                    return None

                user_data = response[0]
                processed = self._process_user_data(user_data)
                return self._log_and_return(
                    processed,
                    "Failed to process user data",
                    "User data fetched: ",
                )

            except MoodleAuthenticationError as e:
                # Authentication issues should trigger a reconnection attempt
                logger.warning(
                    f"Authentication error while fetching user data: {e!s}",
                )
                try:
                    self._reconnect()
                    retries += 1  # Count this as a retry attempt
                except MoodleConnectionError as ce:
                    # If reconnection fails after multiple attempts, return None instead of propagating
                    logger.error(f"Failed to reconnect: {ce!s}")
                    return None

            except (ValueError, AttributeError, TypeError) as e:  # More specific exceptions
                retries += 1
                logger.warning(
                    f"Unexpected error fetching user {user_id} (attempt {retries}/{max_retries}): {e!s}",
                )
                if retries >= max_retries:
                    logger.error(
                        f"Failed to fetch user {user_id} after {max_retries} attempts due to unexpected error.",
                    )
                    return None
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_delay)

        return None

    def _handle_new_notification(
        self,
        message: str,
        current_id: int,
        notification: NotificationData,
    ) -> NotificationData:
        """Handle processing of a new notification.

        Args:
            message: Log message prefix
            current_id: Current notification ID
            notification: Notification data

        Returns:
            The processed notification data
        """
        logger.info(f"{message}{current_id}")
        self.last_notification_id = current_id
        return notification

    def _log_and_return(
        self,
        processed: UserDataT | NotificationDataT | None,
        error_message: str,
        debug_message_prefix: str,
    ) -> UserDataT | NotificationDataT | None:
        if not processed:
            logger.error(error_message)
            return None
        logger.debug(f"{debug_message_prefix}{processed}")
        return processed

    def _process_notification(self, notification: dict) -> NotificationData | None:
        """Process raw notification data into typed format."""
        try:
            # Validate all required fields are present
            required_fields = {"id", "useridfrom", "subject", "fullmessagehtml"}
            if any(field not in notification for field in required_fields):
                missing = required_fields - set(notification.keys())
                logging.error(f"Missing required notification fields: {missing}")
                return None

            # Create TypedDict with validated data
            return NotificationData(
                id=int(notification["id"]),
                useridfrom=int(notification["useridfrom"]),
                subject=str(notification["subject"]),
                fullmessagehtml=str(notification["fullmessagehtml"]),
            )
        except (KeyError, ValueError) as e:
            logging.error(f"Error processing notification data: {e}")
            return None

    def _process_user_data(self, user_data: dict) -> UserData | None:
        """Process raw user data into typed format."""
        try:
            # Validate all required fields are present
            required_fields = {"id", "fullname", "profileimageurl"}
            if any(field not in user_data for field in required_fields):
                missing = required_fields - set(user_data.keys())
                logging.error(f"Missing required user fields: {missing}")
                return None

            # Create TypedDict with validated data
            return UserData(
                id=int(user_data["id"]),
                fullname=str(user_data["fullname"]),
                profileimageurl=str(user_data["profileimageurl"]),
            )
        except (KeyError, ValueError) as e:
            logging.error(f"Error processing user data: {e}")
            return None
