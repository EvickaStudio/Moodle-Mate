import html.entities
import html.parser


class Node:
    """
    A class representing a node in an HTML-like tree structure.

    Attributes:
        node_name (str): The name of the node, converted to uppercase.
        node_type (int): The type of the node (1 = Element, 3 = Text, 8 = Comment, etc.).
        parent (Node, optional): The parent node. Defaults to None.
        children (list): A list of child nodes.
        attributes (dict): A dictionary of attributes for the node.
        data (str): The data contained in the node, used for text nodes.
        is_self_closing (bool): Indicates if the node is self-closing.

    Properties:
        first_child (Node): The first child node, or None if there are no children.
        last_child (Node): The last child node, or None if there are no children.
        next_sibling (Node): The next sibling node, or None if there is no next sibling.
        previous_sibling (Node): The previous sibling node, or None if there is no previous sibling.
        node_value (str): The data contained in the node.
        is_element (bool): Indicates if the node is an element node.

    Methods:
        append_child(child): Appends a child node to the current node.
        remove_self(): Removes the current node from its parent.
        text_content(): Returns the text content of the node and its children.
        get_attribute(attr): Returns the value of the specified attribute.
        set_attribute(attr, value): Sets the value of the specified attribute.
        index_in_parent(node): Returns the index of the node in its parent's children list.
    """

    def __init__(self, node_name, node_type, parent=None):
        """
        Initializes a new instance of the HTMLParser class.

        Args:
            node_name (str): The name of the node.
            node_type (int): The type of the node (1 = Element, 3 = Text, 8 = Comment, etc.).
            parent (HTMLParser, optional): The parent node. Defaults to None.

        Attributes:
            node_name (str): The name of the node in uppercase.
            node_type (int): The type of the node.
            parent (HTMLParser): The parent node.
            children (list): A list of child nodes.
            attributes (dict): A dictionary of node attributes.
            data (str): The data for text nodes.
            is_self_closing (bool): Indicates if the node is self-closing.
        """
        self.node_name = node_name.upper()
        self.node_type = node_type  # 1 = Element, 3 = Text, 8 = Comment, etc.
        self.parent = parent
        self.children = []
        self.attributes = {}
        self.data = ""  # for text nodes
        self.is_self_closing = False

    @property
    def first_child(self):
        """
        Returns the first child of the current node.

        Returns:
            The first child node if it exists, otherwise None.
        """
        return self.children[0] if self.children else None

    @property
    def last_child(self):
        """
        Returns the last child element of the current node.

        Returns:
            The last child element if there are any children, otherwise None.
        """
        return self.children[-1] if self.children else None

    @property
    def next_sibling(self):
        """
        Returns the next sibling of the current node.

        If the current node has no parent or is the last child, returns None.

        Returns:
            The next sibling node if it exists, otherwise None.
        """
        if not self.parent:
            return None
        siblings = self.parent.children
        idx = siblings.index(self)
        return siblings[idx + 1] if idx + 1 < len(siblings) else None

    @property
    def previous_sibling(self):
        """
        Returns the previous sibling of the current node.

        If the current node has no parent or is the first child, returns None.

        Returns:
            The previous sibling node if it exists, otherwise None.
        """
        if not self.parent:
            return None
        siblings = self.parent.children
        idx = siblings.index(self)
        return siblings[idx - 1] if idx - 1 >= 0 else None

    @property
    def node_value(self):
        """
        Returns the value of the current node.

        Returns:
            str: The data contained in the node.
        """
        return self.data

    def append_child(self, child):
        """
        Appends a child node to the current node.

        Args:
            child: The child node to be appended. The child node's parent attribute
                   will be set to the current node.

        Returns:
            None
        """
        child.parent = self
        self.children.append(child)

    def remove_self(self):
        """
        Removes the current node from its parent's children list and sets its parent to None.

        This method should be called when the current node needs to be detached from its parent.
        """
        if self.parent:
            self.parent.children.remove(self)
        self.parent = None

    def text_content(self):
        """
        Returns the text content of the node.

        If the node type is text (3) or CDATA (4), it returns the node's data.
        Otherwise, it recursively concatenates the text content of all child nodes.

        Returns:
            str: The text content of the node.
        """
        if self.node_type in [3, 4]:  # text or cdata
            return self.data
        return "".join([c.text_content() for c in self.children])

    def get_attribute(self, attr):
        """
        Retrieve the value of a specified attribute from the element's attributes.

        Args:
            attr (str): The name of the attribute to retrieve.

        Returns:
            str or None: The value of the specified attribute if it exists,
                         otherwise None.
        """
        return self.attributes.get(attr, None)

    def set_attribute(self, attr, value):
        """
        Set the value of a specified attribute.

        Args:
            attr (str): The name of the attribute to set.
            value (str): The value to assign to the attribute.
        """
        self.attributes[attr] = value

    def index_in_parent(self, node):
        """
        Returns the index of the given node within the children of the current node.

        Args:
            node: The node whose index is to be found.

        Returns:
            int: The index of the node within the children list. If the node is not found, returns 0.
        """
        if not self.children:
            return 0
        return self.children.index(node)

    @property
    def is_element(self):
        """
        Check if the node is an element node.

        Returns:
            bool: True if the node is an element node (node_type == 1), False otherwise.
        """
        return self.node_type == 1


class TurndownHTMLParser(html.parser.HTMLParser):
    """
    A custom HTML parser that converts HTML into a tree of Node objects.

    Attributes:
        root (Node): The root node of the document tree.
        current_node (Node): The current node being processed.

    Methods:
        handle_starttag(tag, attrs):
            Handles the start of an HTML tag.

        handle_endtag(tag):
            Handles the end of an HTML tag.

        handle_startendtag(tag, attrs):
            Handles self-closing HTML tags.

        handle_data(data):
            Handles text data within HTML tags.

        handle_entityref(name):
            Handles named character references (e.g., &amp;).

        handle_charref(name):
            Handles numeric character references (e.g., &#123;).
    """

    def __init__(self):
        """
        Initializes the HTMLParser instance.

        This constructor sets up the HTMLParser with character reference conversion
        disabled. It also initializes the root node of the document tree and sets
        the current node to the root.

        Attributes:
            root (Node): The root node of the document tree.
            current_node (Node): The node currently being processed.
        """
        super().__init__(convert_charrefs=False)
        self.root = Node("document", 1)
        self.current_node = self.root

    def handle_starttag(self, tag, attrs):
        """
        Handles the start tag of an HTML element.

        This method is called when an opening tag is encountered in the HTML
        content being parsed. It creates a new Node object for the tag, sets
        its attributes, and appends it to the current node in the parse tree.
        If the tag is self-closing (e.g., <br>, <img>, <hr>, <meta>, <input>,
        <link>), it marks the node as self-closing. Otherwise, it updates the
        current node to the newly created node.

        Args:
            tag (str): The name of the HTML tag.
            attrs (list of tuple): A list of (attribute, value) tuples representing
                                   the attributes of the tag.
        """
        node = Node(tag, 1, parent=self.current_node)
        for k, v in attrs:
            node.set_attribute(k, v)
        self.current_node.append_child(node)
        if tag in ["br", "img", "hr", "meta", "input", "link"]:
            node.is_self_closing = True
        else:
            self.current_node = node

    def handle_endtag(self, tag):
        """
        Handle the end tag of an HTML element.

        This method is called when an end tag (e.g., </div>) is encountered in the HTML.
        It traverses up the node tree to find the corresponding start tag node and updates
        the current node to its parent.

        Args:
            tag (str): The name of the end tag encountered.
        """
        temp = self.current_node
        while temp is not None and temp.node_name.lower() != tag.lower():
            temp = temp.parent
        if temp is not None:
            self.current_node = temp.parent if temp.parent else temp

    def handle_startendtag(self, tag, attrs):
        """
        Handle self-closing HTML tags.

        This method is called when a self-closing tag is encountered in the HTML
        being parsed. It creates a new Node object representing the tag, sets its
        attributes, and appends it to the current node in the parse tree.

        Args:
            tag (str): The name of the HTML tag.
            attrs (list of tuple): A list of (attribute, value) pairs representing
                the attributes of the tag.
        """
        node = Node(tag, 1, parent=self.current_node)
        node.is_self_closing = True
        for k, v in attrs:
            node.set_attribute(k, v)
        self.current_node.append_child(node)

    def handle_data(self, data):
        """
        Handles text data within an HTML element.

        This method creates a text node with the given data and appends it
        to the current node in the HTML tree.

        Args:
            data (str): The text data to be handled and added to the current node.
        """
        text_node = Node("#text", 3, parent=self.current_node)
        text_node.data = data
        self.current_node.append_child(text_node)

    def handle_entityref(self, name):
        """
        Handle HTML entity references.

        This method is called to process HTML entity references (e.g., &amp;).
        It converts the entity reference to its corresponding character and
        appends it as a text node to the current node.

        Args:
            name (str): The name of the entity reference (e.g., 'amp' for &amp;).

        """
        text_node = Node("#text", 3, parent=self.current_node)
        c = html.entities.html5.get(name, f"&{name};")
        text_node.data = c
        self.current_node.append_child(text_node)

    def handle_charref(self, name):
        """
        Handle character references in HTML.

        This method processes character references in the form of `&#123;` or `&#x7B;`
        and converts them to their corresponding character. If the character reference
        is invalid, it will be preserved as is.

        Args:
            name (str): The character reference name. It can be in decimal (e.g., '123')
                        or hexadecimal (e.g., 'x7B') format.

        Raises:
            ValueError: If the character reference cannot be converted to an integer.

        """
        text_node = Node("#text", 3, parent=self.current_node)
        try:
            if name.startswith("x"):
                codepoint = int(name[1:], 16)
            else:
                codepoint = int(name)
            text_node.data = chr(codepoint)
        except ValueError:
            text_node.data = f"&#{name};"
        self.current_node.append_child(text_node)


def parse_from_string(html):
    """
    Parses an HTML string and returns the root of the parsed structure.

    Args:
        html (str): The HTML string to be parsed.

    Returns:
        Element: The root element of the parsed HTML structure.
    """
    parser = TurndownHTMLParser()
    parser.feed(html)
    parser.close()
    return parser.root
