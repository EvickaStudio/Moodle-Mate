"""Input validation and sanitization for Moodle Mate."""

import html
import logging
import re
from typing import Any, ClassVar
from urllib.parse import urlparse

import bleach

logger = logging.getLogger(__name__)


class InputValidator:
    """Input validation and sanitization utilities."""

    # HTML tags allowed in notifications
    ALLOWED_HTML_TAGS: ClassVar[list[str]] = [
        "p",
        "br",
        "strong",
        "em",
        "b",
        "i",
        "u",
        "ol",
        "ul",
        "li",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "blockquote",
        "code",
        "pre",
        "a",  # Allow links for clickable URLs in notifications
    ]

    # HTML attributes allowed (safe attributes for security)
    ALLOWED_HTML_ATTRIBUTES: ClassVar[dict[str, list[str]]] = {
        "a": ["href", "title"],  # Allow href and title attributes for links
        "*": ["class"],  # Allow class attribute on any element
    }

    # URL validation patterns
    MOODLE_URL_PATTERN = re.compile(
        r"^https?://[a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,})+(?:/.*)?$"
    )

    # Username validation pattern
    USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9._-]{1,100}$")

    # API key pattern validation
    API_KEY_PATTERNS: ClassVar[dict[str, re.Pattern[str]]] = {
        "openai": re.compile(r"^sk-[A-Za-z0-9_-]{48,}$"),
        "discord": re.compile(r"^[a-zA-Z0-9_-]{24,}$"),
        "pushbullet": re.compile(r"^[a-zA-Z0-9._-]{43}$"),
    }

    @classmethod
    def sanitize_notification_data(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Sanitize notification data to prevent XSS and injection attacks.

        Args:
            data: Raw notification data dictionary

        Returns:
            Sanitized notification data
        """
        if not isinstance(data, dict):
            logger.warning("Invalid data type for sanitization: expected dict")
            return {}

        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                # First, unescape any existing HTML entities
                unescaped = html.unescape(value)

                # Remove potentially dangerous HTML tags and attributes
                cleaned = bleach.clean(
                    unescaped,
                    tags=cls.ALLOWED_HTML_TAGS,
                    attributes=cls.ALLOWED_HTML_ATTRIBUTES,
                    strip=True,
                )

                # Additional XSS protection
                safe_value = cls._xss_protection(cleaned)
                sanitized[key] = safe_value

            elif isinstance(value, dict):
                # Recursively sanitize nested dictionaries
                sanitized[key] = cls.sanitize_notification_data(value)
            elif isinstance(value, list):
                # Sanitize list items
                sanitized[key] = [
                    cls.sanitize_notification_data({"item": item})["item"]
                    if isinstance(item, dict | str)
                    else item
                    for item in value
                ]
            else:
                # Keep other types as-is
                sanitized[key] = value

        logger.debug(f"Sanitized notification data with {len(data)} fields")
        return sanitized

    @classmethod
    def _xss_protection(cls, text: str) -> str:
        """Additional XSS protection for text content.

        Args:
            text: Text to protect against XSS

        Returns:
            XSS-protected text
        """
        if not isinstance(text, str):
            return text

        # Remove javascript: URLs
        text = re.sub(r"javascript\s*:", "", text, flags=re.IGNORECASE)

        # Remove on* event handlers
        text = re.sub(r"on\w+\s*=", "", text, flags=re.IGNORECASE)

        # Remove data: URLs that could be malicious
        text = re.sub(r"data\s*:", "", text, flags=re.IGNORECASE)

        return text

    @classmethod
    def validate_moodle_url(cls, url: str) -> bool:
        """Validate Moodle instance URL.

        Args:
            url: URL to validate

        Returns:
            True if valid, False otherwise

        Raises:
            ValueError: If URL format is invalid
        """
        if not url or not isinstance(url, str):
            raise ValueError("URL must be a non-empty string")

        # Basic URL format validation
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("Invalid URL format - missing scheme or domain")

            # Enforce HTTPS for security
            if parsed.scheme not in ["http", "https"]:
                raise ValueError("URL must use HTTP or HTTPS protocol")

            # Recommend HTTPS for security
            if parsed.scheme == "http":
                logger.warning(f"Insecure URL detected: {url} - HTTPS recommended")

            # Check against Moodle URL pattern
            if not cls.MOODLE_URL_PATTERN.match(url):
                raise ValueError("URL format is not valid for Moodle instances")

            return True

        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"URL validation error: {e}") from e

    @classmethod
    def validate_username(cls, username: str) -> bool:
        """Validate username format.

        Args:
            username: Username to validate

        Returns:
            True if valid, False otherwise

        Raises:
            ValueError: If username format is invalid
        """
        if not username or not isinstance(username, str):
            raise ValueError("Username must be a non-empty string")

        username = username.strip()
        if not username:
            raise ValueError("Username cannot be empty")

        if not cls.USERNAME_PATTERN.match(username):
            raise ValueError("Username contains invalid characters")

        return True

    @classmethod
    def validate_password(cls, password: str) -> bool:
        """Validate password format.

        Args:
            password: Password to validate

        Returns:
            True if valid, False otherwise

        Raises:
            ValueError: If password format is invalid
        """
        if not password or not isinstance(password, str):
            raise ValueError("Password must be a non-empty string")

        password = password.strip()
        if not password:
            raise ValueError("Password cannot be empty")

        # Basic password validation - prevent empty or extremely long passwords
        if len(password) > 256:
            raise ValueError("Password is too long (maximum 256 characters)")

        return True

    @classmethod
    def validate_api_key(cls, api_key: str, provider: str) -> bool:
        """Validate API key format for different providers.

        Args:
            api_key: API key to validate
            provider: Provider name (openai, discord, pushbullet)

        Returns:
            True if valid format, False otherwise
        """
        if not api_key or not isinstance(api_key, str):
            return False

        pattern = cls.API_KEY_PATTERNS.get(provider.lower())
        if pattern:
            return bool(pattern.match(api_key))

        # If no specific pattern, do basic validation
        return len(api_key) >= 10 and api_key.isprintable()

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """Sanitize filename to prevent directory traversal.

        Args:
            filename: Filename to sanitize

        Returns:
            Sanitized filename
        """
        if not filename or not isinstance(filename, str):
            return "default"

        # Remove path separators and dangerous characters
        sanitized = re.sub(r'[<>:"/\\|?*]', "", filename)
        sanitized = re.sub(r"\.\.", "", sanitized)  # Remove directory traversal
        sanitized = sanitized.strip()

        # Ensure it's not empty after sanitization
        if not sanitized:
            return "default"

        return sanitized

    @classmethod
    def validate_html_content(cls, content: str) -> bool:
        """Validate HTML content for security.

        Args:
            content: HTML content to validate

        Returns:
            True if safe, False otherwise
        """
        if not content or not isinstance(content, str):
            return True

        # Check for dangerous patterns
        dangerous_patterns = [
            r"<script[^>]*>",
            r"javascript\s*:",
            r"on\w+\s*=",
            r"data\s*:",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                logger.warning(
                    f"Potentially dangerous HTML content detected: {pattern}"
                )
                return False

        return True

    @classmethod
    def sanitize_log_message(cls, message: str) -> str:
        """Sanitize log messages to prevent information disclosure.

        Args:
            message: Log message to sanitize

        Returns:
            Sanitized log message
        """
        if not message or not isinstance(message, str):
            return ""

        # Remove potential sensitive information
        sanitized = message

        # Mask potential API keys
        sanitized = re.sub(
            r"(sk-[A-Za-z0-9_-]{10})[A-Za-z0-9_-]{38,}", r"\1***", sanitized
        )

        # Mask potential passwords
        sanitized = re.sub(
            r'(password["\s]*[:=]["\s]*)([^"\'\s]{8,})',
            r"\1***",
            sanitized,
            flags=re.IGNORECASE,
        )

        # Mask potential tokens
        sanitized = re.sub(
            r'(token["\s]*[:=]["\s]*)([a-zA-Z0-9_-]{20,})',
            r"\1***",
            sanitized,
            flags=re.IGNORECASE,
        )

        return sanitized
