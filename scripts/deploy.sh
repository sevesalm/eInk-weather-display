#!/bin/bash

set -euxo pipefail

source scripts/config.env

# This copies all needed files (and a bit more) on Raspberry
rsync -av --rsync-path="sudo rsync" --delete ./${APP_NAME} ${HOSTNAME}:${APP_ROOT_DIRECTORY}
rsync -av --rsync-path="sudo rsync" scripts/run.sh scripts/start_tmux_session.sh scripts/config.env ${HOSTNAME}:${APP_DIRECTORY}

ssh ${HOSTNAME} "cd ${APP_DIRECTORY}; ./start_tmux_session.sh"
