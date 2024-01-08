import configparser

from gpt.openai_chat import GPT

config = configparser.ConfigParser()
config.read("config.ini")
openaikey = config["moodle"]["openaikey"]
gpt = GPT()
gpt.api_key = openaikey

ptomz = """
What was my last message, if i didn't send you one, return "TOMATOE"
"""

# create a new assistant with context
assistant = gpt.context_assistant(prompt=ptomz)
print(assistant)

# generate a new thread
thread_id = gpt.create_thread()
print(thread_id)
# update the thread
gpt.update_thread(thread_id)
# run the assistant in new thread (no context from first conversation)
assistant = gpt.context_assistant(prompt=ptomz)
print(assistant)
