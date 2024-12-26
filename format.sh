#! /bin/bash

isort .
black .
black --check .
flake8 .
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
mypy --ignore-missing-imports --exclude notification/discord.py --exclude utils/logo.py --exclude src/turndown/turndown.py --exclude example --exclude main.py --exclude moodle/moodle_notification_handler.py --follow-imports=skip .