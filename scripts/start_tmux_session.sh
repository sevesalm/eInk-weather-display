#!/bin/bash

set -uxo pipefail

source ./config.env

# Check if the session already exists
tmux has-session -t ${SESSION_NAME}

if [ $? == 0 ]; then
  # Delete the old session if it exists
  tmux kill-session -t ${SESSION_NAME}
fi

tmux new-session -d -s ${SESSION_NAME} ./run.sh

# Scroll with the mouse wheel instead of sending arrow keys to the app
tmux set-option -t ${SESSION_NAME} mouse on
