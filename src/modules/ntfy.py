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
Helper class for sending notifications.
"""

import logging

from requests.exceptions import RequestException

from src.utils.request_manager import request_manager

logger = logging.getLogger(__name__)


class Ntfy:
    """
    Class for sending notifications.

    Example:

    >>> from notification.ntfy import Ntfy

    >>> server_ip = "http://11.11.11.11/"
    # >>> topic = "TOPIC"
    >>> notification = Ntfy()
    >>> notification.server_url = server_ip
    >>> notification.sendNTFY(topic, title="New Notification", message="HELLO WORLD", priority="urgent")
    """

    def __init__(self):
        """
        Initialize the Ntfy class.
        """
        self.server_url = None
        self.topic = None
        self.session = request_manager.session

    def send_notification(self, topic, title, message, priority="urgent") -> bool:
        """
        Send a notification.

        Args:
            topic (str): The topic of the notification, can be changed to send to different topics on the same server.
            title (str): The title of the notification.
            message (str): The message of the notification.
            priority (str, optional): The priority of the notification. Defaults to "urgent".
        """
        url = self.server_url + topic
        request_manager.update_headers(
            {
                "Title": title,
                "Priority": priority,
                "Tags": "email",
            }
        )
        try:
            response = self.session.post(url, data=message)
            response.raise_for_status()  # Raise an exception if the request was not successful
            return True
        except RequestException as e:
            logging.error(f"Error sending ntfy notification: {e}")
            return False
