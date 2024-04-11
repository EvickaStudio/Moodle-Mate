from html.parser import HTMLParser


class DiscordMarkdownConverter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = ""
        self.link_text = ""  # Initialize link_text
        self.href = ""  # Initialize href

    def handle_starttag(self, tag, attrs):
        if tag in ["b", "strong"]:
            self.result += "**"
        elif tag in ["i", "em"]:
            self.result += "*"
        elif tag == "a":
            self.href = next((v for k, v in attrs if k == "href"), "")
            self.link_text = ""  # Reset link_text for each new link
        elif tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            self.result += "#" * int(tag[1]) + " "  # Adjust for heading levels
        elif tag == "p":
            self.result += "\n"  # Add paragraph breaks
        elif tag in ["pre", "code"]:
            self.result += "```"

    def handle_endtag(self, tag):
        if tag in ["b", "strong"]:
            self.result += "**"
        elif tag in ["i", "em"]:
            self.result += "*"
        elif tag in ["pre", "code"]:
            self.result += "```"
        elif tag == "br":
            self.result += "\n"

    def handle_data(self, data):
        if self.lasttag == "a":
            self.link_text += data.strip()  # Build link text
        elif self.lasttag == "span" and data.strip() == "MH":
            # Ignore "MH" inside "span" tags
            pass
        elif self.lasttag != "div":
            self.result += data.strip()


def html_to_discord_md(html):
    converter = DiscordMarkdownConverter()
    converter.feed(html)
    return converter.result
