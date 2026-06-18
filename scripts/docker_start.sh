#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${SERVICE_ROOT}"

python scripts/wait_for_db.py

if [[ "${INIT_DB_ON_START:-true}" == "true" ]]; then
  python scripts/init_db.py
fi

exec python -m api.grpc_server
