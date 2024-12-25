"""
The collapseWhitespace function is adapted from collapse-whitespace by Luc Thevenard.

The MIT License (MIT)

Copyright (c) 2014 Luc Thevenard <lucthevenard@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software ...
"""

import re


def collapse_whitespace(element, is_block, is_void, is_pre):
    """
    Collapses consecutive whitespace characters into a single space within the given element's text nodes,
    while preserving whitespace in preformatted text and void elements.

    Args:
        element (Node): The root element to process.
        is_block (function): A function that takes a node and returns True if it is a block-level element.
        is_void (function): A function that takes a node and returns True if it is a void element.
        is_pre (function): A function that takes a node and returns True if it is a preformatted text element.

    Returns:
        None
    """

    if not element.first_child or is_pre(element):
        return

    prev_text = None
    keep_leading_ws = False

    prev = None
    node = _next(prev, element, is_pre)

    while node != element:
        if node.node_type in (3, 4):  # TEXT_NODE or CDATA_SECTION_NODE
            text_data = node.data
            # Reduces multiple whitespaces to a single space
            text_data = _re_sub(r"[ \r\n\t]+", " ", text_data)

            # When leading whitespace should be removed
            if (
                (not prev_text or prev_text.data.endswith(" "))
                and (not keep_leading_ws)
                and text_data.startswith(" ")
            ):
                text_data = text_data[1:]

            if not text_data:
                # Node remove
                node = _remove(node)
                continue

            node.data = text_data
            prev_text = node

        elif node.node_type == 1:  # ELEMENT_NODE
            if is_block(node) or node.node_name == "BR":
                if prev_text:
                    prev_text.data = prev_text.data.rstrip()
                prev_text = None
                keep_leading_ws = False
            elif is_void(node) or is_pre(node):
                # Void-Elemente or PRE wont get trimmed
                prev_text = None
                keep_leading_ws = True
            else:
                keep_leading_ws = False
        else:
            node = _remove(node)
            continue

        next_node = _next(prev, node, is_pre)
        prev = node
        node = next_node

    if prev_text:
        prev_text.data = prev_text.data.rstrip()
        if not prev_text.data:
            _remove(prev_text)


def _remove(node):
    """
    Removes the given node from its parent and returns the next node to process.

    If the node has a next sibling, that sibling is returned. Otherwise, the parent node is returned.

    Args:
        node: The node to be removed.

    Returns:
        The next node to process after the removal.
    """
    next_node = node.next_sibling if node.next_sibling else node.parent
    node.remove_self()
    return next_node


def _next(prev, current, is_pre):
    """
    Determine the next node to process in a tree structure.

    Args:
        prev: The previous node that was processed.
        current: The current node being processed.
        is_pre (function): A function that takes a node and returns a boolean indicating
                           whether the node is a preformatted text node.

    Returns:
        The next node to process. This could be the next sibling, the first child, or the parent
        of the current node, depending on the structure and the conditions provided.
    """

    if (prev and prev.parent == current) or is_pre(current):
        return current.next_sibling if current.next_sibling else current.parent
    return (
        current.first_child
        if current.first_child
        else (current.next_sibling if current.next_sibling else current.parent)
    )


def _re_sub(pattern, repl, string):
    """
    Replace occurrences of a pattern in a string with a replacement.

    Args:
        pattern (str): The regular expression pattern to search for.
        repl (str): The replacement string.
        string (str): The string to search within.

    Returns:
        str: The string with the pattern replaced by the replacement.
    """
    return re.sub(pattern, repl, string)
