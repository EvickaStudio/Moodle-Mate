import time
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from moodlemate.app import MoodleMateApp
from moodlemate.notifications.processor import ProcessingResult


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

    app._send_health_notification("subject", "message")

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
