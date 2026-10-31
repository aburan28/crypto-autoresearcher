#!/usr/bin/env bash
# resources: the driver records peak_rss_bytes and cpu_seconds in its own manifest.yaml for each replay
# J2a(1)-(3): replay selftest, analyze-main and analyze-final through the bound driver's trial entry point
# (run.py trial ...) with the run directory inside this task's outputs/, never under experiments/.
# The driver's inputs_from resolve to the recorded run directories (run.py RUNS_DIR), so the analyze replays
# read the recorded census jobs files and design.json. The kernel is compiled by the driver into
# tempfile.mkdtemp under $TMPDIR (a scratch path), never into implementation/.
# The run id passed is the planned one because run.py asserts trial["run_id"] == --run-id; the files written
# here are review replays, not run records, and are never cited as runs.
#
# usage: replay.sh <interpreter> <outdir-name>     (run from the repository root)
set -u
PY="$1"
OUT="coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-924d2c/reviews/TASK-20261029-e54312/outputs/$2"
export TMPDIR=/tmp/claude-0/j2-scratch/tmp
mkdir -p "$OUT" "$TMPDIR"
"$PY" -B -I -c 'import json,sys; print(json.dumps({"version": sys.version, "executable": sys.executable, "flags_isolated": sys.flags.isolated, "dont_write_bytecode": sys.dont_write_bytecode}))' > "$OUT/interpreter.json"
for spec in "selftest RUN-PFDR-e44a19" "analyze-main RUN-PFDR-243425" "analyze-final RUN-PFDR-089edc"; do
  set -- $spec
  TR="$1"; RID="$2"; RD="$OUT/$TR"
  mkdir -p "$RD"
  T0=$(date +%s.%N)
  "$PY" -B -I experiments/EXP-PFDR-bb0d26/implementation/run.py trial \
      --run-dir "$(pwd)/$RD" --run-id "$RID" --trial-id "$TR" --plan experiments/EXP-PFDR-bb0d26/trial-plan.json \
      > "$RD/replay.stdout.log" 2> "$RD/replay.stderr.log"
  RC=$?
  T1=$(date +%s.%N)
  echo "{\"trial\": \"$TR\", \"run_id_passed\": \"$RID\", \"exit_code\": $RC, \"wall_seconds\": $(printf "%.3f" "$(echo "$T1 - $T0" | bc)")}" > "$RD/replay.exit.json"
  echo "$TR rc=$RC"
done
