from fakeopen_chat_stream import FGPT

gpt = FGPT()
response = gpt.chat_completion(
    system_message="You are a helpful assistant.", user_message="How are you?"
)
