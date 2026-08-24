#!/bin/sh
# TASK-20260803-6ba122 full paired sweep.
# Seed depends on (r, trial-stream) ONLY, not on the layer, so trial t carries the
# SAME keys and base across NZ/Z1/Z4 at a given r.  Paired design, as preregistered.
set -u
cd "$(dirname "$0")"
mkdir -p arms
: > runs.jsonl
for r in 4 5 6 7; do
  for L in 0 1 4; do
    SEED=$((1000000 + r * 1000))
    TAG="r${r}_L${L}"
    CMD="./nib ${r} 0 ${SEED} 0 40 ${L}"
    T0=$(date +%s.%N)
    $CMD > "arms/${TAG}.json" 2> "arms/${TAG}.err"
    EX=$?
    T1=$(date +%s.%N)
    printf '{"tag":"%s","command":"%s","exit_status":%d,"seed":%d,"r":%d,"layer_code":%d,"rand_sbox":0,"trials":40,"wall_s":%s,"stdout":"arms/%s.json","stderr":"arms/%s.err"}\n' \
      "$TAG" "$CMD" "$EX" "$SEED" "$r" "$L" "$(echo "$T1 $T0" | awk '{printf "%.3f", $1-$2}')" "$TAG" "$TAG" >> runs.jsonl
    echo "done $TAG exit=$EX"
  done
done
