"""
Helper class for sending notifications.
"""

import requests


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

    def sendNTFY(self, topic, title, message, priority="urgent"):
        """
        Send a notification.

        Args:
            topic (str): The topic of the notification, can be changed to send to different topics on the same server.
            title (str): The title of the notification.
            message (str): The message of the notification.
            priority (str, optional): The priority of the notification. Defaults to "urgent".
        """
        url = self.server_url + topic
        headers = {
            "Title": title,
            "Priority": priority,
            "Tags": "email",
        }
        try:
            response = requests.post(url, data=message, headers=headers)
            response.raise_for_status()  # Raise an exception if the request was not successful
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while sending the notification: {e}")
