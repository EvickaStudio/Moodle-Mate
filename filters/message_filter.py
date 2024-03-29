# Copyright 2024 EvickaStudio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# To be impelemented
# This file will contain different filter for moodle messages
# as the moodle notification that are fetched via the moodle api
# are plain html and contain a lot of unwanted information such as
# information about the course, forum, etc.

import logging
import re

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
        return ""  # Return an empty string instead of None


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
    return "\n".join(text.splitlines()[:-1])


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
            text = " ".join(p.get_text().split())
            if text:
                formatted_paragraphs.append(text)

        formatted_text = "\n".join(formatted_paragraphs)

        # Extract and format images
        images = [img["src"] for img in content.find_all("img")]
        # if images:
        #     formatted_images = [f"![image]({img})" for img in images]
        #     formatted_text += "\n\n" + "\n".join(formatted_images)

        return formatted_text
    except Exception as e:
        return f"An error occurred during HTML parsing: {e}"


# Example usage:
# html_content = "<html>...</html>"
# text = parse_html_to_text(html_content)
# print(text)
