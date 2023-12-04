# To be impelemented
# This file will contain different filter for moodle messages
# as the moodle notification that are fetched via the moodle api
# are plain html and contain a lot of unwanted information such as
# information about the course, forum, etc.

import logging

from bs4 import BeautifulSoup


def parse_html_to_text(html: str) -> str:
    """
    Parse HTML content and extract the text.

    Args:
        html (str): The HTML content to parse.

    Returns:
        str: The extracted text from the HTML.

    Raises:
        ValueError: If the HTML content is empty.
    """
    if not html:
        raise ValueError("HTML content is required")

    try:
        soup = BeautifulSoup(html, "html.parser")

        # Extract text and remove unnecessary whitespace
        cleaned_text = remove_whitespace(soup.get_text())

        # Filter out the last line
        cleaned_text = remove_last_line(cleaned_text)

        return cleaned_text
    except Exception as e:
        logging.exception("An unexpected error occurred during HTML parsing")
        return None


def remove_whitespace(text: str) -> str:
    """
    Remove excess whitespace from the text.

    Args:
        text (str): The text to clean.

    Returns:
        str: The cleaned text.
    """
    temp = "\n".join([line.rstrip() for line in text.splitlines() if line.strip()])
    return "\n".join([line for line in temp.splitlines() if not line.startswith("   ")])


def remove_last_line(text: str) -> str:
    """
    Remove the last line from the text.

    Args:
        text (str): The text to clean.

    Returns:
        str: The text without the last line.
    """
    return "\n".join(text.splitlines()[:-1])


# Example usage:
# html_content = "<html>...</html>"
# text = parse_html_to_text(html_content)
# print(text)
