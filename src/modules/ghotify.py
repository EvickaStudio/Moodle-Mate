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

# gotify.py

import logging

import requests


class Gotify:
    """Gotify notification module."""

    def __init__(self, url: str, token: str) -> None:
        """Initialize with Gotify instance URL and token."""
        self.url = url
        self.token = token

    def send_notification(self, title: str, message: str) -> bool:
        """Send a notification to Gotify.

        Sends a notification with the given title and message to the configured Gotify instance.
        Returns True if the notification was sent successfully, False otherwise.
        """
        """Send notification to Gotify."""
        headers = {"X-Gotify-Key": self.token}
        data = {"title": title, "message": message}

        try:
            response = requests.post(
                f"{self.url}/message", headers=headers, json=data
            )
            if response.status_code == 200:
                logging.info("Notification sent to Gotify")
                return True
            else:
                logging.error(
                    "Error sending to Gotify, status %s", response.status_code
                )
                return False
        except requests.RequestException as e:
            logging.error("Error sending Gotify notification: %s", e)
            return False
