from html.parser import HTMLParser


class DiscordMarkdownConverter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []
        self.href = None
        self.tag_map = {
            "b": "**",
            "strong": "**",
            "i": "*",
            "em": "*",
            "a": "[",
            "pre": "```",
            "code": "```",
            "h1": "# ",
            "h2": "## ",
            "h3": "### ",
            "h4": "#### ",
            "h5": "##### ",
            "h6": "###### ",
            "p": "\n\n",
            "br": "\n",
        }

    def handle_starttag(self, tag, attrs):
        if tag in self.tag_map:
            self.result.append(self.tag_map[tag])
        if tag == "a":
            self.href = dict(attrs).get("href", "")

    def handle_endtag(self, tag):
        if tag in self.tag_map and tag != "a":
            self.result.append(self.tag_map[tag])
        if tag == "a" and self.href:
            self.result.append(f"]({self.href})")
            self.href = None

    def handle_data(self, data):
        self.result.append(data)

    def get_result(self):
        return "".join(self.result).strip()


def html_to_discord_md(html):
    converter = DiscordMarkdownConverter()
    converter.feed(html)
    return converter.get_result()
