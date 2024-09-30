import logging

from src.gpt.deepinfra import GPT as GPTDeepinfra
from src.gpt.openai_chat import GPT
from src.utils.handle_exceptions import handle_exceptions
from src.utils.load_config import Config


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
        self.test = False

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

            if self.test:
                # Test with cognitivecomputations/dolphin-2.6-mixtral-8x7b
                ai = GPTDeepinfra(api_key=self.api_key)
                return ai.chat_completion(self.system_message, text or "")

            else:
                if self.model is None or self.model == "":
                    self.model = "gpt-3.5-turbo-1106"
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
