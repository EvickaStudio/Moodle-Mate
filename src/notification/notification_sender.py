import logging

from src.modules.discord import Discord
from src.modules.pushbullet import Pushbullet
from src.moodle.moodle_notification_handler import MoodleNotificationHandler
from src.utils.handle_exceptions import handle_exceptions
from src.utils.load_config import Config


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
    def __init__(self, config: Config, bot_name: str, thumbnail: str) -> None:
        self.pushbullet_key = config.get_config("moodle", "pushbulletkey")
        self.webhook_url = config.get_config("moodle", "webhookUrl")
        self.pushbullet_state = int(
            config.get_config("moodle", "pushbulletState")
        )
        self.webhook_state = int(config.get_config("moodle", "webhookState"))
        self.model = config.get_config("moodle", "model")
        self.bot_name = bot_name
        self.thumbnail = thumbnail
        self.webhook_discord = Discord(
            self.webhook_url, self.bot_name, self.thumbnail
        )
        self.moodle_handler = MoodleNotificationHandler(config)

    # userifrom defauls to null, if you want to use your own user id, use the parameter useridfrom
    @handle_exceptions
    def send(
        self, subject: str, text: str, summary: str, useridfrom: int = None
    ) -> None:
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
                if useridfrom is not None:
                    useridfrom_info = self.moodle_handler.user_id_from(
                        useridfrom
                    )
                    fullname = useridfrom_info["fullname"]
                    profile_url = useridfrom_info["profileimageurl"]
                else:
                    useridfrom_info = "69"
                    fullname = "EvickaStudio"
                    profile_url = (
                        "https://avatars.githubusercontent.com/u/68477970"
                    )

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
