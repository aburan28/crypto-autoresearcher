#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -lt 1 ]; then
  echo 'Usage: run_batch.sh OUTPUT_DIRECTORY [PUBLIC_BATCH_SEED] [WORKERS]' >&2
  exit 2
fi
task_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
task_python="${RESEARCH_PYTHON:-$task_dir/.venv/bin/python}"
batch_output="$1"
batch_seed="${2:-solinas-generator-cohorts-20261012}"
batch_workers="${3:-3}"
mkdir -p -- "$batch_output"
"$task_python" -u "$task_dir/research.py" run --output "$batch_output" --seed "$batch_seed" --workers "$batch_workers"
"$task_python" -u "$task_dir/research.py" verify --output "$batch_output"
"$task_python" -u "$task_dir/research.py" analyze --output "$batch_output"
