import json
import logging

import requests


class GPT:
    """
    Interface for the groq API.

    Methods:
    __init__(...) -> None: Initialize the class.
    api_key: str | None: The API key for groq.
    chat_completion(...) -> str: Generates a response using the chat completion endpoint of groq API.
    """

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def chat_completion(self, system_message: str, user_message: str) -> str:
        """
        Generates a response using the chat completion endpoint of groq API.
        """

        logging.info("Requesting chat completion from OpenAI")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        data = {
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            "model": "llama2-70b-4096",
            "temperature": 0.5,
            "max_tokens": 1024,
            "top_p": 1,
            "stream": False,
            "stop": None,
        }

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            data=json.dumps(data),
        )

        if response.status_code != 200:
            return f"Error: {response.text}"
        completion = response.json()
        return (
            completion["choices"][0]["message"]["content"]
            if completion["choices"]
            else ""
        )


# Exam
# Example usage of the GPT class
# gpt = GPT("your_api_key")
# response = gpt.chat_completion("Assistant", "Hello!")

# print(response)
