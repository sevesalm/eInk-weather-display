#!/bin/bash

# Installs uv, Python and the Python dependencies on Raspberry, copies the app over and (re)starts it.
# Usage: scripts/deploy.sh [--fresh]
#   --fresh  Recreate the virtual env from scratch (e.g. after a Python upgrade or to remove stale packages)

set -euxo pipefail

source scripts/config.env

FRESH=false
for arg in "$@"; do
  case $arg in
    --fresh) FRESH=true ;;
    *) echo "Unknown argument: $arg" >&2; exit 1 ;;
  esac
done

PYTHON_VERSION=3.14
UV='~/.local/bin/uv' # Full path since ~/.local/bin is not in PATH for non-interactive SSH sessions

# Dependencies
ssh $HOSTNAME "test -x $UV || (set -o pipefail && curl -LsSf https://astral.sh/uv/install.sh | sh)"
ssh $HOSTNAME "mkdir -p $VENV_ROOT_DIRECTORY"
if [ "$FRESH" = true ]; then
  ssh $HOSTNAME "cd $VENV_ROOT_DIRECTORY && $UV venv --clear --python $PYTHON_VERSION $VENV_NAME"
else
  ssh $HOSTNAME "test -d $VENV_DIRECTORY || (cd $VENV_ROOT_DIRECTORY && $UV venv --python $PYTHON_VERSION $VENV_NAME)"
fi
rsync -av --delete requirements $HOSTNAME:$VENV_ROOT_DIRECTORY
ssh $HOSTNAME "$UV pip install --compile-bytecode --python $VENV_DIRECTORY -r $VENV_ROOT_DIRECTORY/requirements/raspberry.txt && rm -rf $VENV_ROOT_DIRECTORY/requirements"

# App. This copies all needed files (and a bit more) on Raspberry
rsync -av --rsync-path="sudo rsync" --delete --exclude "logger.log*" --exclude "svg_icons/preview" --exclude "svg_icons/archive" ./${APP_NAME} ${HOSTNAME}:${APP_ROOT_DIRECTORY}
rsync -av --rsync-path="sudo rsync" scripts/run.sh scripts/start_tmux_session.sh scripts/config.env ${HOSTNAME}:${APP_DIRECTORY}

ssh ${HOSTNAME} "cd ${APP_DIRECTORY}; ./start_tmux_session.sh"
