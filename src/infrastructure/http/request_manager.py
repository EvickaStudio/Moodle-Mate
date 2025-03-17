import time
from typing import Optional

import requests

from src.core.version import __version__


class RequestManager:
    """Global request session manager with consistent headers."""

    _instance: Optional["RequestManager"] = None
    _session: Optional[requests.Session] = None
    _session_created_at: float = 0

    def __new__(cls) -> "RequestManager":
        if cls._instance is None:
            cls._instance = super(RequestManager, cls).__new__(cls)
            cls._instance._setup_session()
        return cls._instance

    def _setup_session(self) -> None:
        """Setup the global session with default headers."""
        # Close existing session if it exists
        if self._session is not None:
            self._session.close()

        self._session = requests.Session()
        self._session.headers.update(
            {
                "User-Agent": f"MoodleMate/{__version__} (+https://github.com/EvickaStudio/Moodle-Mate)",
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )
        self._session_created_at = time.time()

    @property
    def session(self) -> requests.Session:
        """Get the global session instance."""
        if self._session is None:
            self._setup_session()
        assert self._session is not None
        return self._session

    def update_headers(self, headers: dict) -> None:
        """Update session headers with new values."""
        if self._session is None:
            self._setup_session()
        assert self._session is not None
        self._session.headers.update(headers)

    def reset_session(self) -> None:
        """Reset the session completely, creating a new one."""
        self._setup_session()

    @property
    def session_age_hours(self) -> float:
        """Return the age of the current session in hours."""
        if self._session_created_at == 0:
            return 0
        return (time.time() - self._session_created_at) / 3600


# Global instance
request_manager = RequestManager()
