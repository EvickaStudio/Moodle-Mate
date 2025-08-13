from unittest.mock import MagicMock

import pytest

from src.core.config.schema import AIConfig
from src.core.notification.summarizer import NotificationSummarizer
from src.core.service_locator import ServiceLocator
from src.services.ai.chat import GPT


class DummyGPT(GPT):
    def chat_completion(
        self, model, system_message, user_message, temperature, max_tokens
    ):
        return "SUMMARIZED"


@pytest.fixture
def config_with_ai():
    cfg = MagicMock()
    cfg.ai = AIConfig(
        enabled=True,
        api_key="sk-" + "a" * 60,
        model="gpt-4o-mini",
        temperature=0.1,
        max_tokens=64,
        system_prompt="Summarize",
        endpoint=None,
    )
    return cfg


def test_init_requires_api_key():
    cfg = MagicMock()
    cfg.ai = AIConfig(enabled=True, api_key="")
    with pytest.raises(ValueError):
        NotificationSummarizer(cfg)


def test_init_disabled_allows_no_provider():
    cfg = MagicMock()
    cfg.ai = AIConfig(enabled=False)
    # Should not raise
    NotificationSummarizer(cfg)


def test_summarize_happy_path(config_with_ai):
    ServiceLocator.register("gpt", DummyGPT())
    summarizer = NotificationSummarizer(config_with_ai)
    assert summarizer.summarize("Some long text") == "SUMMARIZED"


def test_summarize_empty_raises(config_with_ai):
    ServiceLocator.register("gpt", DummyGPT())
    summarizer = NotificationSummarizer(config_with_ai)
    with pytest.raises(ValueError):
        summarizer.summarize("  ")


def test_summarize_disabled_returns_input():
    cfg = MagicMock()
    cfg.ai = AIConfig(enabled=False)
    summarizer = NotificationSummarizer(cfg)
    # When disabled, code returns the original text
    assert summarizer.summarize("abc") == "abc"
