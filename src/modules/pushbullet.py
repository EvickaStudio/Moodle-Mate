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
