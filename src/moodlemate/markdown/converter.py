import logging
import re

from .turndown import MarkdownConverter
from .utils.html_parser import parse_from_string
from .utils.utilities import is_block

TURNDOWN = MarkdownConverter({"headingStyle": "atx", "codeBlockStyle": "fenced"})

logger = logging.getLogger(__name__)

MAX_PSEUDO_LIST_ITEM_LENGTH = 90
PSEUDO_LIST_ITEM_TERMINATORS = (".", "!", "?", ":")


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


def convert_plain_text(html_content: str) -> str:
    """Flatten complex HTML iteratively, retaining text, breaks and link destinations."""
    parts: list[str] = []
    stack = [(parse_from_string(html_content), False)]
    while stack:
        node, closing = stack.pop()
        if node.node_type == 3:
            parts.append(TURNDOWN.escape(node.data))
            continue
        if closing:
            if node.node_name == "A" and (href := node.get_attribute("href")):
                parts.append(f" ({TURNDOWN.escape(href)})")
        else:
            stack.append((node, True))
            stack.extend((child, False) for child in reversed(node.children))
        if is_block(node) or (node.node_name == "BR" and not closing):
            parts.append("\n")
    return re.sub(r"\n{3,}", "\n\n", "".join(parts)).strip()


# If Turndown produces malformed lines or other unexpected Markdown output,
# mdformat can be used to format the markdown to comply with the CommonMark spec.
# (currently not used)
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

    text = _fix_split_bold_email_markers(text)

    # Convert "heading + spaced lines" blocks into compact bullet lists.
    text = normalize_spaced_list_blocks(text)

    # Ensure there are no blank lines between list items.
    text = compact_list_item_spacing(text)
    # Final pass to preserve compact paragraph spacing after all rewrites.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text


def _fix_split_bold_email_markers(text: str) -> str:
    """
    Remove bold markers split around email lines in Moodle messages.

    Example:
    "**info@example.com\n**Weitere Infos" -> "info@example.com\nWeitere Infos"
    """
    text = re.sub(r"\*\*([^\n*]+@[^\n*]+)\n\*\*([^\n]+)", r"\1\n\2", text)
    return re.sub(r"(?m)^\*\*$", "", text)


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
        consumed_separator = False
        while scan_idx < len(lines):
            candidate = lines[scan_idx].strip()
            if not _is_list_item_candidate(candidate):
                break
            items.append(candidate)
            scan_idx += 1
            if scan_idx < len(lines) and not lines[scan_idx].strip():
                scan_idx += 1
                consumed_separator = True
            else:
                consumed_separator = False
                break

        if len(items) < 2:
            normalized.append(line)
            idx += 1
            continue

        normalized.extend([line, ""])
        normalized.extend(f"- {item}" for item in items)
        if (
            consumed_separator
            and scan_idx < len(lines)
            and lines[scan_idx].strip()
            and not _is_list_item_candidate(lines[scan_idx].strip())
        ):
            normalized.append("")
        idx = scan_idx
        continue

    return "\n".join(normalized)


def _is_list_intro_line(line: str) -> bool:
    stripped = line.strip()
    # Moodle sometimes renders prose-list headings as "Was Dich erwartet:".
    return bool(stripped) and stripped.endswith(":")


def _is_list_item_candidate(line: str) -> bool:
    # Keep this conservative so full prose paragraphs are not converted to bullets.
    return bool(line) and not (
        line.startswith(("-", "*", "+"))
        or len(line) > MAX_PSEUDO_LIST_ITEM_LENGTH
        or line.endswith(PSEUDO_LIST_ITEM_TERMINATORS)
    )
