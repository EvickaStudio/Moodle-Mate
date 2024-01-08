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

from gpt.openai_chat import GPT
from moodle.load_config import Config
from utils.handle_exceptions import handle_exceptions


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
        self.model = config.get_config("moodle", "model")
        # print(f"Model = {self.model}")  # Debug line

    @handle_exceptions
    def summarize(self, text: str, use_assistant_api: bool = False) -> str:
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
                if self.model is None or self.system_message is None:
                    raise ValueError(
                        "Model and system message must not be None"
                    )
                return ai.chat_completion(
                    self.model, self.system_message, text or ""
                )

            return ai.context_assistant(prompt=text)
        except Exception as e:
            logging.exception(f"Failed to summarize with {self.model}")
            raise e
