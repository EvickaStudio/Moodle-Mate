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

from moodle.load_config import Config
from moodle.moodle_notification_handler import MoodleNotificationHandler
from notification.notification_sender import NotificationSender
from notification.notification_summarizer import NotificationSummarizer
from utils.main_loop import main_loop
from utils.screen import clear_screen, logo
from utils.setup_logging import setup_logging

# Constants, can be changed here
SLEEP_DURATION_SECONDS = (
    60  # how many seconds to sleep between each iteration of the loop
)
MAX_RETRIES = (
    3  # maximum number of retries for fetching and processing notifications
)

# This is the main loop of the program. We'll keep looping until something breaks
if __name__ == "__main__":
    # Clear the screen and print the logo
    clear_screen()
    print(logo)
    # Setup logging
    # Uncomment the following line to disable logging/ output to console
    setup_logging()
    # Initialize Config object
    config = Config("config.ini")
    # Initialize other classes with the Config object
    moodle_handler = MoodleNotificationHandler(config)
    summarizer = NotificationSummarizer(config)
    sender = NotificationSender(config)
    summary = (
        int(config.get_config("moodle", "summary"))
        if config.get_config("moodle", "summary")
        else 0
    )
    fakeopen = (
        int(config.get_config("moodle", "fakeopen"))
        if config.get_config("moodle", "fakeopen")
        else 0
    )
    # Start the main loop
    main_loop(
        moodle_handler,
        summarizer,
        sender,
        summary,
        SLEEP_DURATION_SECONDS,
        MAX_RETRIES,
    )
