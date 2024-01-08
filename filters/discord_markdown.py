# Copyright 2024 EvickaStudio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
from html.parser import HTMLParser


class DiscordMarkdownConverter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = ""
        self.capture_data = False
        self.url = ""

    def handle_starttag(self, tag, attrs):
        if tag == "td" and ("class", "content") in attrs:
            self.capture_data = True
        elif tag == "a" and self.capture_data:
            href = next((v for k, v in attrs if k == "href"), "")
            self.result += "["
            self.url = href
        elif tag == "b" and self.capture_data:
            self.result += "**"

    def handle_endtag(self, tag):
        if tag == "td" and self.capture_data:
            self.capture_data = False
        elif tag == "a" and self.capture_data and self.url:
            self.result += f"]({self.url})"
            self.url = ""
        elif tag == "b" and self.capture_data:
            self.result += "**"

    def handle_data(self, data):
        if self.capture_data:
            self.result += data.strip()


def html_to_discord_md(html):
    converter = DiscordMarkdownConverter()
    converter.feed(html)
    return converter.result
