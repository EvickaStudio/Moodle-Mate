import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from moodlemate.moodle import api as moodle_api_module
from moodlemate.moodle.api import MoodleAPI


@pytest.fixture
def api(monkeypatch, tmp_path) -> MoodleAPI:
    monkeypatch.setenv("MOODLE_SESSION_FILE", str(tmp_path / "moodle_session.json"))
    return MoodleAPI(
        url="https://moodle.example.edu",
        username="alice",
        password="password123",
        session_encryption_key="unit-test-secret",
    )


def test_login_success_sets_token_and_saves_state(api: MoodleAPI, monkeypatch):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"token": "abc123"}
    api.session = Mock()
    api.session.post.return_value = response
    api._save_session_state = Mock()
    monkeypatch.setattr(
        moodle_api_module.rate_limiter_manager,
        "is_allowed",
        lambda *_args, **_kwargs: True,
    )

    assert api.login() is True
    assert api.token == "abc123"
    api._save_session_state.assert_called_once()


def test_login_returns_false_when_api_returns_error(api: MoodleAPI, monkeypatch):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"error": "Invalid login"}
    api.session = Mock()
    api.session.post.return_value = response
    monkeypatch.setattr(
        moodle_api_module.rate_limiter_manager,
        "is_allowed",
        lambda *_args, **_kwargs: True,
    )

    assert api.login() is False
    assert api.token is None


def test_login_returns_false_on_request_exception(api: MoodleAPI, monkeypatch):
    response = Mock()
    response.raise_for_status.side_effect = moodle_api_module.RequestException(
        "network error"
    )
    api.session = Mock()
    api.session.post.return_value = response
    api._save_session_state = Mock()
    monkeypatch.setattr(
        moodle_api_module.rate_limiter_manager,
        "is_allowed",
        lambda *_args, **_kwargs: True,
    )

    assert api.login() is False
    assert api.token is None
    api._save_session_state.assert_not_called()


def test_login_raises_when_rate_limited(api: MoodleAPI, monkeypatch):
    monkeypatch.setattr(
        moodle_api_module.rate_limiter_manager,
        "is_allowed",
        lambda *_args, **_kwargs: False,
    )

    with pytest.raises(ValueError, match="Too many login attempts"):
        api.login()


def test_get_site_info_requires_token(api: MoodleAPI):
    api.token = None
    assert api.get_site_info() is None


def test_refresh_session_resets_session_and_reauthenticates(
    api: MoodleAPI, monkeypatch
):
    api.login = Mock(return_value=True)
    api._clear_session_state = Mock()
    reset_session = Mock()
    fresh_session = Mock()
    monkeypatch.setattr(
        moodle_api_module.request_manager, "reset_session", reset_session
    )
    monkeypatch.setattr(
        moodle_api_module.request_manager,
        "get_session",
        Mock(return_value=fresh_session),
    )

    assert api.refresh_session() is True
    reset_session.assert_called_once_with("moodle")
    api._clear_session_state.assert_called_once()
    assert api.session is fresh_session
    api.login.assert_called_once()


def test_post_returns_none_when_rate_limited(api: MoodleAPI, monkeypatch):
    api.token = "token"
    monkeypatch.setattr(
        moodle_api_module.rate_limiter_manager,
        "is_allowed",
        lambda *_args, **_kwargs: False,
    )

    assert api._post("message_popup_get_popup_notifications", user_id=1) is None


def test_post_returns_response_payload(api: MoodleAPI, monkeypatch):
    api.token = "token"
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"notifications": []}
    api.session = Mock()
    api.session.post.return_value = response
    api._save_session_state = Mock()
    monkeypatch.setattr(
        moodle_api_module.rate_limiter_manager,
        "is_allowed",
        lambda *_args, **_kwargs: True,
    )

    result = api._post("message_popup_get_popup_notifications", user_id=1, limit=5)

    assert result == {"notifications": []}
    api._save_session_state.assert_called_once()


def test_restore_session_state_loads_encrypted_payload(api: MoodleAPI):
    assert api._session_fernet is not None
    payload = {
        "token": "restored-token",
        "userid": 321,
    }
    encrypted = api._session_fernet.encrypt(json.dumps(payload).encode("utf-8")).decode(
        "utf-8"
    )
    session_file = Path(api.session_state_file)
    session_file.write_text(
        json.dumps({"version": 1, "ciphertext": encrypted}),
        encoding="utf-8",
    )
    api.token = None
    api.userid = None

    restored = api._restore_session_state()

    assert restored is True
    assert api.token == "restored-token"
    assert api.userid == 321


def test_clear_session_state_clears_memory_and_file(api: MoodleAPI, tmp_path):
    cache_file = tmp_path / "session.json"
    cache_file.write_text("{}", encoding="utf-8")
    api.session_state_file = str(cache_file)
    api.session = Mock()
    api.session.cookies = Mock()
    api.token = "token"
    api.userid = 111

    api._clear_session_state()

    assert api.token is None
    assert api.userid is None
    api.session.cookies.clear.assert_called_once()
    assert not cache_file.exists()


def test_cipher_not_created_without_secret(monkeypatch, tmp_path):
    monkeypatch.setenv("MOODLE_SESSION_FILE", str(tmp_path / "moodle_session.json"))
    monkeypatch.delenv("MOODLEMATE_SESSION_ENCRYPTION_KEY", raising=False)

    api = MoodleAPI(
        url="https://moodle.example.edu",
        username="alice",
        password="password123",
        session_encryption_key=None,
    )

    assert api._session_fernet is None
