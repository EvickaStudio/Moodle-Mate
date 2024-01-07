# To be implemented
# This file will contain different filters for Moodle messages
# as the Moodle notification that are fetched via the Moodle API
# are plain HTML and contain a lot of unwanted information such as
# information about the course, forum, etc.

import logging

from bs4 import BeautifulSoup

PARAGRAPHS_JOINER = "  "


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
        cleaned_text = soup.get_text().strip()

        # Filter out the last line
        # only if more than 4 lines
        cleaned_text = remove_last_line(cleaned_text)

        return cleaned_text
    except Exception as e:
        logging.exception("An unexpected error occurred during HTML parsing")
        raise e


def remove_whitespace(text: str) -> str:
    """
    Remove excess whitespace from the text.

    Args:
        text (str): The text to clean.

    Returns:
        str: The cleaned text.
    """
    temp = "\n".join(
        [line.rstrip() for line in text.splitlines() if line.strip()]
    )
    return "\n".join(
        [line for line in temp.splitlines() if not line.startswith("   ")]
    )


def remove_last_line(text: str) -> str:
    """
    Remove the last line from the text.

    Args:
        text (str): The text to clean.

    Returns:
        str: The text without the last line.
    """
    lines = text.splitlines()
    return "\n".join(lines[:-1]) if len(lines) > 1 else text


def extract_and_format_for_discord(html: str) -> str:
    """
    Extract relevant content from HTML and format it for Discord.

    Args:
        html (str): The HTML content to parse.

    Returns:
        str: The formatted text for Discord.
    """
    if not html:
        raise ValueError("HTML content is required")

    try:
        return _extract_content(html)
    except Exception as e:
        return f"An error occurred during HTML parsing: {e}"


def _extract_content(html):
    soup = BeautifulSoup(html, "html.parser")

    # Extract main content
    content = soup.find("td", class_="content")
    if not content:
        return "No main content found."

    # Handle links and bold text
    for tag in content.find_all(["a", "b"]):
        if tag.name == "a":
            tag.replace_with(f"[{tag.get_text().strip()}]({tag['href']})")
        elif tag.name == "b":
            tag.replace_with(f"**{tag.get_text().strip()}**")

    # Process paragraphs
    paragraphs = content.find_all("p")
    formatted_paragraphs = []
    for p in paragraphs:
        if text := PARAGRAPHS_JOINER.join(p.get_text().split()):
            formatted_paragraphs.append(text)

    # Extract and format images
    # images = [img["src"] for img in content.find_all("img")]
    return "\n".join(formatted_paragraphs)


# Example usage:
# html_content = "<html>...</html>"
# text = parse_html_to_text(html_content)
# print(text)
