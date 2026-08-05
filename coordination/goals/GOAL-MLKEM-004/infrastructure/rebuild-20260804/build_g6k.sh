#!/usr/bin/env bash
# g6k build, route 3.
#
# KN-TECH-14efa5 records two g6k fixes (build isolation hides Cython; missing
# libgmp.so dev symlink). This container needs a THIRD, which that entry does
# not cover: the g6k sdist unpacks with file mtimes that make `make` believe the
# autotools outputs are stale, so it invokes aclocal-1.16 to regenerate them --
# and this container has no autotools at all (no aclocal, automake, autoconf).
# The fix is to touch the shipped generated files in dependency order so make
# treats them as current and never reaches for autotools.
set -u

LOG=/tmp/instrument_rebuild.log
run() {
  echo "" | tee -a "$LOG"
  echo "\$ $*" | tee -a "$LOG"
  "$@" 2>&1 | tee -a "$LOG"
  echo "[exit ${PIPESTATUS[0]}]" | tee -a "$LOG"
}

echo "" | tee -a "$LOG"
echo "=== ROUTE 3 (g6k, autotools-free) started $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" | tee -a "$LOG"
echo "ROUTE 2's g6k step FAILED above: make wanted aclocal-1.16; no autotools present." | tee -a "$LOG"

export LIBRARY_PATH="/tmp/gmplink:${LIBRARY_PATH:-}"
export LDFLAGS="-L/tmp/gmplink"

rm -rf /tmp/g6kbuild && mkdir -p /tmp/g6kbuild
cd /tmp/g6kbuild || exit 1

run /tmp/sagevenv/bin/pip download --no-deps --no-binary :all: --no-build-isolation g6k
run tar xzf g6k-0.1.2.tar.gz
cd g6k-0.1.2 || exit 1

run ls -la
echo "" | tee -a "$LOG"
echo "\$ touch generated autotools outputs in dependency order" | tee -a "$LOG"
# Oldest first: the inputs, then each generated file strictly newer than its deps.
for f in configure.ac configure.in Makefile.am m4/*.m4; do [ -e "$f" ] && touch "$f"; done
sleep 1
for f in aclocal.m4; do [ -e "$f" ] && touch "$f"; done
sleep 1
for f in configure config.h.in config.hpp.in Makefile.in */Makefile.in; do [ -e "$f" ] && touch "$f"; done
run ls -la --time-style=full-iso aclocal.m4 configure Makefile.in

run /tmp/sagevenv/bin/pip install --no-cache-dir --no-build-isolation .

echo "=== ROUTE 3 finished $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" | tee -a "$LOG"
