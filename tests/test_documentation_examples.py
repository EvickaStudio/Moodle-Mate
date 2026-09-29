import re
from pathlib import Path
from unittest.mock import Mock

from moodlemate.infrastructure.http.request_manager import request_manager

ROOT = Path(__file__).parents[1]


def test_documented_markdown_example_runs():
    document = (ROOT / "src/moodlemate/markdown/README.md").read_text()
    namespace = {}
    exec(re.search(r"```python\n(.*?)```", document, re.DOTALL)[1], namespace)
    assert namespace["markdown"] == "# Hello, World!"


def test_documented_provider_uses_its_own_session(monkeypatch):
    document = (ROOT / "docs/how-to/add-custom-provider.md").read_text()
    namespace = {}
    exec(re.search(r"```python\n(.*?)```", document, re.DOTALL)[1], namespace)
    provider = namespace["MyServiceProvider"]("dummy-key", "https://provider.invalid")
    assert provider.session is request_manager.get_session("provider_my_service")
    assert provider.session is not request_manager.get_session("moodle")
    response = Mock(status_code=200)
    post = Mock(return_value=response)
    monkeypatch.setattr(provider.session, "post", post)
    assert provider.send("Title", "Body", "Summary") is True
    post.assert_called_once_with(
        "https://provider.invalid/send",
        json={"title": "Title", "body": "Body", "summary": "Summary"},
        headers={"Authorization": "Bearer dummy-key"},
    )
    assert "Authorization" not in request_manager.get_session("moodle").headers
    response.status_code = 500
    assert provider.send("Title", "Body") is False
