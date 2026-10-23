#!/bin/sh
# Thin native command driver. Python below only hashes/parses/writes metadata.
set -eu
HA=/Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015
PACKET=coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/replay-diagnostic-015-v1
cd "$HA"
META="$PACKET/metadata.py"
PY=/Library/Frameworks/Python.framework/Versions/3.13/bin/python3
ROOT=/Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/diagnostic-EXP-ISOU-807cb5
if [ "$#" -ne 2 ] || { [ "$1" != run ] && [ "$1" != _run ]; } || [ "$2" != "$ROOT" ]; then
  echo 'Use exactly: native-command.sh run FROZEN_ABSOLUTE_OUTPUT_ROOT' >&2
  exit 64
fi
if [ "$1" = run ]; then
  test ! -e "$ROOT.outer-os-time.txt"
  exec /usr/bin/time -l -o "$ROOT.outer-os-time.txt" /bin/sh "$PACKET/native-command.sh" _run "$ROOT"
fi
"$PY" "$META" preflight "$ROOT"
mkdir "$ROOT"
blocked=
while IFS='|' read -r index run _arm binary input timeout outer trace; do
  if [ -n "$blocked" ]; then
    "$PY" "$META" nonstart "$index" "$blocked"
    continue
  fi
  "$PY" "$META" begin "$index"
  dir="$ROOT/$run"
  if [ "$trace" = on ]; then
    export ISOGENY_REPLAY_TRACE="$dir/replay-trace.jsonl"
  else
    unset ISOGENY_REPLAY_TRACE
  fi
  rc=0
  /opt/homebrew/bin/gtimeout --kill-after=5 "$outer" /usr/bin/time -l -o "$dir/os-time.txt" "$binary" challenge judge --input "$input" --out "$dir/native" --timeout "$timeout" >"$dir/stdout.log" 2>"$dir/stderr.log" || rc=$?
  unset ISOGENY_REPLAY_TRACE
  printf '%s\n' "$rc" > "$dir/outer-command.exit-code.txt"
  if "$PY" "$META" finish "$index" "$rc"; then
    :
  else
    blocked="dependency_or_integrity_failure_after_$run"
  fi
done < "$PACKET/trials.psv"
"$PY" "$META" summary
"$PY" "$META" check
# Exit zero means complete observation delivery; read every native verdict.
