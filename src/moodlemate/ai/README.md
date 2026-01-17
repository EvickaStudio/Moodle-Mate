# OpenAI Chat/Assistant Module

## Overview

This module provides a robust interface to OpenAI's API for integrating chat or assistant functionalities using GPT models.

## Installation

Install and update the OpenAI Python library:

```bash
pip install -U openai tiktoken
```

## Usage

### Initialize

Create a `GPT` class instance:

```python
from moodlemate.ai import GPT

gpt = GPT()
```

### Set API Key

Set your OpenAI API key:

```python
gpt.api_key = "your_openai_api_key"
```

### Set Custom Endpoint (Optional)

Set a custom API endpoint if needed:

```python
gpt.endpoint = "https://your-custom-endpoint.com/v1/"
```

### Chat Completion

Generate a response using a model, system message, and user message:

```python
response = gpt.chat_completion(
    model="gpt-4o-mini",
    system_message="Your system message",
    user_message="Your user message",
    temperature=0.7,
    max_tokens=None  # Optional limit
)
print(response)
```

<!-- ### Context Assistant

Use the assistant with context awareness (placeholder for future implementation):

```python
response = gpt.context_assistant(prompt="Your prompt message")
print(response)
``` -->

## Error Handling

The module includes robust error handling with automatic retries for transient errors:

- Rate limit errors: Automatically retries with exponential backoff
- API timeouts: Automatically retries with exponential backoff
- Connection errors: Automatically retries with exponential backoff
- Server errors (5xx): Automatically retries with exponential backoff
- Client errors (4xx): Raises appropriate exceptions

This makes the module suitable for 24/7 operation without manual intervention.

## Supported Models

The module supports various OpenAI models with built-in cost tracking:

- GPT-4o (`gpt-4o`)
- GPT-4o-mini (`gpt-4o-mini`)
- O1 (`o1`)
- O1-mini (`o1-mini`)
- O3-mini (`o3-mini`)

## Function Descriptions

### `api_key(self, key: str) -> None:`

Set and validate the API key, ensuring it is not empty and matches the expected format.

### `endpoint(self, url: str) -> None:`

Set a custom API endpoint URL for using services like Ollama or OpenRouter.

### `chat_completion(self, model: str, system_message: str, user_message: str, temperature: float = 0.7, max_tokens: Optional[int] = None) -> str:`

Generate a response from the chat API using the specified model and prompts. Includes automatic retries for transient errors.

### `count_tokens(self, text: str, model: str = "gpt-4o-mini") -> int:`

Count the number of tokens in the given text for the specified model.

### `context_assistant(self, prompt: str) -> str:`

A context-aware assistant (placeholder for future implementation).

## Dependencies

- `openai` (version 1.5+)
- `tiktoken`
