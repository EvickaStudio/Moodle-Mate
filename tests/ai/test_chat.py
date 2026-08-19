from unittest.mock import MagicMock, Mock

import pytest

from moodlemate.ai.chat import GPT
from moodlemate.ai.errors import InvalidAPIKeyError


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
