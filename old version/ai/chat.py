"""
Chat module for OpenAI API

Author: EvickaStudio
Data: 18.11.2023
Github: @EvickaStudio
"""

import openai


class GPT:
    def __init__(self) -> None:
        self._apiKey = None

    @property
    def apiKey(self):
        return self._apiKey

    @apiKey.setter
    def apiKey(self, key):
        self._apiKey = key
        openai.api_key = key

    def chatCompletion(self, model, systemMessage, userMessage):
        """
        Chat completion endpoint for OpenAI API

        Args:
            model (str): The model to use for chat completion. Valid options are 'gpt-3.5-turbo' and 'gpt-4' for example.
            systemMessage (str): The system message to provide context for the conversation.
            userMessage (str): The user message to generate a response.

        Returns:
            str: The generated response from the chat completion.

        Examples:
            ```python
            gpt = GPT()
            gpt.apiKey = "your_api_key"

            response = gpt.chatCompletion(
                model="gpt-3.5-turbo",
                systemMessage="You are a xxx",
                userMessage="How are you?"
            )
            print(response)
            ```
        """
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": systemMessage,  # System message set in config
                    },
                    {"role": "user", "content": userMessage},  # Moodle message input
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None
