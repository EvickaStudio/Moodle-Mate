"""Exception handling for Moodle Mate."""

from .domain import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    DependencyError,
    MoodleMateException,
    NetworkError,
    NotificationError,
    ProviderError,
    RateLimitError,
    SecurityError,
    ServiceError,
    TimeoutError,
    ValidationError,
)

__all__ = [
    "APIError",
    "AuthenticationError",
    "ConfigurationError",
    "DependencyError",
    "MoodleMateException",
    "NetworkError",
    "NotificationError",
    "ProviderError",
    "RateLimitError",
    "SecurityError",
    "ServiceError",
    "TimeoutError",
    "ValidationError",
]
