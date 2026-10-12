#!/usr/bin/env bash
set -euo pipefail
# Requires Python 3.10+, a C compiler, and OpenSSL development headers.
# Debian/Ubuntu: sudo apt-get install python3-venv build-essential libssl-dev
task_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
python3 -m venv "$task_dir/.venv"
"$task_dir/.venv/bin/python" -m pip install -r "$task_dir/requirements.txt"
"$task_dir/.venv/bin/python" -m unittest discover -s "$task_dir/tests" -v
