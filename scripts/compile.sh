# This script copies C source code to Raspberry Pi, compiles the shared library and fetches it back

set -euxo pipefail

source scripts/config.env

rsync -av --delete clib clib78 ${HOSTNAME}:${APP_ROOT_DIRECTORY}
ssh ${HOSTNAME} DIRECTORY=${APP_ROOT_DIRECTORY} 'bash -s' <<'ENDSSH'
  cd ${DIRECTORY}/clib78
  make
  cd ${DIRECTORY}/clib
  make
ENDSSH

rsync -v ${HOSTNAME}:"${APP_ROOT_DIRECTORY}/clib78/epd78.so ${APP_ROOT_DIRECTORY}/clib/epd37.so" eInk-weather-display/lib
