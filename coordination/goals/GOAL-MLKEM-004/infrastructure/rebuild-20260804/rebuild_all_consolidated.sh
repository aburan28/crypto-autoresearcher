#!/usr/bin/env bash
# Consolidated GOAL-MLKEM-004 instrument rebuild.
# Combines KN-TECH-14efa5 (the passagemath route) with the four additional
# fixes recorded in KN-TECH-797223, applied up front instead of on failure.
set -u

LOG=/tmp/instrument_rebuild.log
: > "$LOG"
run() {
  echo "" | tee -a "$LOG"
  echo "\$ $*" | tee -a "$LOG"
  "$@" 2>&1 | tee -a "$LOG"
  echo "[exit ${PIPESTATUS[0]}]" | tee -a "$LOG"
}

echo "=== consolidated rebuild started $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" | tee -a "$LOG"
run uname -a
run python3 --version

# KN-TECH-797223 fixes 1-3: the build dependencies whose absence caused three
# separate failures last time. sudo is available here, so install rather than
# work around.
run sudo apt-get update -qq
run sudo apt-get install -y -qq automake autoconf libtool m4 libgmp-dev python3.12-dev python3.12-venv

# With python3.12-venv present, KN-TECH-14efa5's original venv route works.
run rm -rf /tmp/sagevenv
run python3 -m venv /tmp/sagevenv
run /tmp/sagevenv/bin/pip install --no-cache-dir --upgrade pip
run /tmp/sagevenv/bin/pip install --no-cache-dir passagemath-standard

# KN-TECH-797223 fix 4: g6k imports pkg_resources, dropped in setuptools 81+.
run /tmp/sagevenv/bin/pip install --no-cache-dir "setuptools<81"
run /tmp/sagevenv/bin/pip install --no-cache-dir Cython
run /tmp/sagevenv/bin/pip install --no-cache-dir --no-build-isolation g6k

run /tmp/sagevenv/bin/python -c "import g6k; print('g6k import OK')"
echo "=== consolidated rebuild finished $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" | tee -a "$LOG"
