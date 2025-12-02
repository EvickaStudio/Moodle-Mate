import time
from typing import Optional, Tuple, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.core.version import __version__


class TimeoutSession(requests.Session):
    """requests.Session subclass that enforces a default timeout."""

    def __init__(self, default_timeout: Union[float, Tuple[float, float]]) -> None:
        super().__init__()
        self._default_timeout = default_timeout

    def request(self, method, url, **kwargs):  # type: ignore[override]
        if "timeout" not in kwargs or kwargs["timeout"] is None:
            kwargs["timeout"] = self._default_timeout
        return super().request(method, url, **kwargs)


class RequestManager:
    """Global request session manager with consistent headers."""

    _instance: Optional["RequestManager"] = None
    _session: Optional[requests.Session] = None
    _session_created_at: float = 0
    _default_timeout: Union[float, Tuple[float, float]] = (10, 30)

    def __new__(cls) -> "RequestManager":
        if cls._instance is None:
            cls._instance = super(RequestManager, cls).__new__(cls)
            cls._instance._setup_session()
        return cls._instance

    def _setup_session(self) -> None:
        """Setup the global session with security defaults and connection pooling."""
        # Close existing session if it exists
        if self._session is not None:
            self._session.close()

        self._session = TimeoutSession(self._default_timeout)

        # Security headers
        self._session.headers.update(
            {
                "User-Agent": f"MoodleMate/{__version__} (+https://github.com/EvickaStudio/Moodle-Mate)",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }
        )

        # Security: Enable SSL certificate verification
        self._session.verify = True

        # Security: Default timeout enforced by TimeoutSession

        # Configure retry strategy with backoff
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=[
                "HEAD",
                "GET",
                "POST",
                "PUT",
                "DELETE",
                "OPTIONS",
                "TRACE",
            ],
        )

        # Configure connection pooling
        adapter = HTTPAdapter(
            pool_connections=10,  # Number of connection pools
            pool_maxsize=10,  # Maximum number of connections in the pool
            max_retries=retry_strategy,
        )

        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

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
