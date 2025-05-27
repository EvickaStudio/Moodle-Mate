import logging
import re
from typing import Dict, List, Optional

import openai  # version 1.5
import tiktoken
from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam

from .calculate import ModelPricing, ModelType
from .errors import (
    APIConnectionError,
    APITimeoutError,
    ChatCompletionError,
    ClientError,
    InvalidAPIKeyError,
    RateLimitExceededError,
    ServerError,
    TokenizationError,
)


class GPT:
    """
    Interface for the OpenAI API with improved error handling and type safety.

    This class provides a type-safe interface to OpenAI's API with proper
    error handling, token counting, and cost tracking.

    Attributes:
        PRICING: Mapping of model types to their pricing information
        api_key: The OpenAI API key (property with validation)
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GPT, cls).__new__(cls)
            cls._instance._init_gpt()
        return cls._instance

    def _init_gpt(self):
        """Initialize GPT instance."""
        self._api_key = None
        self._endpoint = None
        self.PRICING = {
            ModelType.GPT4O.value: ModelPricing(2.50, 10.00),
            ModelType.GPT4O_MINI.value: ModelPricing(0.15, 0.60),
            ModelType.O1.value: ModelPricing(15.00, 60.00),
            ModelType.O1_MINI.value: ModelPricing(1.10, 4.40),
            ModelType.O3_MINI.value: ModelPricing(1.10, 4.40),
        }
        self._api_key_pattern = re.compile(r"^sk-[A-Za-z0-9_-]{48,}$")

    @property
    def is_openrouter(self) -> bool:
        """Check if the current endpoint is for OpenRouter."""
        return "openrouter.ai" in self._endpoint if self._endpoint else False

    @property
    def api_key(self) -> Optional[str]:
        """Get the configured API key."""
        return self._api_key

    @api_key.setter
    def api_key(self, key: str) -> None:
        """
        Set and validate the API key.

        Args:
            key: The OpenAI API key to use

        Raises:
            InvalidAPIKeyError: If the key is empty or invalid
        """
        if not key:
            raise InvalidAPIKeyError("API key cannot be empty")

        if not self._api_key_pattern.match(key):
            raise InvalidAPIKeyError(
                "Invalid API key format. Expected format: 'sk-' followed by 48+ alphanumeric characters"
            )

        self._api_key = key
        openai.api_key = key

    @property
    def endpoint(self) -> Optional[str]:
        """Get the configured API endpoint."""
        return self._endpoint

    @endpoint.setter
    def endpoint(self, url: str) -> None:
        """
        Set the API endpoint URL.
        This can be useful for using a custom endpoint
        like ollama or other services like openrouter

        Args:
            url: The OpenAI API endpoint URL
        """
        self._endpoint = url
        openai.base_url = url

    def count_tokens(self, text: str, model: str = ModelType.GPT4O_MINI.value) -> int:
        """
        Count tokens in text for a specific model.

        Args:
            text: The text to tokenize
            model: The model to use for tokenization

        Returns:
            Number of tokens in the text

        Raises:
            TokenizationError: If token counting fails
        """
        try:
            encoder = tiktoken.encoding_for_model(model)
            return len(encoder.encode(text))
        except Exception as e:
            raise TokenizationError(
                f"Failed to count tokens for model {model}: {str(e)}"
            ) from e

    def _validate_model(self, model: str) -> None:
        """
        Validate model and log warning if pricing info is unavailable.

        Args:
            model: The model name to validate
        """
        if model not in self.PRICING:
            logging.warning(
                f"Model '{model}' not in pricing database. Cost tracking will be disabled."
            )

    def chat_completion(
        self,
        model: str,
        system_message: str,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate a response using OpenAI's chat completion.

        This method handles the chat completion request with proper error handling
        and cost logging. It includes automatic retries for transient errors.

        Args:
            model: The model to use
            system_message: Context message for the AI
            user_message: The user's input message
            temperature: Controls randomness (0.0-2.0)
            max_tokens: Optional maximum tokens in response

        Returns:
            The generated response text

        Raises:
            ChatCompletionError: If the completion fails after retries
            RateLimitExceededError: If rate limits are exceeded after retries
            APITimeoutError: If requests time out after retries
            APIConnectionError: If connection issues persist after retries
            ServerError: If server errors persist after retries
            ClientError: If there's a client-side error
            ValueError: If the model is not supported
        """
        self._validate_model(model)
        logging.info(f"Requesting chat completion using model: {model}")

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]

        try:
            return self._chat_completion(messages, model, temperature, max_tokens)
        except TokenizationError as e:
            raise ChatCompletionError(f"Token counting failed: {str(e)}") from e
        except Exception as e:
            raise ChatCompletionError(f"Chat completion failed: {str(e)}") from e

    def _chat_completion(  # noqa: C901
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: Optional[int],
    ) -> str:  # sourcery skip: low-code-quality
        """Internal method to handle chat completion requests."""
        max_retries = 3
        retry_delay = 2  # seconds

        for attempt in range(1, max_retries + 1):
            try:
                # Convert messages to the expected type
                typed_messages: List[ChatCompletionMessageParam] = []
                for msg in messages:
                    if msg["role"] == "system":
                        typed_messages.append(
                            {"role": "system", "content": msg["content"]}
                        )
                    elif msg["role"] == "user":
                        typed_messages.append(
                            {"role": "user", "content": msg["content"]}
                        )
                    elif msg["role"] == "assistant":
                        typed_messages.append(
                            {"role": "assistant", "content": msg["content"]}
                        )
                    # Add other roles as needed

                # Prepare extra headers if using OpenRouter
                extra_headers = None
                if self.is_openrouter:
                    extra_headers = {
                        "HTTP-Referer": "https://github.com/EvickaStudio/Moodle-Mate",
                        "X-Title": "Moodle-Mate",
                    }

                # Make the API call first since token counting might fail for unknown models
                response: ChatCompletion = openai.chat.completions.create(
                    model=model,
                    messages=typed_messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    extra_headers=extra_headers,
                )

                # Extract and validate response
                if not response.choices:
                    raise ChatCompletionError("No completion choices returned")

                output_text = response.choices[0].message.content or ""

                # Only calculate and log costs for known models
                if model in self.PRICING:
                    input_tokens = sum(
                        self.count_tokens(msg["content"], model=model)
                        for msg in messages
                    )
                    output_tokens = self.count_tokens(output_text, model=model)

                    pricing = self.PRICING[model]
                    input_cost, output_cost, total_cost = pricing.calculate_costs(
                        input_tokens, output_tokens
                    )

                    logging.info(
                        f"\n{'-'*40}\n"
                        f"{'Model':<15}: {model}\n"
                        f"{'Input Tokens':<15}: {input_tokens:,}\n"
                        f"{'Output Tokens':<15}: {output_tokens:,}\n"
                        f"{'Input Cost':<15}: ${input_cost:.6f}\n"
                        f"{'Output Cost':<15}: ${output_cost:.6f}\n"
                        f"{'Total Cost':<15}: ${total_cost:.6f}\n"
                        f"{'-'*40}"
                    )
                else:
                    logging.info(
                        f"\n{'-'*40}\n"
                        f"{'Model':<15}: {model}\n"
                        f"{'Cost Tracking':<15}: Disabled (unknown model)\n"
                        f"{'-'*40}"
                    )

                return output_text

            except openai.RateLimitError as e:
                if attempt >= max_retries:
                    raise RateLimitExceededError(
                        f"Rate limit exceeded after {max_retries} attempts: {str(e)}"
                    ) from e

                wait_time = retry_delay * (2 ** (attempt - 1))  # Exponential backoff
                logging.warning(
                    f"Rate limit exceeded. Retrying in {wait_time} seconds... (Attempt {attempt}/{max_retries})"
                )
                import time

                time.sleep(wait_time)
            except openai.APITimeoutError as e:
                if attempt >= max_retries:
                    raise APITimeoutError(
                        f"API request timed out after {max_retries} attempts: {str(e)}"
                    ) from e

                wait_time = retry_delay * (2 ** (attempt - 1))
                logging.warning(
                    f"API timeout. Retrying in {wait_time} seconds... (Attempt {attempt}/{max_retries})"
                )
                import time

                time.sleep(wait_time)
            except openai.APIConnectionError as e:
                if attempt >= max_retries:
                    raise APIConnectionError(
                        f"API connection failed after {max_retries} attempts: {str(e)}"
                    ) from e

                wait_time = retry_delay * (2 ** (attempt - 1))
                logging.warning(
                    f"API connection error. Retrying in {wait_time} seconds... (Attempt {attempt}/{max_retries})"
                )
                import time

                time.sleep(wait_time)
            except openai.APIError as e:
                if 500 <= getattr(e, "status_code", 0) < 600:
                    if attempt >= max_retries:
                        raise ServerError(
                            f"OpenAI server error after {max_retries} attempts: {str(e)}"
                        ) from e
                    wait_time = retry_delay * (2 ** (attempt - 1))
                    logging.warning(
                        f"Server error. Retrying in {wait_time} seconds... (Attempt {attempt}/{max_retries})"
                    )
                    import time

                    time.sleep(wait_time)
                elif 400 <= getattr(e, "status_code", 0) < 500:
                    raise ClientError(f"Client error: {str(e)}") from e
                else:
                    raise ChatCompletionError(f"API error: {str(e)}") from e

            except Exception as e:
                raise ChatCompletionError(f"Chat completion failed: {str(e)}") from e

        # Add this line to handle the case when all retries fail but no exception is raised
        raise ChatCompletionError(
            f"Chat completion failed after {max_retries} attempts"
        )

    def context_assistant(self, prompt: str) -> str:
        """
        Generate a response using the assistant API.

        Note: This is a placeholder for future implementation.
        Currently returns an empty string as the feature is not implemented.

        Args:
            prompt: The input prompt

        Returns:
            Empty string (feature not implemented)
        """
        logging.warning("Assistant API support is not implemented")
        return ""
