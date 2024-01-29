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

import logging

from moodle.load_config import Config
from moodle.moodle_notification_handler import MoodleNotificationHandler
from notification.discord import Discord
from notification.pushbullet import Pushbullet
from utils.handle_exceptions import handle_exceptions


class NotificationSender:
    """
    The NotificationSender class handles the sending of notifications to different platforms.

    Args:
        api_config (dict): The API configuration containing the Pushbullet API key and Discord webhook URL.

    Attributes:
        pushbullet_key (str): The Pushbullet API key.
        webhook_url (str): The Discord webhook URL.
        pushbullet_state (int): The state of Pushbullet notifications.
        webhook_state (int): The state of Discord notifications.
    """

    @handle_exceptions
    def __init__(self, config: Config) -> None:
        self.pushbullet_key = config.get_config("moodle", "pushbulletkey")
        self.webhook_url = config.get_config("moodle", "webhookUrl")
        self.pushbullet_state = int(
            config.get_config("moodle", "pushbulletState")
        )
        self.webhook_state = int(config.get_config("moodle", "webhookState"))
        self.model = config.get_config("moodle", "model")
        self.webhook_discord = Discord(self.webhook_url)
        self.moodle_handler = MoodleNotificationHandler(config)

    @handle_exceptions
    def send(self, subject: str, text: str, summary: str, useridfrom: int):
        """
        Sends a notification to Pushbullet and Discord.

        Args:
            subject (str): The subject of the notification.
            text (str): The body of the notification.
            summary (str): A summary of the notification.
            useridfrom (int): The user ID of the sender.

        Raises:
            Exception: If the notification fails to send.
        """
        try:
            # If State is set to 1, send notifications
            if self.pushbullet_state == 1:
                logging.info("Sending notification to Pushbullet")
                pb = Pushbullet(self.pushbullet_key)
                pb.send_notification(subject, summary)

            if self.webhook_state == 1:
                logging.info("Sending notification to Discord")

                useridfrom_info = self.moodle_handler.user_id_from(useridfrom)
                fullname = useridfrom_info["fullname"]
                profile_url = useridfrom_info["profileimageurl"]
                data = {
                    "username": fullname,
                    "avatar_url": profile_url,
                    "embeds": [
                        {
                            "title": subject,
                            "description": text,
                            "color": self.webhook_discord.random_color(),
                        }
                    ],
                }

                # print(data) # debug
                self.webhook_discord(
                    subject=subject,
                    text=text,
                    summary=summary,
                    fullname=fullname,
                    picture_url=profile_url,
                )

            else:
                logging.info("No notification service selected")

        except Exception as e:
            logging.exception("Failed to send notification")
            raise e

    @handle_exceptions
    def send_simple(self, subject: str, text: str) -> None:
        try:
            logging.info("Sending notification to Discord")
            self.webhook_discord.send_simple(subject, text)
        except Exception as e:
            logging.exception("Failed to send notification")
            raise e
