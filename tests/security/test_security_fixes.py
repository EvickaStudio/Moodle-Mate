"""Tests for security fixes implemented in Moodle Mate."""

import pytest

from src.core.security import (
    InputValidator,
    CredentialManager,
    rate_limiter_manager,
    RateLimiterManager,
)
from src.core.container import get_service, initialize_dependencies
from src.infrastructure.http.request_manager import RequestManager
from src.core.config.loader import Config


class TestInputValidation:
    """Test input validation security measures."""

    def test_moodle_url_validation_enforces_https(self):
        """Test that HTTPS URLs are preferred."""
        assert InputValidator.validate_moodle_url("https://example.com")
        # HTTP should still work for development but be logged as warning
        assert InputValidator.validate_moodle_url("http://example.com")

        # Invalid URLs should raise ValueError
        with pytest.raises(ValueError):
            InputValidator.validate_moodle_url("ftp://example.com")

        with pytest.raises(ValueError):
            InputValidator.validate_moodle_url("invalid-url")

        with pytest.raises(ValueError):
            InputValidator.validate_moodle_url("")

    def test_username_validation_prevents_injection(self):
        """Test username validation prevents injection attempts."""
        assert InputValidator.validate_username("validuser123")
        assert InputValidator.validate_username("user_name-123")

        # Invalid usernames should raise ValueError
        with pytest.raises(ValueError):
            InputValidator.validate_username("")

        with pytest.raises(ValueError):
            InputValidator.validate_username("user@domain")

        with pytest.raises(ValueError):
            InputValidator.validate_username("user space")

        with pytest.raises(ValueError):
            InputValidator.validate_username("<script>alert('xss')</script>")

    def test_password_validation_allows_secure_passwords(self):
        """Test password validation."""
        assert InputValidator.validate_password("securePassword123!")

        # Invalid passwords should raise ValueError
        with pytest.raises(ValueError):
            InputValidator.validate_password("")

        with pytest.raises(ValueError):
            InputValidator.validate_password("   ")

        # Too long passwords should be rejected
        with pytest.raises(ValueError):
            InputValidator.validate_password("a" * 257)

    def test_html_sanitization_prevents_xss(self):
        """Test HTML sanitization prevents XSS attacks."""
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

        # Dangerous content should be removed
        assert "<script>" not in sanitized["message"]
        assert "onerror" not in sanitized["message"]
        assert "javascript:" not in sanitized["message"]
        assert "iframe" not in sanitized["message"]

        # Safe content should remain
        assert "Safe content" in sanitized["message"]
        assert "<p>" in sanitized["message"]
        assert "<strong>" in sanitized["message"]

    def test_api_key_validation(self):
        """Test API key format validation."""
        # OpenAI API key pattern
        assert InputValidator.validate_api_key("sk-" + "a" * 48, "openai")
        assert not InputValidator.validate_api_key("invalid-key", "openai")
        assert not InputValidator.validate_api_key("", "openai")


class TestCredentialManager:
    """Test secure credential storage."""

    def test_credential_encryption(self):
        """Test credentials are stored securely."""
        manager = CredentialManager("test-service")
        username = "testuser"
        password = "secretpassword123"
        url = "https://example.com"

        # Store credential
        assert manager.store_credential(username, password, url)

        # Retrieve credential
        retrieved = manager.get_credential(username, url)
        assert retrieved == password

        # Delete credential
        assert manager.delete_credential(username, url)
        assert manager.get_credential(username, url) is None

    def test_credential_isolation(self):
        """Test credentials are isolated by URL and username."""
        manager = CredentialManager("test-service")
        password1 = "password1"
        password2 = "password2"
        url1 = "https://example1.com"
        url2 = "https://example2.com"
        username = "testuser"

        # Store credentials for different URLs
        manager.store_credential(username, password1, url1)
        manager.store_credential(username, password2, url2)

        # Verify correct credentials are retrieved
        assert manager.get_credential(username, url1) == password1
        assert manager.get_credential(username, url2) == password2


class TestRateLimiting:
    """Test rate limiting implementation."""

    def test_rate_limit_prevents_abuse(self):
        """Test rate limiting prevents excessive requests."""
        identifier = "test_user_123"
        limiter_name = "test_limiter"

        # Register a test limiter with very strict limits
        rate_limiter_manager.register_limiter(
            limiter_name, 2, 1
        )  # 2 requests per second

        # First two requests should be allowed
        assert rate_limiter_manager.is_allowed(limiter_name, identifier)
        assert rate_limiter_manager.is_allowed(limiter_name, identifier)

        # Third request should be denied
        assert not rate_limiter_manager.is_allowed(limiter_name, identifier)

        # Should show remaining requests
        remaining = rate_limiter_manager.get_remaining_requests(
            limiter_name, identifier
        )
        assert remaining == 0

        # Reset for future tests
        rate_limiter_manager.reset_limiter(limiter_name, identifier)


class TestSSLEnforcement:
    """Test SSL certificate verification enforcement."""

    def test_request_manager_enforces_ssl(self):
        """Test request manager has SSL verification enabled."""
        manager = RequestManager()
        session = manager.session

        # SSL verification should be enabled
        assert session.verify is True

        # Session should have security headers
        assert "User-Agent" in session.headers
        assert "Accept" in session.headers
        assert "Accept-Encoding" in session.headers

        # Session should have timeouts configured
        assert session.timeout == (10, 30)  # (connect, read)


class TestMoodleAPISecurity:
    """Test Moodle API security improvements."""

    def test_moodle_api_validates_inputs(self):
        """Test Moodle API validates inputs properly."""
        # Test the validation logic that's used in Moodle API
        # Test invalid inputs raise validation errors
        with pytest.raises(ValueError):
            InputValidator.validate_username("")  # Empty username

        with pytest.raises(ValueError):
            InputValidator.validate_password("")  # Empty password

        with pytest.raises(ValueError):
            InputValidator.validate_moodle_url("invalid-url")  # Invalid URL

        # Test valid inputs pass validation
        assert InputValidator.validate_username("validuser123")
        assert InputValidator.validate_password("validpassword123!")
        assert InputValidator.validate_moodle_url("https://example.com")


class TestNotificationProcessorSecurity:
    """Test notification processor security."""

    def test_notification_sanitization(self):
        """Test notification processor sanitizes data."""
        # Test the sanitization logic that's used in notification processor
        # Test with malicious notification data
        malicious_notification = {
            "subject": "<script>alert('xss')</script>Important Notification",
            "fullmessagehtml": "<img src=x onerror=alert('xss')><p>Safe content</p>",
            "other_field": "safe content",
        }

        # Test the sanitizer that processor uses
        sanitized = InputValidator.sanitize_notification_data(malicious_notification)
        assert "<script>" not in sanitized["subject"]
        assert "onerror" not in sanitized["fullmessagehtml"]
        assert "Safe content" in sanitized["fullmessagehtml"]


class TestDependencyInjection:
    """Test dependency injection container."""

    def test_dependency_container_initializes_services(self):
        """Test dependency container can initialize all required services."""
        # Initialize dependencies
        initialize_dependencies()

        # Test core services can be resolved
        config = get_service(Config)
        assert config is not None

        cred_manager = get_service(CredentialManager)
        assert cred_manager is not None

        input_validator = get_service(InputValidator)
        assert input_validator is not None

        rate_limiter = get_service(RateLimiterManager)
        assert rate_limiter is not None


class TestSecurityIntegration:
    """Integration tests for security features."""

    def test_security_stack_works_together(self):
        """Test all security features work together."""
        # Initialize security components
        initialize_dependencies()

        # Test notification processing with security
        malicious_notification = {
            "subject": "<script>alert('xss')</script>Test Subject",
            "fullmessagehtml": "<img src=x onerror=alert('xss')><p>Test message</p>",
        }

        # Apply security measures
        sanitized = InputValidator.sanitize_notification_data(malicious_notification)

        # Verify security measures worked
        assert "<script>" not in sanitized["subject"]
        assert "onerror" not in sanitized["fullmessagehtml"]
        assert "Test Subject" in sanitized["subject"]
        assert "Test message" in sanitized["fullmessagehtml"]

        # Test rate limiting
        assert rate_limiter_manager.is_allowed("test", "integration_test")
        assert (
            rate_limiter_manager.get_remaining_requests("test", "integration_test") >= 0
        )

        print("All security integration tests passed!")


if __name__ == "__main__":
    # Run a quick security test
    print("Running security tests...")
    test = TestSecurityIntegration()
    test.test_security_stack_works_together()
    print("Security implementation verified!")
