import logging
from contextlib import suppress
from logging.handlers import RotatingFileHandler

import pytest

from moodlemate.infrastructure.logging.setup import ColoredFormatter, setup_logging


def _reset_root_logger() -> None:
    root = logging.getLogger()
    for handler in list(root.handlers):
        root.removeHandler(handler)
        with suppress(Exception):
            handler.close()


@pytest.mark.parametrize("custom_directory", [False, True])
def test_setup_logging_creates_handlers_and_log_dir(
    monkeypatch, tmp_path, custom_directory
):
    monkeypatch.chdir(tmp_path)
    log_dir = tmp_path / "logs"
    if custom_directory:
        log_dir = tmp_path / "custom" / "nested" / "logs"
        monkeypatch.setenv("MOODLE_LOG_DIR", str(log_dir))
    else:
        monkeypatch.delenv("MOODLE_LOG_DIR", raising=False)
    _reset_root_logger()

    setup_logging("DEBUG")

    root = logging.getLogger()
    assert (log_dir / "moodlemate.log").exists()
    assert any(isinstance(h, RotatingFileHandler) for h in root.handlers)
    assert any(isinstance(h, logging.StreamHandler) for h in root.handlers)
    assert logging.getLogger("urllib3").level == logging.WARNING
    assert logging.getLogger("requests").level == logging.WARNING

    _reset_root_logger()


def test_colored_formatter_applies_level_color_and_restores_levelname():
    formatter = ColoredFormatter("%(levelname)s %(name)s %(message)s")
    record = logging.LogRecord(
        name="moodlemate.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="hello",
        args=(),
        exc_info=None,
    )

    rendered = formatter.format(record)

    assert "\033[32m" in rendered
    assert "\033[35m" in rendered
    assert "hello" in rendered
    assert record.levelname == "INFO"
