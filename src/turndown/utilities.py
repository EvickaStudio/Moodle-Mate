import re

BLOCK_ELEMENTS = [
    "ADDRESS",
    "ARTICLE",
    "ASIDE",
    "AUDIO",
    "BLOCKQUOTE",
    "BODY",
    "CANVAS",
    "CENTER",
    "DD",
    "DIR",
    "DIV",
    "DL",
    "DT",
    "FIELDSET",
    "FIGCAPTION",
    "FIGURE",
    "FOOTER",
    "FORM",
    "FRAMESET",
    "H1",
    "H2",
    "H3",
    "H4",
    "H5",
    "H6",
    "HEADER",
    "HGROUP",
    "HR",
    "HTML",
    "ISINDEX",
    "LI",
    "MAIN",
    "MENU",
    "NAV",
    "NOFRAMES",
    "NOSCRIPT",
    "OL",
    "OUTPUT",
    "P",
    "PRE",
    "SECTION",
    "TABLE",
    "TBODY",
    "TD",
    "TFOOT",
    "TH",
    "THEAD",
    "TR",
    "UL",
]
VOID_ELEMENTS = [
    "AREA",
    "BASE",
    "BR",
    "COL",
    "COMMAND",
    "EMBED",
    "HR",
    "IMG",
    "INPUT",
    "KEYGEN",
    "LINK",
    "META",
    "PARAM",
    "SOURCE",
    "TRACK",
    "WBR",
]
MEANINGFUL_WHEN_BLANK = [
    "A",
    "TABLE",
    "THEAD",
    "TBODY",
    "TFOOT",
    "TH",
    "TD",
    "IFRAME",
    "SCRIPT",
    "AUDIO",
    "VIDEO",
]


def extend(destination, *sources):
    """
    Extends the destination dictionary with key-value pairs from one or more source dictionaries.

    Args:
        destination (dict): The dictionary to be extended.
        *sources (dict): One or more dictionaries containing key-value pairs to add to the destination.

    Returns:
        dict: The extended destination dictionary.
    """
    for source in sources:
        for k, v in source.items():
            destination[k] = v
    return destination


def repeat(character, count):
    """
    Repeats a given character a specified number of times.

    Args:
        character (str): The character to be repeated.
        count (int): The number of times to repeat the character.

    Returns:
        str: A string containing the repeated character.
    """
    return character * count


def trim_leading_newlines(string):
    """
    Remove leading newlines from a given string.

    Args:
        string (str): The input string from which leading newlines should be removed.

    Returns:
        str: The string with leading newlines removed.
    """

    return re.sub(r"^\n+", "", string)


def trim_trailing_newlines(string):
    """
    Remove trailing newline characters from the given string.

    Args:
        string (str): The input string from which trailing newlines will be removed.

    Returns:
        str: The string with trailing newline characters removed.
    """

    return re.sub(r"\n+$", "", string)


def is_block(node):
    """
    Check if a given node is a block-level element.

    Args:
        node (Node): The node to check. It should have a 'node_name' attribute.

    Returns:
        bool: True if the node is a block-level element, False otherwise.
    """
    return node.node_name in BLOCK_ELEMENTS


def is_void(node):
    """
    Check if a given node is a void element.

    Void elements are HTML elements that do not have closing tags.

    Args:
        node (Node): The node to check.

    Returns:
        bool: True if the node is a void element, False otherwise.
    """
    return node.node_name in VOID_ELEMENTS


def has_void(node):
    """
    Checks if a given node or any of its descendants is a void element.

    A void element is an element that cannot have any child nodes.

    Args:
        node: The root node to start the search from. It is expected to have a 'children' attribute which is iterable.

    Returns:
        bool: True if the node or any of its descendants is a void element, False otherwise.
    """
    stack = [node]
    while stack:
        current = stack.pop()
        for c in current.children:
            if is_void(c):
                return True
            stack.append(c)
    return False


def is_meaningful_when_blank(node):
    """
    Check if a node is considered meaningful when it is blank.

    Args:
        node (Node): The node to check. It should have an attribute `node_name`.

    Returns:
        bool: True if the node's name is in the MEANINGFUL_WHEN_BLANK set, False otherwise.
    """
    return node.node_name in MEANINGFUL_WHEN_BLANK


def has_meaningful_when_blank(node):
    """
    Determines if a node or any of its descendants have meaningful content when blank.

    This function traverses the given node and its children to check if any of them
    are considered meaningful when blank. It uses a depth-first search approach.

    Args:
        node: The root node to start the traversal from. It is expected to have a
              'children' attribute that is iterable.

    Returns:
        bool: True if any node or its descendants are meaningful when blank, False otherwise.
    """
    stack = [node]
    while stack:
        current = stack.pop()
        for c in current.children:
            if is_meaningful_when_blank(c):
                return True
            stack.append(c)
    return False


def clean_attribute(attribute):
    """
    Cleans the given attribute by reducing large amounts of whitespace or line breaks.

    Args:
        attribute (str): The attribute to be cleaned.

    Returns:
        str: The cleaned attribute with reduced whitespace and line breaks.
    """
    if not attribute:
        return ""
    import re

    # Replace multiple newlines with a single newline
    return re.sub(r"(\n+\s*)+", "\n", attribute)
