import time
from collections.abc import Mapping
from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from moodlemate.core.version import __version__


class TimeoutSession(requests.Session):
    """requests.Session subclass that enforces a default timeout."""

    def __init__(self, default_timeout: float | tuple[float, float]) -> None:
        super().__init__()
        self._default_timeout = default_timeout

    def request(self, method: str, url: str, **kwargs: Any) -> requests.Response:  # type: ignore[override]
        if "timeout" not in kwargs or kwargs["timeout"] is None:
            kwargs["timeout"] = self._default_timeout
        return super().request(method, url, **kwargs)


class RequestManager:
    """Global request session manager with scoped sessions and consistent defaults."""

    _instance: Optional["RequestManager"] = None
    _sessions: dict[str, requests.Session]
    _session_created_at: dict[str, float]
    _default_timeout: float | tuple[float, float] = (10, 30)
    _retry_total: int = 3
    _backoff_factor: float = 1.0

    def __new__(cls) -> "RequestManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._sessions = {}
            cls._instance._session_created_at = {}
            cls._instance._setup_sessions()
        return cls._instance

    def _build_session(self) -> requests.Session:
        """Build a session with security defaults and connection pooling."""
        session = TimeoutSession(self._default_timeout)

        # Security headers
        session.headers.update(
            {
                "User-Agent": f"MoodleMate/{__version__} (+https://github.com/EvickaStudio/Moodle-Mate)",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }
        )

        # Security: Enable SSL certificate verification
        session.verify = True

        # Security: Default timeout enforced by TimeoutSession

        # Configure retry strategy with backoff for idempotent requests only
        retry_strategy = Retry(
            total=self._retry_total,
            backoff_factor=self._backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )

        # Configure connection pooling
        adapter = HTTPAdapter(
            pool_connections=10,  # Number of connection pools
            pool_maxsize=10,  # Maximum number of connections in the pool
            max_retries=retry_strategy,
        )

        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _setup_sessions(self) -> None:
        """Reset all scoped sessions."""
        for session in self._sessions.values():
            session.close()

        self._sessions.clear()
        self._session_created_at.clear()
        self.get_session("default")

    def _setup_session(self) -> None:
        """Backward-compatible alias for legacy callers/tests."""
        self._setup_sessions()

    def configure(
        self,
        connect_timeout: float,
        read_timeout: float,
        retry_total: int,
        backoff_factor: float,
    ) -> None:
        """Configure timeouts and retries, rebuilding all sessions."""
        self._default_timeout = (connect_timeout, read_timeout)
        self._retry_total = retry_total
        self._backoff_factor = backoff_factor
        self._setup_sessions()

    def get_session(self, scope: str = "default") -> requests.Session:
        """Get or create a scoped session instance."""
        if scope not in self._sessions:
            self._sessions[scope] = self._build_session()
            self._session_created_at[scope] = time.time()
        return self._sessions[scope]

    @property
    def session(self) -> requests.Session:
        """Get the default session instance."""
        return self.get_session("default")

    def update_headers(
        self, headers: Mapping[str, str], scope: str = "default"
    ) -> None:
        """Update headers for a specific scoped session."""
        self.get_session(scope).headers.update(dict(headers))

    def reset_session(self, scope: str = "default") -> None:
        """Reset a specific scoped session."""
        if scope in self._sessions:
            self._sessions[scope].close()
            del self._sessions[scope]
            del self._session_created_at[scope]
        self.get_session(scope)

    @property
    def session_age_hours(self) -> float:
        """Return the age of the default session in hours."""
        return self.get_session_age_hours("default")

    def get_session_age_hours(self, scope: str = "default") -> float:
        """Return the age of a scoped session in hours."""
        created_at = self._session_created_at.get(scope)
        if created_at is None:
            return 0
        return (time.time() - created_at) / 3600


# Global instance
request_manager = RequestManager()
