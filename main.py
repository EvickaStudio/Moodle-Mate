import logging
import os
import time
import traceback

from filters.message_filter import extract_and_format_for_discord
from gpt.openai_chat import GPT
from moodle.load_config import Config
from moodle.moodle_notification_handler import MoodleNotificationHandler
from notification.discord import Discord
from notification.pushbullet import Pushbullet
from utils.handle_exceptions import handle_exceptions
from utils.logo import logo
from utils.setup_logging import setup_logging


# Clear screen
def clear_screen() -> None:
    """
    Clears the terminal screen.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """

    os.system("cls" if os.name == "nt" else "clear")


# Constants
sleep_duration_seconds: int = 60
max_retries: int = 3


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
    def __init__(self, config: Config) -> None:
        self.api_key = config.get_config("moodle", "openaikey")
        self.system_message = config.get_config("moodle", "systemmessage")

    @handle_exceptions
    def summarize(
        self, text: str, configModel: str, use_assistant_api: bool = False
    ) -> str:
        """
        Summarizes the given text using GPT-3 API or FGPT.

        Args:
            text (str): The text to summarize.
            configModel (str): The GPT-3 model to use, or 'FGPT' to use FGPT.
            use_assistant_api (bool, optional): Whether to use the chat completion or assistant API. Defaults to False.

        Returns:
            str: The summarized text.

        Raises:
            Exception: If summarization fails.
        """
        try:
            # Test option, summarize the text using assistant and not the
            # chat completion API, for testing ATM.
            ai = GPT()
            ai.api_key = self.api_key
            if not use_assistant_api:
                return ai.chat_completion(configModel, self.system_message, text)

            logging.info(f"Test = {self.test}, summarizing with Asistant API")
            return ai.context_assistant(prompt=text)
        except Exception as e:
            logging.exception(f"Failed to summarize with {configModel}")
            raise e


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
        self.pushbullet_state = int(config.get_config("moodle", "pushbulletState"))
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
                dc = Discord(self.webhook_url)
                useridfrom_info = moodle_handler.user_id_from(useridfrom)
                fullname = useridfrom_info[0]["fullname"]
                profile_url = useridfrom_info[0]["profileimageurl"]
                dc(
                    subject=subject,
                    text=text,
                    summary=summary,
                    fullname=fullname,
                    picture_url=profile_url,
                )

        except Exception as e:
            logging.exception("Failed to send notification")
            raise e

    @handle_exceptions
    def send_simple(self, subject: str, text: str) -> None:
        try:
            logging.info("Sending notification to Discord")
            dc = Discord(self.webhook_url)
            dc.send_simple(subject, text)
        except Exception as e:
            logging.exception("Failed to send notification")
            raise e


def main_loop(
    handler,
    summarizer,
    sender,
    summary,
    sleep_duration=sleep_duration_seconds,
    max_retries=max_retries,
):
    """
    Main loop of the program. Fetches and processes notifications at regular intervals.

    :param handler: Instance of MoodleNotificationHandler for fetching notifications.
    :param summarizer: Instance of NotificationSummarizer for summarizing notifications.
    :param sender: Instance of NotificationSender for sending notifications.
    :param sleep_duration: Time to sleep between each iteration of the loop.
    :param max_retries: Maximum number of retries for fetching and processing notifications.
    """
    retry_count = 0
    summary_setting = int(summary)

    while True:
        try:
            if (
                notification := handler.fetch_newest_notification()
            ):  # If there is a new notification
                if text := extract_and_format_for_discord(
                    notification["fullmessagehtml"]
                ):
                    if summary_setting == 1:
                        logging.info("Summarizing text...")
                        summary = summarizer.summarize(text, configModel=sender.model)
                    elif summary_setting == 0:
                        logging.info("Summary is set to 0, not summarizing text")
                        summary = ""
                    else:
                        logging.error("Error while checking the summary setting")
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
                # Send error message via Discord if max retries reached
                error_message = (
                    f"An error occurred in the main loop:\n\n{traceback.format_exc()}"
                )
                sender.send_simple("Error", error_message)
                logging.error("Max retries reached. Exiting main loop.")
                break
            else:
                logging.warning(f"Retrying ({retry_count}/{max_retries})...")
                time.sleep(sleep_duration)

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
    summary = int(config.get_config("moodle", "summary"))  # 1 = summary, 0 = no summary
    fakeopen = int(
        config.get_config("moodle", "fakeopen")
    )  # 1 = fake open, 0 = openai when selected

    main_loop(moodle_handler, summarizer, sender, summary)
