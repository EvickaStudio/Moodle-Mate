import html
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from moodlemate.core.security import InputValidator
from moodlemate.markdown import convert


def test_markdown_links_cannot_create_executable_attributes(tmp_path):
    browser = shutil.which("chromium") or shutil.which("google-chrome")
    if browser is None:
        pytest.skip("Chromium or Google Chrome is required for the DOM regression")
    template = (
        Path(__file__).parents[2] / "src/moodlemate/web/templates/index.html"
    ).read_text()
    functions = "\n".join(
        re.search(r"    function " + name + r"\([^\n]*\) \{[\s\S]*?\n    \}", template)[
            0
        ]
        for name in ("escapeHtml", "escapeAttribute", "renderInlineMarkdown")
    )
    raw = '<p>[Read](https://example.invalid/"onmouseove<b></b>r="globalThis.executed=true)</p>'
    sanitized = InputValidator.sanitize_notification_data({"fullmessagehtml": raw})
    values = [
        convert(sanitized["fullmessagehtml"]),
        '[AI](https://example.invalid/"onmouseover="globalThis.executed=true)',
        "[Encoded](https://example.invalid/&quot;onmouseover=&quot;globalThis.executed=true)",
        "[**Course**](https://example.invalid/?id=42&section=1) and `code`",
    ]
    fixture = tmp_path / "renderer.html"
    fixture.write_text(
        '<!doctype html><pre id="result"></pre><script>'
        + functions
        + "\nconst values = "
        + json.dumps(values).replace("<", "\\u003c")
        + """;
        const results = values.map(value => {
            const root = document.createElement('div');
            root.innerHTML = renderInlineMarkdown(value);
            document.body.append(root);
            const link = root.querySelector('a');
            link.dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));
            return {attributes: link.getAttributeNames(), href: link.getAttribute('href'),
                    text: link.textContent, bold: !!link.querySelector('strong'),
                    code: root.querySelector('code')?.textContent};
        });
        document.getElementById('result').textContent = JSON.stringify({results, executed: !!globalThis.executed});
        </script>"""
    )
    output = subprocess.run(
        [
            browser,
            "--headless",
            "--no-sandbox",
            "--disable-gpu",
            "--disable-background-networking",
            "--disable-component-update",
            "--host-resolver-rules=MAP * ~NOTFOUND",
            "--no-first-run",
            f"--user-data-dir={tmp_path / 'profile'}",
            "--dump-dom",
            fixture.as_uri(),
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    ).stdout
    result = json.loads(
        html.unescape(re.search(r'<pre id="result">(.*?)</pre>', output)[1])
    )
    assert not result["executed"]
    for link in result["results"]:
        assert set(link["attributes"]) == {"href", "target", "rel"}
    control = result["results"][-1]
    assert control["href"] == "https://example.invalid/?id=42&section=1"
    assert control["text"] == "Course"
    assert control["bold"] and control["code"] == "code"
