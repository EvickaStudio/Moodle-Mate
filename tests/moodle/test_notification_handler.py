import time
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from moodlemate.moodle.errors import MoodleConnectionError
from moodlemate.moodle.notification_handler import MoodleNotificationHandler


def _build_handler(last_notification_id: int | None = 10) -> MoodleNotificationHandler:
    handler = MoodleNotificationHandler.__new__(MoodleNotificationHandler)
    handler.settings = SimpleNamespace(
        moodle=SimpleNamespace(initial_fetch_count=3),
    )
    handler.api = Mock()
    handler.state_manager = Mock(last_notification_id=last_notification_id)
    handler.last_notification_id = last_notification_id
    handler.moodle_user_id = 42
    handler.last_successful_connection = time.time()
    handler.session_timeout = 3600
    handler.max_reconnect_attempts = 3
    handler.reconnect_delay = 0
    return handler


def test_init_logs_in_and_loads_user_id():
    settings = SimpleNamespace(moodle=SimpleNamespace(initial_fetch_count=1))
    api = Mock()
    api.login.return_value = True
    api.get_user_id.return_value = 123
    state_manager = Mock(last_notification_id=55)

    handler = MoodleNotificationHandler(settings, api, state_manager)

    assert handler.moodle_user_id == 123
    assert handler.last_notification_id == 55
    api.login.assert_called_once()
    api.get_user_id.assert_called_once()


def test_fetch_latest_notification_returns_processed_notification():
    handler = _build_handler()
    handler._ensure_connection = Mock()
    handler.api.get_popup_notifications.return_value = {
        "notifications": [
            {
                "id": 99,
                "useridfrom": 7,
                "subject": "Update",
                "fullmessagehtml": "<p>body</p>",
            }
        ]
    }

    result = handler.fetch_latest_notification()

    assert result == {
        "id": 99,
        "useridfrom": 7,
        "subject": "Update",
        "fullmessagehtml": "<p>body</p>",
    }


def test_fetch_newest_notification_uses_initial_fetch_when_no_state():
    handler = _build_handler(last_notification_id=None)
    handler._handle_initial_fetch = Mock(return_value=[{"id": 1}])

    result = handler.fetch_newest_notification()

    assert result == [{"id": 1}]
    handler._handle_initial_fetch.assert_called_once()


def test_fetch_newest_notification_returns_none_when_latest_is_not_newer():
    handler = _build_handler(last_notification_id=20)
    handler.fetch_latest_notification = Mock(
        return_value={
            "id": 20,
            "useridfrom": 1,
            "subject": "Same",
            "fullmessagehtml": "x",
        }
    )

    assert handler.fetch_newest_notification() is None


def test_mark_notification_processed_updates_state_manager():
    handler = _build_handler(last_notification_id=2)

    handler.mark_notification_processed(11)

    assert handler.last_notification_id == 11
    handler.state_manager.set_last_notification_id.assert_called_once_with(11)


def test_handle_initial_fetch_processes_notifications_in_reverse_order():
    handler = _build_handler(last_notification_id=None)
    notifications = [
        {"id": 1, "useridfrom": 1, "subject": "A", "fullmessagehtml": "A"},
        {"id": 2, "useridfrom": 1, "subject": "B", "fullmessagehtml": "B"},
        {"id": 3, "useridfrom": 1, "subject": "C", "fullmessagehtml": "C"},
    ]
    handler.fetch_notifications = Mock(return_value=notifications)
    call_order: list[int] = []
    handler._handle_new_notification = Mock(
        side_effect=lambda *_args: call_order.append(_args[1])
    )  # type: ignore[assignment]

    result = handler._handle_initial_fetch()

    assert result == notifications
    assert call_order == [3, 2, 1]


def test_fetch_notifications_raises_after_retries(monkeypatch):
    handler = _build_handler()
    handler._fetch_notifications = Mock(side_effect=RuntimeError("boom"))
    monkeypatch.setattr(
        "moodlemate.moodle.notification_handler.time.sleep", lambda *_: None
    )

    with pytest.raises(MoodleConnectionError, match="Failed to fetch notifications"):
        handler.fetch_notifications(limit=5)


def test_user_id_from_accepts_list_payload():
    handler = _build_handler()
    handler._ensure_connection = Mock()
    handler.api.core_user_get_users_by_field.return_value = [
        {"id": "5", "fullname": "Alice", "profileimageurl": "https://img.local/u.png"}
    ]

    result = handler.user_id_from(5)

    assert result == {
        "id": 5,
        "fullname": "Alice",
        "profileimageurl": "https://img.local/u.png",
    }


def test_process_notification_returns_none_for_missing_fields():
    handler = _build_handler()

    assert handler._process_notification({"id": 1, "subject": "incomplete"}) is None
