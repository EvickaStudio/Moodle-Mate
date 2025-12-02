"""Exception handling for Moodle Mate."""

from .domain import (
    MoodleMateException,
    ConfigurationError,
    NotificationError,
    ProviderError,
    SecurityError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    APIError,
    NetworkError,
    TimeoutError,
    ServiceError,
    DependencyError,
)

__all__ = [
    "MoodleMateException",
    "ConfigurationError",
    "NotificationError",
    "ProviderError",
    "SecurityError",
    "AuthenticationError",
    "ValidationError",
    "RateLimitError",
    "APIError",
    "NetworkError",
    "TimeoutError",
    "ServiceError",
    "DependencyError",
]