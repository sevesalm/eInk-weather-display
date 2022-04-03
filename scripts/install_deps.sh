#!/bin/bash

set -euxo pipefail

source scripts/config.env

ssh $HOSTNAME "mkdir -p $VENV_ROOT_DIRECTORY"
rsync -av --delete requirements.txt $HOSTNAME:$VENV_ROOT_DIRECTORY
ssh $HOSTNAME "cd $VENV_ROOT_DIRECTORY && python -m venv $VENV_NAME"
ssh $HOSTNAME "source $VENV_DIRECTORY/bin/activate && pip install -r $VENV_ROOT_DIRECTORY/requirements.txt && rm $VENV_ROOT_DIRECTORY/requirements.txt"
