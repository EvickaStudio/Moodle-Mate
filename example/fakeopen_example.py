from gpt.fakeopen_chat import FGPT

gpt = FGPT()

response = gpt.chat_completion(
    system_message="You are a helpful assistant.",
    user_message="How are you?",
    model="gpt-4-1106-preview",
)
print(response)
# Thank you for asking! As a computer program, I don't have feelings, but I'm here and ready to assist you. How can I help you today?
