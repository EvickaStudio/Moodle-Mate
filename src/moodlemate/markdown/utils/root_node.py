import copy
import logging

from .html_parser import parse_from_string
from .utilities import is_block, is_void
from .whitespace import collapse_whitespace

logger = logging.getLogger(__name__)


class HTMLComplexityError(ValueError):
    """HTML exceeds the safe work budget for recursive Markdown conversion."""


def _check_complexity(root):
    # ponytail: bound the recursive converter; use iterative conversion for larger trees.
    stack = [(root, 0)]
    visited = 0
    while stack:
        node, depth = stack.pop()
        visited += 1
        if depth > 64 or visited > 10_000:
            raise HTMLComplexityError("HTML is too complex for Markdown conversion")
        stack.extend((child, depth + 1) for child in node.children)


def build_root_node(input_obj, options):
    """
    Wraps (and possibly parses) an input (HTML string or Node) into a single root node.

    1) If the input is a string, parse it as HTML inside <x-turndown>.
    2) Otherwise, copy the supplied subtree without its ancestors.
    3) Finally, collapse whitespace on the root based on the options.

    Args:
        input_obj (str or Node): Some HTML or a Node.
        options (dict): Additional configuration.

    Returns:
        Node: The resulting root node.
    """
    if isinstance(input_obj, str):
        doc = parse_from_string(
            f"<x-turndown id='turndown-root'>{input_obj}</x-turndown>"
        )
        root = _find_turndown_root(doc)
    else:
        root = input_obj

    _check_complexity(root)
    if not isinstance(input_obj, str):
        root = copy.deepcopy(root, {id(root.parent): None})

    # Collapse whitespace
    collapse_whitespace(
        element=root,
        is_block_fn=is_block,
        is_void_fn=is_void,
        is_pre_fn=(
            (lambda n: _is_pre_or_code(n, options))
            if options.get("preformattedCode")
            else _is_pre_or_code
        ),
    )
    return root


def _find_turndown_root(document_node):
    """
    DFS for a node named X-TURNDOWN. If found, return it; otherwise fallback to original doc node.
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
    Basic check: node is <pre> or <code>.
    """
    return node.node_name in ["PRE", "CODE"]
