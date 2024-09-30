import os
import subprocess


# Git Path
SCRIPT_PATH = os.path.join("assets", "convert.js")


def convert(html_content: str) -> str:
    """
    Converts HTML content to another format using a Node.js script (turndown).
    Args:
        html_content (str): The HTML content to be converted.
    Returns:
        str: The converted content.
    Raises:
        RuntimeError: If the Node.js script returns a non-zero exit code.
    """
    result = subprocess.run(
        ["node", SCRIPT_PATH],
        input=html_content,
        text=True,
        capture_output=True,
        encoding="utf-8",
    )

    if result.returncode != 0:
<<<<<<< HEAD
        print(f"Error: {result.stderr}")
=======
        raise RuntimeError(result.stderr)
>>>>>>> bd33e8684ba946aa1a388b58032d45ff080eb148

    return result.stdout
