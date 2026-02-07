import logging
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from moodlemate.ai.chat import GPT
    from moodlemate.config import Settings


class NotificationSummarizer:
    """Summarizes notification content using AI."""

    def __init__(self, settings: "Settings", ai_provider: Optional["GPT"] = None):
        """Initialize the summarizer.

        Args:
            settings: Configuration instance
            ai_provider: Injected GPT service (optional)
        """
        self.config = settings.ai
        self.ai_provider = ai_provider

        if not self.config.enabled:
            logging.info("AI summarization is disabled")
            return

        if not self.config.api_key:
            logging.warning(
                "AI enabled without API key. This is only valid for endpoints that do not require a key."
            )

        if self.config.enabled and not self.ai_provider:
            raise ValueError("AI is enabled but no AI provider was injected.")

    def summarize(self, text: str) -> str:
        """Summarize the given text.

        Args:
            text: The text to summarize

        Returns:
            The summarized text

        Raises:
            ValueError: If the input text is empty
        """
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty")

        if not self.config.enabled:
            return text

        if not self.ai_provider:
            # Should be caught in init but safe guard
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
            # Don't raise, just return original text so notification still goes out
            return text
