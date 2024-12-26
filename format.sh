#! /bin/bash

isort .
black .
clear
# wait for 1 second
sleep 1
flake8 .
mypy --ignore-missing-imports --exclude notification/discord.py --exclude utils/logo.py --exclude src/turndown/turndown.py --exclude example --exclude main.py --exclude moodle/moodle_notification_handler.py --follow-imports=skip .