"""
Chat module for FakeOpen API
Free alternative to OpenAI API

Author: EvickaStudio
Date: 06.12.2023
Github: @EvickaStudio
"""

import json
import logging

import requests


class FGPT:
    def __init__(self) -> None:
        self.api_key = (
            "pk-this-is-a-real-free-pool-token-for-everyone"  # Hardcoded API key
        )
        self.base_url = "https://ai.fakeopen.com/v1/chat/completions"

    def _get_headers(self) -> dict:
        """
        Generates the headers required for the API request.

        Returns:
            dict: A dictionary of headers for the request.
        """
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Accept": "*/*",
            "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://chat.geekgpt.org/",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "Origin": "https://chat.geekgpt.org",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "DNT": "1",
            "Sec-GPC": "1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "TE": "trailers",
        }

    def chat_completion(
        self,
        systemMessage: str,
        userMessage: str,
        model: str = "gpt-4-32k",
        temperature: float = 1,
        presence_penalty: float = 0,
        top_p: float = 1,
        frequency_penalty: float = 0,
        stream: bool = False,
    ) -> str:
        """
        Sends a request to the chat completion endpoint of the API.

        Args:
            systemMessage (str): The system message to provide context for the conversation.
            userMessage (str): The user message to generate a response.
            model (str, optional): The model to use. Defaults to "gpt-4-32k".
            temperature (float, optional): The temperature for the response. Defaults to 1.
            presence_penalty (float, optional): The presence penalty. Defaults to 0.
            top_p (float, optional): The top p value. Defaults to 1.
            frequency_penalty (float, optional): The frequency penalty. Defaults to 0.
            stream (bool, optional): Whether to stream the response. Defaults to False cuz i didn't implement it.

        Returns:
            str: The response from the API or an error message.
        """
        data = {
            "messages": [
                {"role": "system", "content": systemMessage},
                {"role": "user", "content": userMessage},
            ],
            "model": model,
            "temperature": temperature,
            "presence_penalty": presence_penalty,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "stream": stream,
        }

        try:
            response = requests.post(
                self.base_url, headers=self._get_headers(), data=json.dumps(data)
            )
            response_json = response.json()
            message = response_json["choices"][0]["message"]["content"]
            return message
        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")
            return None


# Example usage
# gpt = GPT()
# response = gpt.chat_completion(
#     systemMessage="You are a helpful assistant.",
#     userMessage="How are you?"
# )
# print(response)
