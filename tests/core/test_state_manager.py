import json

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
