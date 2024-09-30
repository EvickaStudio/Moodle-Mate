import logging
import sys
import time
import traceback

from src.filters.converter import convert


class NotificationProcessor:
    def __init__(
        self,
        handler,
        summarizer,
        sender,
        summary_setting,
        sleep_duration,
        max_retries,
    ):
        self.handler = handler
        self.summarizer = summarizer
        self.sender = sender
        self.summary_setting = summary_setting
        self.sleep_duration = sleep_duration
        self.max_retries = max_retries

    def run(self):
        retry_count = 0
        while True:
            try:
                if notification := self.handler.fetch_newest_notification():
                    # # print(notification)
                    # print(notification["fullmessagehtml"])
                    if text := convert(notification["fullmessagehtml"]):
                        # print(text)
                        logging.info(
                            f"Original text: {notification['fullmessagehtml']}"
                        )
                        logging.info(f"Converted text: {text}")

                        if self.summary_setting == 1:
                            logging.info("Summarizing text...")
                            summary = self.summarizer.summarize(
                                notification["fullmessagehtml"]
                            )
                        else:
                            logging.info("Summary is disabled.")
                            summary = ""

                        self.sender.send(
                            notification["subject"],
                            text,
                            summary,
                            notification["useridfrom"],
                        )
                retry_count = 0  # Reset retry count if successful
                time.sleep(self.sleep_duration)
            except KeyboardInterrupt:
                logging.info("Exiting main loop")
                break
            except Exception:
                logging.exception("An error occurred in the main loop")
                retry_count += 1
                if retry_count > self.max_retries:
                    error_message = f"An error occurred in the main loop:\n\n{traceback.format_exc()}"
                    # Optionally, send the error message via Discord
                    # self.sender.send_simple("Error", error_message)
                    logging.error("Max retries reached. Exiting main loop.")
                    sys.exit(1)
                else:
                    logging.warning(
                        f"Retrying ({retry_count}/{self.max_retries})..."
                    )
                    time.sleep(self.sleep_duration)
