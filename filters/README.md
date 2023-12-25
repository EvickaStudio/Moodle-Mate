# Moodle Message Filter Module

## Overview

`message_filter.py` is a Python module designed to process and filter messages retrieved from Moodle. It effectively parses HTML-formatted Moodle notifications, removing extraneous details (like course and forum information) and converts them into a format suitable for Discord, preserving the original structure of the content.

## Features

- **HTML Parsing**: Converts Moodle notifications, which are in HTML format, into plain text.
- **Content Filtering**: Eliminates unnecessary information, focusing on the core message.
- **Discord Formatting**: Transforms the text to be Discord-friendly, maintaining the original content structure.
- **Whitespace and Line Management**: Cleans excessive whitespace and manages line breaks for readability.

## Functions

### `parse_html_to_text(html: str) -> str`

Parses HTML content and extracts the essential text, handling empty content cases.

### `remove_whitespace(text: str) -> str`

Cleans up the text by removing extra spaces and aligning the formatting.

### `remove_last_line(text: str) -> str`

Eliminates the last line from the text, often containing irrelevant information.

### `extract_and_format_for_discord(html: str) -> str`

Processes HTML content specifically for Discord, formatting links, bold texts, and paragraphs.

## Usage

1. **Import the Module**: Include `message_filter.py` in your Python project.
2. **Parse HTML Content**: Use `parse_html_to_text` to convert Moodle HTML notifications into plain text.
3. **Format for Discord**: Apply `extract_and_format_for_discord` to make the text Discord-friendly.

### Example

```python
# html_content = "<html>...</html>"  # Replace with actual HTML content
# text = parse_html_to_text(html_content)
# print(text)
```

## Dependencies

- `BeautifulSoup` from `bs4`: Used for parsing HTML content.
- `logging`: For logging exceptions and errors during parsing.
- `re`: Regular expressions for text processing.

## Installation

Ensure you have the required dependencies:

```bash
pip install beautifulsoup4
```

## Notes

- The module is specifically tailored for Moodle notifications and may require adjustments for other HTML formats.
- Error handling is implemented to manage unexpected parsing issues.
