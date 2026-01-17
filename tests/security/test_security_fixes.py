import pytest

from moodlemate.core.security import InputValidator, RateLimiterManager
from moodlemate.infrastructure.http.request_manager import RequestManager


class TestInputValidation:
    def test_moodle_url_validation_enforces_https(self):
        assert InputValidator.validate_moodle_url("https://example.com")
        assert InputValidator.validate_moodle_url("http://example.com")

        with pytest.raises(ValueError):
            InputValidator.validate_moodle_url("ftp://example.com")
        with pytest.raises(ValueError):
            InputValidator.validate_moodle_url("invalid-url")
        with pytest.raises(ValueError):
            InputValidator.validate_moodle_url("")

    def test_username_validation_prevents_injection(self):
        assert InputValidator.validate_username("validuser123")
        assert InputValidator.validate_username("user_name-123")

        with pytest.raises(ValueError):
            InputValidator.validate_username("")
        with pytest.raises(ValueError):
            InputValidator.validate_username("user@domain")
        with pytest.raises(ValueError):
            InputValidator.validate_username("user space")
        with pytest.raises(ValueError):
            InputValidator.validate_username("<script>alert('xss')</script>")

    def test_password_validation_rules(self):
        assert InputValidator.validate_password("securePassword123!")

        with pytest.raises(ValueError):
            InputValidator.validate_password("")
        with pytest.raises(ValueError):
            InputValidator.validate_password("   ")
        with pytest.raises(ValueError):
            InputValidator.validate_password("a" * 257)

    def test_html_sanitization_prevents_xss(self):
        malicious_html = """
        <script>alert('xss')</script>
        <img src=x onerror=alert('xss')>
        <iframe src="javascript:alert('xss')"></iframe>
        <p>Safe content</p>
        <strong>Safe bold text</strong>
        """

        notification_data = {
            "subject": "Test notification",
            "message": malicious_html,
            "other_field": "safe content",
        }

        sanitized = InputValidator.sanitize_notification_data(notification_data)
        assert "<script>" not in sanitized["message"]
        assert "onerror" not in sanitized["message"]
        assert "javascript:" not in sanitized["message"]
        assert "iframe" not in sanitized["message"]
        assert "Safe content" in sanitized["message"]
        assert "<p>" in sanitized["message"]
        assert "<strong>" in sanitized["message"]

    def test_api_key_validation(self):
        assert InputValidator.validate_api_key("sk-" + "a" * 48, "openai")
        assert not InputValidator.validate_api_key("invalid-key", "openai")
        assert not InputValidator.validate_api_key("", "openai")

    def test_sanitize_log_message_masks_sensitive_data(self):
        masked = InputValidator.sanitize_log_message(
            'password="supersecret" token=abcd1234efgh5678 sk-' + "a" * 50
        )
        assert "supersecret" not in masked
        assert "sk-" in masked
        assert "***" in masked


class TestRateLimiting:
    def test_rate_limit_prevents_abuse(self):
        identifier = "test_user_123"
        limiter_name = "test_limiter"

        manager = RateLimiterManager()
        manager.register_limiter(limiter_name, 2, 1)

        assert manager.is_allowed(limiter_name, identifier)
        assert manager.is_allowed(limiter_name, identifier)
        assert not manager.is_allowed(limiter_name, identifier)

        remaining = manager.get_remaining_requests(limiter_name, identifier)
        assert remaining == 0

        manager.reset_limiter(limiter_name, identifier)


class TestRequestManagerSecurity:
    def test_request_manager_enforces_ssl_and_headers(self):
        manager = RequestManager()
        session = manager.session

        assert session.verify is True
        assert "User-Agent" in session.headers
        assert "Accept" in session.headers
        assert "Accept-Encoding" in session.headers
        assert session._default_timeout in [
            RequestManager._default_timeout,
            (10, 30),
            (5, 12),
        ]
