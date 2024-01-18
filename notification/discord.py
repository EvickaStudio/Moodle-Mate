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

"""
Send notifications to Discord via webhooks.

Author: EvickaStudio
Date: 30.11.2023
Github: @EvickaStudio
"""

import datetime
import logging
import random

import requests


class Discord:
    """
    Discord client class to send notifications via webhooks.

    This class allows sending rich embed notifications or simple text
    messages to a Discord channel via a webhook URL.

    Methods:

        random_color() -> str:
            Generate a random hex color code to use for embeds.

        __call__(...) -> bool:
            Send a notification to the configured webhook URL. Supports
            both rich embed and simple text message formats.

    """

    """
    Class representing a Discord webhook client.

    Methods:
        random_color() -> str: Generate a random color.
        __call__(...) -> bool: Send a notification to Discord.
    """

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    @staticmethod
    def random_color() -> str:
        return "#{:02x}{:02x}{:02x}".format(
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )

    def __call__(
        self,
        subject: str,
        text: str,
        *,
        summary: str = "",
        fullname: str = "",
        picture_url: str = "",
        embed: bool = True,
    ):
        try:
            if not embed:
                return self.send_simple(subject, text)

            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            embed_json = {
                "title": subject,
                "description": text,
                "color": int(self.random_color()[1:], 16),
                "fields": [],
                "author": {},
                "footer": {},
            }

            if summary:
                embed_json["fields"].append({"name": "TL;DR", "value": summary})

            if fullname and picture_url:
                embed_json["author"]["name"] = fullname
                embed_json["author"]["icon_url"] = picture_url

            embed_json["footer"]["text"] = f"{current_time} - Moodle-Mate"
            embed_json["footer"][
                "icon_url"
            ] = "https://avatars.githubusercontent.com/u/68477970?v=4"

            payload = {"embeds": [embed_json]}
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()

            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Error sending Discord notification: {e}")
            return False

    def send_simple(self, subject: str, text: str) -> None:
        try:
            payload = {"content": f"<strong>{subject}</strong>\n{text}"}
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Error sending Discord notification: {e}")
            return False
