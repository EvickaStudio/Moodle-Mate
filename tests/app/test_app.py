import json
import time
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from requests.exceptions import ConnectionError, JSONDecodeError

from moodlemate.app import MoodleMateApp
from moodlemate.core.state_manager import StateManager
from moodlemate.moodle.api import MoodleAPI
from moodlemate.moodle.notification_handler import MoodleNotificationHandler
from moodlemate.notifications.processor import NotificationProcessor, ProcessingResult


def _build_settings(
    *,
    web_enabled: bool = False,
    auth_secret: str | None = "secret",
    health_enabled: bool = False,
    failure_threshold: int | None = None,
    target_provider: str | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        web=SimpleNamespace(
            enabled=web_enabled,
            auth_secret=auth_secret,
            host="127.0.0.1",
            port=9095,
        ),
        notification=SimpleNamespace(fetch_interval=60, max_retries=5),
        health=SimpleNamespace(
            enabled=health_enabled,
            heartbeat_interval=None,
            failure_alert_threshold=failure_threshold,
            target_provider=target_provider,
            failure_alert_cooldown=3600,
            stale_after=None,
        ),
    )


def _build_app(settings: SimpleNamespace) -> MoodleMateApp:
    return MoodleMateApp(
        settings=settings,
        notification_processor=Mock(providers=[]),
        moodle_handler=Mock(),
        moodle_api=Mock(),
        state_manager=Mock(),
    )


def test_run_saves_state_on_keyboard_interrupt():
    settings = _build_settings()
    app = _build_app(settings)
    app._main_loop = Mock(side_effect=KeyboardInterrupt)

    app.run()

    app.state_manager.maybe_save_state.assert_called_once_with(force=True)


def test_request_shutdown_stops_polling_and_web_server():
    app = _build_app(_build_settings())
    app._web_server = Mock(should_exit=False)

    app._request_shutdown()

    assert app._shutdown_event.is_set()
    assert app._web_server.should_exit is True


def test_stop_web_ui_joins_server_thread():
    app = _build_app(_build_settings())
    app._web_server = Mock(should_exit=False, force_exit=False)
    app._web_server_thread = Mock()
    app._web_server_thread.is_alive.return_value = True

    app._stop_web_ui()

    assert app._web_server.should_exit is True
    app._web_server_thread.join.assert_any_call(timeout=3.0)
    assert app._web_server.force_exit is True
    app._web_server_thread.join.assert_any_call(timeout=1.0)


def test_stop_web_ui_handles_late_server_initialization():
    app = _build_app(_build_settings())
    app._web_server = None
    server_mock = Mock(should_exit=False, force_exit=False)

    def side_effect(*args, **kwargs):
        app._web_server = server_mock

    app._web_server_thread = Mock()
    app._web_server_thread.is_alive.return_value = True
    app._web_server_thread.join.side_effect = side_effect

    app._stop_web_ui()

    assert server_mock.should_exit is True
    assert server_mock.force_exit is True


def test_fetch_and_process_notifications_marks_processed_ids():
    settings = _build_settings()
    app = _build_app(settings)
    app.moodle_handler.fetch_newest_notification.return_value = [
        {"id": 101, "subject": "A", "fullmessagehtml": "<p>A</p>", "useridfrom": 1},
        {"id": 102, "subject": "B", "fullmessagehtml": "<p>B</p>", "useridfrom": 2},
    ]
    app.notification_processor.process.return_value = ProcessingResult(delivered=True)

    result = app._fetch_and_process_notifications()

    assert result is True
    assert app.notification_processor.process.call_count == 2
    app.moodle_handler.mark_notification_processed.assert_any_call(101)
    app.moodle_handler.mark_notification_processed.assert_any_call(102)


def test_failed_delivery_does_not_advance_checkpoint():
    settings = _build_settings()
    app = _build_app(settings)
    app.moodle_handler.fetch_newest_notification.return_value = [
        {"id": 101, "subject": "A", "fullmessagehtml": "<p>A</p>"}
    ]
    app.notification_processor.process.return_value = ProcessingResult(delivered=False)

    with pytest.raises(RuntimeError, match="not delivered"):
        app._fetch_and_process_notifications.__wrapped__(app)

    app.moodle_handler.mark_notification_processed.assert_not_called()


@pytest.mark.parametrize(
    "timestamp_key,url_key,author",
    [
        ("timecreated", "contexturl", {"fullname": "Teacher"}),
        ("created", "url", "Teacher"),
        ("time", "url", {"firstname": "Teacher"}),
    ],
)
def test_moodle_metadata_reaches_course_filter_and_history(
    timestamp_key, url_key, author, monkeypatch, tmp_path
):
    monkeypatch.setattr(StateManager, "_instance", None)
    state = StateManager(str(tmp_path / "state.json"))
    state.set_last_notification_id(100)
    settings = _build_settings()
    settings.filters = SimpleNamespace(
        ignore_subjects_containing=[], ignore_courses_by_id=[42]
    )
    metadata = {
        timestamp_key: "1700000000",
        url_key: "https://moodle.example.edu/mod/forum/view.php?id=1",
        "component": "mod_forum",
        "eventtype": "posts",
        "userfrom": author,
    }
    api = Mock()
    api.login.return_value = True
    api.get_user_id.return_value = 1
    api.get_popup_notifications.return_value = {
        "notifications": [
            {
                "id": 102,
                "useridfrom": 7,
                "subject": "Included",
                "fullmessagehtml": "<p>Body</p>",
                "courseid": "43",
                **metadata,
            },
            {
                "id": 101,
                "useridfrom": 7,
                "subject": "Ignored course",
                "fullmessagehtml": "<p>Body</p>",
                "courseid": "42",
                **metadata,
            },
        ]
    }
    provider = Mock(provider_name="test")
    provider.send.return_value = True
    processor = NotificationProcessor(settings, [provider], state)
    handler = MoodleNotificationHandler(settings, api, state)
    app = MoodleMateApp(settings, processor, handler, api, state)

    assert app._fetch_and_process_notifications() is True
    provider.send.assert_called_once()
    assert provider.send.call_args.args[0] == "Included"
    assert state.last_notification_id == 102
    entry = state.get_history()[0]
    assert entry["timestamp"] == 1700000000
    assert entry["context_url"] == metadata[url_key]
    assert entry["course"] == 43
    assert entry["component"] == "mod_forum"
    assert entry["event_type"] == "posts"
    assert entry["author"] == "Teacher"


@pytest.mark.parametrize("failure", [False, RuntimeError("provider unavailable")])
def test_partial_delivery_retries_only_pending_providers_after_restart(
    failure, monkeypatch, tmp_path
):
    monkeypatch.setattr(StateManager, "_instance", None)
    state_file = tmp_path / "state.json"
    state = StateManager(str(state_file))
    state.set_last_notification_id(100)
    settings = _build_settings()
    settings.filters = SimpleNamespace(
        ignore_subjects_containing=[], ignore_courses_by_id=[]
    )
    notification = {
        "id": 101,
        "useridfrom": 1,
        "subject": "Update",
        "fullmessagehtml": "<p>Body</p>",
    }
    api = Mock()
    api.login.return_value = True
    api.get_user_id.return_value = 42
    api.get_popup_notifications.return_value = {"notifications": [notification]}
    successful = Mock(provider_name="successful")
    successful.send.return_value = True
    pending = Mock(provider_name="pending")
    pending.send.side_effect = [failure, False]
    processor = NotificationProcessor(settings, [successful, pending], state)
    handler = MoodleNotificationHandler(settings, api, state)
    app = MoodleMateApp(settings, processor, handler, api, state)

    for _ in range(2):
        with pytest.raises(RuntimeError, match="not delivered"):
            app._fetch_and_process_notifications.__wrapped__(app)

    successful.send.assert_called_once()
    assert pending.send.call_count == 2
    assert handler.last_notification_id == state.last_notification_id == 100
    assert state.get_history() == []

    # Restart without a manual state save: each successful send must be durable.
    monkeypatch.setattr(StateManager, "_instance", None)
    restored_state = StateManager(str(state_file))
    successful = Mock(provider_name="successful")
    successful.send.return_value = True
    pending = Mock(provider_name="pending")
    pending.send.return_value = True
    processor = NotificationProcessor(settings, [successful, pending], restored_state)
    handler = MoodleNotificationHandler(settings, api, restored_state)
    restarted_app = MoodleMateApp(settings, processor, handler, api, restored_state)

    assert restarted_app._fetch_and_process_notifications() is True
    successful.send.assert_not_called()
    pending.send.assert_called_once()
    assert handler.last_notification_id == restored_state.last_notification_id == 101
    history = restored_state.get_history()
    assert len(history) == 1
    assert history[0]["providers"] == ["successful", "pending"]

    # Receipts belong to one notification; both providers get the next message.
    notification["id"] = 102
    assert restarted_app._fetch_and_process_notifications() is True
    successful.send.assert_called_once()
    assert pending.send.call_count == 2
    restored_state.maybe_save_state(force=True)
    assert json.loads(state_file.read_text()) == {"last_notification_id": 102}


def test_test_notification_reports_partial_delivery():
    app = _build_app(_build_settings())
    app.notification_processor.process.return_value = ProcessingResult(
        delivered=False, providers_sent=("successful",)
    )

    with pytest.raises(RuntimeError, match="all enabled providers"):
        app.send_test_notification()


@pytest.mark.parametrize(
    "body",
    [
        "<blockquote>" * 1500 + "Meaningful text" + "</blockquote>" * 1500,
        "&lt;blockquote&gt;" * 1500 + "Meaningful text" + "&lt;/blockquote&gt;" * 1500,
        "<blockquote>" * 1500 + "Meaningful text",
        "<em>" * 1500 + "Meaningful text" + "</em>" * 1500,
        "<b>x</b>" * 5001 + "Meaningful text",
    ],
    ids=["nested", "encoded", "unclosed", "inline", "wide"],
)
def test_complex_content_uses_fallback_and_preserves_delivery_retries(
    body, monkeypatch, tmp_path
):
    monkeypatch.setattr(StateManager, "_instance", None)
    state = StateManager(str(tmp_path / "state.json"))
    state.set_last_notification_id(100)
    settings = _build_settings()
    settings.filters = SimpleNamespace(
        ignore_subjects_containing=[], ignore_courses_by_id=[]
    )
    handler = Mock()
    handler.fetch_newest_notification.return_value = [
        {"id": 101, "subject": "Complex", "fullmessagehtml": body},
        {
            "id": 102,
            "subject": "Normal",
            "fullmessagehtml": "<p>Normal <b>body</b></p>",
        },
    ]
    handler.mark_notification_processed.side_effect = state.set_last_notification_id
    provider = Mock(provider_name="test")
    provider.send.side_effect = [False, True, True]
    processor = NotificationProcessor(settings, [provider], state)
    app = MoodleMateApp(settings, processor, handler, Mock(), state)

    with pytest.raises(RuntimeError, match="not delivered"):
        app._fetch_and_process_notifications.__wrapped__(app)
    assert state.last_notification_id == 100
    provider.send.assert_called_once()
    assert "Formatting simplified" in provider.send.call_args.args[1]
    assert "Meaningful text" in provider.send.call_args.args[1]

    assert app._fetch_and_process_notifications() is True
    assert state.last_notification_id == 102
    assert provider.send.call_count == 3
    assert "**body**" in provider.send.call_args.args[1]
    assert [item["id"] for item in state.get_history()] == [102, 101]


@pytest.mark.parametrize("failed_id", [101, 102, 103])
def test_initial_delivery_failure_remains_pending_after_restart(
    failed_id, monkeypatch, tmp_path
):
    monkeypatch.setattr(StateManager, "_instance", None)
    state_file = str(tmp_path / "state.json")
    state = StateManager(state_file)
    settings = _build_settings()
    settings.moodle = SimpleNamespace(initial_fetch_count=3)
    api = Mock()
    api.login.return_value = True
    api.get_user_id.return_value = 42
    api.get_popup_notifications.return_value = {
        "notifications": [
            {
                "id": identifier,
                "useridfrom": 1,
                "subject": "Update",
                "fullmessagehtml": "Body",
            }
            for identifier in (103, 102, 101)
        ]
    }
    handler = MoodleNotificationHandler(settings, api, state)
    processor = Mock()
    processor.process.side_effect = lambda notification: ProcessingResult(
        delivered=notification["id"] != failed_id
    )
    app = MoodleMateApp(settings, processor, handler, api, state)

    with pytest.raises(RuntimeError, match="not delivered"):
        app._fetch_and_process_notifications.__wrapped__(app)

    last_delivered = None if failed_id == 101 else failed_id - 1
    assert handler.last_notification_id == last_delivered
    assert state.last_notification_id == last_delivered
    state.maybe_save_state(force=True)

    monkeypatch.setattr(StateManager, "_instance", None)
    restored_state = StateManager(state_file)
    restored_handler = MoodleNotificationHandler(settings, api, restored_state)
    restarted_app = MoodleMateApp(
        settings, processor, restored_handler, api, restored_state
    )
    processor.process.side_effect = None
    processor.process.return_value = ProcessingResult(delivered=True)
    processor.process.reset_mock()

    assert restarted_app._fetch_and_process_notifications() is True
    assert [call.args[0]["id"] for call in processor.process.call_args_list] == list(
        range(failed_id, 104)
    )
    assert restored_handler.last_notification_id == 103
    assert restored_state.last_notification_id == 103

    processor.process.reset_mock()
    assert restarted_app._fetch_and_process_notifications() is True
    processor.process.assert_not_called()


@pytest.mark.parametrize("first_run", [False, True])
@pytest.mark.parametrize(
    "failure",
    [
        "transport",
        "invalid_token",
        "api_error",
        "invalid_json",
        "malformed_payload",
        "rate_limited",
        "missing_token",
    ],
)
def test_failed_moodle_poll_stays_unhealthy_until_valid_response(
    first_run, failure, monkeypatch, tmp_path
):
    monkeypatch.setenv("MOODLE_SESSION_FILE", str(tmp_path / "session.json"))
    monkeypatch.setattr(
        "moodlemate.moodle.notification_handler.time.sleep", lambda _: None
    )
    allowed = Mock(return_value=failure != "rate_limited")
    monkeypatch.setattr(
        "moodlemate.moodle.api.rate_limiter_manager.is_allowed", allowed
    )
    api = MoodleAPI("https://moodle.example.edu", "alice", "dummy-password")
    api.token = None if failure == "missing_token" else "dummy-token"
    api.login = Mock(return_value=True)
    api.get_user_id = Mock(return_value=42)
    api.session = Mock()
    response = api.session.post.return_value
    response.json.return_value = {"notifications": []}
    if failure == "transport":
        response.raise_for_status.side_effect = ConnectionError("simulated outage")
    elif failure in ("invalid_token", "api_error"):
        response.json.return_value = {
            "exception": "webservice_access_exception",
            "errorcode": "invalidtoken"
            if failure == "invalid_token"
            else "accessdenied",
        }
    elif failure == "invalid_json":
        response.json.side_effect = JSONDecodeError("Invalid JSON", "x", 0)
    elif failure == "malformed_payload":
        response.json.return_value = {"notifications": None}

    settings = _build_settings()
    settings.moodle = SimpleNamespace(initial_fetch_count=3)
    state = Mock(last_notification_id=None if first_run else 100)
    handler = MoodleNotificationHandler(settings, api, state)
    app = MoodleMateApp(settings, Mock(providers=[]), handler, api, state)
    previous_success = time.time() - 600
    app._last_successful_poll = previous_success
    app._outage_alerted = True
    app._send_health_notification = Mock()
    app._check_and_refresh_session = Mock()
    monkeypatch.setattr(
        app._shutdown_event, "wait", lambda _: app._shutdown_event.set()
    )

    app._main_loop()
    app._shutdown_event.clear()

    assert app._last_successful_poll == previous_success
    assert app._last_poll_error
    assert not app.get_health_status()[0]
    assert app._outage_alerted
    app._send_health_notification.assert_not_called()
    app.notification_processor.process.assert_not_called()
    state.set_last_notification_id.assert_not_called()
    if failure in ("invalid_token", "missing_token"):
        assert api.login.call_count > 1

    allowed.return_value = True
    api.token = "valid-token"
    response.raise_for_status.side_effect = None
    response.json.side_effect = None
    response.json.return_value = {"notifications": []}

    app._main_loop()
    app._shutdown_event.clear()

    assert app._last_successful_poll > previous_success
    assert app._last_poll_error is None
    assert app.get_health_status()[0]
    assert not app._outage_alerted
    app._send_health_notification.assert_called_once_with(
        "Moodle-Mate Recovered",
        "Moodle-Mate successfully connected to Moodle again.",
    )


def test_handle_error_triggers_failure_alert_at_threshold():
    settings = _build_settings(
        health_enabled=True,
        failure_threshold=2,
    )
    app = _build_app(settings)
    app._send_failure_alert = Mock()

    consecutive_errors, sleep_seconds = app._handle_error(1, RuntimeError("boom"))

    assert consecutive_errors == 2
    assert sleep_seconds == 60
    app._send_failure_alert.assert_called_once()


def test_send_health_notification_uses_target_provider():
    settings = _build_settings(
        health_enabled=True,
        target_provider="discord",
    )
    app = _build_app(settings)
    discord = Mock()
    discord.provider_name = "discord"
    discord.send.return_value = True
    app.notification_processor.providers = [discord]

    assert app._send_health_notification("subject", "message") is True

    discord.send.assert_called_once_with("subject", "message")


def test_check_and_refresh_session_calls_api_when_session_is_old(monkeypatch):
    settings = _build_settings()
    app = _build_app(settings)
    app.moodle_api.refresh_session.return_value = True

    monkeypatch.setattr(
        "moodlemate.app.request_manager.get_session_age_hours",
        lambda _scope: 25.0,
    )

    app._check_and_refresh_session(interval=24.0)

    app.moodle_api.refresh_session.assert_called_once()


def test_send_heartbeat_if_due_sends_notification():
    settings = _build_settings(health_enabled=True, target_provider="discord")
    settings.health.heartbeat_interval = 1
    app = _build_app(settings)
    app._send_health_notification = Mock()
    app._last_heartbeat_sent = time.time() - (2 * 3600)

    app._send_heartbeat_if_due()

    app._send_health_notification.assert_called_once()


@pytest.mark.parametrize("failure", [False, RuntimeError("provider unavailable")])
def test_health_delivery_failure_keeps_alerts_pending(failure, monkeypatch):
    monkeypatch.setattr("moodlemate.app.time.time", lambda: 10_000.0)
    settings = _build_settings(
        health_enabled=True, target_provider="discord", failure_threshold=1
    )
    settings.health.heartbeat_interval = 1
    app = _build_app(settings)
    provider = Mock(provider_name="discord")
    provider.send.side_effect = [failure, True, failure, True, failure, True]
    app.notification_processor.providers = [provider]

    app._send_heartbeat_if_due()
    assert app._last_heartbeat_sent == 0
    assert "healthy" not in provider.send.call_args.args[1]
    app._send_heartbeat_if_due()
    assert app._last_heartbeat_sent == 10_000
    app._send_heartbeat_if_due()
    assert provider.send.call_count == 2

    app._handle_error(0, RuntimeError("Moodle unavailable"))
    assert app._last_failure_alert_sent == 0
    assert not app._outage_alerted
    app._handle_error(1, RuntimeError("Moodle unavailable"))
    assert app._last_failure_alert_sent == 10_000
    assert app._outage_alerted
    app._handle_error(2, RuntimeError("Moodle unavailable"))
    assert provider.send.call_count == 4

    app._record_poll_success()
    assert app._outage_alerted
    app._record_poll_success()
    assert not app._outage_alerted
    assert app._last_failure_alert_sent == 0
    assert provider.send.call_count == 6


def test_missing_health_provider_does_not_acknowledge_delivery():
    settings = _build_settings(
        health_enabled=True, target_provider="missing", failure_threshold=1
    )
    app = _build_app(settings)
    assert app._send_health_notification("Subject", "Body") is False
    app._handle_error(0, RuntimeError("Moodle unavailable"))
    assert app._last_failure_alert_sent == 0
    assert not app._outage_alerted
