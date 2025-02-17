import re
# import logging
from .turndown import MarkdownConverter

TURNDOWN = MarkdownConverter({"headingStyle": "atx", "codeBlockStyle": "fenced"})

# logger = logging.getLogger(__name__)

def convert(html_content: str) -> str:
    """
    Converts HTML content to Markdown using TurndownService.

    Args:
        html_content (str): The HTML content to be converted.

    Returns:
        str: The converted and cleaned content.
    """
    # logger.info(f"Original HTML content:\n{html_content}")
    md_output = TURNDOWN.to_markdown(html_content)
    # logger.info(f"Raw markdown output:\n{md_output}")
    cleaned = clean_converted_text(md_output)
    # logger.info(f"Final cleaned markdown:\n{cleaned}")
    return cleaned


def clean_converted_text(text: str) -> str:
    """
    Cleans the converted text by applying regex replacements.
    Makes the output Discord-embed safe.

    Args:
        text (str): The text to be cleaned.

    Returns:
        str: The cleaned text.
    """
    # Remove navigation breadcrumbs
    text = re.sub(r'\[.*?\]\(.*?\)\s*»\s*', '', text)
    
    # Remove all image patterns
    patterns = [
        r"!\[.*?\]\(.*?\)",  # Standard markdown images
        r"!\[.*?%.*?\]",     # Images with percent encoding
        r"\[!\[.*?\]\(.*?\)\]\(.*?\)",  # Nested images
        r"!\[.*?\]",         # Incomplete image tags
        r"\[.*?\]\(.*?\.(?:png|jpg|jpeg|gif|bmp|webp).*?\)",  # Links to images
        r"\[\]\(.*?\)",      # Empty links
    ]
    
    for pattern in patterns:
        text = re.sub(pattern, "", text)
    
    # Clean up broken/truncated links
    text = re.sub(r'\[.*?\]\([^)]*$', "", text)
    
    # Remove empty links and their brackets
    text = re.sub(r'\s*\[[\s\S]*?\]\s*\(\s*#\s*\)', "", text)
    
    # Remove forum management links at the bottom
    text = re.sub(r'\[Forum abbestellen\].*$', '', text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\[Diskussion im Forum zeigen\].*$', '', text, flags=re.MULTILINE | re.DOTALL)
    
    # Clean up multiple newlines, spaces and underscores
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'_{2,}', '___', text)
    
    # Remove any remaining empty lines at the start/end
    text = text.strip()
    
    # Remove any double spaces after cleaning
    text = re.sub(r' +', ' ', text)
    
    # Ensure there's no more than one blank line between paragraphs
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    return text