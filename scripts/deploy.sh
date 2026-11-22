#!/bin/bash

# Installs uv, Python and the Python dependencies on Raspberry, copies the app over and (re)starts it as a systemd service.
# Usage: scripts/deploy.sh [--fresh]
#   --fresh  Recreate the virtual env from scratch (e.g. after a Python upgrade or if it is broken)

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

# Share one SSH connection between all ssh and rsync calls so the handshake is done only once.
# The socket goes in a short path under /tmp since Unix socket paths are limited to ~100 characters on macOS.
SSH_CONTROL_DIR=$(mktemp -d /tmp/deploy-ssh.XXXXXX)
SSH="ssh -o ControlMaster=auto -o ControlPath=${SSH_CONTROL_DIR}/%C -o ControlPersist=60"
trap '$SSH -O exit $HOSTNAME 2>/dev/null; rm -rf "$SSH_CONTROL_DIR"' EXIT

# Copy the requirements and the app. The app copy includes all needed files (and a bit more).
rsync -av -e "$SSH" --rsync-path="mkdir -p $VENV_ROOT_DIRECTORY && rsync" --delete requirements $HOSTNAME:$VENV_ROOT_DIRECTORY
rsync -av -e "$SSH" --rsync-path="sudo rsync" --delete --exclude "logger.log*" --exclude "svg_icons/README.md" --exclude "svg_icons/archive" ./${APP_NAME} ${HOSTNAME}:${APP_ROOT_DIRECTORY}

# Install dependencies and (re)start the service
$SSH $HOSTNAME FRESH=$FRESH PYTHON_VERSION=$PYTHON_VERSION SERVICE_NAME=$SERVICE_NAME APP_DIRECTORY=$APP_DIRECTORY VENV_ROOT_DIRECTORY=$VENV_ROOT_DIRECTORY VENV_DIRECTORY=$VENV_DIRECTORY 'bash -s' <<'ENDSSH'
  set -euxo pipefail
  UV=~/.local/bin/uv # Full path since ~/.local/bin is not in PATH for non-interactive SSH sessions

  # Dependencies
  test -x $UV || curl -LsSf https://astral.sh/uv/install.sh | sh
  if [ "$FRESH" = true ]; then
    $UV venv --clear --python $PYTHON_VERSION $VENV_DIRECTORY
  else
    test -d $VENV_DIRECTORY || $UV venv --python $PYTHON_VERSION $VENV_DIRECTORY
  fi
  # Sync makes the venv match the requirements exactly, removing dropped packages. The requirements only pin
  # the direct dependencies and sync installs only what is listed, so first resolve the full set for this Python.
  $UV pip compile --quiet --python $VENV_DIRECTORY -o $VENV_ROOT_DIRECTORY/requirements/raspberry.lock.txt $VENV_ROOT_DIRECTORY/requirements/raspberry.txt
  $UV pip sync --compile-bytecode --python $VENV_DIRECTORY $VENV_ROOT_DIRECTORY/requirements/raspberry.lock.txt
  rm -rf $VENV_ROOT_DIRECTORY/requirements

  # Service. Runs as root, which the BCM2835 display library (/dev/mem) and bleson Bluetooth need.
  # Paths are resolved here since config.env may use paths relative to the SSH user's home.
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
