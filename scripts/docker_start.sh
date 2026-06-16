#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${SERVICE_ROOT}"

python scripts/wait_for_db.py

if [[ "${INIT_DB_ON_START:-true}" == "true" ]]; then
  python scripts/init_db.py
fi

exec python -m uvicorn api.app:app --host "${AUTH_SERVICE_HOST:-0.0.0.0}" --port "${AUTH_SERVICE_PORT:-8004}"
