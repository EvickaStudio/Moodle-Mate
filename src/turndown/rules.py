# flake8: noqa: E501


class Rules:
    """
    The Rules class is responsible for managing and applying rules based on given configuration options. It supports adding, keeping, and removing rules, as well as determining the appropriate rule for a given node.


    Methods:
        __init__(options):

        add(key, rule):

        keep(filter_func):

        remove(filter_func):

        forNode(node):

        forEach(fn):

        _find_rule(rules_list, node):
    """

    def __init__(self, options):
        """
        Initialize the Rules class with the given options.

        Args:
            options (dict): A dictionary containing configuration options for the rules.
                - "blankReplacement" (str): The replacement string for blank rules.
                - "keepReplacement" (str): The replacement string for rules to keep.
                - "defaultReplacement" (str): The replacement string for default rules.
                - "rules" (dict): A dictionary of custom rules where keys are rule names and values are rule definitions.

        Attributes:
            options (dict): The configuration options for the rules.
            _keep (list): A list to store rules to keep.
            _remove (list): A list to store rules to remove.
            blankRule (dict): A dictionary containing the replacement string for blank rules.
            keepReplacement (str): The replacement string for rules to keep.
            defaultRule (dict): A dictionary containing the replacement string for default rules.
            array (list): A list to store custom rule definitions.
        """
        self.options = options
        self._keep = []
        self._remove = []

        self.blankRule = {"replacement": options["blankReplacement"]}
        self.keepReplacement = options["keepReplacement"]
        self.defaultRule = {"replacement": options["defaultReplacement"]}
        self.array = []
        for k, v in options["rules"].items():
            self.array.append(v)

    def add(self, key, rule):
        """
        Add a rule to the beginning of the array.

        Parameters:
        key (str): The key associated with the rule.
        rule (object): The rule to be added to the array.
        """
        self.array.insert(0, rule)

    def keep(self, filter_func):
        """
        Adds a filter function to the list of keep rules.

        Args:
            filter_func (function): A function that takes an element as input and
                                    returns True if the element should be kept,
                                    False otherwise.
        """
        self._keep.insert(
            0, {"filter": filter_func, "replacement": self.keepReplacement}
        )

    def remove(self, filter_func):
        """
        Adds a removal rule to the list of rules.

        This method inserts a new rule at the beginning of the `_remove` list. The rule consists of a filter function and a replacement function that returns an empty string.

        Args:
            filter_func (function): A function that determines whether an element should be removed. It should take an element as an argument and return a boolean.
        """
        self._remove.insert(
            0, {"filter": filter_func, "replacement": lambda c, n, o: ""}
        )

    def forNode(self, node):
        """
        Determines the appropriate rule for a given node.

        This method first checks if the node is blank and returns the blankRule if true.
        If the node is not blank, it searches for a matching rule in the following order:
        1. self.array
        2. self._keep
        3. self._remove

        If a matching rule is found in any of these collections, it is returned.
        Otherwise, the defaultRule is returned.

        Args:
            node: The node for which the rule needs to be determined.

        Returns:
            The rule that matches the node, or the defaultRule if no match is found.
        """
        if getattr(node, "is_blank", False):
            return self.blankRule

        # Search for a matching rule
        rule = (
            self._find_rule(self.array, node)
            or self._find_rule(self._keep, node)
            or self._find_rule(self._remove, node)
        )
        return rule if rule else self.defaultRule

    def forEach(self, fn):
        """
        Applies a given function to each element in the array.

        Args:
            fn (function): A function that takes two arguments, the current element
                           and its index, and performs an operation on them.
        """
        for i, rule in enumerate(self.array):
            fn(rule, i)

    def _find_rule(self, rules_list, node):
        """
        Find and return the first rule object from the given list that matches the specified node.

        Args:
            rules_list (list): A list of rule objects, where each rule object is a dictionary
                               containing a "filter" key.
            node (object): The node to be matched against the filter of each rule object.

        Returns:
            dict or None: The first rule object that matches the node, or None if no match is found.
        """
        for rule_obj in rules_list:
            if _filter_value(rule_obj["filter"], node, self.options):
                return rule_obj
        return None


def _filter_value(filter_item, node, options):
    """
    Determines if a node matches a given filter.

    Args:
        filter_item (Union[str, list, callable]): The filter to apply. This can be:
            - A string: The node's name must match this string (case-insensitive).
            - A list: The node's name must be one of the strings in this list (case-insensitive).
            - A callable: A function that takes the node and options as arguments and returns a boolean.
        node (Node): The node to be checked.
        options (dict): Additional options that may be used by the callable filter.

    Returns:
        bool: True if the node matches the filter, False otherwise.

    Raises:
        TypeError: If the filter_item is not a string, list, or callable.
    """
    if isinstance(filter_item, str):
        return filter_item == node.node_name.lower()
    elif isinstance(filter_item, list):
        return node.node_name.lower() in filter_item
    elif callable(filter_item):
        return filter_item(node, options)
    else:
        raise TypeError("Filter must be string, list, or callable.")
