from fakeopen_chat import FGPT

gpt = FGPT()
response = gpt.chat_completion(
    systemMessage="You are a helpful assistant.", userMessage="How are you?"
)
print(response)
