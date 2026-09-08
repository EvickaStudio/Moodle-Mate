"""Build and test the dashboard in an isolated container with dummy Moodle I/O."""

import json
import os
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = """
from unittest.mock import Mock
from moodlemate.app import MoodleMateApp
from moodlemate.config import Settings
from moodlemate.core.state_manager import StateManager
from moodlemate.notifications.processor import NotificationProcessor

settings = Settings(_env_file=None,
    moodle={"url": "https://moodle.invalid", "username": "test", "password": "dummy"},
    ai={"enabled": False}, web={"auth_secret": "smoke-test-only"})
state = StateManager()
handler = Mock()
handler.fetch_newest_notification.return_value = None
MoodleMateApp(settings, NotificationProcessor(settings, [], state), handler, Mock(), state).run()
"""


def docker(*args):
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("MOODLE")
    }
    return subprocess.check_output(
        ["docker", *args], text=True, cwd=ROOT, env=environment
    ).strip()


def main():
    with tempfile.TemporaryDirectory(prefix="moodlemate-docker-") as directory:
        temporary = Path(directory)
        shutil.copy(ROOT / "docker-compose.yml", temporary / "compose.yml")
        (temporary / ".env").write_text("MOODLEMATE_WEB__PORT=19095\n")
        config = json.loads(
            docker(
                "compose",
                "--env-file",
                str(temporary / ".env"),
                "--project-directory",
                directory,
                "-f",
                str(temporary / "compose.yml"),
                "config",
                "--format",
                "json",
            )
        )
        service = config["services"]["moodlemate"]
        assert service["environment"]["MOODLEMATE_WEB__HOST"] == "0.0.0.0"
        assert service["ports"][0]["host_ip"] == "127.0.0.1"
        assert service["ports"][0]["target"] == 19095
        assert service["ports"][0]["published"] == "19095"

        tag = f"moodlemate-smoke:{temporary.name}"
        subprocess.run(["docker", "build", "-t", tag, "."], cwd=ROOT, check=True)
        container = None
        try:
            container = docker(
                "run",
                "--detach",
                "--publish",
                "127.0.0.1::9095",
                tag,
                "python",
                "-c",
                APP,
            )
            base_url = "http://" + docker("port", container, "9095/tcp")
            deadline = time.monotonic() + 45
            while True:
                try:
                    with urllib.request.urlopen(
                        base_url + "/healthz", timeout=2
                    ) as response:
                        assert json.load(response)["status"] == "ok"
                    break
                except (urllib.error.URLError, TimeoutError):
                    if time.monotonic() >= deadline:
                        raise
                    time.sleep(0.5)
            with urllib.request.urlopen(base_url + "/login", timeout=2) as response:
                assert response.status == 200
            try:
                urllib.request.urlopen(base_url + "/api/status", timeout=2)
            except urllib.error.HTTPError as error:
                assert error.code == 401
            else:
                raise AssertionError("Dashboard API must require authentication")
            print("Docker dashboard smoke test passed")
        finally:
            if container:
                print(docker("logs", container))
                docker("rm", "--force", container)
            docker("image", "rm", tag)


if __name__ == "__main__":
    main()
