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

import pytest

from filters.message_filter import (extract_and_format_for_discord,
                                    parse_html_to_text, remove_last_line,
                                    remove_whitespace)


def test_parse_html_to_text():
    html = "<html>...</html>"
    expected_text = "..."
    assert parse_html_to_text(html) == expected_text


def test_parse_html_to_text_empty_html():
    html = ""
    with pytest.raises(ValueError):
        parse_html_to_text(html)


def test_remove_whitespace():
    text = """Hello   
    World"""
    expected_cleaned_text = "Hello"
    assert remove_whitespace(text) == expected_cleaned_text


def test_remove_last_line():
    text = "Line 1\nLine 2\nLine 3"
    expected_text_without_last_line = "Line 1\nLine 2"
    print(remove_last_line(text))
    assert remove_last_line(text) == expected_text_without_last_line


# def test_extract_and_format_for_discord():
#     html = "<html><td class='content'><p>Paragraph 1</p><p>Paragraph 2</p></td></html>"
#     expected_formatted_text = "Paragraph 1\nParagraph 2"
#     assert extract_and_format_for_discord(html) == expected_formatted_text


# def test_extract_and_format_for_discord_empty_html():
#     html = ""
#     with pytest.raises(ValueError):
#         extract_and_format_for_discord(html)
