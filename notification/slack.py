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

# slack.py

import logging

import requests


class Slack:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_notification(self, subject, text):
        payload = {"text": f"*{subject}*\n{text}"}

        try:
            response = requests.post(self.webhook_url, json=payload)
            if response.status_code != 200:
                raise ValueError(
                    f"Request to slack returned an error {response.status_code}, the response is:\n{response.text}"
                )
            return True
        except Exception as e:
            logging.error(f"Error sending notification to Slack: {e}")
            return False
