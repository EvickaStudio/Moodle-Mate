import re

from .utilities import (
    has_meaningful_when_blank,
    has_void,
    is_block,
    is_meaningful_when_blank,
    is_void,
)


def enhance_node(node, options):
    """
    Enhances the given node with additional properties.

    Args:
        node: The node object to be enhanced.
        options: Additional options that may influence the enhancement.

    Returns:
        The enhanced node with the following additional properties:
            - is_block: A boolean indicating if the node is a block element.
            - is_code: A boolean indicating if the node is a code element or has a parent that is a code element.
            - is_blank: A boolean indicating if the node is blank.
            - flanking_whitespace: Information about the flanking whitespace of the node.
    """
    node.is_block = is_block(node)
    node.is_code = (node.node_name == "CODE") or (
        node.parent and getattr(node.parent, "is_code", False)
    )
    node.is_blank = _is_blank(node)
    node.flanking_whitespace = _flanking_whitespace(node, options)
    return node


def _is_blank(node):
    """
    Determines if a given node is considered "blank".

    A node is considered blank if:
    - It is not a void node and not meaningful when blank.
    - It is a text or CDATA node containing only whitespace.
    - None of its children are void or meaningful when blank.
    - All of its children are also considered blank.

    Args:
        node: The node to check.

    Returns:
        bool: True if the node is blank, False otherwise.
    """
    if is_void(node) or is_meaningful_when_blank(node):
        return False
    if node.node_type in [3, 4]:  # Text or CDATA node

        return bool(re.match(r"^\s*$", node.data))
    # Check children
    if has_void(node) or has_meaningful_when_blank(node):
        return False
    # Check children recursively
    return all(_is_blank(child) for child in node.children)


def _flanking_whitespace(node, options):
    """
    Determines the leading and trailing whitespace for a given node based on its context.

    If the node is a block element or if it is a code element with the "preformattedCode" option enabled,
    no leading or trailing whitespace is returned.

    Args:
        node: The node object containing text content and metadata.
        options: A dictionary of options that may affect whitespace handling.

    Returns:
        A dictionary with two keys:
            - "leading": A string representing the leading whitespace.
            - "trailing": A string representing the trailing whitespace.
    """
    if node.is_block or (options.get("preformattedCode") and node.is_code):
        return {"leading": "", "trailing": ""}

    text = node.text_content()
    leading, trailing = _edge_whitespace(text)

    # When there is whitespace on the left in the neighbor, get rid
    if leading and _is_flanked_by_whitespace("left", node, options):
        leading = ""
    # Analogously for the right side
    if trailing and _is_flanked_by_whitespace("right", node, options):
        trailing = ""

    return {"leading": leading, "trailing": trailing}


def _edge_whitespace(string):
    """
    Extracts leading and trailing whitespace from a given string.

    Args:
        string (str): The input string from which to extract whitespace.

    Returns:
        tuple: A tuple containing two strings:
            - The leading whitespace.
            - The trailing whitespace.
            If no leading or trailing whitespace is found, empty strings are returned.
    """
    match = re.match(r"^(\s*)(.*?)(\s*)$", string, flags=re.DOTALL)
    if match:
        return match.group(1), match.group(3)
    return "", ""


def _is_flanked_by_whitespace(side, node, options):
    """
    Check if a node is flanked by whitespace on the specified side.

    Args:
        side (str): The side to check for whitespace, either "left" or "right".
        node (Node): The node to check.
        options (dict): Additional options that may affect the check.

    Returns:
        bool: True if the node is flanked by whitespace on the specified side, False otherwise.
    """
    sibling = node.previous_sibling if side == "left" else node.next_sibling
    if sibling:
        if (
            sibling.node_type == 3
            and sibling.data
            and sibling.data.endswith(" ")
            and side == "left"
        ):
            return True
        if (
            sibling.node_type == 3
            and sibling.data
            and sibling.data.startswith(" ")
            and side == "right"
        ):
            return True
        if options.get("preformattedCode") and sibling.node_name == "CODE":
            return False
        # Check for inline elements
        if sibling.node_type == 1 and not is_block(sibling):
            text = sibling.text_content()
            if side == "left":
                return text.endswith(" ")
            else:
                return text.startswith(" ")
    return False
