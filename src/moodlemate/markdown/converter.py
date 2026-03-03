import logging
import re

from .turndown import MarkdownConverter

TURNDOWN = MarkdownConverter({"headingStyle": "atx", "codeBlockStyle": "fenced"})

logger = logging.getLogger(__name__)


def convert(html_content: str) -> str:
    """
    Converts HTML content to Markdown using TurndownService.

    Args:
        html_content (str): The HTML content to be converted.

    Returns:
        str: The converted and cleaned content.
    """
    # logger.info(f"Original HTML content:\n{html_content}")
    return apply_custom_rules(TURNDOWN.to_markdown(html_content))


# When turndown markdown conversion is not working as expected and malformes lines etc.
# mdformat can be used to format the markdown to comply with commonmark spec. (currently not used)
# def format_markdown(text: str) -> str:
#     """
#     Formats Markdown content with mdformat.
#     """
#     import mdformat
#     return mdformat.text(text).strip()


def apply_custom_rules(text: str) -> str:
    """
    Applies a custom set of rules to the already converted markdown text.
    Makes the output Discord-embed safe.

    Args:
        text (str): The Markdown text to be cleaned.

    Returns:
        str: The cleaned markdown text.
    """

    # Remove navigation breadcrumbs
    text = re.sub(r"\[.*?\]\(.*?\)\s*»\s*", "", text)

    # Remove all image patterns
    patterns = [
        r"!\[.*?\]\(.*?\)",  # Standard markdown images
        r"!\[.*?%.*?\]",  # Images with percent encoding
        r"\[!\[.*?\]\(.*?\)\]\(.*?\)",  # Nested images
        r"!\[.*?\]",  # Incomplete image tags
        r"\[.*?\]\(.*?\.(?:png|jpg|jpeg|gif|bmp|webp).*?\)",  # Links to images
        r"\[\]\(.*?\)",  # Empty links
    ]

    for pattern in patterns:
        text = re.sub(pattern, "", text)

    # Clean up broken/truncated links
    text = re.sub(r"\[.*?\]\([^)]*$", "", text)

    # Remove empty links and their brackets
    text = re.sub(r"\s*\[[\s\S]*?\]\s*\(\s*#\s*\)", "", text)

    # Remove forum management links at the bottom
    text = re.sub(r"\[Forum abbestellen\].*$", "", text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(
        r"\[Diskussion im Forum zeigen\].*$", "", text, flags=re.MULTILINE | re.DOTALL
    )

    # Clean up multiple newlines, spaces and underscores
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"_{2,}", "___", text)

    # Remove any remaining empty lines at the start/end
    text = text.strip()

    # Remove any double spaces after cleaning
    text = re.sub(r" +", " ", text)

    # Ensure there's no more than one blank line between paragraphs
    text = re.sub(r"\n\s*\n", "\n\n", text)

    # Fix broken bold markers split across lines (seen in some Moodle messages).
    text = re.sub(r"\*\*([^\n*]+@[^\n*]+)\n\*\*([^\n]+)", r"\1\n\2", text)
    text = re.sub(r"(?m)^\*\*$", "", text)

    # Convert "heading + spaced lines" blocks into compact bullet lists.
    text = normalize_spaced_list_blocks(text)

    # Ensure there are no blank lines between list items.
    text = compact_list_item_spacing(text)

    return text


def compact_list_item_spacing(text: str) -> str:
    """Collapse blank lines between consecutive markdown list items."""
    text = re.sub(r"(?m)^([*+-]\s.+)\n\n(?=[*+-]\s)", r"\1\n", text)
    text = re.sub(r"(?m)^(\d+\.\s.+)\n\n(?=\d+\.\s)", r"\1\n", text)
    return text


def normalize_spaced_list_blocks(text: str) -> str:
    """
    Convert pseudo-lists into markdown bullet lists.

    This targets patterns like:
    "Was Dich erwartet:" + blank lines + short item lines.
    """
    lines = text.splitlines()
    normalized: list[str] = []
    idx = 0

    while idx < len(lines):
        line = lines[idx]
        if not _is_list_intro_line(line):
            normalized.append(line)
            idx += 1
            continue

        item_idx = idx + 1
        while item_idx < len(lines) and not lines[item_idx].strip():
            item_idx += 1

        items: list[str] = []
        scan_idx = item_idx
        while scan_idx < len(lines):
            candidate = lines[scan_idx].strip()
            if not _is_list_item_candidate(candidate):
                break
            items.append(candidate)
            scan_idx += 1
            if scan_idx < len(lines) and not lines[scan_idx].strip():
                scan_idx += 1
            else:
                break

        if len(items) < 2:
            normalized.append(line)
            idx += 1
            continue

        normalized.extend([line, ""])
        normalized.extend(f"- {item}" for item in items)
        idx = scan_idx
        continue

    return "\n".join(normalized)


def _is_list_intro_line(line: str) -> bool:
    stripped = line.strip()
    return bool(stripped) and stripped.endswith(":")


def _is_list_item_candidate(line: str) -> bool:
    return bool(line) and not (
        line.startswith(("-", "*", "+"))
        or len(line) > 90
        or line.endswith((".", "!", "?", ":"))
    )
