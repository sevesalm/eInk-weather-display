#!/bin/bash

set -euxo pipefail

source scripts/config.env

ssh $HOSTNAME "mkdir -p $VENV_ROOT_DIRECTORY"
rsync -av --delete requirements $HOSTNAME:$VENV_ROOT_DIRECTORY
ssh $HOSTNAME "cd $VENV_ROOT_DIRECTORY && python -m venv $VENV_NAME"
ssh $HOSTNAME "source $VENV_DIRECTORY/bin/activate && pip install -r $VENV_ROOT_DIRECTORY/requirements/raspberry.txt && rm -rf $VENV_ROOT_DIRECTORY/requirements"
