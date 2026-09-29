import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize("custom_session", [False, True])
def test_entrypoint_exports_prepared_paths(tmp_path, custom_session):
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("MOODLE")
    }
    state = tmp_path / "state"
    logs = tmp_path / "nested" / "logs"
    session = (tmp_path / "custom" if custom_session else state) / "moodle_session.json"
    environment.update(MOODLE_STATE_DIR=str(state), MOODLE_LOG_DIR=str(logs))
    if custom_session:
        environment["MOODLE_SESSION_FILE"] = str(session)
    # Exercise the non-root entrypoint path even when pytest runs as root.
    binary_dir = tmp_path / "bin"
    binary_dir.mkdir()
    fake_id = binary_dir / "id"
    fake_id.write_text("#!/bin/sh\nprintf '1000\\n'\n")
    fake_id.chmod(0o755)
    environment["PATH"] = str(binary_dir) + os.pathsep + environment["PATH"]
    result = subprocess.run(
        [
            "bash",
            str(Path(__file__).parents[2] / "docker/entrypoint.sh"),
            sys.executable,
            "-c",
            "import json, os; print(json.dumps({k: os.getenv(k) for k in "
            "('MOODLE_STATE_DIR', 'MOODLE_SESSION_FILE', 'MOODLE_LOG_DIR')}))",
        ],
        env=environment,
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    assert json.loads(result.stdout) == {
        "MOODLE_STATE_DIR": str(state),
        "MOODLE_SESSION_FILE": str(session),
        "MOODLE_LOG_DIR": str(logs),
    }
    assert session.is_file()
    assert logs.is_dir()
