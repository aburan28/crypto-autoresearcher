#!/usr/bin/env bash
set -u
LOG=/tmp/instrument_rebuild.log
run() { echo "" | tee -a "$LOG"; echo "\$ $*" | tee -a "$LOG"; "$@" 2>&1 | tee -a "$LOG"; echo "[exit ${PIPESTATUS[0]}]" | tee -a "$LOG"; }
echo "" | tee -a "$LOG"
echo "=== ROUTE 4 g6k build started $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" | tee -a "$LOG"
rm -rf /tmp/g6kbuild && mkdir -p /tmp/g6kbuild && cd /tmp/g6kbuild || exit 1
run /tmp/sagevenv/bin/pip download --no-deps --no-binary :all: --no-build-isolation g6k
run tar xzf g6k-0.1.2.tar.gz
cd g6k-0.1.2 || exit 1
run /tmp/sagevenv/bin/pip install --no-cache-dir --no-build-isolation .
echo "=== ROUTE 4 g6k build finished $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" | tee -a "$LOG"
