#!/bin/bash

set -euxo pipefail

source scripts/config.env

PYTHON_VERSION=3.14
UV='~/.local/bin/uv' # Full path since ~/.local/bin is not in PATH for non-interactive SSH sessions

ssh $HOSTNAME "test -x $UV || (set -o pipefail && curl -LsSf https://astral.sh/uv/install.sh | sh)"
ssh $HOSTNAME "mkdir -p $VENV_ROOT_DIRECTORY"
rsync -av --delete requirements $HOSTNAME:$VENV_ROOT_DIRECTORY
ssh $HOSTNAME "cd $VENV_ROOT_DIRECTORY && $UV venv --clear --python $PYTHON_VERSION $VENV_NAME"
ssh $HOSTNAME "$UV pip install --compile-bytecode --python $VENV_DIRECTORY -r $VENV_ROOT_DIRECTORY/requirements/raspberry.txt && rm -rf $VENV_ROOT_DIRECTORY/requirements"
