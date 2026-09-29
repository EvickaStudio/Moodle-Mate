import logging
import time
from typing import TYPE_CHECKING, Any, NotRequired, TypedDict

from moodlemate.core.state_manager import StateManager
from moodlemate.moodle.api import MoodleAPI

from .errors import MoodleAuthenticationError, MoodleConnectionError

if TYPE_CHECKING:
    from moodlemate.config import Settings

logger = logging.getLogger(__name__)


class NotificationData(TypedDict):
    """Type definition for Moodle notification data."""

    id: int
    useridfrom: int
    subject: str
    fullmessagehtml: str
    courseid: NotRequired[int]
    contexturl: NotRequired[str]
    url: NotRequired[str]
    timecreated: NotRequired[int]
    created: NotRequired[int]
    time: NotRequired[int]
    component: NotRequired[str]
    eventtype: NotRequired[str]
    userfrom: NotRequired[str | dict[str, str]]


class UserData(TypedDict):
    """Type definition for Moodle user data."""

    id: int
    fullname: str
    profileimageurl: str


class MoodleNotificationHandler:
    """
    Handles fetching and processing of Moodle notifications.

    This class manages the connection to Moodle, authentication,
    and retrieval of notifications and user information.
    """

    def __init__(
        self, settings: "Settings", api: MoodleAPI, state_manager: StateManager
    ) -> None:
        """
        Initialize the handler without contacting Moodle until the first fetch.

        Args:
            settings: Application configuration
            api: Moodle API instance
            state_manager: State manager instance

        """
        self.settings = settings
        self.api = api
        self.state_manager = state_manager
        self.moodle_user_id: int | None = None
        self.last_notification_id = state_manager.last_notification_id
        self.last_successful_connection = 0.0
        self.session_timeout = 3600  # Default session timeout of 1 hour
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 60  # Initial delay for reconnection attempts

    def _login(self) -> None:
        """
        Authenticate with Moodle.

        Raises:
            MoodleAuthenticationError: If authentication fails
        """
        try:
            # API instance already has credentials from its init
            if not self.api.login():
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

        if (
            not self.api.token
            or self.moodle_user_id is None
            or time_since_last_connection > self.session_timeout
        ):
            logger.info("Moodle session missing or expired. Connecting...")
            self._reconnect()

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
                    f"Reconnection attempt {attempts + 1}/{self.max_reconnect_attempts}"
                )
                self._login()

                # Get and update user ID
                user_id = self.api.get_user_id()
                if not user_id:
                    raise MoodleAuthenticationError(
                        "Failed to get user ID after reconnection"
                    )

                self.moodle_user_id = user_id
                logger.info(f"Reconnection successful. User ID: {self.moodle_user_id}")
                return
            except (MoodleAuthenticationError, MoodleConnectionError) as e:
                attempts += 1
                if attempts >= self.max_reconnect_attempts:
                    raise MoodleConnectionError(
                        f"Failed to reconnect after {self.max_reconnect_attempts} attempts: {e!s}"
                    ) from e

                logger.warning(
                    f"Reconnection failed (attempt {attempts}/{self.max_reconnect_attempts}): {e!s}"
                )
                logger.info(f"Retrying in {current_delay} seconds...")

                time.sleep(current_delay)
                current_delay = min(
                    current_delay * 2, max_delay
                )  # Exponential backoff with cap

    def fetch_latest_notifications(self) -> list[NotificationData] | None:
        """
        Fetch the most recent batch of notifications from Moodle.

        Returns:
            The latest notification batch if available, None otherwise

        Raises:
            MoodleConnectionError: If connection fails repeatedly
        """
        return self.fetch_notifications()

    def fetch_latest_notification(self) -> NotificationData | None:
        """
        Fetch the single most recent notification from Moodle.

        Returns:
            The latest notification if available, None otherwise

        Raises:
            MoodleConnectionError: If connection fails repeatedly
        """
        notifications = self.fetch_latest_notifications()
        if not notifications:
            return None
        return notifications[0]

    def fetch_newest_notification(self) -> list[NotificationData] | None:
        """
        Fetch only notifications newer than the last processed one.

        Returns:
            A list of the newest unprocessed notifications if available, None otherwise

        Raises:
            MoodleConnectionError: If fetching notifications fails
        """
        try:
            # First run: handle initial fetch
            if self.last_notification_id is None:
                return self._handle_initial_fetch()

            notifications = self.fetch_latest_notifications()
            if not notifications:
                return None

            unseen_notifications = [
                notification
                for notification in notifications
                if notification["id"] > self.last_notification_id
            ]
            unseen_notifications.sort(key=lambda notification: notification["id"])

            if unseen_notifications:
                return [
                    self._handle_new_notification(
                        "New notification found: ID ",
                        notification["id"],
                        notification,
                    )
                    for notification in unseen_notifications
                ]

            logger.debug(
                "No new notifications. Current IDs: %s, Last ID: %s",
                [notification["id"] for notification in notifications],
                self.last_notification_id,
            )
            return None

        except MoodleConnectionError as e:
            logger.error(f"Connection error while fetching new notifications: {e!s}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching new notifications: {e!s}")
            raise MoodleConnectionError(
                f"Unexpected error fetching notifications: {e!s}"
            ) from e

    def user_id_from(self, user_id: int) -> UserData | None:
        """
        Fetch user information by ID.

        Args:
            user_id: The Moodle user ID to look up

        Returns:
            User information if found, None otherwise

        Raises:
            MoodleConnectionError: If the API call fails
        """
        retry_delay = 30  # Initial delay in seconds
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
                self.last_successful_connection = time.time()

                if not response:
                    logger.info(f"No user found with ID {user_id}")
                    return None

                user_data = None
                if isinstance(response, list):
                    if response:
                        user_data = response[0]
                elif isinstance(response, dict):
                    users = response.get("users")
                    if isinstance(users, list) and users:
                        user_data = users[0]
                    elif "id" in response:
                        user_data = response

                if not isinstance(user_data, dict):
                    logger.warning(
                        "Unexpected user lookup response format for user_id=%s: %r",
                        user_id,
                        type(response).__name__,
                    )
                    return None

                processed = self._process_user_data(user_data)
                return self._log_and_return(
                    processed, "Failed to process user data", "User data fetched: "
                )

            except MoodleAuthenticationError as e:
                # Authentication issues should trigger a reconnection attempt
                logger.warning(f"Authentication error while fetching user data: {e!s}")
                try:
                    self._reconnect()
                    retries += 1  # Count this as a retry attempt
                except MoodleConnectionError as ce:
                    # If reconnection fails after multiple attempts, return None instead of propagating
                    logger.error(f"Failed to reconnect: {ce!s}")
                    return None

            except Exception as e:
                retries += 1
                if retries >= max_retries:
                    logger.error(
                        f"Failed to fetch user {user_id} after {max_retries} attempts: {e!s}"
                    )
                    return None  # Return None instead of raising to maintain 24/7 operation

                logger.warning(
                    f"Failed to fetch user (attempt {retries}/{max_retries}): {e!s}"
                )
                logger.info(f"Retrying in {retry_delay} seconds...")

                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_delay)  # Exponential backoff

        return None

    def _handle_new_notification(
        self,
        message: str,
        current_id: int,
        notification: NotificationData,
        update_state: bool = False,
    ) -> NotificationData:
        """Handle processing of a new notification.

        Args:
            message: Log message prefix
            current_id: Current notification ID
            notification: Notification data
            update_state: Flag indicating whether to persist the ID immediately

        Returns:
            The processed notification data
        """
        logger.info(f"{message}{current_id}")
        if update_state:
            self.mark_notification_processed(current_id)
        return notification

    def mark_notification_processed(self, notification_id: int) -> None:
        """Persist the last successfully processed notification ID."""
        self.last_notification_id = notification_id
        self.state_manager.set_last_notification_id(notification_id)

    def _log_and_return(self, processed, error_message, debug_message_prefix):
        if not processed:
            logger.error(error_message)
            return None
        logger.debug("%s", debug_message_prefix)
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

            # Retain the optional metadata used by filters and dashboard history.
            metadata: dict[str, Any] = {}
            for key in ("courseid", "timecreated", "created", "time"):
                try:
                    metadata[key] = int(notification[key])
                except (KeyError, TypeError, ValueError, OverflowError):
                    continue
            for key in ("contexturl", "url", "component", "eventtype"):
                if isinstance(value := notification.get(key), str):
                    metadata[key] = value
            author = notification.get("userfrom")
            if isinstance(author, str):
                metadata["userfrom"] = author
            elif isinstance(author, dict):
                metadata["userfrom"] = {
                    key: value
                    for key in ("fullname", "firstname", "username")
                    if isinstance(value := author.get(key), str)
                }

            # Create TypedDict with validated data
            return NotificationData(
                id=int(notification["id"]),
                useridfrom=int(notification["useridfrom"]),
                subject=str(notification["subject"]),
                fullmessagehtml=str(notification["fullmessagehtml"]),
                **metadata,
            )
        except (KeyError, ValueError) as e:
            logging.error("Error processing notification data (%s)", type(e).__name__)
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
            logging.error("Error processing user data (%s)", type(e).__name__)
            return None

    def _handle_initial_fetch(self) -> list[NotificationData] | None:
        """Handles the initial fetch of notifications on the first run."""
        logger.info("First run detected. Performing initial fetch.")
        initial_id = self.state_manager.initial_notification_id
        limit = self.settings.moodle.initial_fetch_count if initial_id is None else None
        notifications = self.fetch_notifications(limit=limit)

        if not notifications:
            logger.info("No notifications found on initial fetch.")
            return None

        if initial_id is not None:
            notifications = [item for item in notifications if item["id"] >= initial_id]
            if not notifications:
                return None

        logger.info(f"Fetched {len(notifications)} notifications on initial run.")
        notifications.sort(key=lambda notification: notification["id"])
        self.state_manager.pin_initial_notification(notifications[0]["id"])
        for notification in notifications:
            self._handle_new_notification(
                "Processing initial notification: ID ",
                notification["id"],
                notification,
            )
        return notifications

    def fetch_notifications(
        self, limit: int | None = None
    ) -> list[NotificationData] | None:
        """Fetches a specified number of recent notifications from Moodle."""
        retry_delay = 60  # Initial delay in seconds
        max_delay = 300  # Maximum delay of 5 minutes
        max_retries = 5  # Maximum number of retries
        retries = 0

        while retries < max_retries:
            try:
                return self._fetch_notifications(limit)
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
                        f"Failed to fetch notifications after {max_retries} attempts"
                    ) from e

                logger.warning(
                    f"Failed to fetch notifications (attempt {retries}/{max_retries}): {e!s}"
                )
                logger.info(f"Retrying in {retry_delay} seconds...")

                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_delay)  # Exponential backoff

        raise MoodleConnectionError(
            f"Failed to fetch notifications after {max_retries} attempts"
        )

    def _fetch_notifications(self, limit: int | None) -> list[NotificationData] | None:
        # Ensure connection is active before making the request
        self._ensure_connection()

        logger.info("Fetching notifications from Moodle (limit=%s)", limit)
        # Ensure moodle_user_id is not None before passing it
        if self.moodle_user_id is None:
            raise MoodleAuthenticationError("User ID is not available")

        response = self.api.get_popup_notifications(self.moodle_user_id, limit=limit)

        if not isinstance(response, dict):
            raise MoodleConnectionError("Unexpected Moodle response type")

        notifications = response.get("notifications")
        if not isinstance(notifications, list):
            raise MoodleConnectionError(
                "Moodle response is missing a notifications list"
            )

        self.last_successful_connection = time.time()
        if not notifications:
            logger.info("No notifications found")
            return None

        # Validate notification format
        processed_notifications = []
        for notification in notifications:
            if processed := self._process_notification(notification):
                processed_notifications.append(processed)
        return processed_notifications
