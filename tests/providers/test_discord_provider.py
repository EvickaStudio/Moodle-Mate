from unittest.mock import MagicMock

import pytest

from src.providers.notification.discord.provider import DiscordProvider


@pytest.fixture
def provider():
    return DiscordProvider(
        webhook_url="https://discord.test/webhook",
        bot_name="Bot",
        thumbnail_url="https://example.com/img.png",
    )


def test_create_embed_has_summary(provider):
    embed = provider.create_notification_embed("Subject", "Body", summary="Sum")
    data = embed.to_dict()
    assert data["title"] == "Subject"
    assert data["description"] == "Body"
    assert any(f["name"] == "Summary" for f in data["fields"])  # type: ignore[index]


def test_send_success(provider, monkeypatch):
    mock_session = MagicMock()
    mock_response = MagicMock(status_code=204, text="")
    mock_session.post.return_value = mock_response
    provider.session = mock_session  # inject mocked session

    ok = provider.send("S", "M", "T")
    assert ok is True
    mock_session.post.assert_called_once()


def test_send_failure_logs_and_returns_false(provider, monkeypatch):
    mock_session = MagicMock()
    mock_response = MagicMock(status_code=400, text="bad")
    mock_session.post.return_value = mock_response
    provider.session = mock_session

    ok = provider.send("S", "M")
    assert ok is False
