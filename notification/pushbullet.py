"""
pushbullet module for sending push notifications

Author: EvickaStudio
Data: 07.10.2023
Github: @EvickaStudio
"""

import logging

import requests


class Pushbullet:
    def __init__(self, api_key: str):
        """
        Initializes a pushbullet instance with the provided API key.

        Args:
            api_key (str): The API key for pushbullet.

        Returns:
            None
        """
        self.api_key = api_key
        self.url = "https://api.pushbullet.com/v2/pushes"

    def send_notification(self, title: str, body: str) -> bool:
        """
        Sends a push notification with the provided title and body.

        Args:
            title (str): The title of the push notification.
            body (str): The body of the push notification.

        Returns:
            bool: True if the push notification was sent successfully, False otherwise.
        """
        headers = {"Access-Token": self.api_key}
        data = {"type": "note", "title": title, "body": body}
        try:
            response = requests.post(
                url=self.url, headers=headers, json=data, timeout=5
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logging.error(
                f"Error sending pushbullet notification: {e}. Response status code: {response.status_code}, response text: {response.text}"
            )
            return False
