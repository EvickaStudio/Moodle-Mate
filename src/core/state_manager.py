import json
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class StateManager:
    """Manages the application's persistent state."""

    _instance = None

    def __new__(cls, state_file: str = "state.json"):
        if cls._instance is None:
            cls._instance = super(StateManager, cls).__new__(cls)
            cls._instance._init_state(state_file)
        return cls._instance

    def _init_state(self, state_file: str):
        """Initialize the StateManager."""
        self.state_file = state_file
        self.last_notification_id: Optional[int] = None
        self._load_state()

    def _load_state(self) -> None:
        """Loads the last known state from the state file."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    state = json.load(f)
                    self.last_notification_id = state.get("last_notification_id")
                    logger.info(
                        f"Loaded state from {self.state_file}. Last notification ID: {self.last_notification_id}"
                    )
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Could not read state file {self.state_file}: {e}")
        else:
            logger.info("No state file found. Starting with a fresh state.")

    def save_state(self) -> None:
        """Saves the current state to the state file."""
        try:
            state = {"last_notification_id": self.last_notification_id}
            with open(self.state_file, "w") as f:
                json.dump(state, f, indent=4)
            logger.info(f"Successfully saved state to {self.state_file}.")
        except IOError as e:
            logger.error(f"Could not write to state file {self.state_file}: {e}")

    def set_last_notification_id(self, notification_id: int):
        """Updates the last notification ID."""
        if notification_id > (self.last_notification_id or 0):
            self.last_notification_id = notification_id
