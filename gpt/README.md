# OpenAI Chat Completion Module

## Overview

This module, `openai_chat.py`, provides an interface to OpenAI's API for integrating chat functionalities using GPT-3.5-Turbo and GPT-4 modelss.

## Installation

Install OpenAI Python library:

```bash
pip install openai
```

## Usage

### Initialize

Create a `GPT` class instance:

```python
from openai_chat import GPT

gpt = GPT()
```

### Set API Key

Set your OpenAI API key:

```python
gpt.apiKey = "your_openai_api_key"
```

### Chat Completion

Generate a response using a model, system message, and user message:

```python
response = gpt.chat_completion(
    model="gpt-3.5-turbo",
    systemMessage="Your system message",
    userMessage="Your user message"
)
print(response)
```

## Dependencies

- Requires `openai` library (v1.3.6 for current api version)
