import configparser
import logging

from openai_chat import GPT

config = configparser.ConfigParser()
config.read("config.ini")
openaikey = config["moodle"]["openaikey"]
gpt = GPT()
gpt.apiKey = openaikey

ptomz = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Aliquam sit amet ipsum sed velit vulputate aliquet.
Sed in magna sit amet turpis volutpat luctus.
"""

assistant = gpt.assistant(prompt=ptomz)
print(assistant)