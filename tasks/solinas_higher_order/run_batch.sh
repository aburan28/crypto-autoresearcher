#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
TASK_PYTHON="${RESEARCH_PYTHON:-$TASK_DIR/.venv/bin/python}"
exec "$TASK_PYTHON" "$TASK_DIR/research.py" batch "$@"
