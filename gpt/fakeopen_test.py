from fakeopen_chat import FGPT

gpt = FGPT()

response = gpt.chat_completion(
    system_message="You are a helpful assistant.",
    user_message="How are you?",
    model="gpt-4-1106-preview"
)
print(response)