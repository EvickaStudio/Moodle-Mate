import logging
from typing import List
from unittest.mock import Mock

import pytest

from src.core.notification.base import NotificationProvider
from src.core.notification.processor import NotificationProcessor


class DummyProvider(NotificationProvider):
    """Test provider to capture sends."""

    def __init__(self):
        self.sent: List[tuple[str, str, str | None]] = []

    def send(self, subject: str, message: str, summary: str | None = None) -> bool:
        self.sent.append((subject, message, summary))
        return True


@pytest.fixture
def fake_config(tmp_path):
    """Minimal config-like object for processor tests."""
    cfg = Mock()
    # filters
    cfg.filters.ignore_subjects_containing = ["ignore-me"]
    # ai
    cfg.ai.enabled = False
    return cfg


@pytest.fixture
def provider():
    return DummyProvider()


@pytest.fixture
def processor(fake_config, provider):
    return NotificationProcessor(fake_config, [provider])


def test_happy_path_converts_and_sends(processor, provider):
    notification = {
        "subject": "Hello",
        "fullmessagehtml": "<p>Hi <strong>there</strong></p>",
    }
    processor.process(notification)
    assert provider.sent and provider.sent[0][0] == "Hello"
    # markdown conversion should remove tags
    assert "**there**" in provider.sent[0][1]


def test_ignored_by_subject_filter(processor, provider, caplog):
    caplog.set_level(logging.INFO)
    notification = {"subject": "Please IGNORE-ME now", "fullmessagehtml": "<p>x</p>"}
    processor.process(notification)
    assert provider.sent == []
    assert any("ignored by filter" in rec.message for rec in caplog.records)


def test_missing_subject_raises_and_is_logged(processor, provider, caplog):
    caplog.set_level(logging.ERROR)
    notification = {"fullmessagehtml": "<p>content</p>"}
    processor.process(notification)
    assert provider.sent == []
    assert any(
        "Failed to process notification" in rec.message for rec in caplog.records
    )


def test_missing_message_raises_and_is_logged(processor, provider, caplog):
    caplog.set_level(logging.ERROR)
    notification = {"subject": "No body"}
    processor.process(notification)
    assert provider.sent == []
    assert any(
        "Failed to process notification" in rec.message for rec in caplog.records
    )
