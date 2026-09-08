import json
from unittest.mock import MagicMock, Mock

import httpx
import openai
import pytest

from moodlemate.ai.chat import GPT
from moodlemate.ai.errors import InvalidAPIKeyError
from moodlemate.config import Settings
from moodlemate.notifications.summarizer import (
    NotificationSummarizer,
    initialize_summarizer,
)


@pytest.fixture(autouse=True)
def reset_gpt_singleton():
    GPT._instance = None
    yield
    GPT._instance = None


def test_gpt_singleton_and_init():
    gpt1 = GPT()
    gpt2 = GPT()
    assert gpt1 is gpt2
    assert gpt1.api_key is None
    assert gpt1.endpoint is None


def test_gpt_api_key_validation():
    gpt = GPT()
    with pytest.raises(InvalidAPIKeyError, match="API key cannot be empty"):
        gpt.api_key = ""

    with pytest.raises(InvalidAPIKeyError, match="Invalid API key format"):
        gpt.api_key = "invalid-key"

    valid_key = "sk-" + "a" * 48
    gpt.api_key = valid_key
    assert gpt.api_key == valid_key


def test_gpt_endpoint_and_custom_key():
    gpt = GPT()
    gpt.endpoint = "https://openrouter.ai/api/v1"
    assert gpt.is_openrouter is True

    # Custom endpoint allows non sk- format key
    gpt.api_key = "custom-key"
    assert gpt.api_key == "custom-key"


def test_gpt_client_instantiation(monkeypatch):
    mock_openai = Mock()
    monkeypatch.setattr("openai.OpenAI", mock_openai)

    gpt = GPT()
    gpt.api_key = "sk-" + "a" * 48
    gpt.endpoint = "https://api.openai.com/v1"

    client = gpt._get_client()
    mock_openai.assert_called_once_with(
        api_key=gpt.api_key,
        base_url=gpt.endpoint,
    )
    assert client == mock_openai.return_value

    # Second call reuses cached client instance
    client2 = gpt._get_client()
    assert client2 is client
    assert mock_openai.call_count == 1

    # Changing endpoint invalidates cache
    gpt.endpoint = "https://other.ai/v1"
    gpt._get_client()
    assert mock_openai.call_count == 2


def test_chat_completion_success(monkeypatch):
    mock_client = Mock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Summary result"
    mock_client.chat.completions.create.return_value = mock_response

    monkeypatch.setattr("openai.OpenAI", Mock(return_value=mock_client))

    gpt = GPT()
    gpt.api_key = "sk-" + "a" * 48

    result = gpt.chat_completion(
        model="gpt-4o-mini",
        system_message="You summarize",
        user_message="Hello world",
        temperature=0.2,
        max_tokens=50,
    )

    assert result == "Summary result"
    mock_client.chat.completions.create.assert_called_once()


@pytest.mark.parametrize(
    "model", ["gpt-5-nano", "gpt-5-nano-2025-08-07", "gpt-5-mini", "gpt-5"]
)
def test_gpt5_requests_use_supported_parameters(model, monkeypatch):
    client = Mock()
    client.chat.completions.create.return_value = Mock(
        choices=[Mock(message=Mock(content="Summary"))]
    )
    gpt = GPT()
    monkeypatch.setattr(gpt, "_get_client", lambda: client)
    monkeypatch.setattr(gpt, "count_tokens", lambda *args, **kwargs: 1)

    assert gpt.chat_completion(model, "Summarize", "Body", max_tokens=2048) == "Summary"
    arguments = client.chat.completions.create.call_args.kwargs
    assert "temperature" not in arguments
    assert "max_tokens" not in arguments
    assert arguments["max_completion_tokens"] == 2048
    assert arguments["reasoning_effort"] == "minimal"


@pytest.mark.parametrize("model", ["gpt-4o-mini", "local-model", "gpt-5-chat-latest"])
def test_other_model_requests_preserve_sampling_parameters(model, monkeypatch):
    client = Mock()
    client.chat.completions.create.return_value = Mock(
        choices=[Mock(message=Mock(content="Summary"))]
    )
    gpt = GPT()
    monkeypatch.setattr(gpt, "_get_client", lambda: client)
    monkeypatch.setattr(gpt, "count_tokens", lambda *args, **kwargs: 1)

    assert (
        gpt.chat_completion(model, "Summarize", "Body", temperature=0.3, max_tokens=150)
        == "Summary"
    )
    arguments = client.chat.completions.create.call_args.kwargs
    assert arguments["temperature"] == 0.3
    assert arguments["max_tokens"] == 150
    assert "reasoning_effort" not in arguments


def test_empty_completion_preserves_original_notification(monkeypatch):
    client = Mock()
    client.chat.completions.create.return_value = Mock(
        choices=[Mock(message=Mock(content=""))]
    )
    gpt = GPT()
    monkeypatch.setattr(gpt, "_get_client", lambda: client)
    settings = Settings(
        _env_file=None,
        moodle={
            "url": "https://moodle.example.edu",
            "username": "test",
            "password": "dummy",
        },
    )
    summarizer = NotificationSummarizer(settings, gpt)

    assert summarizer.summarize("Original notification") == "Original notification"
    assert (
        client.chat.completions.create.call_args.kwargs["max_completion_tokens"] == 2048
    )


@pytest.mark.parametrize(
    "endpoint,key",
    [
        ("http://127.0.0.1:11434/v1", "local-key"),
        ("http://127.0.0.1:11434/v1", ""),
        (None, "sk-" + "a" * 48),
    ],
)
def test_summarizer_initialization_sends_configured_authentication(
    endpoint, key, monkeypatch
):
    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "id": "test",
                "object": "chat.completion",
                "created": 1,
                "model": "test-model",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "Summary"},
                        "finish_reason": "stop",
                    }
                ],
            },
        )

    original_client = openai.OpenAI
    with httpx.Client(transport=httpx.MockTransport(respond)) as http_client:
        monkeypatch.setattr(
            openai,
            "OpenAI",
            lambda **kwargs: original_client(http_client=http_client, **kwargs),
        )
        settings = Settings(
            _env_file=None,
            moodle={
                "url": "https://moodle.example.edu",
                "username": "test",
                "password": "dummy",
            },
            ai={
                "enabled": True,
                "api_key": key,
                "endpoint": endpoint,
                "model": "test-model",
            },
        )
        summarizer = initialize_summarizer(settings)
        assert summarizer.summarize("Body") == "Summary"

    assert len(requests) == 1
    assert (
        str(requests[0].url)
        == (endpoint or "https://api.openai.com/v1") + "/chat/completions"
    )
    assert requests[0].headers.get("authorization") == (
        f"Bearer {key}" if key else None
    )
    assert json.loads(requests[0].content)["model"] == "test-model"


@pytest.mark.parametrize("endpoint", [None, "https://api.openai.com/v1/"])
def test_openai_endpoint_still_requires_a_key(endpoint):
    gpt = GPT()
    gpt.endpoint = endpoint
    with pytest.raises(InvalidAPIKeyError):
        gpt.api_key = ""


def test_initializer_clears_previous_custom_endpoint():
    GPT().endpoint = "http://127.0.0.1:11434/v1"
    settings = Settings(
        _env_file=None,
        moodle={
            "url": "https://moodle.example.edu",
            "username": "test",
            "password": "dummy",
        },
        ai={"api_key": "not-an-openai-key"},
    )
    with pytest.raises(InvalidAPIKeyError):
        initialize_summarizer(settings)
