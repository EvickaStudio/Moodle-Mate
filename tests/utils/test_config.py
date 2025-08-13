from pathlib import Path
from textwrap import dedent

import pytest

from src.core.config.loader import Config


def write_cfg(tmp_path: Path, content: str) -> Path:
    cfg = tmp_path / "config.ini"
    cfg.write_text(dedent(content))
    return cfg


def test_config_initialization(tmp_path: Path):
    path = write_cfg(
        tmp_path,
        """
        [moodle]
        url = https://example.com
        username = u
        password = p
        initial_fetch_count = 2
        """,
    )
    cfg = Config(str(path))
    assert cfg.moodle.url.endswith("example.com")


def test_ai_defaults_and_overrides(tmp_path: Path):
    path = write_cfg(
        tmp_path,
        """
        [moodle]
        url = x
        username = u
        password = p

        [ai]
        enabled = 0
        model = gpt-4o-mini
        temperature = 0.9
        max_tokens = 256
        system_prompt = Hello
        """,
    )
    cfg = Config(str(path))
    assert cfg.ai.enabled is False
    assert cfg.ai.model == "gpt-4o-mini"
    assert cfg.ai.temperature == 0.9
    assert cfg.ai.max_tokens == 256
    assert cfg.ai.system_prompt == "Hello"


def test_filters_lists_parsed(tmp_path: Path):
    path = write_cfg(
        tmp_path,
        """
        [moodle]
        url = x
        username = u
        password = p

        [filters]
        ignore_subjects_containing = spam, eggs ,  ham
        ignore_courses_by_id = 1,2, 3
        """,
    )
    cfg = Config(str(path))
    assert cfg.filters.ignore_subjects_containing == ["spam", "eggs", "ham"]
    assert cfg.filters.ignore_courses_by_id == [1, 2, 3]


def test_missing_config_file_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        Config(str(tmp_path / "missing.ini"))


def test_webhook_and_discord_sections(tmp_path: Path):
    path = write_cfg(
        tmp_path,
        """
        [moodle]
        url = x
        username = u
        password = p

        [discord]
        enabled = 1
        webhook_url = https://discord
        bot_name = Bot
        thumbnail_url = https://img

        [webhook_site]
        enabled = yes
        webhook_url = https://webhook.site/abc
        include_summary = 0
        """,
    )
    cfg = Config(str(path))
    assert cfg.discord.enabled is True
    assert cfg.discord.webhook_url.startswith("https://discord")
    assert cfg.webhook_site.enabled is True
    assert cfg.webhook_site.include_summary is False


def test_health_config_optional_ints(tmp_path: Path):
    path = write_cfg(
        tmp_path,
        """
        [moodle]
        url = x
        username = u
        password = p

        [health]
        enabled = true
        heartbeat_interval = 60
        failure_alert_threshold = 5
        target_provider = discord
        """,
    )
    cfg = Config(str(path))
    assert cfg.health.enabled is True
    assert cfg.health.heartbeat_interval == 60
    assert cfg.health.failure_alert_threshold == 5
    assert cfg.health.target_provider == "discord"
