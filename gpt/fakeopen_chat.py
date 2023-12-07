"""
Chat module for FakeOpen API
Free alternative to OpenAI API

Author: EvickaStudio
Date: 06.12.2023
Github: @EvickaStudio
"""

import json
import logging
import os
from typing import Dict, Optional

import requests


class FGPT:
    def __init__(self) -> None:
        self.api_key = "pk-this-is-a-real-free-pool-token-for-everyone"  # Hardcoded API key, cuz its public
        self.base_url = "https://ai.fakeopen.com/v1/chat/completions"

    def _get_headers(self) -> Dict[str, str]:
        """
        Generates the headers required for the API request.

        Returns:
            Dict[str, str]: A dictionary of headers for the request.
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
        system_message: str,
        user_message: str,
        model: str = "gpt-4-1106-preview",
        temperature: float = 1.0,
        presence_penalty: float = 0.0,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        stream: bool = False,
    ) -> Optional[str]:
        """
        Sends a request to the chat completion endpoint of the API.

        Args:
            system_message (str): The system message to provide context for the conversation.
            user_message (str): The user message to generate a response.
            model (str, optional): The model to use. Defaults to "gpt-4-32k".
            temperature (float, optional): The temperature of the chat completion. Defaults to 1.0.
            presence_penalty (float, optional): The presence penalty of the chat completion. Defaults to 0.0.
            top_p (float, optional): The top p of the chat completion. Defaults to 1.0.
            frequency_penalty (float, optional): The frequency penalty of the chat completion. Defaults to 0.0.
            stream (bool, optional): Whether to stream the chat completion. Defaults to False, cuz i didn't implement it yet.

            Tested Models:
                - gpt-3.5-turbo # GPT-3 Turbo, 4K context size
                - gpt-3.5-turbo-16k # GPT-3, 16K context size (Will point to gpt-3.5-turbo-1106 starting Dec 11, 2023.)
                - gpt-3.5-turbo-1106 # GPT-3 Turbo, 16K context size
                - gpt-4 # GPT-4, 8K context size
                - gpt-4-32k # GPT-4, 32K context size
                - gpt-4-1106-preview # GPT-4 Turbo, 128K context size

        Returns:
            Optional[str]: The response from the API or None in case of an error.
        """
        data = {
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
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
            response.raise_for_status()
            response_json = response.json()
            return (
                response_json.get("choices", [{}])[0].get("message", {}).get("content")
            )
        except requests.RequestException as e:
            logging.error(f"HTTP error occurred: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
        return None


# Example usage
# gpt = FGPT()
# response = gpt.chat_completion(
#     system_message="You are a helpful assistant.",
#     user_message="How are you?"
# )
# print(response)
