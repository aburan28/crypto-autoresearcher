#!/bin/bash
# PTM-5 driver: 200 instances per (m, rung), rungs 12..24, m = 3, 4, 5; one guarded process at a time.
D=/home/user/crypto-autoresearcher/coordination/review/pfdr-twfloor-20261001/reviews/TASK-20260929-575e80/attacks
PY=/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/venv-ci/bin/python
cd $D
for m in 3 4 5; do
  for bits in 12 14 16 18 20 22 24; do
    $PY guard.py ptm5_m${m}_b${bits} -- $PY ptm5_engine.py out/ptm5_results.jsonl $m $bits 0 200
  done
done
echo PTM5_DONE
