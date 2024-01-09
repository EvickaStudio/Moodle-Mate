# Copyright 2024 EvickaStudio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
