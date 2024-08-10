import subprocess

def convert(html_content: str) -> str:
    result = subprocess.run(
        ["node", "assets\\convert.js"],
        input=html_content,
        text=True,
        capture_output=True,
        encoding="utf-8"
    )

    return result.stdout
