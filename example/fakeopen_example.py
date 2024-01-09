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

from gpt.fakeopen_chat import FGPT

gpt = FGPT()

response = gpt.chat_completion(
    system_message="You are a helpful assistant.",
    user_message="How are you?",
    model="gpt-4-1106-preview",
)
print(response)
# Thank you for asking! As a computer program, I don't have feelings, but I'm here and ready to assist you. How can I help you today?
