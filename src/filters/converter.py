import os
import re
import subprocess

# Git Path
SCRIPT_PATH = os.path.join("assets", "convert.js")


def convert(html_content: str) -> str:
    """
    Converts HTML content to another format using a Node.js script (turndown).

    Args:
        html_content (str): The HTML content to be converted.

    Returns:
        str: The converted and cleaned content.

    Raises:
        FileNotFoundError: If the Node.js script is not found.
        RuntimeError: If the Node.js script returns a non-zero exit code.
    """
    if not os.path.exists(SCRIPT_PATH):
        raise FileNotFoundError(f"Script not found: {SCRIPT_PATH}")

    result = subprocess.run(
        ["node", SCRIPT_PATH],
        input=html_content,
        text=True,
        capture_output=True,
        encoding="utf-8",
    )

    if result.returncode != 0:
        raise RuntimeError(f"Error in conversion script: {result.stderr}")

    return clean_converted_text(result.stdout)


def clean_converted_text(text: str) -> str:
    """
    Cleans the converted text by applying regex replacements.

    Args:
        text (str): The text to be cleaned.

    Returns:
        str: The cleaned text.
    """
    reg = r"\[!\[.*\]\(.*\)\]\(.*\)"
    text = re.sub(reg, "", text)
    text = text.replace("* * *", "")
    return text
