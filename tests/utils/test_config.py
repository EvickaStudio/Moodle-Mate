
from src.config import Settings


def _set_required_env(monkeypatch) -> None:
    monkeypatch.setenv("MOODLEMATE_MOODLE__URL", "https://example.com")
    monkeypatch.setenv("MOODLEMATE_MOODLE__USERNAME", "user")
    monkeypatch.setenv("MOODLEMATE_MOODLE__PASSWORD", "pass")


def test_settings_loads_required_moodle(monkeypatch):
    _set_required_env(monkeypatch)
    settings = Settings()
    assert settings.moodle.url == "https://example.com"
    assert settings.moodle.username == "user"
    assert settings.moodle.password == "pass"


def test_settings_defaults_are_applied(monkeypatch):
    _set_required_env(monkeypatch)
    settings = Settings()
    assert settings.ai.enabled is True
    assert settings.notification.fetch_interval == 60
    assert settings.notification.max_retries == 5
    assert settings.filters.ignore_subjects_containing == []


def test_settings_env_overrides(monkeypatch):
    _set_required_env(monkeypatch)
    monkeypatch.setenv("MOODLEMATE_AI__ENABLED", "0")
    monkeypatch.setenv("MOODLEMATE_AI__MODEL", "gpt-4o-mini")
    monkeypatch.setenv("MOODLEMATE_AI__TEMPERATURE", "0.9")
    monkeypatch.setenv("MOODLEMATE_AI__MAX_TOKENS", "256")
    monkeypatch.setenv("MOODLEMATE_AI__SYSTEM_PROMPT", "Hello")
    settings = Settings()

    assert settings.ai.enabled is False
    assert settings.ai.model == "gpt-4o-mini"
    assert settings.ai.temperature == 0.9
    assert settings.ai.max_tokens == 256
    assert settings.ai.system_prompt == "Hello"


def test_health_config_optional_ints(monkeypatch):
    _set_required_env(monkeypatch)
    monkeypatch.setenv("MOODLEMATE_HEALTH__ENABLED", "true")
    monkeypatch.setenv("MOODLEMATE_HEALTH__HEARTBEAT_INTERVAL", "60")
    monkeypatch.setenv("MOODLEMATE_HEALTH__FAILURE_ALERT_THRESHOLD", "5")
    monkeypatch.setenv("MOODLEMATE_HEALTH__TARGET_PROVIDER", "discord")

    settings = Settings()
    assert settings.health.enabled is True
    assert settings.health.heartbeat_interval == 60
    assert settings.health.failure_alert_threshold == 5
    assert settings.health.target_provider == "discord"
