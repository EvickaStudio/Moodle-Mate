"""Domain-specific exceptions for Moodle Mate."""


class MoodleMateException(Exception):
    """Base exception for Moodle Mate."""

    def __init__(self, message: str, correlation_id: str | None = None, **kwargs):
        """Initialize exception with optional correlation ID and context.

        Args:
            message: Error message
            correlation_id: Optional correlation ID for tracking
            **kwargs: Additional context
        """
        super().__init__(message)
        self.message = message
        self.correlation_id = correlation_id
        self.context = kwargs

    def __str__(self) -> str:
        """String representation with correlation ID if available."""
        base_msg = self.message
        if self.correlation_id:
            base_msg = f"[{self.correlation_id}] {base_msg}"
        return base_msg


class ConfigurationError(MoodleMateException):
    """Configuration-related errors."""

    pass


class NotificationError(MoodleMateException):
    """Notification processing errors."""

    pass


class ProviderError(NotificationError):
    """Provider-specific errors."""

    pass


class SecurityError(MoodleMateException):
    """Security-related errors."""

    pass


class AuthenticationError(SecurityError):
    """Authentication and authorization errors."""

    pass


class ValidationError(SecurityError):
    """Input validation errors."""

    pass


class RateLimitError(SecurityError):
    """Rate limiting errors."""

    pass


class APIError(MoodleMateException):
    """API communication errors."""

    pass


class NetworkError(APIError):
    """Network connectivity errors."""

    pass


class TimeoutError(NetworkError):
    """Request timeout errors."""

    pass


class ServiceError(MoodleMateException):
    """Service initialization and management errors."""

    pass


class DependencyError(ServiceError):
    """Dependency injection and service locator errors."""

    pass
