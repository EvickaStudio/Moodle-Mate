"""
Chat module for OpenAI API

Author: EvickaStudio
Date: 18.11.2023
Github: @EvickaStudio
"""

import logging

import openai  # version 1.3.6


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


# Example usage
# gpt = GPT()
# gpt.apiKey = "your_api_key"
# response = gpt.chat_completion(
#     model="gpt-3.5-turbo",
#     systemMessage="You are a helpful assistant.",
#     userMessage="How are you?"
# )
# print(response)
