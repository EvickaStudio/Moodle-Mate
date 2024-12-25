# flake8: noqa: E501

import functools

from .commonmark_rules import COMMONMARK_RULES
from .node import enhance_node
from .root_node import RootNode
from .rules import Rules
from .utilities import extend, trim_leading_newlines, trim_trailing_newlines


class TurndownService:
    """
    Python Turndown - A Python port of the Turndown JavaScript HTML-to-Markdown converter.

    Methods
    -------
    __init__(options=None)
        Initializes the TurndownService with the given options.

    turndown(input_obj)
        Converts the given HTML (string or Node) to Markdown.

    use(plugin)
        Registers one or more plugins.

    addRule(key, rule)
        Adds a rule to the TurndownService.

    keep(filter_func)
        Keeps elements that match the filter function.

    remove(filter_func)
        Removes elements that match the filter function.

    escape(string)
        Escapes special Markdown characters in the given string.

    _process(parentNode)
        Reduces the DOM subtree to its Markdown string.

    _post_process(output)
        Performs post-processing on the Markdown output.

    _append_references(rule_obj, nonlocal_output)
        Appends references to the Markdown output based on the rule object.

    _replacement_for_node(node)
        Returns the Markdown replacement for the given node.
    """

    def __init__(self, options=None):
        """
        Initialize the Turndown instance with the given options.

        Parameters:
        options (dict, optional): A dictionary of options to customize the behavior of the Turndown instance.
            If not provided, default options will be used. The available options are:
            - rules: The set of rules to use for converting HTML to Markdown. Default is COMMONMARK_RULES.
            - headingStyle: The style to use for headings. Default is "setext".
            - hr: The string to use for horizontal rules. Default is "* * *".
            - bulletListMarker: The marker to use for bullet lists. Default is "*".
            - codeBlockStyle: The style to use for code blocks. Default is "indented".
            - fence: The string to use for fenced code blocks. Default is "```".
            - emDelimiter: The delimiter to use for emphasis. Default is "_".
            - strongDelimiter: The delimiter to use for strong emphasis. Default is "**".
            - linkStyle: The style to use for links. Default is "inlined".
            - linkReferenceStyle: The style to use for link references. Default is "full".
            - br: The string to use for line breaks. Default is "  ".
            - preformattedCode: Whether to preserve preformatted code blocks. Default is False.
            - blankReplacement: A function to replace blank nodes. Default is a lambda function.
            - keepReplacement: A function to replace nodes that should be kept. Default is a lambda function.
            - defaultReplacement: A function to replace nodes by default. Default is a lambda function.
        """
        if options is None:
            options = {}

        defaults = {
            "rules": COMMONMARK_RULES,
            "headingStyle": "setext",
            "hr": "* * *",
            "bulletListMarker": "*",
            "codeBlockStyle": "indented",
            "fence": "```",
            "emDelimiter": "_",
            "strongDelimiter": "**",
            "linkStyle": "inlined",
            "linkReferenceStyle": "full",
            "br": "  ",
            "preformattedCode": False,
            "blankReplacement": lambda content, node: (
                "\n\n" if getattr(node, "is_block", False) else ""
            ),
            "keepReplacement": lambda content, node: (
                "\n\n" + node.outer_html + "\n\n"
                if getattr(node, "is_block", False)
                else node.outer_html
            ),
            "defaultReplacement": lambda content, node: (
                "\n\n" + content + "\n\n"
                if getattr(node, "is_block", False)
                else content
            ),
        }
        self.options = extend({}, defaults, options)
        self.rules = Rules(self.options)

    def turndown(self, input_obj):
        """
        Converts the given HTML (string or node) to Markdown.

        Args:
            input_obj (str or Node): The HTML content to be converted. It can be a string or a valid Node object.

        Returns:
            str: The converted Markdown content.

        Raises:
            TypeError: If the input_obj is neither a string nor a valid Node.

        Notes:
            - If the input_obj is an empty string, an empty string is returned.
            - Leading and trailing newlines are removed from the output.
        """
        if not _can_convert(input_obj):
            raise TypeError(
                f"{input_obj} ist kein String oder ein valider Node."
            )

        if isinstance(input_obj, str) and input_obj.strip() == "":
            return ""

        root = RootNode(input_obj, self.options)
        output = self._process(root)
        output = self._post_process(output)
        return output.strip("\r\n ")

    def use(self, plugin):
        """
        Applies a plugin or a list of plugins to the current instance.

        Args:
            plugin (Union[Callable, List[Callable]]): A single plugin function or a list of plugin functions to be applied.

        Returns:
            self: The current instance with the applied plugin(s).

        Raises:
            TypeError: If the plugin is neither a function nor a list of functions.
        """
        if isinstance(plugin, list):
            for p in plugin:
                self.use(p)
        elif callable(plugin):
            plugin(self)
        else:
            raise TypeError("plugin must be a function or list of functions")
        return self

    def addRule(self, key, rule):
        """
        Adds a rule to the rules collection.

        Args:
            key (str): The key associated with the rule.
            rule (object): The rule to be added.

        Returns:
            self: The instance of the class to allow method chaining.
        """
        self.rules.add(key, rule)
        return self

    def keep(self, filter_func):
        """
        Adds a filter function to the rules to keep certain elements.

        Args:
            filter_func (function): A function that takes an element as an argument
                                    and returns True if the element should be kept,
                                    False otherwise.

        Returns:
            self: The instance of the class to allow method chaining.
        """
        self.rules.keep(filter_func)
        return self

    def remove(self, filter_func):
        """
        Removes a rule from the rules list based on the provided filter function.

        Args:
            filter_func (function): A function that determines which rule to remove.
                                    It should take a rule as an argument and return
                                    True if the rule should be removed, False otherwise.

        Returns:
            self: The instance of the class to allow method chaining.
        """
        self.rules.remove(filter_func)
        return self

    def escape(self, string):
        """
        Escapes special Markdown characters in the given string to prevent them from being interpreted as Markdown syntax.

        Args:
            string (str): The input string that may contain special Markdown characters.

        Returns:
            str: The escaped string with special Markdown characters replaced by their escaped versions.

        The following characters are escaped:
            - Backslash (\)
            - Asterisk (*)
            - Hyphen (-) at the beginning of a line
            - Plus (+) at the beginning of a line
            - Equals (=) at the beginning of a line
            - Hash (#) at the beginning of a line
            - Backtick (`)
            - Tilde (~) at the beginning of a line
            - Square brackets ([ and ])
            - Greater-than sign (>) at the beginning of a line
            - Underscore (_)
            - Number followed by a period (e.g., 1. ) at the beginning of a line
        """
        escapes = [
            (r"\\", r"\\\\"),
            (r"\*", r"\\*"),
            (r"^-", r"\\-"),
            (r"^\+ ", r"\\+ "),
            (r"^(=+)", r"\\\1"),
            (r"^(#{1,6}) ", r"\\\1 "),
            (r"`", r"\\`"),
            (r"^~~~", r"\\~~~"),
            (r"\[", r"\\["),
            (r"\]", r"\\]"),
            (r"^>", r"\\>"),
            (r"_", r"\\_"),
            (r"^(\d+)\. ", r"\1\\. "),
        ]
        import re

        for pat, repl in escapes:
            string = re.sub(pat, repl, string, flags=re.MULTILINE)
        return string

    def _process(self, parentNode):
        """
        Processes the given parent node and its children to generate a string representation.

        Args:
            parentNode (Node): The parent node to process. It should have a 'children' attribute
                               which is a list of child nodes.

        Returns:
            str: The string representation of the processed nodes.

        The function uses a reducer to iterate over the child nodes of the parent node. For each
        node, it enhances the node, determines its type, and generates a replacement string based
        on the node type. Text nodes (node_type == 3) are either taken as-is if they are code or
        escaped. Element nodes (node_type == 1) are processed using a replacement function. The
        results are concatenated into a single string.
        """

        def reducer(output, node):
            """
            Reduces the given node to a string representation and appends it to the output.

            Args:
                output (str): The current accumulated output string.
                node (Node): The node to be processed and reduced.

            Returns:
                str: The updated output string with the node's string representation appended.
            """
            node = enhance_node(node, self.options)
            replacement = ""
            if node.node_type == 3:
                # Text
                replacement = (
                    node.node_value
                    if node.is_code
                    else self.escape(node.node_value)
                )
            elif node.node_type == 1:
                replacement = self._replacement_for_node(node)
            return _join(output, replacement)

        return functools.reduce(reducer, parentNode.children, "")

    def _post_process(self, output):
        """
        Post-processes the given output by appending additional content based on rules.

        This method iterates over the rules and applies the 'append' function of each rule
        (if it exists and is callable) to the output. The results of these 'append' functions
        are concatenated to the original output.

        Args:
            output (str): The initial output to be post-processed.

        Returns:
            str: The post-processed output with additional content appended based on the rules.
        """

        def do_append(rule_obj):
            """
            Appends content based on the provided rule object.

            This function checks if the rule object contains an "append" key and if the
            corresponding value is a callable function. If both conditions are met, it
            calls the function with the current options and returns the result.
            Otherwise, it returns an empty string.

            Args:
                rule_obj (dict): A dictionary that may contain an "append" key with a
                                 callable value.

            Returns:
                str: The result of the callable function if present, otherwise an empty string.
            """
            if "append" in rule_obj and callable(rule_obj["append"]):
                return rule_obj["append"](self.options)
            return ""

        nonlocal_output = [output]

        self.rules.forEach(
            lambda r, i: (
                nonlocal_output.__setitem__(
                    0, _join(nonlocal_output[0], do_append(r))
                )
                if do_append(r)
                else None
            )
        )
        return nonlocal_output[0]

        # Python 3 closure trick
        nonlocal_output = [output]
        self.rules.forEach(
            lambda r, i: self._append_references(r, nonlocal_output)
        )
        return nonlocal_output[0]

    def _append_references(self, rule_obj, nonlocal_output):
        """
        Appends references to the nonlocal output if the rule object contains an append function.

        Args:
            rule_obj (dict): A dictionary containing the rule object. It should have an "append" key with a callable value.
            nonlocal_output (list): A list where the first element is a string to which the appended references will be added.

        Returns:
            None
        """
        if "append" in rule_obj and callable(rule_obj["append"]):
            appended = rule_obj["append"](self.options)
            if appended:
                nonlocal_output[0] = _join(nonlocal_output[0], appended)

    def _replacement_for_node(self, node):
        """
        Generates the replacement string for a given node based on the applicable rule.

        Args:
            node (Node): The node to be processed.

        Returns:
            str: The replacement string for the node, including any leading or trailing whitespace.
        """
        rule = self.rules.forNode(node)
        content = self._process(node)
        whitespace = node.flanking_whitespace
        leading = whitespace["leading"]
        trailing = whitespace["trailing"]
        if leading or trailing:
            content = content.strip()
        return (
            leading
            + rule["replacement"](content, node, self.options)
            + trailing
        )


def _join(output, replacement):
    """
    Joins two strings with a calculated number of newlines between them.

    This function trims trailing newlines from the first string and leading
    newlines from the second string, then calculates the number of newlines
    needed to separate them. The maximum number of newlines inserted is two.

    Args:
        output (str): The first string to join.
        replacement (str): The second string to join.

    Returns:
        str: The joined string with appropriate newlines in between.
    """
    s1 = trim_trailing_newlines(output)
    s2 = trim_leading_newlines(replacement)
    # Calculate number of newlines needed to separate the strings
    nls = (len(output) - len(s1)) + (len(replacement) - len(s2))
    sep = "\n\n"[0:nls]  # max 2 newlines
    return s1 + sep + s2


def _can_convert(x):
    """
    Check if the input can be converted.

    This function determines if the given input `x` can be converted based on its type or attributes.

    Args:
        x: The input to check. It can be of any type.

    Returns:
        bool: True if the input can be converted, False otherwise.

    The function returns True if:
    - `x` is a string.
    - `x` has an attribute `node_type` and its value is one of [1, 9, 11] (representing Element, Document, or DocumentFragment).

    The function returns False if:
    - `x` is None.
    - `x` does not meet any of the above conditions.
    """
    if x is None:
        return False
    if isinstance(x, str):
        return True
    if hasattr(x, "node_type"):
        # 1 = Element, 9 = Document, 11 = DocumentFragment
        return x.node_type in [1, 9, 11]
    return False
