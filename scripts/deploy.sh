#!/bin/bash

# Installs uv, Python and the Python dependencies on Raspberry, copies the app over and (re)starts it as a systemd service.
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
SERVICE_NAME=eink-weather
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
rsync -av --rsync-path="sudo rsync" --delete --exclude "logger.log*" --exclude "svg_icons/README.md" --exclude "svg_icons/archive" ./${APP_NAME} ${HOSTNAME}:${APP_ROOT_DIRECTORY}

# Service. Runs as root, which the BCM2835 display library (/dev/mem) and bleson Bluetooth need.
# Paths are resolved on Raspberry since config.env may use paths relative to the SSH user's home.
ssh ${HOSTNAME} SERVICE_NAME=${SERVICE_NAME} APP_DIRECTORY=${APP_DIRECTORY} VENV_DIRECTORY=${VENV_DIRECTORY} 'bash -s' <<'ENDSSH'
  set -euo pipefail
  APP_DIRECTORY=$(realpath "$APP_DIRECTORY")
  VENV_DIRECTORY=$(realpath "$VENV_DIRECTORY")
  sudo tee /etc/systemd/system/${SERVICE_NAME}.service >/dev/null <<EOF
[Unit]
Description=eInk weather display
Wants=network-online.target
After=network-online.target time-sync.target

[Service]
WorkingDirectory=${APP_DIRECTORY}
Environment=RUUVI_BLE_ADAPTER=bleson
Environment=PYTHONUNBUFFERED=1
ExecStart=${VENV_DIRECTORY}/bin/python ${APP_DIRECTORY}/weather-display.py
# Always, since the app logs errors and exits with status 0
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
EOF
  # Stop the app if it was started in tmux by an older version of this script
  tmux kill-session -t eInk-weather-display 2>/dev/null || true
  sudo systemctl daemon-reload
  sudo systemctl enable ${SERVICE_NAME}
  sudo systemctl restart ${SERVICE_NAME}
ENDSSH
