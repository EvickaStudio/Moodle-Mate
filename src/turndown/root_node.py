import copy

from .collapse_whitespace import collapse_whitespace
from .html_parser import parse_from_string
from .utilities import is_block, is_void


def RootNode(input_obj, options):
    """
    Processes the input object to create a root node for further manipulation.

    If the input object is a string, it is parsed as HTML and wrapped in a custom
    <x-turndown> element. If the input object is not a string, it is deep-copied.

    The function then collapses whitespace in the root element based on the provided
    options.

    Args:
        input_obj (str or object): The input object to be processed. Can be an HTML string
                                   or any other object.
        options (dict): A dictionary of options that influence how the input object is processed.
                        The key "preformattedCode" is used to determine if preformatted code blocks
                        should be handled differently.

    Returns:
        object: The processed root node.
    """

    if isinstance(input_obj, str):
        # Parse HTML
        doc = parse_from_string(
            f"<x-turndown id='turndown-root'>{input_obj}</x-turndown>"
        )
        root = _find_turndown_root(doc)
    else:

        root = copy.deepcopy(input_obj)

    collapse_whitespace(
        element=root,
        is_block=is_block,
        is_void=is_void,
        is_pre=(
            (lambda n: _is_pre_or_code(n, options))
            if options.get("preformattedCode")
            else _is_pre_or_code
        ),
    )
    return root


def _find_turndown_root(document_node):
    """
    Searches for the x-turndown element in the document node tree.

    This function traverses the tree of nodes starting from the given
    document node and looks for a node with the name "X-TURNDOWN".
    If such a node is found, it is returned. If no such node is found,
    the original document node is returned.

    Args:
        document_node (Node): The root node of the document tree to search.

    Returns:
        Node: The node with the name "X-TURNDOWN" if found, otherwise the
        original document node.
    """
    stack = [document_node]
    while stack:
        current = stack.pop()
        if current.node_name == "X-TURNDOWN":
            return current
        stack.extend(reversed(current.children))
    return document_node


def _is_pre_or_code(node, options=None):
    """
    Check if the given node is a <pre> or <code> HTML element.

    Args:
        node (Node): The node to check, which should have a 'node_name' attribute.
        options (dict, optional): Additional options for the check (currently unused).

    Returns:
        bool: True if the node is a <pre> or <code> element, False otherwise.
    """
    return (node.node_name == "PRE") or (node.node_name == "CODE")
