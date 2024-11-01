"""
Chat module using Deepinfra with openai style

Author: EvickaStudio
Date: 29.01.2024
Github: @EvickaStudio
"""

import logging

from openai import OpenAI


class GPT:
    """
    Interface for the OpenAI API with custom url/ model for Deepinfra.
    ....
    """

    def __init__(self, api_key: str) -> None:
        self.model = "cognitivecomputations/dolphin-2.6-mixtral-8x7b"
        self.base_url = "https://api.deepinfra.com/v1/openai"
        self.api_key = (
            api_key  # Set the api_key before initializing the OpenAI client
        )
        self.openai = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def chat_completion(self, system_message: str, user_message: str) -> str:
        """
        Generates a response using the chat completion endpoint of OpenAI API.
        ....
        Args:
            model (str): The model to use for chat completion.
            system_message (str): The system message to provide context for the conversation.
            user_message (str): The user message to generate a response.
        ....
        Returns:
            str: The generated response from the chat completion, or an empty string if an error occurs.
        """
        logging.info("Requesting chat completion from OpenAI")
        response = self.openai.chat.completions.create(
            model=self.model,
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


# Example usage of the GPT class
# gpt = GPT("your_api_key")
# response = gpt.chat_completion("Assistant", "Hello!")

# print(response)
