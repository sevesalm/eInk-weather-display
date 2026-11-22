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

SERVICE_NAME=eink-weather

# Share one SSH connection between all ssh and rsync calls so the handshake is done only once.
# The socket goes in a short path under /tmp since Unix socket paths are limited to ~100 characters on macOS.
SSH_CONTROL_DIR=$(mktemp -d /tmp/deploy-ssh.XXXXXX)
SSH="ssh -o ControlMaster=auto -o ControlPath=${SSH_CONTROL_DIR}/%C -o ControlPersist=60"
trap '$SSH -O exit $HOSTNAME 2>/dev/null; rm -rf "$SSH_CONTROL_DIR"' EXIT

# Copy the app and the uv project files (pyproject.toml, uv.lock, .python-version) into the app directory.
# The copy includes all needed files (and a bit more).
rsync -av -e "$SSH" --rsync-path="sudo rsync" --delete --exclude "logger.log*" --exclude "svg_icons/README.md" --exclude "svg_icons/archive" ./${APP_NAME}/ pyproject.toml uv.lock .python-version ${HOSTNAME}:${APP_DIRECTORY}/

# Install dependencies and (re)start the service
$SSH $HOSTNAME FRESH=$FRESH SERVICE_NAME=$SERVICE_NAME APP_DIRECTORY=$APP_DIRECTORY VENV_DIRECTORY=$VENV_DIRECTORY 'bash -s' <<'ENDSSH'
  set -euxo pipefail
  UV=~/.local/bin/uv # Full path since ~/.local/bin is not in PATH for non-interactive SSH sessions
  # Resolve the paths since config.env may use paths relative to the SSH user's home. -m since the venv may not exist yet.
  APP_DIRECTORY=$(realpath "$APP_DIRECTORY")
  VENV_DIRECTORY=$(realpath -m "$VENV_DIRECTORY")

  # Dependencies. uv sync installs the Python version in .python-version, creates the venv if needed and makes it
  # match uv.lock exactly, removing dropped packages. --frozen installs from uv.lock as is, without re-resolving.
  test -x $UV || curl -LsSf https://astral.sh/uv/install.sh | sh
  if [ "$FRESH" = true ]; then
    rm -rf $VENV_DIRECTORY
  fi
  cd $APP_DIRECTORY
  UV_PROJECT_ENVIRONMENT=$VENV_DIRECTORY $UV sync --frozen --no-dev --group raspberry --compile-bytecode

  # Service. Runs as root, which the BCM2835 display library (/dev/mem) and bleson Bluetooth need.
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
  # Keep the systemd journal in RAM only to reduce SD card wear. Logs are lost on reboot; warnings and errors
  # are also in logger.log. journald is restarted only when the setting changes.
  JOURNALD_CONF=/etc/systemd/journald.conf.d/eink-weather-volatile.conf
  if ! printf '[Journal]\nStorage=volatile\n' | cmp -s - $JOURNALD_CONF; then
    sudo mkdir -p $(dirname $JOURNALD_CONF)
    printf '[Journal]\nStorage=volatile\n' | sudo tee $JOURNALD_CONF >/dev/null
    sudo systemctl restart systemd-journald
  fi

  # Stop the app if it was started in tmux by an older version of this script
  tmux kill-session -t eInk-weather-display 2>/dev/null || true
  sudo systemctl daemon-reload
  sudo systemctl enable ${SERVICE_NAME}
  sudo systemctl restart ${SERVICE_NAME}
ENDSSH
