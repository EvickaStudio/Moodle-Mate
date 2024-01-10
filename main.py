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

# from notification.notification_sender import NotificationSender
from notification.notification_summarizer import NotificationSummarizer
from notification.pushbullet import Pushbullet
from utils.handle_exceptions import handle_exceptions
from utils.main_loop import main_loop
from utils.screen import clear_screen, logo
from utils.setup_logging import setup_logging

# Constants
sleep_duration_seconds: int = 60
max_retries: int = 3


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

                useridfrom_info = moodle_handler.user_id_from(useridfrom)
                fullname = useridfrom_info["fullname"]
                profile_url = useridfrom_info["profileimageurl"]
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


# This is the main loop of the program. We'll keep looping until something breaks
if __name__ == "__main__":
    clear_screen()
    print(logo)
    setup_logging()

    # Initialize Config object
    config = Config("config.ini")

    # Initialize other classes with the Config object
    moodle_handler = MoodleNotificationHandler(config)
    summarizer = NotificationSummarizer(config)
    sender = NotificationSender(config)
    summary = int(
        config.get_config("moodle", "summary")
    )  # 1 = summary, 0 = no summary
    if summary == "" or summary is None:
        summary = 0
    fakeopen = int(
        config.get_config("moodle", "fakeopen")
    )  # 1 = fake open, 0 = openai when selected
    if fakeopen == "" or fakeopen is None:
        fakeopen = 0

    main_loop(
        moodle_handler,
        summarizer,
        sender,
        summary,
        sleep_duration_seconds,
        max_retries,
    )
