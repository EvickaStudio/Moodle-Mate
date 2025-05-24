import logging

from src.core.config.loader import Config
from src.core.service_locator import ServiceLocator
from src.services.ai.chat import GPT


class NotificationSummarizer:
    """
    Provides functionality to summarize notification content using an AI provider.

    This class interfaces with an AI service (currently `GPT` via `ServiceLocator`)
    to generate concise summaries of notification messages. It is configured using
    the `AIConfig` section of the application's overall configuration.

    If AI summarization is disabled in the configuration or if an API key is missing,
    it will not attempt to summarize and may log appropriate messages or raise errors
    during initialization.

    The primary method `summarize(text: str)` takes a string of text and returns
    its AI-generated summary.

    Attributes:
        config (AIConfig): The AI-specific configuration (api_key, model, etc.).
        ai_provider (GPT | None): An instance of the AI provider (e.g., GPT) if AI is
            enabled and configured; otherwise, it might not be fully initialized if
            summarization is disabled, though constructor logic aims to prevent this.

    Raises:
        ValueError: During initialization if AI is enabled but `api_key` is missing.

    Example:
        Assuming `app_config` is a loaded `Config` object and AI is enabled:
        >>> try:
        ...     summarizer = NotificationSummarizer(config=app_config)
        ...     original_text = "This is a very long notification message that needs to be shortened."
        ...     summary = summarizer.summarize(original_text)
        ...     print(f"Summary: {summary}")
        ... except ValueError as e:
        ...     print(f"Error initializing summarizer: {e}")
        ... except Exception as e: # E.g., network error during summarization
        ...     print(f"Error summarizing: {e}")
    """

    def __init__(self, config: Config):
        """
        Initialize the NotificationSummarizer.

        Sets up the AI provider based on the provided application configuration.
        If AI is disabled or the API key is missing, an `ValueError` may be raised
        or a log message will indicate that summarization is inactive.

        Args:
            config (Config): The main application configuration object, from which
                AI settings (`config.ai`) will be extracted.

        Raises:
            TypeError: If `config` is not an instance of `Config`.
            ValueError: If `config.ai.enabled` is True but `config.ai.api_key` is not provided.
            KeyError: If the 'gpt' service is not registered in the ServiceLocator when AI is enabled.
            TypeError: If the registered 'gpt' service is not of type GPT.
        """
        if not isinstance(config, Config):
            raise TypeError("config must be an instance of Config.")

        self.config = config.ai
        if not self.config.enabled:
            logging.info("AI summarization is disabled")
            return

        if not self.config.api_key:
            raise ValueError("AI API key is required for summarization")

        self.ai_provider = ServiceLocator().get("gpt", GPT)
        self.ai_provider.api_key = self.config.api_key
        if self.config.endpoint:
            self.ai_provider.endpoint = self.config.endpoint

    def summarize(self, text: str) -> str:
        """
        Generate an AI-powered summary for the given text.

        If AI summarization is disabled in the configuration, this method will
        return the original text directly without attempting to summarize.

        Args:
            text (str): The input text content to be summarized.

        Returns:
            str: The AI-generated summary of the text, or the original text if
                 summarization is disabled or fails and the error is not re-raised.

        Raises:
            TypeError: If `text` is not a string.
            ValueError: If the input `text` is empty or contains only whitespace.
            Exception: Re-raises exceptions that occur during the AI provider's
                       `chat_completion` call (e.g., network errors, API errors)
                       after logging them.
        """
        if not isinstance(text, str):
            raise TypeError("text must be a string.")
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty")

        if not self.config.enabled:
            return text

        try:
            return self.ai_provider.chat_completion(
                model=self.config.model,
                system_message=self.config.system_prompt,
                user_message=text,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )
        except Exception as e:
            logging.error(f"Failed to summarize text: {e!s}")
            raise
