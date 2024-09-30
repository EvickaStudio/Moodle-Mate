import os
import subprocess


def convert(html_content: str) -> str:
    script_path = os.path.join("assets", "convert.js")
    result = subprocess.run(
        ["node", script_path],
        input=html_content,
        text=True,
        capture_output=True,
        encoding="utf-8",
    )

    if result.returncode != 0:
        print(f"Error: {result.stderr}")

    return result.stdout
