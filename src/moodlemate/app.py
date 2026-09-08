import logging
import signal
import threading
import time
from typing import TYPE_CHECKING

import uvicorn

from moodlemate.core.utils.retry import with_retry
from moodlemate.infrastructure.http.request_manager import request_manager
from moodlemate.notifications.summarizer import initialize_summarizer
from moodlemate.providers.notification import initialize_providers
from moodlemate.web.api import WebUI

if TYPE_CHECKING:
    from moodlemate.config import Settings
    from moodlemate.core.state_manager import StateManager
    from moodlemate.moodle.api import MoodleAPI
    from moodlemate.moodle.notification_handler import MoodleNotificationHandler
    from moodlemate.notifications.processor import NotificationProcessor


class MoodleMateApp:
    """Encapsulates the main application logic for Moodle Mate."""

    def __init__(
        self,
        settings: "Settings",
        notification_processor: "NotificationProcessor",
        moodle_handler: "MoodleNotificationHandler",
        moodle_api: "MoodleAPI",
        state_manager: "StateManager",
    ):
        self.settings = settings
        self.notification_processor = notification_processor
        self.moodle_handler = moodle_handler
        self.moodle_api = moodle_api
        self.state_manager = state_manager
        self._last_heartbeat_sent: float = 0.0
        self._last_failure_alert_sent: float = 0.0
        self._outage_alerted = False
        self._started_at = time.time()
        self._last_successful_poll: float | None = None
        self._last_poll_error: str | None = None
        self._shutdown_event = threading.Event()
        # ponytail: serialize runtime changes with delivery; use a command queue if updates must be nonblocking.
        self._runtime_lock = threading.RLock()
        self._web_server: uvicorn.Server | None = None
        self._web_server_thread: threading.Thread | None = None

    def apply_settings(self, settings: "Settings") -> None:
        """Apply validated settings and refresh their consumers between deliveries."""
        with self._runtime_lock:
            providers = initialize_providers(settings)
            summarizer = initialize_summarizer(settings)
            request_manager.configure(
                connect_timeout=settings.notification.connect_timeout,
                read_timeout=settings.notification.read_timeout,
                retry_total=settings.notification.retry_total,
                backoff_factor=settings.notification.retry_backoff_factor,
            )
            for field in settings.__class__.model_fields:
                setattr(self.settings, field, getattr(settings, field))
            self.notification_processor.providers = providers
            self.notification_processor.summarizer = summarizer

    def run(self) -> None:
        """Starts the main application loop."""
        self._install_signal_handlers()
        try:
            if self.settings.web.enabled:
                self._start_web_ui()

            self._main_loop()
        except KeyboardInterrupt:
            logging.info("Shutting down gracefully...")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e!s}")
            raise
        finally:
            self._shutdown_event.set()
            self._stop_web_ui()
            self.state_manager.maybe_save_state(force=True)
            request_manager.close()

    def _install_signal_handlers(self) -> None:
        """Translate service stop signals into a graceful loop shutdown."""
        if threading.current_thread() is not threading.main_thread():
            return

        def request_shutdown(signum: int, _frame: object) -> None:
            logging.info("Received signal %s; shutting down gracefully...", signum)
            self._request_shutdown()

        signal.signal(signal.SIGINT, request_shutdown)
        signal.signal(signal.SIGTERM, request_shutdown)

    def _request_shutdown(self) -> None:
        """Wake the polling loop and request an immediate web-server stop."""
        self._shutdown_event.set()
        if self._web_server is not None:
            self._web_server.should_exit = True

    def _start_web_ui(self):
        """Starts the Web UI server in a separate thread."""
        if not self.settings.web.auth_secret:
            raise ValueError(
                "Web UI requires `MOODLEMATE_WEB__AUTH_SECRET` for secure access."
            )

        web_ui = WebUI(self.settings, self.state_manager, self)
        app = web_ui.get_app()

        def run_server():
            if self.settings.web.host not in {"127.0.0.1", "localhost"}:
                logging.warning(
                    "Web UI host overridden to 127.0.0.1 (localhost-only mode)."
                )
            host = "127.0.0.1"
            self.settings.web.host = host
            port = self.settings.web.port
            logging.info(f"Starting Web UI on http://{host}:{port}")
            config = uvicorn.Config(app, host=host, port=port, log_level="warning")
            self._web_server = uvicorn.Server(config)
            self._web_server.run()

        self._web_server_thread = threading.Thread(target=run_server, daemon=True)
        self._web_server_thread.start()

    def _stop_web_ui(self) -> None:
        """Stop Uvicorn explicitly instead of leaving its daemon loop running."""
        server = self._web_server
        if server is not None:
            server.should_exit = True
        thread = self._web_server_thread
        if thread is None or not thread.is_alive():
            return

        thread.join(timeout=3.0)
        server = self._web_server
        if server is not None:
            server.should_exit = True
        if thread.is_alive() and server is not None:
            logging.warning("Web UI did not stop promptly; forcing shutdown.")
            server.force_exit = True
            thread.join(timeout=1.0)

    def _main_loop(self) -> None:
        """The main loop that continuously fetches and processes notifications."""
        consecutive_errors = 0
        session_refresh_interval = 24.0  # hours

        while not self._shutdown_event.is_set():
            try:
                with self._runtime_lock:
                    self._check_and_refresh_session(session_refresh_interval)

                    if self._fetch_and_process_notifications():
                        consecutive_errors = 0
                        self.state_manager.maybe_save_state()
                        self._record_poll_success()

                    self._send_heartbeat_if_due()

                sleep_time = self._calculate_sleep_time(
                    consecutive_errors, self.settings.notification.fetch_interval
                )
                self._shutdown_event.wait(sleep_time)

            except Exception as e:
                with self._runtime_lock:
                    consecutive_errors, error_sleep = self._handle_error(
                        consecutive_errors, e
                    )
                    self._last_poll_error = str(e)
                self._shutdown_event.wait(error_sleep)

    def _check_and_refresh_session(self, interval: float) -> None:
        """Checks if the session needs to be refreshed and does so if necessary."""
        session_age = request_manager.get_session_age_hours("moodle")
        if session_age >= interval:
            logging.info(f"Session is {session_age:.2f} hours old. Refreshing...")
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
                result = self.notification_processor.process(notification)
                if not result.should_checkpoint:
                    raise RuntimeError(
                        "Notification was not delivered; checkpoint retained for retry"
                    )
                notification_id = notification.get("id")
                if notification_id is not None:
                    self.moodle_handler.mark_notification_processed(notification_id)
        return True

    def _handle_error(
        self, consecutive_errors: int, error: Exception
    ) -> tuple[int, float]:
        """Handles errors that occur during the main loop."""
        consecutive_errors += 1
        logging.error(
            f"Error during execution (attempt {consecutive_errors}): {error!s}"
        )

        # Check if a failure alert should be sent
        if (
            self.settings.health.enabled
            and self.settings.health.failure_alert_threshold is not None
            and consecutive_errors >= self.settings.health.failure_alert_threshold
        ):
            now = time.time()
            cooldown = self.settings.health.failure_alert_cooldown
            if now - self._last_failure_alert_sent >= cooldown:
                self._send_failure_alert(error)
                self._last_failure_alert_sent = now
                self._outage_alerted = True

        if consecutive_errors >= self.settings.notification.max_retries:
            logging.critical("Persistent errors; continuing with maximum backoff...")
            consecutive_errors = max(1, self.settings.notification.max_retries)

        error_sleep = min(30 * (2 ** (consecutive_errors - 1)), 300)
        logging.info(f"Waiting {error_sleep} seconds before retry...")

        return consecutive_errors, error_sleep

    def _record_poll_success(self) -> None:
        """Record a successful Moodle poll and announce recovery once."""
        self._last_successful_poll = time.time()
        self._last_poll_error = None
        if self._outage_alerted:
            self._send_health_notification(
                "Moodle-Mate Recovered",
                "Moodle-Mate successfully connected to Moodle again.",
            )
            self._outage_alerted = False
            self._last_failure_alert_sent = 0.0

    def get_health_status(self) -> tuple[bool, dict[str, object]]:
        """Return readiness based on the freshness of successful Moodle polls."""
        now = time.time()
        stale_after = self.settings.health.stale_after or max(
            self.settings.notification.fetch_interval * 3, 300
        )
        reference = self._last_successful_poll or self._started_at
        age = max(0.0, now - reference)
        healthy = age <= stale_after and not self._shutdown_event.is_set()
        return healthy, {
            "status": "ok" if healthy else "unhealthy",
            "last_successful_poll": self._last_successful_poll,
            "seconds_since_success": round(age, 1),
            "last_error": self._last_poll_error,
        }

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
            "fullmessagehtml": "<p>This is a test notification from Moodle-Mate. If you received this, your notification providers are configured correctly!</p>",
        }
        with self._runtime_lock:
            result = self.notification_processor.process(test_notification_data)
        if not result.delivered:
            raise RuntimeError(
                "Test notification was not delivered to all enabled providers"
            )
        logging.info("Test notification sent.")

    def _send_heartbeat_if_due(self) -> None:
        """Sends a heartbeat notification if the interval has passed."""
        if (
            not self.settings.health.enabled
            or self.settings.health.heartbeat_interval is None
        ):
            return

        current_time = time.time()
        if (
            current_time - self._last_heartbeat_sent
        ) / 3600 >= self.settings.health.heartbeat_interval:
            logging.info("Sending heartbeat notification...")
            subject = "Moodle-Mate Heartbeat"
            message = "Moodle-Mate is still running and healthy!"
            self._send_health_notification(subject, message)
            self._last_heartbeat_sent = current_time

    def _send_failure_alert(self, error: Exception) -> None:
        """Sends a failure alert notification."""
        if not self.settings.health.enabled:
            return

        logging.error(f"Sending failure alert: {error}")
        subject = "Moodle-Mate Failure Alert!"
        message = f"Moodle-Mate encountered a critical error: {error}"
        self._send_health_notification(subject, message)

    def _send_health_notification(self, subject: str, message: str) -> None:
        """Helper to send health-related notifications to the target provider."""
        if not self.settings.health.target_provider:
            logging.warning("No target provider configured for health notifications.")
            return

        target_provider_name = self.settings.health.target_provider.lower()
        for provider in self.notification_processor.providers:
            provider_name = (
                getattr(provider, "provider_name", None) or provider.__class__.__name__
            ).lower()
            if provider_name == target_provider_name:
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
