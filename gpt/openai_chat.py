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

"""
Chat module for OpenAI API

Author: EvickaStudio
Date: 25.12.2023
Github: @EvickaStudio
"""

import configparser
import logging
import re
from time import sleep
from typing import Optional

import openai  # version 1.5


class GPT:
    """
    Interface for the OpenAI API.

    Methods:
    __init__(...) -> None: Initialize the class.
    api_key: str | None: The API key for OpenAI.
    """

    def __init__(self) -> None:
        self._api_key: Optional[str] = None
        # self.api_key_regex /regex(\/sk-\w{48}\/)/
        self.api_key_regex = r"^sk-[A-Za-z0-9]{48}$"

    @property
    def api_key(self) -> str | None:
        """
        Gets the API key for OpenAI.

        Returns:
            str | None: The API key.
        """
        return self._api_key

    @api_key.setter
    def api_key(self, key: str) -> None:
        """
        Sets the API key for OpenAI and validates it.

        Args:
            key (str): The API key for OpenAI.

        Raises:
            ValueError: If the API key is empty or invalid.
        """
        if not key:
            raise ValueError("API key cannot be empty")

        if not re.match(self.api_key_regex, key):
            raise ValueError("API key is invalid")

        self._api_key = key
        openai.api_key = key

    def chat_completion(
        self, model: str, system_message: str, user_message: str
    ) -> str:
        """
        Generates a response using the chat completion endpoint of OpenAI API.

        Args:
            model (str): The model to use for chat completion.
            system_message (str): The system message to provide context for the conversation.
            user_message (str): The user message to generate a response.

        Returns:
            str: The generated response from the chat completion, or an empty string if an error occurs.
        """
        logging.info("Requesting chat completion from OpenAI")
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_message,
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
        )
        return response.choices[0].message.content if response.choices else ""

    def assistant(self, prompt: str, thread_id: Optional[str] = None) -> str:
        """
        Assistant endpoint for OpenAI API.

        It creates for each message/summary a different thread to keep the cost low,
        also notifications don't need to be appended, as they have different context.
        The greater the context, the greater the cost.

        Args:
            prompt (str): The prompt message for the assistant.
            thread_id (str): The ID of the thread to use. If None, a new thread will be created.

        Returns:
            str: The response message from the assistant.
        """
        logging.info("Requesting assistant from OpenAI")
        return self.run_assistant(prompt, thread_id)

    def context_assistant(self, prompt: str) -> str:
        """
        Generates a response using the assistant endpoint of OpenAI API with saved context.

        Args:
            prompt (str): The prompt message for the assistant.

        Returns:
            str: The response message from the assistant.
        """
        thread_id = self.resume_thread()
        return self.assistant(prompt, thread_id)

    def run_assistant(self, text, thread_id):
        """
        Runs the assistant to generate a response.

        Args:
            text (str): The text message for the assistant.
            thread_id (str): The ID of the thread to use.

        Returns:
            str: The response message from the assistant.
        """
        if thread_id is None:
            thread_id = openai.beta.threads.create().id

        assistant_id = (
            "asst_Zvg2CnDYdcv3l9BcbtyURZIN"  # --> Moodle-Mate assistant
        )
        message = openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=text,
        )
        run = openai.beta.threads.runs.create(
            thread_id=thread_id, assistant_id=assistant_id
        )

        result = openai.beta.threads.runs.retrieve(
            thread_id=thread_id, run_id=run.id
        )

        delay = 0.5
        while result.status != "completed":
            result = openai.beta.threads.runs.retrieve(
                thread_id=thread_id, run_id=run.id
            )
            sleep(delay)
            delay += 0.5
            delay = min(delay, 10)

        logging.info(f"Status: {result.status}")

        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        return next(
            (
                message.content[0].text.value
                for message in messages.data
                if message.role == "assistant"
            ),
            None,
        )

    def create_thread(self) -> str:
        """
        Creates a new thread for the assistant.

        Returns:
            str: The thread ID.
        """
        return openai.beta.threads.create().id

    def save_thread(self, thread_id: str) -> None:
        """
        Saves the thread ID to a config file for resuming the conversation later.

        Args:
            thread_id (str): The thread ID to save.
        """
        self.save_or_update_thread(thread_id, "Thread saved")

    def update_thread(self, thread_id: str) -> None:
        """
        Updates the thread ID in the config file with a fresh one (clears the conversation).

        Args:
            thread_id (str): The thread ID to update.
        """
        self.save_or_update_thread(thread_id, "Thread updated")

    def save_or_update_thread(self, thread_id: str, message: str) -> None:
        """
        Saves or updates the thread ID in the config file.

        Args:
            thread_id (str): The thread ID to save or update.
            message (str): The message to log after saving or updating the thread.
        """
        config = configparser.ConfigParser()
        config.read("thread.ini")
        config["THREAD"] = {"thread_id": thread_id}
        with open("thread.ini", "w") as configfile:
            config.write(configfile)
            logging.info(message)

    def resume_thread(self) -> str:
        """
        Resumes the thread from the config file or creates a new thread if not found.

        Returns:
            str: The thread ID.
        """
        config = configparser.ConfigParser()
        config.read("thread.ini")
        if "THREAD" not in config or "thread_id" not in config["THREAD"]:
            thread_id = self.create_thread()
            self.save_thread(thread_id)
        else:
            thread_id = config["THREAD"]["thread_id"]
        return thread_id


# Example usage
# gpt = GPT()
# gpt.api_key = "your_api_key"
# response = gpt.chat_completion(
#     model="gpt-3.5-turbo",
#     systemMessage="You are a helpful assistant.",
#     userMessage="How are you?"
# )
# print(response)
