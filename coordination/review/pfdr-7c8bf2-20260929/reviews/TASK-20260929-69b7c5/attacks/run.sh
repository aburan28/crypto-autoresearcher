#!/bin/sh
# Declared launcher for every red-team computation (RT-2, RT-6).
# Usage: sh run.sh <script.py>   -> writes out/<script>.log (stdout+stderr)
# Single process, nice 19, one BLAS thread, no bytecode, 1 GB address-space cap.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
PY=/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/venv-ci/bin/python
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
mkdir -p "$HERE/out"
avail_kb=$(awk '/MemAvailable/ {print $2}' /proc/meminfo)
if [ "$avail_kb" -lt 3145728 ]; then echo "refusing: MemAvailable ${avail_kb} kB < 3 GB (RT-6)"; exit 3; fi
name=$(basename "$1" .py)
( ulimit -v 1048576; cd "$HERE" && nice -n 19 "$PY" "$1" ) > "$HERE/out/$name.log" 2>&1
tail -n 60 "$HERE/out/$name.log"
