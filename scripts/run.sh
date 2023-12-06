#!/bin/bash

set -euxo pipefail

source ./config.env

. ${VENV_DIRECTORY}/bin/activate
sudo RUUVI_BLE_ADAPTER="Bleson" ${VENV_DIRECTORY}/bin/python ${APP_DIRECTORY}/weather-display.py; exec ${SHELL}  # Leaves the tmux session running so we can see errors
