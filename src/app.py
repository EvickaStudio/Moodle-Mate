import logging
import time

from src.core.config.loader import Config
from src.core.notification.processor import NotificationProcessor
from src.core.service_locator import ServiceLocator
from src.core.services import initialize_services
from src.core.state_manager import StateManager
from src.core.utils.retry import with_retry
from src.infrastructure.http.request_manager import request_manager
from src.services.moodle.api import MoodleAPI
from src.services.moodle.notification_handler import MoodleNotificationHandler


class MoodleMateApp:
    """Encapsulates the main application logic for Moodle Mate."""

    def __init__(self):
        self.config: Config
        self.notification_processor: NotificationProcessor
        self.moodle_handler: MoodleNotificationHandler
        self.moodle_api: MoodleAPI
        self.state_manager: StateManager
        self._last_heartbeat_sent: float = 0.0
        self._initialize()

    def _initialize(self) -> None:
        """Initializes services and components."""
        initialize_services()
        locator = ServiceLocator()
        self.config = locator.get("config", Config)
        self.notification_processor = locator.get(
            "notification_processor", NotificationProcessor
        )
        self.moodle_handler = locator.get("moodle_handler", MoodleNotificationHandler)
        self.moodle_api = locator.get("moodle_api", MoodleAPI)
        self.state_manager = locator.get("state_manager", StateManager)

    def run(self) -> None:
        """Starts the main application loop."""
        try:
            self._main_loop()
        except KeyboardInterrupt:
            logging.info("Shutting down gracefully...")
            self.state_manager.save_state()
        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")
            raise

    def _main_loop(self) -> None:
        """The main loop that continuously fetches and processes notifications."""
        consecutive_errors = 0
        session_refresh_interval = 24.0  # hours

        while True:
            try:
                self._check_and_refresh_session(session_refresh_interval)

                if self._fetch_and_process_notifications():
                    consecutive_errors = 0

                self._send_heartbeat_if_due()

                sleep_time = self._calculate_sleep_time(
                    consecutive_errors, self.config.notification.fetch_interval
                )
                time.sleep(sleep_time)

            except Exception as e:
                consecutive_errors, error_sleep = self._handle_error(
                    consecutive_errors, e
                )
                time.sleep(error_sleep)

    def _check_and_refresh_session(self, interval: float) -> None:
        """Checks if the session needs to be refreshed and does so if necessary."""
        if request_manager.session_age_hours >= interval:
            logging.info(
                f"Session is {request_manager.session_age_hours:.2f} hours old. Refreshing..."
            )
            if self.moodle_api.refresh_session():
                logging.info("Session successfully refreshed")
            else:
                logging.error(
                    "Failed to refresh session. Continuing with existing session."
                )

    @with_retry(max_retries=3, base_delay=5.0, max_delay=30.0)
    def _fetch_and_process_notifications(self) -> bool:
        """Fetches and processes the latest notifications."""
        notifications = self.moodle_handler.fetch_newest_notification()
        if notifications:
            for notification in notifications:
                self.notification_processor.process(notification)
        return True

    def _handle_error(
        self, consecutive_errors: int, error: Exception
    ) -> tuple[int, float]:
        """Handles errors that occur during the main loop."""
        consecutive_errors += 1
        logging.error(
            f"Error during execution (attempt {consecutive_errors}): {str(error)}"
        )

        # Check if a failure alert should be sent
        if (
            self.config.health.enabled
            and self.config.health.failure_alert_threshold is not None
            and consecutive_errors >= self.config.health.failure_alert_threshold
        ):
            self._send_failure_alert(error)

        if consecutive_errors >= self.config.notification.max_retries:
            logging.critical("Too many consecutive errors. Restarting main loop...")
            consecutive_errors = 0

        error_sleep = min(30 * (2 ** (consecutive_errors - 1)), 300)
        logging.info(f"Waiting {error_sleep} seconds before retry...")

        return consecutive_errors, error_sleep

    def _calculate_sleep_time(
        self, consecutive_errors: int, base_interval: int
    ) -> float:
        """Calculates adaptive sleep time based on the number of consecutive errors."""
        if consecutive_errors > 0:
            return min(base_interval * (2**consecutive_errors), 300)
        return float(base_interval)

    def send_test_notification(self) -> None:
        """Sends a test notification to all configured providers."""
        logging.info("Sending test notification...")
        test_notification_data = {
            "id": 0,
            "useridfrom": 0,
            "subject": "Moodle-Mate Test Notification",
            "fullmessagehtml": "<p>This is a test notification from Moodle-Mate. If you received this, your notification providers are configured correctly!</p>",  # noqa: E501
        }
        self.notification_processor.process(test_notification_data)
        logging.info("Test notification sent.")

    def _send_heartbeat_if_due(self) -> None:
        """Sends a heartbeat notification if the interval has passed."""
        if (
            not self.config.health.enabled
            or self.config.health.heartbeat_interval is None
        ):
            return

        current_time = time.time()
        if (
            current_time - self._last_heartbeat_sent
        ) / 3600 >= self.config.health.heartbeat_interval:
            logging.info("Sending heartbeat notification...")
            subject = "Moodle-Mate Heartbeat"
            message = "Moodle-Mate is still running and healthy!"
            self._send_health_notification(subject, message)
            self._last_heartbeat_sent = current_time

    def _send_failure_alert(self, error: Exception) -> None:
        """Sends a failure alert notification."""
        if not self.config.health.enabled:
            return

        logging.error(f"Sending failure alert: {error}")
        subject = "Moodle-Mate Failure Alert!"
        message = f"Moodle-Mate encountered a critical error: {error}"
        self._send_health_notification(subject, message)

    def _send_health_notification(self, subject: str, message: str) -> None:
        """Helper to send health-related notifications to the target provider."""
        if not self.config.health.target_provider:
            logging.warning("No target provider configured for health notifications.")
            return

        target_provider_name = self.config.health.target_provider.lower()
        for provider in self.notification_processor.providers:
            if provider.provider_name.lower() == target_provider_name:
                try:
                    provider.send(subject, message)
                    logging.info(
                        f"Health notification sent via {provider.provider_name}."
                    )
                    return
                except Exception as e:
                    logging.error(
                        f"Failed to send health notification via {provider.provider_name}: {e}"
                    )
        logging.warning(
            f"Target health provider '{target_provider_name}' not found or not enabled."
        )
