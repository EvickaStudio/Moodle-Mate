import json
from unittest.mock import Mock

import pytest

from moodlemate.core.state_manager import StateManager


def test_loads_legacy_checkpoint_without_delivery_receipts(monkeypatch, tmp_path):
    monkeypatch.setattr(StateManager, "_instance", None)
    state_file = tmp_path / "state.json"
    state_file.write_text('{"last_notification_id": 42}')

    manager = StateManager(str(state_file))

    assert manager.last_notification_id == 42
    assert manager.get_delivered_providers(43) == set()


def test_state_save_uses_atomic_replace(monkeypatch, tmp_path):
    StateManager._instance = None
    state_file = tmp_path / "state.json"
    manager = StateManager(str(state_file))
    manager.set_last_notification_id(42)

    replacements: list[tuple[str, str]] = []
    original_replace = __import__("os").replace

    def track_replace(source: str, destination: str) -> None:
        replacements.append((source, destination))
        original_replace(source, destination)

    monkeypatch.setattr("moodlemate.core.state_manager.os.replace", track_replace)
    manager.save_state()

    assert replacements
    assert replacements[0][1] == str(state_file)
    assert json.loads(state_file.read_text()) == {"last_notification_id": 42}
    assert list(tmp_path.glob("*.tmp")) == []
    StateManager._instance = None


def test_initial_window_survives_restart_and_clears_on_checkpoint(
    monkeypatch, tmp_path
):
    monkeypatch.setattr(StateManager, "_instance", None)
    path = tmp_path / "state.json"
    state = StateManager(str(path))
    state.pin_initial_notification(1)
    state.pin_initial_notification(10)
    assert state.last_notification_id is None
    monkeypatch.setattr(StateManager, "_instance", None)
    restored = StateManager(str(path))
    assert restored.initial_notification_id == 1
    restored.set_last_notification_id(1)
    restored.save_state()
    assert json.loads(path.read_text()) == {"last_notification_id": 1}


def test_initial_window_uses_legacy_partial_delivery_receipts(monkeypatch, tmp_path):
    monkeypatch.setattr(StateManager, "_instance", None)
    path = tmp_path / "state.json"
    path.write_text(
        json.dumps(
            {
                "last_notification_id": None,
                "delivery_receipts": {"9": ["discord"], "10": ["discord"]},
            }
        )
    )
    state = StateManager(str(path))
    assert state.initial_notification_id == 9
    assert state.get_delivered_providers(9) == {"discord"}


def test_initial_window_must_be_saved_before_processing(monkeypatch, tmp_path):
    monkeypatch.setattr(StateManager, "_instance", None)
    path = tmp_path / "state.json"
    state = StateManager(str(path))
    with monkeypatch.context() as patch:
        patch.setattr(
            "moodlemate.core.state_manager.os.replace",
            Mock(side_effect=OSError("disk full")),
        )
        with pytest.raises(OSError, match="initial notification window"):
            state.pin_initial_notification(1)
    assert not path.exists()
    state.pin_initial_notification(2)
    assert json.loads(path.read_text())["initial_notification_id"] == 1
