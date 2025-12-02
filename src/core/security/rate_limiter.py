"""Rate limiting implementation for Moodle Mate."""

import time
import logging
from collections import defaultdict, deque
from typing import Dict, Optional
from threading import Lock
import hashlib

logger = logging.getLogger(__name__)


class TokenBucketRateLimiter:
    """Token bucket rate limiter implementation."""

    def __init__(self, max_requests: int, time_window: int):
        """Initialize rate limiter.

        Args:
            max_requests: Maximum number of requests allowed
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.buckets: Dict[str, deque] = defaultdict(deque)
        self.lock = Lock()

    def _get_bucket_key(self, identifier: str) -> str:
        """Generate a consistent bucket key for an identifier.

        Args:
            identifier: String identifier (URL, username, etc.)

        Returns:
            Consistent bucket key
        """
        # Use hash to create consistent keys and prevent key length issues
        return hashlib.md5(identifier.encode()).hexdigest()

    def is_allowed(self, identifier: str) -> bool:
        """Check if a request is allowed for the given identifier.

        Args:
            identifier: Unique identifier for the requester

        Returns:
            True if request is allowed, False otherwise
        """
        bucket_key = self._get_bucket_key(identifier)

        with self.lock:
            now = time.time()
            bucket = self.buckets[bucket_key]

            # Remove old requests outside the time window
            while bucket and bucket[0] <= now - self.time_window:
                bucket.popleft()

            # Check if we can make a new request
            if len(bucket) < self.max_requests:
                bucket.append(now)
                return True

            # Rate limit exceeded
            return False

    def get_remaining_requests(self, identifier: str) -> int:
        """Get the number of remaining requests for the identifier.

        Args:
            identifier: Unique identifier for the requester

        Returns:
            Number of remaining requests
        """
        bucket_key = self._get_bucket_key(identifier)

        with self.lock:
            now = time.time()
            bucket = self.buckets[bucket_key]

            # Remove old requests
            while bucket and bucket[0] <= now - self.time_window:
                bucket.popleft()

            return max(0, self.max_requests - len(bucket))

    def get_reset_time(self, identifier: str) -> Optional[float]:
        """Get the time when the rate limit will reset.

        Args:
            identifier: Unique identifier for the requester

        Returns:
            Unix timestamp when rate limit resets, or None if no active requests
        """
        bucket_key = self._get_bucket_key(identifier)

        with self.lock:
            bucket = self.buckets[bucket_key]
            if bucket:
                return bucket[0] + self.time_window
            return None

    def reset(self, identifier: str) -> None:
        """Reset the rate limit for a specific identifier.

        Args:
            identifier: Unique identifier for the requester
        """
        bucket_key = self._get_bucket_key(identifier)

        with self.lock:
            if bucket_key in self.buckets:
                del self.buckets[bucket_key]

    def clear_all(self) -> None:
        """Clear all rate limit data (for testing)."""
        with self.lock:
            self.buckets.clear()


class RateLimiterManager:
    """Manages multiple rate limiters for different use cases."""

    def __init__(self):
        """Initialize the rate limiter manager."""
        self.rate_limiters: Dict[str, TokenBucketRateLimiter] = {}
        self.lock = Lock()

        # Default rate limits
        self._setup_default_limits()

    def _setup_default_limits(self) -> None:
        """Setup default rate limits for common use cases."""
        # Moodle API: 60 requests per minute
        self.register_limiter("moodle_api", 60, 60)

        # AI APIs: 100 requests per minute
        self.register_limiter("ai_api", 100, 60)

        # Notification providers: 30 requests per minute
        self.register_limiter("notification_provider", 30, 60)

        # General HTTP requests: 120 requests per minute
        self.register_limiter("http_general", 120, 60)

    def register_limiter(self, name: str, max_requests: int, time_window: int) -> None:
        """Register a new rate limiter.

        Args:
            name: Name of the rate limiter
            max_requests: Maximum requests allowed
            time_window: Time window in seconds
        """
        with self.lock:
            self.rate_limiters[name] = TokenBucketRateLimiter(max_requests, time_window)
            logger.info(
                f"Registered rate limiter '{name}': {max_requests} requests per {time_window}s"
            )

    def is_allowed(self, limiter_name: str, identifier: str) -> bool:
        """Check if a request is allowed.

        Args:
            limiter_name: Name of the rate limiter to use
            identifier: Unique identifier for the requester

        Returns:
            True if allowed, False otherwise
        """
        with self.lock:
            if limiter_name not in self.rate_limiters:
                logger.warning(
                    f"Rate limiter '{limiter_name}' not found, allowing request"
                )
                return True

            return self.rate_limiters[limiter_name].is_allowed(identifier)

    def get_remaining_requests(self, limiter_name: str, identifier: str) -> int:
        """Get remaining requests for a limiter.

        Args:
            limiter_name: Name of the rate limiter
            identifier: Unique identifier for the requester

        Returns:
            Number of remaining requests
        """
        with self.lock:
            if limiter_name not in self.rate_limiters:
                return 999  # Return high number if limiter doesn't exist

            return self.rate_limiters[limiter_name].get_remaining_requests(identifier)

    def get_reset_time(self, limiter_name: str, identifier: str) -> Optional[float]:
        """Get reset time for a limiter.

        Args:
            limiter_name: Name of the rate limiter
            identifier: Unique identifier for the requester

        Returns:
            Reset time or None
        """
        with self.lock:
            if limiter_name not in self.rate_limiters:
                return None

            return self.rate_limiters[limiter_name].get_reset_time(identifier)

    def reset_limiter(self, limiter_name: str, identifier: str) -> None:
        """Reset a specific rate limiter for an identifier.

        Args:
            limiter_name: Name of the rate limiter
            identifier: Unique identifier for the requester
        """
        with self.lock:
            if limiter_name in self.rate_limiters:
                self.rate_limiters[limiter_name].reset(identifier)

    def clear_all_limits(self) -> None:
        """Clear all rate limits (for testing)."""
        with self.lock:
            for limiter in self.rate_limiters.values():
                limiter.clear_all()


# Global rate limiter instance
rate_limiter_manager = RateLimiterManager()


def rate_limit_limiter(limiter_name: str, identifier_key: str = None):
    """Decorator to apply rate limiting to a function.

    Args:
        limiter_name: Name of the rate limiter to use
        identifier_key: Key to extract identifier from function args/kwargs
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate identifier
            if identifier_key:
                if identifier_key in kwargs:
                    identifier = str(kwargs[identifier_key])
                elif len(args) > 0:
                    identifier = str(args[0])
                else:
                    identifier = "default"
            else:
                # Use function name as default identifier
                identifier = func.__name__

            # Check rate limit
            if not rate_limiter_manager.is_allowed(limiter_name, identifier):
                remaining = rate_limiter_manager.get_remaining_requests(
                    limiter_name, identifier
                )
                reset_time = rate_limiter_manager.get_reset_time(
                    limiter_name, identifier
                )

                logger.warning(
                    f"Rate limit exceeded for '{limiter_name}' "
                    f"(identifier: {identifier}, remaining: {remaining}, resets at: {reset_time})"
                )

                # In production, you might want to raise an exception here
                # For now, we'll just log and continue
                return None

            return func(*args, **kwargs)

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper

    return decorator
