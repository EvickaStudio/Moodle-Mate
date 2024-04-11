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
import time
import traceback

from filters.discord_markdown import html_to_discord_md
from filters.message_filter import (
    extract_and_format_for_discord,
    parse_html_to_text,
)
from utils.wirte import write_to_log


def main_loop(
    handler,
    summarizer,
    sender,
    summary,
    sleep_duration,
    max_retries,
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

    # sender.send(
    #     "Bot started",
    #     "Successfully connected to the Moodle API\nChecking for new notifications every "
    #     + str(sleep_duration)
    #     + " seconds",
    #     None,
    # )

    while True:
        try:
            if (
                notification := handler.fetch_newest_notification()
            ):  # If there is a new notification
                if text := html_to_discord_md(notification["fullmessagehtml"]):
                    logging.info(f"Original text: {notification['fullmessagehtml']}")
                    logging.info(f"Converted text: {text}")
                    # Debug, to see notification content uncomment the line below
                    # print(notification["fullmessagehtml"])

                    # Debug, to write notification content to a file uncomment the line below
                    # write_to_log(notification["fullmessagehtml"])
                    if summary_setting == 1:
                        logging.info("Summarizing text...")
                        # To use the OpenAI assistant for summarization, uncomment the line below
                        # and comment: summary = summarizer.summarize(text)
                        # summary = summarizer.summarize(text, True)

                        # summary = summarizer.summarize(notification["fullmessagehtml"])
                        summary = "Test summary"
                    elif summary_setting == 0:
                        logging.info(
                            "Summary is set to 0, not summarizing text"
                        )
                        summary = ""
                    else:
                        logging.error(
                            "Error while checking the summary setting"
                        )
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
                error_message = f"An error occurred in the main loop:\n\n{traceback.format_exc()}"
                # sender.send_simple("Error", error_message)
                logging.error("Max retries reached. Exiting main loop.")
                exit(1)
            else:
                logging.warning(f"Retrying ({retry_count}/{max_retries})...")
                time.sleep(sleep_duration)

            raise e
