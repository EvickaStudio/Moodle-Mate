import logging
import time

import bs4

from ai.chat import GPT
from moodle.api import MoodleAPI
from notification.discord import Discord
from notification.pushbullet import Pushbullet

# Set logging level and print logging messages to console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


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

    def __init__(self, api_config):
        # Load the API key and system message from the config file
        self.api_key = api_config["moodle"]["openaikey"]
        self.system_message = api_config["moodle"]["systemmessage"]

    def summarize(self, text):
        try:
            # Summarize the text using GPT-3 and return the result
            gpt = GPT()
            gpt.apiKey = self.api_key
            return gpt.chatCompletion("gpt-3.5-turbo", self.system_message, text)
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
    logging.info("Starting main loop")
    # Initialize the MoodleNotificationHandler with a config file
    moodle_handler = MoodleNotificationHandler("config.ini")
    # Initialize the summarizer with the config from the handler
    summarizer = NotificationSummarizer(moodle_handler.api.config)
    # Initialize the sender with the same config
    sender = NotificationSender(moodle_handler.api.config)

    while True:
        try:
            # Get the newest notification
            if notification := moodle_handler.fetch_newest_notification():
                # Get the html from the notification
                html = notification["fullmessagehtml"]
                # Parse the html using Beautiful Soup
                soup = bs4.BeautifulSoup(html, "html.parser")
                # Get the text from the parsed html
                text = soup.get_text()
                # Clean the text, removing blank lines and trailing whitespace
                cleaned_text = "\n".join(
                    [ll.rstrip() for ll in text.splitlines() if ll.strip()]
                )
                # Summarize the cleaned text
                summary = summarizer.summarize(cleaned_text)
                # Send the notification using the sender
                sender.send(
                    notification["subject"],
                    cleaned_text,
                    summary,
                    notification["useridfrom"],
                )

            # Sleep for a minute
            time.sleep(60)
        # If something breaks, log it
        except Exception as e:
            logging.exception("An error occurred in the main loop 🤦‍♂️")
