import logging
import time
import traceback

from filters.message_filter import parse_html_to_text
from gpt.openai_chat import GPT
from moodle.load_config import Config
from moodle.moodle_notification_handler import MoodleNotificationHandler
from notification.discord import Discord
from notification.pushbullet import Pushbullet
from utils.handle_exceptions import handle_exceptions
from utils.setup_logging import setup_logging
from utils.logo import logo


class NotificationSummarizer:
    """
    A class that summarizes text using GPT-3 API.

    Attributes:
    api_key (str): The API key for GPT-3 API.
    system_message (str): The system message for the Moodle platform.

    Methods:
    summarize(text): Summarizes the given text using GPT-3 API.
    """

    @handle_exceptions
    def __init__(self, config: Config):
        self.api_key = config.get_config("moodle", "openaikey")
        self.system_message = config.get_config("moodle", "systemmessage")

    @handle_exceptions
    def summarize(self, text, configModel):
        try:
            # Summarize the text using GPT-3 and return the result
            ai = GPT()
            ai.apiKey = self.api_key
            return ai.chat_completion(configModel, self.system_message, text)
        except Exception as e:
            logging.exception(f"Failed to summarize with {configModel}")
            return None


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
    def __init__(self, config: Config):
        self.pushbullet_key = config.get_config("moodle", "pushbulletkey")
        self.webhook_url = config.get_config("moodle", "webhookUrl")
        self.pushbullet_state = int(config.get_config("moodle", "pushbulletState"))
        self.webhook_state = int(config.get_config("moodle", "webhookState"))
        self.model = config.get_config("moodle", "model")

    @handle_exceptions
    def send(self, subject, text, summary, useridfrom):
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
                dc = Discord(self.webhook_url)
                useridfrom_info = moodle_handler.user_id_from(useridfrom)
                fullname = useridfrom_info[0]["fullname"]
                profile_url = useridfrom_info[0]["profileimageurl"]
                dc.send_notification(subject, text, summary, fullname, profile_url)

        except Exception as e:
            logging.exception("Failed to send notification")

    @handle_exceptions
    def send_simple(self, subject, text):
        try:
            logging.info("Sending notification to Discord")
            dc = Discord(self.webhook_url)
            dc.send_simple(subject, text)
        except Exception as e:
            logging.exception("Failed to send notification")


def main_loop(handler, summarizer, sender, summary, sleep_duration=60, max_retries=3):
    """
    Main loop of the program. Fetches and processes notifications at regular intervals.

    :param handler: Instance of MoodleNotificationHandler for fetching notifications.
    :param summarizer: Instance of NotificationSummarizer for summarizing notifications.
    :param sender: Instance of NotificationSender for sending notifications.
    :param sleep_duration: Time to sleep between each iteration of the loop.
    :param max_retries: Maximum number of retries for fetching and processing notifications.
    """
    retry_count = 0
    while True:
        try:
            if notification := handler.fetch_newest_notification():
                if text := parse_html_to_text(notification["fullmessagehtml"]):
                    # if in config summary is set to 1, summarize the text elso leave summary empty
                    if summary == "1":
                        summary = summarizer.summarize(text, configModel=sender.model)
                    else:
                        summary = ""
                    sender.send(
                        notification["subject"],
                        text,
                        summary,
                        notification["useridfrom"],
                    )

            retry_count = 0  # Reset retry count if successful
            time.sleep(sleep_duration)
        except KeyboardInterrupt:
            logging.info("Exiting main loop")
            break
        except Exception as e:
            logging.exception("An error occurred in the main loop")
            retry_count += 1
            if retry_count > max_retries:
                # Send error message via Discord
                error_message = (
                    f"An error occurred in the main loop:\n\n{traceback.format_exc()}"
                )
                sender.send_simple("Error", error_message)
                logging.error("Max retries reached. Exiting main loop.")
                break
            else:
                logging.warning(f"Retrying ({retry_count}/{max_retries})...")
                time.sleep(sleep_duration)


# This is the main loop of the program. We'll keep looping until something breaks
if __name__ == "__main__":
    print(logo)
    setup_logging()

    # Initialize Config object
    config = Config("config.ini")

    # Initialize other classes with the Config object
    moodle_handler = MoodleNotificationHandler(config)
    summarizer = NotificationSummarizer(config)
    sender = NotificationSender(config)
    summary = config.get_config("moodle", "summary")  # 1 = summary, 0 = no summary

    main_loop(moodle_handler, summarizer, sender, summary)
