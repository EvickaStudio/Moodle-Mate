import argparse
import runpy
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import moodlemate.main as main_module


@pytest.fixture
def fake_settings() -> SimpleNamespace:
    return SimpleNamespace(
        moodle=SimpleNamespace(
            url="https://moodle.example.edu",
            username="alice",
            password="supersecret",
        ),
        ai=SimpleNamespace(
            enabled=False,
            api_key="",
            endpoint=None,
            model="gpt-5-nano",
            system_prompt="summary",
            temperature=0.7,
            max_tokens=150,
        ),
        notification=SimpleNamespace(
            connect_timeout=10.0,
            read_timeout=30.0,
            retry_total=3,
            retry_backoff_factor=1.0,
        ),
        session_encryption_key="enc-key",
    )


def test_main_happy_path_initializes_and_runs(monkeypatch, fake_settings):
    args = argparse.Namespace(test_notification=False)
    monkeypatch.setattr(argparse.ArgumentParser, "parse_args", lambda _self: args)
    monkeypatch.setattr(main_module, "setup_logging", Mock())
    monkeypatch.setattr(main_module, "print_logo", Mock())
    monkeypatch.setattr(main_module, "Settings", Mock(return_value=fake_settings))
    init_run = Mock()
    monkeypatch.setattr(main_module, "initialize_and_run_app", init_run)

    main_module.main()

    init_run.assert_called_once_with(fake_settings, args)


def test_main_exits_when_settings_fail(monkeypatch):
    args = argparse.Namespace(test_notification=False)
    monkeypatch.setattr(argparse.ArgumentParser, "parse_args", lambda _self: args)
    monkeypatch.setattr(main_module, "setup_logging", Mock())
    monkeypatch.setattr(main_module, "print_logo", Mock())
    monkeypatch.setattr(main_module, "Settings", Mock(side_effect=RuntimeError("bad")))

    with pytest.raises(SystemExit) as exc:
        main_module.main()

    assert exc.value.code == 1


def test_main_exits_on_startup_failure(monkeypatch, fake_settings):
    args = argparse.Namespace(test_notification=False)
    monkeypatch.setattr(argparse.ArgumentParser, "parse_args", lambda _self: args)
    monkeypatch.setattr(main_module, "setup_logging", Mock())
    monkeypatch.setattr(main_module, "print_logo", Mock())
    monkeypatch.setattr(main_module, "Settings", Mock(return_value=fake_settings))
    monkeypatch.setattr(
        main_module,
        "initialize_and_run_app",
        Mock(side_effect=RuntimeError("startup failed")),
    )

    with pytest.raises(SystemExit) as exc:
        main_module.main()

    assert exc.value.code == 1


def test_initialize_and_run_app_sends_test_notification(monkeypatch, fake_settings):
    args = argparse.Namespace(test_notification=True)
    app = Mock()
    monkeypatch.setattr(main_module.request_manager, "configure", Mock())
    monkeypatch.setattr(main_module, "StateManager", Mock(return_value=Mock()))
    monkeypatch.setattr(main_module, "MoodleAPI", Mock(return_value=Mock()))
    monkeypatch.setattr(main_module, "initialize_providers", Mock(return_value=[]))
    monkeypatch.setattr(main_module, "NotificationProcessor", Mock(return_value=Mock()))
    monkeypatch.setattr(
        main_module,
        "MoodleNotificationHandler",
        Mock(return_value=Mock()),
    )
    monkeypatch.setattr(main_module, "MoodleMateApp", Mock(return_value=app))

    main_module.initialize_and_run_app(fake_settings, args)

    app.send_test_notification.assert_called_once()
    app.run.assert_not_called()


def test_initialize_and_run_app_runs_with_ai_enabled(monkeypatch, fake_settings):
    args = argparse.Namespace(test_notification=False)
    fake_settings.ai.enabled = True
    fake_settings.ai.api_key = "sk-" + ("a" * 48)
    fake_settings.ai.endpoint = "https://api.openai.example/v1"
    state_manager = Mock()
    moodle_api = Mock()
    app = Mock()
    gpt_instance = Mock()

    monkeypatch.setattr(main_module.request_manager, "configure", Mock())
    monkeypatch.setattr(main_module, "StateManager", Mock(return_value=state_manager))
    monkeypatch.setattr(main_module, "MoodleAPI", Mock(return_value=moodle_api))
    monkeypatch.setattr(main_module, "GPT", Mock(return_value=gpt_instance))
    summarizer = Mock()
    monkeypatch.setattr(
        main_module,
        "NotificationSummarizer",
        Mock(return_value=summarizer),
    )
    monkeypatch.setattr(main_module, "initialize_providers", Mock(return_value=[]))
    monkeypatch.setattr(main_module, "NotificationProcessor", Mock(return_value=Mock()))
    monkeypatch.setattr(
        main_module,
        "MoodleNotificationHandler",
        Mock(return_value=Mock()),
    )
    monkeypatch.setattr(main_module, "MoodleMateApp", Mock(return_value=app))

    main_module.initialize_and_run_app(fake_settings, args)

    assert gpt_instance.api_key == fake_settings.ai.api_key
    assert gpt_instance.endpoint == fake_settings.ai.endpoint
    app.run.assert_called_once()
    app.send_test_notification.assert_not_called()


def test_dunder_main_invokes_package_main(monkeypatch):
    called = {"value": False}

    def fake_main():
        called["value"] = True

    monkeypatch.setattr("moodlemate.main.main", fake_main)

    runpy.run_module("moodlemate.__main__", run_name="__main__")

    assert called["value"] is True
