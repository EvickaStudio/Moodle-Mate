<!--
 Copyright 2024 EvickaStudio
 
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
 
     http://www.apache.org/licenses/LICENSE-2.0
 
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
-->

Example:

````ini
[moodle]
; Moodle URL for API access
moodleUrl = https://subdomain.example.com/
; Username and password for Moodle login
username = 123456
password = password
; API key for OpenAI and Pushbullet
openaikey = sk-xxxxx
pushbulletkey = o.xxxxx
; Activate or deactivate Pushbullet and Discord
pushbulletState = 0 ; 1: Activated, 0: Deactivated
webhookState = 1
; Discord webhook URL
webhookUrl = https://discord.com/api/webhooks/xxxxx/xxxxx
; System message for GPT-3 summarization
systemMessage = "YOUR SYSTEM PROMPT HERE, EXAMPLE IN config_example.ini"
; Set GPT model, standard gpt-3.5-turbo
model = gpt-3.5-turbo
; If fake open set to 1 then the bot uses the fakeopen API to generate the summary
fakeopen = 1
; If summary with GPT is set to 1, else 0
summary = 1
````