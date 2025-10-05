#!/usr/bin/env bash

set -euo pipefail

CHECK_POSTGRES=false
CHECK_REDIS=false

: "${WAIT_FOR_COMMAND_SCRIPT:=/app/data/scripts/wait-for-command.sh}"
: "${POSTGRES_HOST:=postgres}"
: "${POSTGRES_PORT:=5432}"
: "${REDIS_HOST:=redis}"
: "${REDIS_PORT:=6379}"

set +e
options=$(
  getopt -o '' \
    --l postgres \
    --l redis \
    -- "$@"
)
# shellcheck disable=SC2181
[[ $? -eq 0 ]] || {
  echo "Incorrect options provided"
  exit 1
}
set -e

eval set -- "${options}"

while true; do
  case "$1" in
  --postgres)
    CHECK_POSTGRES=true;
    shift
    ;;
  --redis)
    CHECK_REDIS=true;
    shift
    ;;
  --)
    shift
    break
    ;;
  *)
    break
    ;;
  esac
done

function postgres_ready() {
  sh "${WAIT_FOR_COMMAND_SCRIPT}" -t 5 -c "nc -z $POSTGRES_HOST $POSTGRES_PORT"
}

function redis_ready() {
  sh "${WAIT_FOR_COMMAND_SCRIPT}" -t 5 -c "nc -z $REDIS_HOST $REDIS_PORT"
}

function main() {
  if [ "${CHECK_POSTGRES}" == "true" ]; then
    until postgres_ready; do
      echo >&2 "Postgres is unavailable - sleeping"
    done
    echo >&2 "Postgres is up - continuing..."
  fi
  if [ "${CHECK_REDIS}" == "true" ]; then
    until redis_ready; do
      echo >&2 "Redis is unavailable - sleeping"
    done
    echo >&2 "Redis is up - continuing..."
  fi
}

main
