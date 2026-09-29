import json
import logging
import traceback
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from urllib.parse import parse_qs

import pytest
from requests import Response
from requests.exceptions import ConnectionError

from moodlemate.moodle import api as moodle_api_module
from moodlemate.moodle.api import MoodleAPI
from moodlemate.moodle.errors import MoodleConnectionError
from moodlemate.moodle.notification_handler import MoodleNotificationHandler


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


def test_get_site_info_returns_none_for_moodle_error_payload(api: MoodleAPI):
    api.token = "token"
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "exception": "invalid_parameter_exception",
        "errorcode": "invalidtoken",
        "message": "Invalid token - token not found",
    }
    api.session = Mock()
    api.session.post.return_value = response

    assert api.get_site_info() is None


def test_get_user_id_returns_none_when_userid_missing(api: MoodleAPI):
    api.token = "token"
    api.get_site_info = Mock(return_value={"sitename": "Demo"})

    assert api.get_user_id() is None


def test_get_user_id_returns_int_userid(api: MoodleAPI):
    api.token = "token"
    api.get_site_info = Mock(return_value={"userid": 42})

    assert api.get_user_id() == 42


def test_get_user_id_coerces_string_userid_to_int(api: MoodleAPI):
    api.token = "token"
    api.get_site_info = Mock(return_value={"userid": "42"})

    assert api.get_user_id() == 42


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


def test_post_raises_when_rate_limited(api: MoodleAPI, monkeypatch):
    api.token = "token"
    monkeypatch.setattr(
        moodle_api_module.rate_limiter_manager,
        "is_allowed",
        lambda *_args, **_kwargs: False,
    )

    with pytest.raises(MoodleConnectionError, match="rate limit"):
        api._post("message_popup_get_popup_notifications", user_id=1)


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


@pytest.mark.parametrize(
    ("method", "args", "payload"),
    [
        ("get_site_info", (), {"userid": 42}),
        ("core_user_get_users_by_field", ("id", "42"), [{"id": 42}]),
        ("get_popup_notifications", (42,), {"notifications": []}),
    ],
)
@pytest.mark.parametrize("failure", [None, "http", "connection"])
def test_rest_tokens_stay_in_form_body_and_out_of_errors(
    api, monkeypatch, caplog, method, args, payload, failure
):
    api.token = "dummy-token-that-must-not-appear"
    monkeypatch.setattr(
        moodle_api_module.rate_limiter_manager, "is_allowed", lambda *_: True
    )
    prepared = []

    def send(request, **_kwargs):
        prepared.append(request)
        if failure == "connection":
            raise ConnectionError(
                f"Failed URL https://example.invalid/?wstoken={api.token}"
            )
        response = Response()
        response.request = request
        response.url = request.url
        response.status_code = 503 if failure else 200
        response._content = json.dumps(payload).encode()
        return response

    monkeypatch.setattr(api.session, "send", send)
    error_text = ""
    if failure and method == "get_popup_notifications":
        with pytest.raises(MoodleConnectionError) as error:
            getattr(api, method)(*args)
        error_text = "".join(traceback.format_exception(error.value))
    else:
        assert getattr(api, method)(*args) == (None if failure else payload)

    assert api.token not in caplog.text + error_text
    assert api.token not in prepared[0].url
    assert parse_qs(prepared[0].body)["wstoken"] == [api.token]
    assert prepared[0].method == "POST"


@pytest.mark.parametrize(
    ("method", "field"),
    [
        ("login", "error"),
        ("get_user_id", "error"),
        ("get_user_id", "userid"),
        ("get_user_id", "key"),
        ("get_popup_notifications", "errorcode"),
    ],
)
def test_moodle_response_errors_cannot_echo_credentials(
    api, monkeypatch, caplog, method, field
):
    secret = "dummy-secret-that-must-not-appear"
    api.token = secret
    payload = {secret: "value"} if field == "key" else {field: secret}
    api.session = Mock()
    api.session.post.return_value.json.return_value = payload
    monkeypatch.setattr(
        moodle_api_module.rate_limiter_manager, "is_allowed", lambda *_: True
    )

    if method == "get_popup_notifications":
        with pytest.raises(MoodleConnectionError) as error:
            api.get_popup_notifications(42)
        assert secret not in "".join(traceback.format_exception(error.value))
    else:
        assert not getattr(api, method)()
    assert secret not in caplog.text


@pytest.mark.parametrize(
    ("kind", "field"),
    [
        ("notification", "id"),
        ("notification", "useridfrom"),
        ("user", "id"),
        ("user", "fullname"),
    ],
)
def test_moodle_handler_diagnostics_do_not_echo_remote_credentials(
    api, monkeypatch, caplog, kind, field
):
    caplog.set_level(logging.DEBUG)
    api.token = "dummy-credential-from-response"
    api.login = Mock(return_value=True)
    api.get_user_id = Mock(return_value=42)
    api.session = Mock()
    monkeypatch.setattr(
        moodle_api_module.rate_limiter_manager, "is_allowed", lambda *_: True
    )
    handler = MoodleNotificationHandler(
        SimpleNamespace(), api, Mock(last_notification_id=0)
    )
    if kind == "notification":
        payload = {
            "id": 1,
            "useridfrom": 2,
            "subject": "Update",
            "fullmessagehtml": "Body",
        }
        payload[field] = api.token
        api.session.post.return_value.json.return_value = {"notifications": [payload]}
        assert handler._fetch_notifications(None) == []
    else:
        payload = {
            "id": 1,
            "fullname": "Alice",
            "profileimageurl": "https://example.invalid/avatar",
        }
        payload[field] = api.token
        api.session.post.return_value.json.return_value = [payload]
        result = handler.user_id_from(1)
        assert (result is not None) == (field == "fullname")
    assert api.token not in caplog.text


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
