# Copyright 2024 EvickaStudio
#
# Licensed under the Apache License, Version 2.0 (the "License")
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


# Import necessary modules
import re
from html.parser import HTMLParser


# Define a class DiscordMarkdownConverter that inherits from HTMLParser
class DiscordMarkdownConverter(HTMLParser):
    def __init__(self):
        # Call the constructor of the parent class
        super().__init__()
        # Initialize an empty string for storing the result
        self.result = ""
        # Boolean flag to capture data
        self.capture_data = False
        # Store the URL when capturing data
        self.url = ""

    # Override handle_starttag method
    def handle_starttag(self, tag, attrs):
        if tag == "td" and ("class", "content") in attrs:
            # Set capture_data flag to True when <td class="content"> is encountered
            self.capture_data = True
        elif tag == "a" and self.capture_data:
            # Get the href attribute value from the dictionary of attributes
            href = next((v for k, v in attrs if k == "href"), "")
            # Append [ to the result
            self.result += "["
            # Store the href value in self.url
            self.url = href
        elif tag == "b" and self.capture_data:
            # Append ** to the result when encountering <b> tag while capturing data
            self.result += "**"

    # Override handle_endtag method
    def handle_endtag(self, tag):
        if tag == "td" and self.capture_data:
            # Reset capture_data flag to False when </td> is encountered
            self.capture_data = False
        elif tag == "a" and self.capture_data and self.url:
            # Append ]({self.url}) to the result when encountering </a> tag while capturing data
            self.result += f"]({self.url})"
            # Reset self.url value
            self.url = ""
        elif tag == "b" and self.capture_data:
            # Append ** to the result when encountering </b> tag while capturing data
            self.result += "**"

    # Override handle_data method
    def handle_data(self, data):
        if self.capture_data:
            # Append the stripped data to the result when capturing data
            self.result += data.strip()


# Define a function html_to_discord_md that takes an HTML string as input
def html_to_discord_md(html):
    # Create an instance of DiscordMarkdownConverter
    converter = DiscordMarkdownConverter()
    # Feed the HTML string to the converter
    converter.feed(html)
    # Return the result after parsing the HTML string
    return converter.result
