import logging
import time
import traceback

import bs4

from ai.chat import GPT
from moodle.api import MoodleAPI
from notification.discord import Discord
from notification.pushbullet import Pushbullet


def setup_logging():
    """
    Set up basic configuration for logging.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def handle_exceptions(func):
    """
    Decorator to handle exceptions in a standardized way across methods.
    Logs the exception and returns None in case of an error.

    :param func: The function to decorate.
    :return: Wrapped function with exception handling.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.exception(f"Exception occurred in {func.__name__}")
            return None

    return wrapper


class MoodleNotificationHandler:
    """
    The MoodleNotificationHandler class handles the fetching of Moodle notifications for a specific user.

    Args:
        config_file (str): The path to the configuration file.

    Raises:
        Exception: If the initialization fails.

    Example:
        ```python
        handler = MoodleNotificationHandler("config.ini")
        notification = handler.fetch_latest_notification()
        if notification:
            print(notification)
        ```

    Attributes:
        api (MoodleAPI): An instance of the MoodleAPI class.
        username (str): The username of the Moodle user.
        password (str): The password of the Moodle user.
        moodle_user_id (int): The ID of the Moodle user.
        last_notification_id (int): The ID of the last notification fetched.
    """

    @handle_exceptions
    def __init__(self, config_file):
        """
        Loads the configuration file and initializes the MoodleNotificationHandler.
        """
        try:
            # Initialize the MoodleAPI with the config file
            self.api = MoodleAPI(config_file)

            # Login to Moodle using the username and password
            self.login()

            # Get the current user ID from Moodle
            self.moodle_user_id = self.api.get_user_id()

            # Initialize the stalk count and last notification ID
            self.stalk_count = 0
            self.last_notification_id = 0
        except Exception as e:
            logging.exception("Initialization failed")
            exit(1)

    @handle_exceptions
    def login(self):
        """
        Logs in to Moodle using the username and password.

        Raises:
            Exception: If the login fails.
        """
        try:
            # Login to Moodle using the username and password
            self.username = self.api.config["moodle"]["username"]
            self.password = self.api.config["moodle"]["password"]
            self.api.login(username=self.username, password=self.password)
        except Exception as e:
            logging.exception("Failed to login to Moodle")

    @handle_exceptions
    def fetch_latest_notification(self):
        """
        Fetches the latest notification from Moodle.
        Latest notification is defined as the first notification in the list of notifications.
        This notification must not be newer than the last notification fetched, it can be the same
        => fetch_newest checks for this.

        Returns:
            dict: A dictionary containing the latest notification.

        """
        try:
            # Count the number of times this method has been called
            logging.info("Fetching notification from Moodle")
            # Parse the last notification from the Moodle API response and return it
            return self.api.get_popup_notifications(self.moodle_user_id)[
                "notifications"
            ][0]
        except Exception as e:
            logging.exception("Failed to fetch Moodle notification")
            return None

    @handle_exceptions
    def fetch_newest_notification(self):
        """
        Fetches the newest notification from Moodle by comparing the ID of the last notification fetched.

        Returns:
            dict: A dictionary containing the newest notification.

        """
        try:
            # Check if there is a newer notification than the last one
            if notification := self.fetch_latest_notification():
                notification_id = notification["id"]

                if notification_id <= self.last_notification_id:
                    # If there isn't, return None
                    return None

                logging.info("Getting newest notification from Moodle")
                # If there is, return the notification and update the last notification ID
                self.last_notification_id = notification_id
                return notification
        except Exception as e:
            logging.exception("Failed to fetch newest Moodle notification")
            return None

    @handle_exceptions
    def user_id_from(self, useridfrom):
        """
        Fetches the user ID from Moodle.

        Args:
            useridfrom (int): The ID of the user.

        Returns:
            dict: A dictionary containing the user ID.

        Example:
            ```python
            user_id = handler.user_id_from(1234)
            if user_id:
                print(user_id)
            ```
        """
        try:
            # Fetches user information from Moodle using given user ID
            return self.api.core_user_get_users_by_field(useridfrom)
        except Exception as e:
            logging.exception("Failed to fetch user id from Moodle")
            return None


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
    def __init__(self, api_config):
        # Load the API key and system message from the config file
        self.api_key = api_config["moodle"]["openaikey"]
        self.system_message = api_config["moodle"]["systemmessage"]

    @handle_exceptions
    def summarize(self, text, configModel):
        try:
            # Summarize the text using GPT-3 and return the result
            gpt = GPT()
            gpt.apiKey = self.api_key
            return gpt.chatCompletion(configModel, self.system_message, text)
        except Exception as e:
            logging.exception("Failed to summarize with GPT-3")
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
    def __init__(self, api_config):
        """
        Initializes a NotificationSender instance.

        Args:
            api_config (dict): The API configuration containing the Pushbullet API key and Discord webhook URL.
        """
        self.pushbullet_key = api_config["moodle"]["pushbulletkey"]
        self.webhook_url = api_config["moodle"]["webhookUrl"]
        self.pushbullet_state = int(api_config["moodle"].get("pushbulletState", 1))
        self.webhook_state = int(api_config["moodle"].get("webhookState", 1))
        self.model = api_config["moodle"]["model"]

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
                pb.push(subject, summary)

            if self.webhook_state == 1:
                logging.info("Sending notification to Discord")
                dc = Discord(self.webhook_url)
                useridfrom_info = moodle_handler.user_id_from(useridfrom)
                fullname = useridfrom_info[0]["fullname"]
                profile_url = useridfrom_info[0]["profileimageurl"]
                dc.send(subject, text, summary, fullname, profile_url)

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




def parse_html_to_text(html):
    """
    Parses the given HTML content to plain text.

    :param html: HTML content as a string.
    :return: Plain text after removing HTML tags.
    """
    try:
        soup = bs4.BeautifulSoup(html, "html.parser")
        return "\n".join(
            [line.rstrip() for line in soup.get_text().splitlines() if line.strip()]
        )
    except Exception as e:
        logging.exception("Failed to parse HTML")
        return None


def main_loop(handler, summarizer, sender, sleep_duration=60, max_retries=3):
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
                    summary = summarizer.summarize(text, configModel=sender.model)
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


logo = """
   __  ___             ____    __  ___     __        ,-------,
  /  |/  /__  ___  ___/ / /__ /  |/  /__ _/ /____   /       / | 
 / /|_/ / _ \/ _ \/ _  / / -_) /|_/ / _ `/ __/ -_) /______ /  /
/_/  /_/\___/\___/\_,_/_/\__/_/  /_/\_,_/\__/\__/ |___/___/  /
 -—--–=¤=—--–-- - -  EvickaStudio  - - --–--—=¤=--|__..___|.'- -
                                                    //
"""

# This is the main loop of the program. We'll keep looping until something breaks
if __name__ == "__main__":
    print(logo)
    setup_logging()

    # Initialize classes with necessary configurations
    moodle_handler = MoodleNotificationHandler("config.ini")
    summarizer = NotificationSummarizer(moodle_handler.api.config)
    sender = NotificationSender(moodle_handler.api.config)

    # Start the main loop
    main_loop(moodle_handler, summarizer, sender)
