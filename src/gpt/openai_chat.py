import configparser
import logging
import re
from time import sleep
from typing import Optional

import openai  # version 1.5
import tiktoken


class GPT:
    """
    Interface for the OpenAI API.

    Methods:
    __init__(...) -> None: Initialize the class.
    api_key: str | None: The API key for OpenAI.
    """

    PRICING = {
        "gpt-4o": {
            "input": 5.00 / 1_000_000,  # $5.00 per 1M input tokens
            "output": 15.00 / 1_000_000,  # $15.00 per 1M output tokens
        },
        "gpt-4o-2024-08-06": {
            "input": 2.50 / 1_000_000,  # $2.50 per 1M input tokens
            "output": 10.00 / 1_000_000,  # $10.00 per 1M output tokens
        },
        "gpt-4o-mini": {
            "input": 0.150 / 1_000_000,  # $0.150 per 1M input tokens
            "output": 0.600 / 1_000_000,  # $0.600 per 1M output tokens
        },
        "gpt-4o-mini-2024-07-18": {
            "input": 0.150 / 1_000_000,  # $0.150 per 1M input tokens
            "output": 0.600 / 1_000_000,  # $0.600 per 1M output tokens
        },
    }

    def __init__(self) -> None:
        self._api_key: Optional[str] = None
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

    def count_tokens(self, text: str, model: str = "gpt-4o-mini") -> int:
        """
        Counts the number of tokens in the given text for the specified model.

        Args:
            text (str): The text to tokenize.
            model (str): The model name.

        Returns:
            int: The number of tokens.
        """
        try:
            encoder = tiktoken.encoding_for_model(model)
            return len(encoder.encode(text))
        except Exception as e:
            logging.error(f"Error counting tokens for model {model}: {e}")
            return 0

    def chat_completion(
        self, model: str, system_message: str, user_message: str
    ) -> str:
        """
        Generates a response using the chat completion endpoint of OpenAI API.
        Logs the pricing details based on token usage.

        Args:
            model (str): The model to use for chat completion.
            system_message (str): The system message to provide context for the conversation.
            user_message (str): The user message to generate a response.

        Returns:
            str: The generated response from the chat completion, or an empty string if an error occurs.
        """
        logging.info("Requesting chat completion from OpenAI")

        if model not in self.PRICING:
            logging.error(f"Model {model} not found in pricing information.")
            return ""

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]

        # Count input tokens
        input_tokens = sum(
            self.count_tokens(message["content"], model=model)
            for message in messages
        )

        try:
            response = openai.chat.completions.create(
                model=model,
                messages=messages,
            )

            output_text = (
                response.choices[0].message.content if response.choices else ""
            )
            output_tokens = self.count_tokens(output_text, model=model)

            # Calculate costs
            input_cost = input_tokens * self.PRICING[model]["input"]
            output_cost = output_tokens * self.PRICING[model]["output"]
            total_cost = input_cost + output_cost

            # Log the costs
            logging.info(
                f"Model: {model}\n"
                f"Input Tokens: {input_tokens}\n"
                f"Output Tokens: {output_tokens}\n"
                f"Input Cost: ${input_cost:.6f}\n"
                f"Output Cost: ${output_cost:.6f}\n"
                f"Total Cost: ${total_cost:.6f}"
            )

            return output_text

        except Exception as e:
            logging.error(f"An error occurred during chat completion: {e}")
            return ""

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
        try:
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
        except Exception as e:
            logging.error(f"An error occurred during assistant run: {e}")
            return ""

    def create_thread(self) -> str:
        """
        Creates a new thread for the assistant.

        Returns:
            str: The thread ID.
        """
        try:
            return openai.beta.threads.create().id
        except Exception as e:
            logging.error(f"An error occurred while creating a new thread: {e}")
            return ""

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
        try:
            config = configparser.ConfigParser()
            config.read("thread.ini")
            config["THREAD"] = {"thread_id": thread_id}
            with open("thread.ini", "w") as configfile:
                config.write(configfile)
                logging.info(message)
        except Exception as e:
            logging.error(
                f"An error occurred while saving/updating the thread: {e}"
            )

    def resume_thread(self) -> str:
        """
        Resumes the thread from the config file or creates a new thread if not found.

        Returns:
            str: The thread ID.
        """
        try:
            config = configparser.ConfigParser()
            config.read("thread.ini")
            if "THREAD" not in config or "thread_id" not in config["THREAD"]:
                thread_id = self.create_thread()
                self.save_thread(thread_id)
            else:
                thread_id = config["THREAD"]["thread_id"]
            return thread_id
        except Exception as e:
            logging.error(f"An error occurred while resuming the thread: {e}")
            return self.create_thread()
