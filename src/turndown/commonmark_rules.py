import re

from .utilities import clean_attribute, repeat


def paragraph_rule(content, node, options):
    """
    Converts the given content into a paragraph by adding newlines before and after it.

    Args:
        content (str): The content to be wrapped in paragraph tags.
        node (Node): The current node being processed (not used in this function).
        options (dict): Additional options for processing (not used in this function).

    Returns:
        str: The content wrapped in paragraph tags with newlines before and after.
    """
    return "\n\n" + content + "\n\n"


def line_break_rule(content, node, options):
    """
    Converts a line break node to a string representation.

    Args:
        content (str): The content of the node.
        node (Node): The node representing the line break.
        options (dict): A dictionary of options, where "br" is the string to use for a line break.

    Returns:
        str: The string representation of the line break followed by a newline character.
    """
    return options["br"] + "\n"


def heading_rule(content, node, options):
    """
    Converts a heading node to a Markdown heading string based on the specified options.

    Args:
        content (str): The text content of the heading.
        node (object): The node object representing the heading element. It should have a 'node_name' attribute
                       which indicates the heading level (e.g., 'H1', 'H2', etc.).
        options (dict): A dictionary of options. It should contain a 'headingStyle' key which determines the
                        style of the heading. Possible values are:
                        - "setext": Uses Setext-style headings for levels 1 and 2.
                        - Any other value: Uses ATX-style headings (with '#' characters).

    Returns:
        str: The Markdown-formatted heading string.
    """
    level = int(node.node_name[1])  # 'H2' -> 2
    style = options["headingStyle"]
    if style == "setext" and level < 3:
        underline = repeat("=" if level == 1 else "-", len(content))
        return f"\n\n{content}\n{underline}\n\n"
    else:
        return "\n\n" + repeat("#", level) + " " + content + "\n\n"


def blockquote_rule(content, node, options):
    """
    Converts the given content into a blockquote format.

    Args:
        content (str): The text content to be converted into a blockquote.
        node: The node element (not used in this function).
        options: Additional options (not used in this function).

    Returns:
        str: The content formatted as a blockquote with '>' at the beginning of each line.
    """
    content = content.strip("\n")
    content = "\n".join(["> " + line for line in content.split("\n")])
    return "\n\n" + content + "\n\n"


def list_rule(content, node, options):
    """
    Processes a list item node and returns its content with appropriate newlines.

    Args:
        content (str): The content of the list item node.
        node (Node): The current node being processed.
        options (dict): Additional options for processing.

    Returns:
        str: The processed content with appropriate newlines.
    """
    parent = node.parent
    if (
        parent
        and parent.node_name == "LI"
        and parent.last_element_child == node
    ):
        return "\n" + content
    else:
        return "\n\n" + content + "\n\n"


def list_item_rule(content, node, options):
    """
    Processes a list item node and formats its content according to CommonMark rules.

    Args:
        content (str): The content of the list item.
        node (Node): The current node representing the list item.
        options (dict): A dictionary of options, including formatting markers.

    Returns:
        str: The formatted list item content with appropriate indentation and markers.
    """
    content = content.lstrip("\n")  # removing leading newlines
    content = content.rstrip("\n") + "\n"
    # every line should be indented by 4 spaces
    content = "\n".join(["    " + line for line in content.split("\n")])
    # Prefix with bullet or number
    parent = node.parent
    marker = options["bulletListMarker"] + "   "
    if parent and parent.node_name == "OL":
        start_attr = parent.get_attribute("start")
        index = parent.index_in_parent(node)  # custom index for ordered lists
        start_index = (int(start_attr) + index) if start_attr else (index + 1)
        marker = f"{start_index}.  "

    # Line breaks should be preserved
    if node.next_sibling and not content.endswith("\n"):
        content += "\n"

    return marker + content


def indented_code_block_rule(content, node, options):
    """
    Converts a CommonMark indented code block node to a string with the appropriate indentation.

    Args:
        content (str): The content of the node.
        node (Node): The CommonMark node representing the indented code block.
        options (dict): Additional options for processing.

    Returns:
        str: The indented code block as a string with each line indented by four spaces.
    """
    code = node.first_child.text_content().replace("\n", "\n    ")
    return "\n\n    " + code + "\n\n"


def fenced_code_block_rule(content, node, options):
    """
    Converts a node representing a code block into a fenced code block string.

    Args:
        content (str): The content of the node.
        node (Node): The node object containing the code block.
        options (dict): A dictionary of options, including the fence character.

    Returns:
        str: A string representing the fenced code block.

    The function extracts the language class from the node's first child, if present,
    and uses it to annotate the code block. It ensures that the fence size is adjusted
    if the code contains sequences of backticks longer than the default fence size.
    """
    class_name = node.first_child.get_attribute("class") or ""
    language = ""

    match = re.search(r"language-(\S+)", class_name)
    if match:
        language = match.group(1)

    code = node.first_child.text_content()
    fence_char = options["fence"][0]
    fence_size = 3

    # Find the longest sequence of fence characters in the code
    fence_in_code_regex = re.compile(r"^" + fence_char + "{3,}", re.MULTILINE)
    for found in fence_in_code_regex.findall(code):
        if len(found) >= fence_size:
            fence_size = len(found) + 1
    fence = fence_char * fence_size

    code = code.rstrip("\n")
    return f"\n\n{fence}{language}\n{code}\n{fence}\n\n"


def horizontal_rule_rule(content, node, options):
    """
    Converts a horizontal rule node to a markdown horizontal rule.

    Args:
        content (str): The content of the node.
        node (object): The node to be converted.
        options (dict): A dictionary of options, where 'hr' is the markdown representation of a horizontal rule.

    Returns:
        str: The markdown representation of the horizontal rule.
    """
    return f"\n\n{options['hr']}\n\n"


def inline_link_rule(content, node, options):
    """
    Converts a node representing a link into a Markdown formatted link.

    Args:
        content (str): The text content of the link.
        node (Node): The node object containing the link attributes.
        options (dict): Additional options for processing the link.

    Returns:
        str: A string representing the Markdown formatted link.
    """
    href = node.get_attribute("href")
    if href:
        href = href.replace("(", r"\(").replace(")", r"\)")
    title = clean_attribute(node.get_attribute("title"))
    if title:
        title = f" \"{title.replace('\"', '\\\"')}\""
    return f"[{content}]({href}{title})"


class ReferenceStyleStore:
    """
    A class to store and manage reference-style links.

    Attributes:
    references (list): A list to store reference-style links.

    Methods:
    add_reference(ref):
        Adds a reference-style link to the store.

    append_references(options):
        Appends all stored references to a string and clears the store.
        Returns the formatted string of references if any exist, otherwise returns an empty string.
    """

    def __init__(self):
        """
        Initializes the instance with an empty list of references.
        """
        self.references = []

    def add_reference(self, ref):
        """
        Adds a reference to the list of references.

        Args:
            ref: The reference to be added.
        """
        self.references.append(ref)

    def append_references(self, options):
        """
        Appends the stored references to a string and clears the references list.

        Args:
            options (dict): A dictionary of options (not used in this method).

        Returns:
            str: A string containing the references separated by newlines,
                 wrapped with two newlines before and after. If there are no
                 references, returns an empty string.
        """
        if self.references:
            s = "\n\n" + "\n".join(self.references) + "\n\n"
            self.references = []
            return s
        return ""


reference_link_store = ReferenceStyleStore()


def reference_link_rule(content, node, options):
    """
    Generates a Markdown reference link based on the provided content, node, and options.

    Args:
        content (str): The text content of the link.
        node (Node): The HTML node containing the link attributes.
        options (dict): A dictionary of options, including the link reference style.

    Returns:
        str: The Markdown reference link.

    The function supports three types of link reference styles:
        - "collapsed": Generates a collapsed reference link.
        - "shortcut": Generates a shortcut reference link.
        - "full" (or any other value): Generates a full reference link with an index.

    The function also stores the generated reference in a global reference link store.
    """
    href = node.get_attribute("href") or ""
    title = clean_attribute(node.get_attribute("title")) or ""
    if title:
        title = f' "{title}"'

    link_ref_style = options["linkReferenceStyle"]
    if link_ref_style == "collapsed":
        replacement = f"[{content}][]"
        ref = f"[{content}]: {href}{title}"
    elif link_ref_style == "shortcut":
        replacement = f"[{content}]"
        ref = f"[{content}]: {href}{title}"
    else:
        # "full" or any other value
        idx = len(reference_link_store.references) + 1
        replacement = f"[{content}][{idx}]"
        ref = f"[{idx}]: {href}{title}"

    reference_link_store.add_reference(ref)
    return replacement


def emphasis_rule(content, node, options):
    """
    Converts the given content into an emphasized (italicized) text using the specified delimiter.

    Args:
        content (str): The text content to be emphasized.
        node (dict): The node object from the document tree (not used in this function).
        options (dict): A dictionary containing options for the conversion.
                        It must include the key "emDelimiter" which specifies the delimiter to use for emphasis.

    Returns:
        str: The emphasized text if content is not empty or whitespace, otherwise an empty string.
    """
    if not content.strip():
        return ""
    return options["emDelimiter"] + content + options["emDelimiter"]


def strong_rule(content, node, options):
    """
    Converts the given content into a strong (bold) text format using the specified delimiter.

    Args:
        content (str): The text content to be formatted.
        node (dict): The current node in the document tree (not used in this function).
        options (dict): A dictionary containing formatting options, specifically the "strongDelimiter" key.

    Returns:
        str: The formatted strong (bold) text, or an empty string if the content is empty or whitespace.
    """
    if not content.strip():
        return ""
    return options["strongDelimiter"] + content + options["strongDelimiter"]


def code_rule(content, node, options):
    """
    Converts a given content string into a code block format suitable for CommonMark.

    Args:
        content (str): The content to be formatted as a code block.
        node (Node): The node object representing the content in the document tree.
        options (dict): Additional options that may affect the formatting.

    Returns:
        str: The content formatted as a code block with appropriate delimiters.
    """
    if not content:
        return ""
    # Replace newlines and carriage returns with spaces
    content = content.replace("\n", " ").replace("\r", "")
    import re

    # Check if the content contains leading or trailing spaces
    pattern = r"^`|^ .*?[^ ].* $|`$"
    extra_space = " " if re.search(pattern, content) else ""
    delimiter = "`"
    # When the content contains backticks, increase the delimiter length
    matches = re.findall(r"`+", content)
    while delimiter in matches:
        delimiter += "`"
    return delimiter + extra_space + content + extra_space + delimiter


def image_rule(content, node, options):
    """
    Converts an HTML image node to a Markdown image syntax.

    Args:
        content (str): The content of the node.
        node (Node): The HTML node representing the image.
        options (dict): Additional options for the conversion.

    Returns:
        str: The Markdown representation of the image, or an empty string if the src attribute is missing.
    """
    alt = clean_attribute(node.get_attribute("alt") or "")
    src = node.get_attribute("src") or ""
    title = clean_attribute(node.get_attribute("title") or "")
    title_part = f' "{title}"' if title else ""
    if src:
        return f"![{alt}]({src}{title_part})"
    return ""


COMMONMARK_RULES = {
    "paragraph": {"filter": "p", "replacement": paragraph_rule},
    "lineBreak": {"filter": "br", "replacement": line_break_rule},
    "heading": {
        "filter": ["h1", "h2", "h3", "h4", "h5", "h6"],
        "replacement": heading_rule,
    },
    "blockquote": {"filter": "blockquote", "replacement": blockquote_rule},
    "list": {"filter": ["ul", "ol"], "replacement": list_rule},
    "listItem": {"filter": "li", "replacement": list_item_rule},
    "indentedCodeBlock": {
        "filter": lambda node, options: (
            options["codeBlockStyle"] == "indented"
            and node.node_name == "PRE"
            and node.first_child
            and node.first_child.node_name == "CODE"
        ),
        "replacement": indented_code_block_rule,
    },
    "fencedCodeBlock": {
        "filter": lambda node, options: (
            options["codeBlockStyle"] == "fenced"
            and node.node_name == "PRE"
            and node.first_child
            and node.first_child.node_name == "CODE"
        ),
        "replacement": fenced_code_block_rule,
    },
    "horizontalRule": {"filter": "hr", "replacement": horizontal_rule_rule},
    "inlineLink": {
        "filter": lambda node, options: (
            options["linkStyle"] == "inlined"
            and node.node_name == "A"
            and node.get_attribute("href")
        ),
        "replacement": inline_link_rule,
    },
    "referenceLink": {
        "filter": lambda node, options: (
            options["linkStyle"] == "referenced"
            and node.node_name == "A"
            and node.get_attribute("href")
        ),
        "replacement": reference_link_rule,
        "append": reference_link_store.append_references,
    },
    "emphasis": {"filter": ["em", "i"], "replacement": emphasis_rule},
    "strong": {"filter": ["strong", "b"], "replacement": strong_rule},
    "code": {
        "filter": lambda node, options: (
            node.node_name == "CODE"
            and not (
                node.parent
                and node.parent.node_name == "PRE"
                and (node.previous_sibling or node.next_sibling)
            )
        ),
        "replacement": lambda content, node, options: code_rule(
            content, node, options
        ),
    },
    "image": {"filter": "img", "replacement": image_rule},
}
