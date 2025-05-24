from unittest.mock import Mock

import pytest

from core.config.loader import Config
from core.notification.base import NotificationProvider
from core.notification.processor import NotificationProcessor


@pytest.fixture
def mock_config() -> Config:
    """Create a mock configuration."""
    config = Mock()
    config.get_discord_enabled.return_value = True
    config.get_pushbullet_enabled.return_value = True
    config.get_summarize_enabled.return_value = True
    return config


@pytest.fixture
def mock_providers() -> list[NotificationProvider]:
    """Create a list of mock notification providers."""
    provider1 = Mock(spec=NotificationProvider)
    provider1.send.return_value = True
    provider2 = Mock(spec=NotificationProvider)
    provider2.send.return_value = True
    return [provider1, provider2]


@pytest.fixture
def processor(mock_config: Config, mock_providers: list[NotificationProvider]) -> NotificationProcessor:
    """Create a notification processor instance."""
    # Since NotificationProcessor is a singleton, ensure we can re-initialize for tests
    NotificationProcessor._instance = None  # type: ignore
    return NotificationProcessor(config=mock_config, providers=mock_providers)


@pytest.fixture
def mock_notification() -> dict:
    """Create a mock notification dictionary."""
    return {"id": 1, "subject": "Test Subject", "fullmessagehtml": "<p>Test message content.</p>"}


def test_process_notification_with_summary(
    processor: NotificationProcessor,
    mock_notification: dict,
    mock_config: Config,
):
    """Test processing a notification with summary enabled."""
    mock_config.ai.enabled = True  # Ensure AI is enabled for summary
    processor.process(mock_notification)
    # Add assertions here to check if summarizer was called, providers received correct data


def test_process_notification_without_summary(
    processor: NotificationProcessor,
    mock_notification: dict,
    mock_config: Config,
) -> None:
    """Test processing a notification without summary."""
    mock_config.ai.enabled = False  # Ensure AI is disabled
    processor.process(mock_notification)
    # Add assertions here, e.g., summarizer not called


def test_process_notification_with_empty_message(processor: NotificationProcessor, mock_config: Config) -> None:
    """Test processing a notification with empty message."""
    mock_config.ai.enabled = False
    notification = {"id": 1, "subject": "Test", "fullmessagehtml": ""}
    processor.process(notification)
    # Assert providers were not called or handled gracefully


def test_process_notification_with_none_message(processor: NotificationProcessor, mock_config: Config) -> None:
    """Test processing a notification with None message."""
    mock_config.ai.enabled = False
    notification = {"id": 1, "subject": "Test", "fullmessagehtml": None}
    processor.process(notification)
    # Assert providers were not called or handled gracefully


def test_process_notification_with_html_message(
    processor: NotificationProcessor,
    mock_notification: dict,
    mock_config: Config,
) -> None:
    """Test processing a notification with HTML message."""
    mock_config.ai.enabled = False
    processor.process(mock_notification)
    # Assert that HTML was converted to markdown for providers


def test_process_notification_with_long_message(processor: NotificationProcessor, mock_config: Config) -> None:
    """Test processing a notification with long message."""
    mock_config.ai.enabled = True  # Example: test summary with long message
    long_html_message = "<p>This is a very long message. " * 100 + "</p>"
    notification = {"id": 1, "subject": "Long Test", "fullmessagehtml": long_html_message}
    processor.process(notification)
    # Assert summarizer called, providers received (potentially truncated or summarized) content


def test_process_notification_with_special_chars(processor: NotificationProcessor, mock_config: Config) -> None:
    """Test processing a notification with special characters."""
    mock_config.ai.enabled = False
    notification = {"id": 1, "subject": "Special Chars Test", "fullmessagehtml": "<p>Test &amp; &lt; &gt; \\\" '</p>"}
    processor.process(notification)
    # Assert special characters are handled/escaped correctly for markdown and providers


def test_process_notification_with_multiple_paragraphs(processor: NotificationProcessor, mock_config: Config) -> None:
    """Test processing a notification with multiple paragraphs."""
    mock_config.ai.enabled = False
    notification = {"id": 1, "subject": "Multi Para Test", "fullmessagehtml": "<p>Paragraph 1.</p><p>Paragraph 2.</p>"}
    processor.process(notification)
    # Assert multiple paragraphs are converted correctly to markdown


def test_process_notification_with_links(processor: NotificationProcessor, mock_config: Config) -> None:
    """Test processing a notification with links."""
    mock_config.ai.enabled = False
    notification = {
        "id": 1,
        "subject": "Link Test",
        "fullmessagehtml": '<p>Check out <a href="https://example.com">this link</a>!</p>',
    }
    processor.process(notification)
    # Assert link is preserved in markdown


def test_process_notification_with_images(processor: NotificationProcessor, mock_config: Config) -> None:
    """Test processing a notification with images."""
    mock_config.ai.enabled = False
    notification = {
        "id": 1,
        "subject": "Image Test",
        "fullmessagehtml": '<p>Look at this image: <img src="test.jpg" alt="Test Image"></p>',
    }
    processor.process(notification)
    # Assert image tag is handled (e.g., converted to markdown image link or alt text)
