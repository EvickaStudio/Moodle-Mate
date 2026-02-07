import json
import logging
import os
import time
from collections import deque
from typing import Any

logger = logging.getLogger(__name__)


class StateManager:
    """Manages the application's persistent state and runtime history."""

    _instance = None

    def __new__(cls, state_file: str | None = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            resolved_state_file = cls._instance._resolve_state_file(state_file)
            cls._instance._init_state(resolved_state_file)
        return cls._instance

    def _init_state(self, state_file: str):
        """Initialize the StateManager."""
        self.state_file = state_file
        self.last_notification_id: int | None = None
        self.notification_history: deque[dict] = deque(maxlen=50)
        self._save_interval_seconds = 15.0
        self._last_saved_at: float = 0.0
        self._dirty = False
        self._load_state()

    def _resolve_state_file(self, provided_path: str | None) -> str:
        """Determine where the state file should live."""
        if provided_path:
            return os.path.abspath(provided_path)

        if env_path := os.getenv("MOODLE_STATE_FILE"):
            return os.path.abspath(env_path)

        state_dir = os.getenv("MOODLE_STATE_DIR", "/app/state")
        if os.path.isdir(state_dir) or os.getenv("MOODLE_STATE_DIR"):
            os.makedirs(state_dir, exist_ok=True)
            return os.path.join(state_dir, "state.json")

        return os.path.abspath("state.json")

    def _load_state(self) -> None:
        """Loads the last known state from the state file."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file) as f:
                    state = json.load(f)
                    self.last_notification_id = state.get("last_notification_id")
                    logger.info(
                        f"Loaded state from {self.state_file}. Last notification ID: {self.last_notification_id}"
                    )
            except (OSError, json.JSONDecodeError) as e:
                logger.error(f"Could not read state file {self.state_file}: {e}")
        else:
            logger.info("No state file found. Starting with a fresh state.")

    def save_state(self) -> None:
        """Saves the current state to the state file."""
        try:
            os.makedirs(os.path.dirname(self.state_file) or ".", exist_ok=True)
            state = {"last_notification_id": self.last_notification_id}
            with open(self.state_file, "w") as f:
                json.dump(state, f, indent=4)
            try:
                os.chmod(self.state_file, 0o600)
            except OSError as e:
                logger.warning(
                    "Could not set restrictive permissions on state file %s: %s",
                    self.state_file,
                    e,
                )
            logger.info(f"Successfully saved state to {self.state_file}.")
            self._dirty = False
            self._last_saved_at = time.time()
        except OSError as e:
            logger.error(f"Could not write to state file {self.state_file}: {e}")

    def set_last_notification_id(self, notification_id: int):
        """Updates the last notification ID."""
        if notification_id > (self.last_notification_id or 0):
            self.last_notification_id = notification_id
            self._dirty = True

    def maybe_save_state(self, force: bool = False) -> None:
        """Persist state when dirty and the interval has elapsed, or when forced."""
        if force:
            self.save_state()
            return

        if not self._dirty:
            return

        if time.time() - self._last_saved_at < self._save_interval_seconds:
            return

        self.save_state()

    def add_notification_to_history(
        self,
        notification: dict[str, Any],
        providers_sent: list[str],
        message: str,
        summary: str | None = None,
    ):
        """Adds a notification with contextual details to the in-memory history."""
        entry = {
            "id": notification.get("id"),
            "subject": notification.get("subject"),
            "message": message,
            "summary": summary,
            "timestamp": self._extract_timestamp(notification),
            "providers": providers_sent,
            "context_url": notification.get("contexturl") or notification.get("url"),
            "component": notification.get("component"),
            "event_type": notification.get("eventtype"),
            "course": notification.get("courseid"),
            "author": self._extract_author(notification),
        }
        self.notification_history.appendleft(entry)

    def _extract_timestamp(self, notification: dict[str, Any]) -> float:
        """Normalizes the timestamp for history entries."""
        raw_timestamp = (
            notification.get("timecreated")
            or notification.get("created")
            or notification.get("time")
        )
        if raw_timestamp is None:
            return time.time()
        try:
            timestamp = float(raw_timestamp)
            if timestamp > 1_000_000_000_000:
                timestamp /= 1000.0
            return timestamp
        except (TypeError, ValueError):
            return time.time()

    @staticmethod
    def _extract_author(notification: dict[str, Any]) -> str | None:
        """Best-effort extraction of the notification author."""
        user_from = notification.get("userfrom")
        if isinstance(user_from, dict):
            return (
                user_from.get("fullname")
                or user_from.get("firstname")
                or user_from.get("username")
            )
        elif isinstance(user_from, str):
            return user_from
        return None

    def get_history(self) -> list[dict]:
        """Returns the notification history."""
        return list(self.notification_history)
