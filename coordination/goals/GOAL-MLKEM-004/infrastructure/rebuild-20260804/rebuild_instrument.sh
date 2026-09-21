#!/usr/bin/env bash
# Rebuild the GOAL-MLKEM-004 instrument per knowledge/techniques/KN-TECH-14efa5.md.
# Every command and its combined stdout+stderr is echoed verbatim.
#
# Deviation from the recipe, recorded rather than hidden: this container's
# python3.12 has no ensurepip, so `python3 -m venv /tmp/sagevenv` cannot create a
# venv with pip (see the ROUTE 1 block, kept in the log). ROUTE 2 below bridges
# that with virtualenv, which vendors its own pip wheel. Everything after venv
# creation follows KN-TECH-14efa5 unchanged.
set -u

LOG=/tmp/instrument_rebuild.log

run() {
  echo "" | tee -a "$LOG"
  echo "\$ $*" | tee -a "$LOG"
  "$@" 2>&1 | tee -a "$LOG"
  echo "[exit ${PIPESTATUS[0]}]" | tee -a "$LOG"
}

echo "" | tee -a "$LOG"
echo "=== ROUTE 2 (virtualenv bootstrap) started $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" | tee -a "$LOG"
echo "ROUTE 1 (python3 -m venv, the KN-TECH-14efa5 route) FAILED above: ensurepip absent." | tee -a "$LOG"

run rm -rf /tmp/sagevenv
run pip3 install --user --break-system-packages --no-cache-dir virtualenv
run python3 -m virtualenv -p python3.12 /tmp/sagevenv
run /tmp/sagevenv/bin/python --version
run /tmp/sagevenv/bin/pip --version

# KN-TECH-14efa5: passagemath-standard, not sagemath-standard.
run /tmp/sagevenv/bin/pip install --no-cache-dir passagemath-standard

# Fix 2 from the recipe: supply the missing -dev symlink for libgmp, no root needed.
mkdir -p /tmp/gmplink
run ln -sf /usr/lib/x86_64-linux-gnu/libgmp.so.10 /tmp/gmplink/libgmp.so
export LIBRARY_PATH="/tmp/gmplink:${LIBRARY_PATH:-}"
export LDFLAGS="-L/tmp/gmplink"
echo "\$ export LIBRARY_PATH=/tmp/gmplink:\$LIBRARY_PATH LDFLAGS=-L/tmp/gmplink" | tee -a "$LOG"

# Fix 1 from the recipe: build isolation hides Cython.
run /tmp/sagevenv/bin/pip install --no-cache-dir Cython
run /tmp/sagevenv/bin/pip install --no-cache-dir --no-build-isolation g6k

run /tmp/sagevenv/bin/pip list

echo "=== ROUTE 2 finished $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" | tee -a "$LOG"
