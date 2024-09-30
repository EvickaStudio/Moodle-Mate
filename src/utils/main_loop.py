import logging
import re
import sys
import time
import traceback

from filters.converter import convert


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
                if text := convert(notification["fullmessagehtml"]):
                    logging.info(
                        f"Original text: {notification['fullmessagehtml']}"
                    )
                    logging.info(f"Converted text: {text}")

                    reg = r"\[!\[.*\]\(.*\)\]\(.*\)"
                    re.sub(reg, "", text)
                    text.replace("***", "")

                    # Debug, to see notification content uncomment the line below
                    # print(notification["fullmessagehtml"])

                    if summary_setting == 1:
                        logging.info("Summarizing text...")
                        # To use the OpenAI assistant for summarization, uncomment the line below
                        # and comment: summary = summarizer.summarize(text)
                        # summary = summarizer.summarize(text, True)

                        summary = summarizer.summarize(
                            notification["fullmessagehtml"]
                        )
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
                sys.exit(1)
            else:
                logging.warning(f"Retrying ({retry_count}/{max_retries})...")
                time.sleep(sleep_duration)

            raise e
