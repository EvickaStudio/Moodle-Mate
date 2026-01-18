class OpenAIError(Exception):
    """Base exception for OpenAI-related errors."""

    pass


class InvalidAPIKeyError(OpenAIError):
    """Raised when the API key is invalid."""

    pass


class TokenizationError(OpenAIError):
    """Raised when token counting fails."""

    pass


class ChatCompletionError(OpenAIError):
    """Raised when chat completion fails."""

    pass


class RateLimitExceededError(OpenAIError):
    """Raised when OpenAI rate limits are exceeded."""

    pass


class APITimeoutError(OpenAIError):
    """Raised when an API request times out."""

    pass


class APIConnectionError(OpenAIError):
    """Raised when there's a connection issue with the API."""

    pass


class ServerError(OpenAIError):
    """Raised when the OpenAI server returns a 5xx error."""

    pass


class ClientError(OpenAIError):
    """Raised when there's a client-side error (4xx)."""

    pass
