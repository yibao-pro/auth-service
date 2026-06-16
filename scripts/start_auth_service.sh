#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

HOST="${AUTH_SERVICE_HOST:-0.0.0.0}"
PORT="${AUTH_SERVICE_PORT:-8004}"

cd "${SERVICE_ROOT}"

exec uvicorn api.app:app --host "${HOST}" --port "${PORT}"
