"""
pushbullet module for sending push notifications

Author: EvickaStudio
Data: 07.10.2023
Github: @EvickaStudio
"""

import json
import logging

import requests


class Pushbullet:
    def __init__(self, api_key):
        """
        Initializes a pushbullet instance with the provided API key.

        Args:
            api_key (str): The API key for pushbullet.

        Returns:
            None
        """
        self.api_key = api_key
        self.url = "https://api.pushbullet.com/v2/pushes"
        self.headers = {
            "Access-Token": self.api_key,
            "Content-Type": "application/json",
        }

    def send_notification(self, title, body) -> bool:
        """
        Sends a push notification with the provided title and body.

        Args:
            title (str): The title of the push notification.
            body (str): The body of the push notification.

        Returns:
            bool: True if the push notification was sent successfully, False otherwise.
        """
        try:
            data = {"type": "note", "title": title, "body": body}
            r = requests.post(self.url, headers=self.headers, data=json.dumps(data))
            r.raise_for_status()  # Raise an exception if the request was not successful
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Error sending pushbullet notification: {e}")
            return False
