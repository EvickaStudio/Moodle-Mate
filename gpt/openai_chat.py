"""
Chat module for OpenAI API

Author: EvickaStudio
Date: 18.11.2023
Github: @EvickaStudio
"""

import logging
import time

import openai  # version 1.5


class GPT:
    def __init__(self) -> None:
        self._apiKey = None

    @property
    def apiKey(self) -> str:
        return self._apiKey

    @apiKey.setter
    def apiKey(self, key: str) -> None:
        """
        Sets the API key and validates that it's not empty.

        Args:
            key (str): The API key for OpenAI.

        Raises:
            ValueError: If the API key is empty.
        """
        if not key:
            raise ValueError("API key cannot be empty")
        self._apiKey = key
        openai.api_key = key

    def chat_completion(self, model: str, systemMessage: str, userMessage: str) -> str:
        """
        Chat completion endpoint for OpenAI API.

        Args:
            model (str): The model to use for chat completion.
            systemMessage (str): The system message to provide context for the conversation.
            userMessage (str): The user message to generate a response.

        Returns:
            str: The generated response from the chat completion, or None if an error occurs.

        Examples:
            ```python
            gpt = GPT()
            gpt.apiKey = "your_api_key"

            response = gpt.chat_completion(
                model="gpt-3.5-turbo",
                systemMessage="You are a xxx",
                userMessage="How are you?"
            )
            print(response)
            ```
        """
        logging.info("Requesting chat completion from OpenAI")
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": systemMessage,
                    },  # System message set in config
                    {
                        "role": "user",
                        "content": userMessage,
                    },  # User message set in config
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")
            return None

    def assistant(self, prompt: str) -> str:
        """
        Assistant endpoint for OpenAI API.

        It creates for each message/ summary a different thread to keep the cost low,
        also notifications dont need to be appended, cuz. they have different context.
        The greater the context, the greater the cost.

        TODO: (optional)
            - keep and append context (not creating a new thread for each message)
              this will cost more but can have a better response (more context)
            - Resume conversation (safe thread after exit)

        Args:
            prompt (str): The prompt message for the assistant.

        Returns:
            str: The response message from the assistant.
        """

        logging.info("Requesting assistant from OpenAI")
        try:
            thread = openai.beta.threads.create()
            assistant_id = "asst_Zvg2CnDYdcv3l9BcbtyURZIN"  # --> Moodle-Mate assistant
            message = openai.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=prompt,
            )
            run = openai.beta.threads.runs.create(
                thread_id=thread.id, assistant_id=assistant_id
            )

            while run.status != "completed":
                run = openai.beta.threads.runs.retrieve(
                    thread_id=thread.id, run_id=run.id
                )
                # print status but on the same line (to avoid spamming the console)
                logging.info(f"Status: {run.status}", end="\r")
                time.sleep(0.5)  # Add a delay to avoid excessive API calls

            messages = openai.beta.threads.messages.list(thread_id=thread.id)
            # Extract the response message
            response_message = None
            for message in messages.data:
                if message.role == "assistant":
                    response_message = message.content[0].text.value
                    break
            return response_message

        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")
            return None


# Example usage
# gpt = GPT()
# gpt.apiKey = "your_api_key"
# response = gpt.chat_completion(
#     model="gpt-3.5-turbo",
#     systemMessage="You are a helpful assistant.",
#     userMessage="How are you?"
# )
# print(response)
