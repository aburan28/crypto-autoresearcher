#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
TASK_VENV="${1:-$TASK_DIR/.venv}"
python3 -m venv "$TASK_VENV"
"$TASK_VENV/bin/python" -m pip install -r "$TASK_DIR/requirements.txt"
"$TASK_VENV/bin/python" -c 'import ctypes; ctypes.CDLL("libcrypto.so.3")'
command -v cc >/dev/null
test -f /usr/include/openssl/ec.h
"$TASK_VENV/bin/python" -m unittest discover -s "$TASK_DIR/tests" -v
