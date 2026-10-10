#!/usr/bin/env bash
# TASK-20261009-33b5cf, joint J-A3, review computation (AMD-20261008-9c080d A-10;
# specification AR-7 method). NOT a run of any experiment.
#
# Runs the two archived EXP-PFDR-011cd0 R12 job commands named in gates G-REPRO
# (4-b30-c10, 4-b32-c10) TWICE each on the 38be58dad bytes of src/, extracted with
#   git archive 38be58dad src | tar -x -C $S/src-38be58dad
# and placed ahead of the repository's src/ on the import path (PYTHONPATH).
# Same wrapper (experiments/EXP-PFDR-1b78f7/amd-1de84f/run_wrapper.py exec), same
# wrapper controls (--watchdog 21600, --rss-cap-bytes 3500000000) and the same census
# arguments as recorded in experiments/EXP-PFDR-0b3699/runs/RUN-PFDR-0b3699-repro/
# attempt-1/jobs/<job>/execution.json; only output paths are moved under the scratch
# directory. The wrapper's --run-id label is a review label, not a run id.
# Sequential (wrapper + one in-process census = 2 processes at a time).
# Afterwards each *.jsonl is compressed with gzip -n, as run_jobs.py gzip_jsonl does.
# No seeds of its own: the census is deterministic from its arguments (curve seeds c).
set -euo pipefail
REPO=/home/user/crypto-autoresearcher
S=/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/33b5cf
PY=/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/venv-ci/bin/python
WRAPPER=$REPO/experiments/EXP-PFDR-1b78f7/amd-1de84f/run_wrapper.py
SPEC="review computation TASK-20261009-33b5cf J-A3 (AMD-20261008-9c080d A-10): archived R12 job command on the 38be58dad bytes of src/, output paths moved to scratch"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=$S/src-38be58dad/src
export GIT_OPTIONAL_LOCKS=0   # the wrapper's git status must not refresh .git/index
cd "$REPO"
for k in 1 2; do
  for bits in 30 32; do
    job=4-b${bits}-c10
    JD=$S/j-a3/$job/run$k
    mkdir -p "$S/j-a3/$job"
    echo "$(date -u +%FT%TZ) start $job run$k"
    "$PY" "$WRAPPER" exec --run-dir "$JD" --run-id "REVIEWCOMP-TASK-20261009-33b5cf-J-A3-$job-run$k" \
      --exp EXP-PFDR-0b3699 --spec-command "$SPEC" --watchdog 21600 --rss-cap-bytes 3500000000 -- \
      "$PY" -m crypto_autoresearcher.index_calculus census --panel main --m 4 --bits $bits \
      --curve-offset 10 --curves 100 --modes table --arms subgroup dickson small_x random_sub_r0 \
      random_sub_r1 random_sub_r2 known_null_sub random_dick_r0 random_dick_r1 random_dick_r2 \
      known_null_dick --known-log-max-bits 0 --retain all --relcount --instance-watchdog 1800 \
      --bases-out "$JD/bases.jsonl" --bases-sample-mod 10 --workers 1 --out "$JD/rows.jsonl" \
      --rows-out "$JD/harvest-rows.jsonl" --staircase-out "$JD/staircase.jsonl"
    for f in "$JD"/*.jsonl; do gzip -n "$f"; done
    echo "$(date -u +%FT%TZ) end $job run$k"
  done
done
echo "$(date -u +%FT%TZ) all done"
