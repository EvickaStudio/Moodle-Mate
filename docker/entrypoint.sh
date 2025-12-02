#!/bin/bash
set -euo pipefail

STATE_DIR="${MOODLE_STATE_DIR:-/app/state}"
SESSION_FILE="${MOODLE_SESSION_FILE:-${STATE_DIR%/}/moodle_session.json}"
LOG_DIR="${MOODLE_LOG_DIR:-/app/logs}"

mkdir -p "$STATE_DIR" "$LOG_DIR" "$(dirname "$SESSION_FILE")"
touch "$SESSION_FILE"

chown -R moodlemate:moodlemate "$STATE_DIR" "$LOG_DIR" "$(dirname "$SESSION_FILE")" "$SESSION_FILE"

exec gosu moodlemate "$@"

