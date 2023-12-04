"""
Send notifications to Discord via webhooks.

Author: EvickaStudio
Data: 30.11.2023
Github: @EvickaStudio
"""

import datetime
import logging
import random

import requests


class Discord:
    """
    discord(webhook_url: str) -> None
        Initializes a Discord object with the provided webhook URL.

        Args:
            webhook_url (str): The URL of the Discord webhook.

        Returns:
            None

    random_color() -> str
        Generates a random color in hexadecimal format.

        Returns:
            str: The randomly generated color.

    send(subject: str, text: str, summary: str, fullname: str, picture_url: str) -> bool
        Sends a message to Discord with the specified subject, text, summary, fullname, and picture URL.

        Args:
            subject (str): The subject of the message.
            text (str): The text content of the message.
            summary (str): A short summary of the message.
            fullname (str): The full name of the sender.
            picture_url (str): The URL of the sender's profile picture.

        Returns:
            bool: True if the message was sent successfully, False otherwise.
    """

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def random_color(self) -> str:
        return "#{:02x}{:02x}{:02x}".format(
            random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
        )

    def send_notification(
        self, subject: str, text: str, summary: str, fullname: str, picture_url: str
    ):
        # Get current time for the timestamp in the footer
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            embed = {
                "title": subject,
                "description": text,
                "color": int(self.random_color()[1:], 16),
                "fields": [
                    {
                        "name": "TL;DR",  # Too long; didn't read
                        "value": summary,  # GPT-3 generated summary
                    }
                ],
                "author": {
                    "name": fullname,  # Full name of the sender
                    "icon_url": picture_url,  # Profile picture of the sender
                },
                "footer": {
                    "text": f"{current_time} - Moodle-Mate",  # Current time and the name of the project
                    "icon_url": "https://avatars.githubusercontent.com/u/68477970?v=4",  # My profile picture <3
                },
            }
            data = {"embeds": [embed]}
            return self._post(data)
        except requests.exceptions.RequestException as e:
            logging.error(f"Error sending Discord notification: {e}")
            return False

    # Simple text message sending
    def send_simple(self, subject: str, text: str) -> None:
        try:
            data = {"content": f"**{subject}**\n{text}"}
            return self._post(data)
        except requests.exceptions.RequestException as e:
            logging.error(f"Error sending Discord notification: {e}")
            return False

    def _post(self, data: dict):
        try:
            r = requests.post(self.webhook_url, json=data)
            r.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Error sending Discord notification: {e}")
            return False
