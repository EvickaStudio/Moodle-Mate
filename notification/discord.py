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
    Class representing a Discord webhook client.

    Methods:
        random_color() -> str: Generate a random color.
        __call__(...) -> bool: Send a notification to Discord.
    """

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def random_color(self) -> str:
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
        if not embed:
            return self.send_simple(subject, text)

        try:
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
