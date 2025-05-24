import logging
import random
import re
import time

import openai  # version 1.5
from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
import tiktoken

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
    Provides an interface to OpenAI's GPT models for chat completions.

    This class encapsulates the logic for interacting with the OpenAI API,
    including API key management, endpoint configuration, token counting,
    cost estimation (basic), and robust error handling for common API issues.
    It is implemented as a singleton to ensure a single, shared instance for
    API interactions.

    Key features:
    - API key and custom endpoint configuration.
    - Token counting using `tiktoken` for specified models.
    - Basic cost tracking for supported models (USD per 1M tokens).
    - Typed error handling for various API and client-side issues (e.g.,
      `InvalidAPIKeyError`, `RateLimitExceededError`, `ChatCompletionError`).
    - Automatic retries for transient API errors during chat completion requests.

    Public methods of interest:
    - `api_key` (property): For setting and validating the OpenAI API key.
    - `endpoint` (property): For setting a custom API endpoint (e.g., for proxies or local models).
    - `count_tokens(text: str, model: str)`: To count tokens for a given text and model.
    - `chat_completion(...)`: To generate a chat response from the AI.
    - `context_assistant(...)`: A specialized method for generating context-aware assistant responses.

    Attributes:
        PRICING (dict[str, ModelPricing]): A class-level dictionary mapping model names
            (from `ModelType` enum) to `ModelPricing` objects, which store input and
            output token costs.
        _api_key (str | None): Internal storage for the API key.
        _endpoint (str | None): Internal storage for the custom API endpoint.
        _api_key_pattern (re.Pattern): Regex for basic API key format validation.

    Example:
        >>> gpt_instance = GPT() # Get singleton instance
        >>> try:
        ...     gpt_instance.api_key = "sk-YourActualOpenAIKey..." # Set your API key
        ...     # For custom endpoints (e.g. local LLM server or proxy):
        ...     # gpt_instance.endpoint = "http://localhost:1234/v1"
        ...     response = gpt_instance.chat_completion(
        ...         model=ModelType.GPT4O_MINI.value,
        ...         system_message="You are a helpful assistant.",
        ...         user_message="What is the capital of France?",
        ...         temperature=0.7,
        ...         max_tokens=50
        ...     )
        ...     print(f"AI Response: {response}")
        ...     tokens = gpt_instance.count_tokens(response, ModelType.GPT4O_MINI.value)
        ...     print(f"Response tokens: {tokens}")
        ... except InvalidAPIKeyError as e:
        ...     print(f"API Key Error: {e}")
        ... except ChatCompletionError as e:
        ...     print(f"Chat Error: {e}")
        ... except Exception as e:
        ...     print(f"An unexpected error occurred: {e}")
    """

    _instance = None

    def __new__(cls) -> "GPT":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
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
    def api_key(self) -> str | None:
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
                "Invalid API key format. Expected format: 'sk-' followed by 48+ alphanumeric characters",
            )

        self._api_key = key
        openai.api_key = key

    @property
    def endpoint(self) -> str | None:
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

        Raises:
            TypeError: If `url` is not a string.
            ValueError: If `url` is an empty string.
        """
        if not isinstance(url, str):
            raise TypeError("endpoint URL must be a string.")
        if not url:
            raise ValueError("endpoint URL cannot be empty.")

        self._endpoint = url
        openai.base_url = url

    def count_tokens(self, text: str, model: str = ModelType.GPT4O_MINI.value) -> int:
        """
        Count the number of tokens a given text string would occupy for a specific model.

        This method uses the `tiktoken` library to encode the text and determine
        the token count. It is useful for estimating API usage and costs before
        making an actual API call, or for ensuring prompts stay within model limits.

        Args:
            text (str): The text string to tokenize and count.
            model (str, optional): The OpenAI model name (e.g., "gpt-4o-mini", "gpt-4").
                Defaults to `ModelType.GPT4O_MINI.value`.
                The model specified affects how tokenization is performed.

        Returns:
            int: The number of tokens the text string translates to for the given model.

        Raises:
            TypeError: If `text` or `model` is not a string.
            ValueError: If `model` is an empty string.
            TokenizationError: If `tiktoken` fails to get an encoder for the model
                or if any other error occurs during tokenization.
        """
        if not isinstance(text, str):
            raise TypeError("Input text must be a string.")
        if not isinstance(model, str):
            raise TypeError("Model name must be a string.")
        if not model:
            raise ValueError("Model name cannot be empty.")

        try:
            encoder = tiktoken.encoding_for_model(model)
            return len(encoder.encode(text))
        except Exception as e:
            raise TokenizationError(
                f"Failed to count tokens for model {model}: {e!s}",
            ) from e

    def _validate_model(self, model: str) -> None:
        """
        Validate model and log warning if pricing info is unavailable.

        Args:
            model: The model name to validate
        """
        if model not in self.PRICING:
            logging.warning(
                f"Model '{model}' not in pricing database. Cost tracking will be disabled.",
            )

    def _validate_chat_completion_params(  # noqa: C901 - Complexity from handling multiple specific API errors
        self,
        model: str,
        system_message: str,
        user_message: str,
        temperature: float,
        max_tokens: int | None,
    ) -> None:
        """Validate parameters for the chat_completion method."""
        if not isinstance(model, str):
            raise TypeError("Model name must be a string.")
        if not model:
            raise ValueError("Model name cannot be empty.")
        if not isinstance(system_message, str):
            # Depending on API, empty system message might be allowed.
            # For now, just type check.
            raise TypeError("System message must be a string.")
        if not isinstance(user_message, str):
            raise TypeError("User message must be a string.")
        if not user_message:  # User message should not be empty
            raise ValueError("User message cannot be empty.")
        if not isinstance(temperature, float):
            raise TypeError("Temperature must be a float.")
        if not (0.0 <= temperature <= 2.0):  # OpenAI's typical range
            raise ValueError("Temperature must be between 0.0 and 2.0.")
        if max_tokens is not None:
            if not isinstance(max_tokens, int):
                raise TypeError("max_tokens must be an integer if provided.")
            if max_tokens <= 0:
                raise ValueError("max_tokens must be a positive integer if provided.")

    def chat_completion(
        self,
        model: str,
        system_message: str,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        """
        Generate a chat completion response from the specified OpenAI model.

        This method constructs a request to the OpenAI chat completions API,
        including system and user messages, temperature, and optional max tokens.
        It handles the underlying API call, including retries for transient errors,
        and extracts the content from the AI's response.

        Before making the API call, it validates the model name and logs a warning
        if pricing information for cost tracking is not available for the model.

        Args:
            model (str): The OpenAI model to use (e.g., `ModelType.GPT4O_MINI.value`,
                "gpt-4", "gpt-3.5-turbo").
            system_message (str): The initial system prompt that sets the context
                or behavior for the AI assistant.
            user_message (str): The user's input or query to the AI.
            temperature (float, optional): Controls the randomness of the output.
                Higher values (e.g., 0.8) make output more random, lower values
                (e.g., 0.2) make it more deterministic. Defaults to 0.7.
            max_tokens (int | None, optional): The maximum number of tokens to generate
                in the response. If None, the model's default will be used. Defaults to None.

        Returns:
            str: The content of the AI-generated message.

        Raises:
            TypeError: If `model`, `system_message`, or `user_message` are not strings,
                       or if `temperature` is not a float, or if `max_tokens` is not an int (when provided).
            ValueError: If `model` is empty, or `temperature` is outside typical range [0.0, 2.0],
                        or `max_tokens` is not positive (when provided).
            ChatCompletionError: If the chat completion process fails due to tokenization
                issues or other unhandled exceptions during the internal `_chat_completion` call.
            This method can also indirectly raise errors caught and re-wrapped by `_chat_completion`,
            such as `RateLimitExceededError`, `APITimeoutError`, `APIConnectionError`,
            `ServerError`, `ClientError`, and `InvalidAPIKeyError` if the API key is invalid
            at the time of the call.
        """
        self._validate_chat_completion_params(
            model,
            system_message,
            user_message,
            temperature,
            max_tokens,
        )
        self._validate_model(model)
        logging.info(f"Requesting chat completion using model: {model}")

        messages_payload = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]

        try:
            return self._chat_completion(
                messages_payload,
                model,
                temperature,
                max_tokens,
            )
        except TokenizationError as e:
            raise ChatCompletionError(f"Token counting failed: {e!s}") from e
        except Exception as e:
            if isinstance(e, ChatCompletionError):
                raise
            logging.error(f"Unexpected error in chat_completion method: {e!s}", exc_info=True)
            raise ChatCompletionError(f"Chat completion failed: {e!s}") from e

    def _prepare_typed_messages(
        self,
        messages: list[dict[str, str]],
    ) -> list[ChatCompletionMessageParam]:
        """Converts a list of message dicts to the OpenAI-expected typed format."""
        typed_messages: list[ChatCompletionMessageParam] = []
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")
            # Ensure content is a string, even if None or other types are passed via msg.get("content")
            # The ChatCompletionMessageParam expects content to be str.
            str_content = str(content) if content is not None else ""

            if role == "system":
                typed_messages.append({"role": "system", "content": str_content})
            elif role == "user":
                typed_messages.append({"role": "user", "content": str_content})
            elif role == "assistant":
                typed_messages.append({"role": "assistant", "content": str_content})
            else:
                logging.warning(
                    f"Unknown message role '{role}' encountered. Skipping message.",
                )
        return typed_messages

    def _log_completion_costs(
        self,
        model: str,
        typed_messages: list[ChatCompletionMessageParam],
        output_text: str,
    ) -> None:
        """Calculates and logs token counts and costs for a completion."""
        if model in self.PRICING:
            try:
                input_tokens = sum(
                    self.count_tokens(str(msg.get("content", "")), model=model) for msg in typed_messages
                )
                output_tokens = self.count_tokens(output_text, model=model)

                pricing = self.PRICING[model]
                input_cost, output_cost, total_cost = pricing.calculate_costs(
                    input_tokens,
                    output_tokens,
                )
                logging.info(
                    f"\n{'-' * 40}\n"
                    f"{'Model':<15}: {model}\n"
                    f"{'Input Tokens':<15}: {input_tokens:,}\n"
                    f"{'Output Tokens':<15}: {output_tokens:,}\n"
                    f"{'Input Cost':<15}: ${input_cost:.6f}\n"
                    f"{'Output Cost':<15}: ${output_cost:.6f}\n"
                    f"{'Total Cost':<15}: ${total_cost:.6f}\n"
                    f"{'-' * 40}",
                )
            except TokenizationError as e:
                logging.warning(f"Could not calculate token costs for model {model} due to tokenization error: {e!s}")
            except Exception as e:  # Catching other unexpected errors during cost calculation
                logging.error(f"Unexpected error during token cost calculation for model {model}: {e!s}", exc_info=True)
        else:
            logging.info(
                f"\n{'-' * 40}\n{'Model':<15}: {model}\n{'Cost Tracking':<15}: Disabled (unknown model)\n{'-' * 40}",
            )

    def _handle_api_error_with_retry(
        self,
        e: openai.APIError,
        attempt: int,
        max_retries: int,
        retry_delay_base: int,
        error_description: str,
    ) -> bool:
        """Handles retry logic for retryable API errors. Returns True if retry should occur."""
        if attempt < max_retries:
            jitter = random.uniform(0, 1)  # noqa: S311 - Jitter for retries is not for crypto
            wait_time = retry_delay_base * (2 ** (attempt - 1)) + jitter
            status_code_info = f" (Status: {e.status_code})" if hasattr(e, "status_code") and e.status_code else ""
            logging.warning(
                f"{error_description}{status_code_info}. Retrying in {wait_time:.2f} seconds... (Attempt {attempt}/{max_retries})",
            )
            time.sleep(wait_time)
            return True  # Indicate retry
        return False  # Indicate max retries reached, caller should raise

    def _make_openai_api_call(
        self,
        model: str,
        typed_messages: list[ChatCompletionMessageParam],
        temperature: float,
        max_tokens: int | None,
    ) -> str:
        """Makes the actual API call to OpenAI and handles initial response parsing."""
        response: ChatCompletion = openai.chat.completions.create(
            model=model,
            messages=typed_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        content = response.choices[0].message.content if response.choices and response.choices[0].message else None
        if content is None:
            logging.warning(
                f"OpenAI API returned null content for model {model}. Finish reason: {response.choices[0].finish_reason if response.choices else 'N/A'}",
            )
            output_text = ""
        else:
            output_text = content

        self._log_completion_costs(model, typed_messages, output_text)
        return output_text

    def _handle_openai_api_exception(  # noqa: C901 - Complexity from handling multiple specific API errors
        self,
        e: openai.APIError,
        attempt: int,
        max_retries: int,
        retry_delay_base: int,
    ) -> bool:  # Returns True if retry should be attempted, otherwise False (and appropriate exception is raised)
        """Handles specific OpenAI API errors, applying retry logic or raising specific custom errors."""
        # Retryable OpenAI API errors
        if isinstance(
            e,
            openai.RateLimitError | openai.APITimeoutError | openai.APIConnectionError | openai.InternalServerError,
        ):
            error_map = {
                openai.RateLimitError: ("Rate limit", RateLimitExceededError),
                openai.APITimeoutError: ("API timeout", APITimeoutError),
                openai.APIConnectionError: ("API connection error", APIConnectionError),
                openai.InternalServerError: ("OpenAI server error", ServerError),
            }
            error_desc, error_class = "Unknown retryable error", ChatCompletionError  # Defaults
            for error_type_key, (desc, err_class) in error_map.items():
                if isinstance(e, error_type_key):
                    error_desc, error_class = desc, err_class
                    break

            if self._handle_api_error_with_retry(e, attempt, max_retries, retry_delay_base, error_desc):
                return True  # Retry
            else:
                status_code_info = f" ({e.status_code})" if hasattr(e, "status_code") and e.status_code else ""
                raise error_class(f"{error_desc}{status_code_info} after {max_retries} attempts: {e!s}") from e

        # Non-retryable OpenAI API errors (typically 4xx client errors)
        elif isinstance(e, openai.AuthenticationError):  # HTTP 401
            raise InvalidAPIKeyError(f"OpenAI authentication error (401): {e!s}") from e
        elif isinstance(e, openai.NotFoundError):  # HTTP 404
            raise ClientError(f"OpenAI API endpoint or resource not found (404): {e!s}") from e
        elif isinstance(e, openai.PermissionDeniedError):  # HTTP 403
            raise ClientError(f"OpenAI permission denied (403): {e!s}") from e
        elif isinstance(e, openai.BadRequestError):  # HTTP 400
            raise ClientError(f"OpenAI bad request (400): {e!s}") from e
        elif isinstance(e, openai.UnprocessableEntityError):  # HTTP 422
            raise ClientError(f"OpenAI unprocessable entity (422): {e!s}") from e
        elif isinstance(e, openai.ConflictError):  # HTTP 409
            raise ClientError(f"OpenAI conflict error (409): {e!s}") from e
        # Catch-all for any other openai.APIError not specifically handled above
        else:
            logging.error(
                f"Unhandled OpenAI APIError (Status: {getattr(e, 'status_code', 'N/A')}). Error: {e!s}",
                exc_info=True,
            )
            if hasattr(e, "status_code") and 500 <= e.status_code < 600 and attempt < max_retries:
                if self._handle_api_error_with_retry(
                    e,
                    attempt,
                    max_retries,
                    retry_delay_base,
                    "Unhandled server-side OpenAI APIError",
                ):
                    return True  # Retry
            raise ClientError(f"Unhandled OpenAI APIError after processing: {e!s}") from e
        return False  # Should not be reached if an exception is raised

    def _chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int | None,
    ) -> str:
        """Internal method to handle chat completion requests with retries and error handling."""
        max_retries = 3
        retry_delay_base = 2  # seconds

        typed_messages = self._prepare_typed_messages(messages)
        if not typed_messages:
            raise ChatCompletionError("No valid messages to send after preparation.")

        for attempt in range(1, max_retries + 1):
            try:
                return self._make_openai_api_call(model, typed_messages, temperature, max_tokens)
            except openai.APIError as e:
                if self._handle_openai_api_exception(e, attempt, max_retries, retry_delay_base):
                    continue  # Proceed to next attempt if _handle_openai_api_exception indicated a retry
                # If not retrying, an exception would have been raised by _handle_openai_api_exception

            except TokenizationError:  # If self.count_tokens (called by _log_completion_costs) fails
                logging.error(
                    "TokenizationError during cost calculation within chat completion attempt.",
                    exc_info=True,
                )
                raise
            except Exception as e:  # Catch any other unexpected Python error
                if isinstance(e, ChatCompletionError):
                    raise
                logging.error(f"Unexpected Python error during chat completion attempt {attempt}: {e!s}", exc_info=True)
                raise ChatCompletionError(f"Unexpected internal error during chat completion attempt: {e!s}") from e

        raise ChatCompletionError(
            f"Chat completion failed after {max_retries} attempts (loop exhausted without specific error).",
        )

    def context_assistant(self, prompt: str) -> str:
        """
        Generate a context-aware assistant response using a predefined system message.

        This method is a specialized version of `chat_completion` that uses a fixed
        system message designed to make the AI act as a helpful context-aware assistant.
        It is useful for tasks where the AI needs to understand and respond to user
        input within a specific contextual framework, often related to analyzing or
        transforming the provided prompt text itself.

        Args:
            prompt (str): The user's input or query that requires a context-aware
                response from the assistant.

        Returns:
            str: The AI-generated assistant message.

        Raises:
            TypeError: If `prompt` is not a string.
            ValueError: If `prompt` is an empty string.
            ChatCompletionError: If the underlying chat completion process fails.
            Can also raise other errors inherited from `_chat_completion` like
            `InvalidAPIKeyError`, `RateLimitExceededError`, etc.
        """
        if not isinstance(prompt, str):
            raise TypeError("Prompt must be a string.")
        if not prompt:
            raise ValueError("Prompt cannot be empty.")

        system_message = "You are a helpful assistant."
        return self.chat_completion(
            model=ModelType.GPT4O_MINI.value,
            system_message=system_message,
            user_message=prompt,
            temperature=0.7,
            max_tokens=150,
        )
