from unittest.mock import MagicMock

import pytest

from moodlemate.ai.chat import GPT
from moodlemate.config import AIConfig
from moodlemate.notifications.summarizer import NotificationSummarizer


class DummyGPT(GPT):
    def chat_completion(
        self, model, system_message, user_message, temperature, max_tokens
    ):
        return "SUMMARIZED"


class ExplodingGPT(GPT):
    def chat_completion(
        self, model, system_message, user_message, temperature, max_tokens
    ):
        raise RuntimeError("boom")


@pytest.fixture
def config_with_ai():
    cfg = MagicMock()
    cfg.ai = AIConfig(
        enabled=True,
        api_key="sk-test-key-for-testing-only-do-not-use-in-production-1234567890",
        model="gpt-4o-mini",
        temperature=0.1,
        max_tokens=64,
        system_prompt="Summarize",
        endpoint=None,
    )
    return cfg


def test_init_enabled_requires_provider(config_with_ai):
    with pytest.raises(ValueError):
        NotificationSummarizer(config_with_ai)


def test_init_disabled_allows_no_provider():
    cfg = MagicMock()
    cfg.ai = AIConfig(enabled=False)
    NotificationSummarizer(cfg)


def test_summarize_happy_path(config_with_ai):
    summarizer = NotificationSummarizer(config_with_ai, DummyGPT())
    assert summarizer.summarize("Some long text") == "SUMMARIZED"


def test_summarize_empty_raises(config_with_ai):
    summarizer = NotificationSummarizer(config_with_ai, DummyGPT())
    with pytest.raises(ValueError):
        summarizer.summarize("  ")


def test_summarize_disabled_returns_input():
    cfg = MagicMock()
    cfg.ai = AIConfig(enabled=False)
    summarizer = NotificationSummarizer(cfg)
    assert summarizer.summarize("abc") == "abc"


def test_summarize_logs_and_returns_original_on_error(config_with_ai):
    summarizer = NotificationSummarizer(config_with_ai, ExplodingGPT())
    assert summarizer.summarize("content") == "content"
