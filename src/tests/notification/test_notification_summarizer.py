# ruff: noqa: S101
from unittest.mock import Mock, patch

import pytest

from core.notification.summarizer import NotificationSummarizer
from src.core.config.loader import Config


@pytest.fixture
def mock_config() -> Config:
    """Create a mock configuration that specs the Config class."""
    config = Mock(spec=Config)

    config.ai = Mock()
    config.ai.enabled = True
    config.ai.api_key = "test-key"
    config.ai.model = "gpt-3.5-turbo"
    config.ai.endpoint = "https://api.openai.com/v1"
    config.ai.temperature = 0.7
    config.ai.max_tokens = 150
    config.ai.context = "Test context"

    return config


def test_summarizer_initialization(mock_config: Config) -> None:
    """Test summarizer initialization."""
    summarizer = NotificationSummarizer(mock_config)
    assert summarizer is not None


def test_summarize_with_empty_text(mock_config: Config) -> None:
    """Test summarization with empty text."""
    summarizer = NotificationSummarizer(mock_config)
    assert summarizer.summarize("") is None


def test_summarize_with_short_text(mock_config: Config) -> None:
    """Test summarization with short text."""
    summarizer = NotificationSummarizer(mock_config)
    text = "This is a short text."
    assert summarizer.summarize(text) is None


def test_summarize_with_long_text(mock_config: Config) -> None:
    """Test summarization with long text."""
    summarizer = NotificationSummarizer(mock_config)
    text = "This is a very long text. " * 50
    with patch("src.core.service_locator.ServiceLocator.get") as mock_service_get:
        mock_gpt_instance = Mock()
        mock_gpt_instance.chat_completion.return_value = "Summary"
        mock_service_get.return_value = mock_gpt_instance

        assert summarizer.summarize(text) == "Summary"
        mock_service_get.assert_called_once_with("gpt")


def test_summarize_with_html_text(mock_config: Config) -> None:
    """Test summarization with HTML text."""
    summarizer = NotificationSummarizer(mock_config)
    text = "<p>This is a very long text with HTML tags.</p> " * 50
    with patch("src.core.service_locator.ServiceLocator.get") as mock_service_get:
        mock_gpt_instance = Mock()
        mock_gpt_instance.chat_completion.return_value = "Summary of HTML"
        mock_service_get.return_value = mock_gpt_instance

        assert summarizer.summarize(text) == "Summary of HTML"
        mock_service_get.assert_called_once_with("gpt")


def test_summarize_with_api_error(mock_config: Config) -> None:
    """Test summarization with API error."""
    summarizer = NotificationSummarizer(mock_config)
    text = "This is a very long text. " * 50
    with patch("src.core.service_locator.ServiceLocator.get") as mock_service_get:
        mock_gpt_instance = Mock()
        mock_gpt_instance.chat_completion.side_effect = Exception("API Error")
        mock_service_get.return_value = mock_gpt_instance

        assert summarizer.summarize(text) is None
        mock_service_get.assert_called_once_with("gpt")


def test_summarize_disabled(mock_config: Config) -> None:
    """Test summarization when disabled."""
    mock_config.ai.enabled = False
    summarizer = NotificationSummarizer(mock_config)
    assert summarizer.summarize("Any text") is None
