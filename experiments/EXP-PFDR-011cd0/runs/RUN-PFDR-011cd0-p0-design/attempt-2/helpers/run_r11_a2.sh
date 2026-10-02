#!/bin/bash
# R11 P0 design driver (TASK-20261001-7f7a33)
set -u
cd /home/user/crypto-autoresearcher
PY=/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/venv-ci/bin/python
W=experiments/EXP-PFDR-1b78f7/amd-1de84f/run_wrapper.py
E=experiments/EXP-PFDR-011cd0
RID=RUN-PFDR-011cd0-p0-design
RD=$E/runs/$RID/attempt-2
B=coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-f29c96/attacks/out/02_bundles.jsonl
export PYTHONDONTWRITEBYTECODE=1
SPEC="<PY> $E/design_curves.py --spec $E/specification.yaml --out RUN_DIR/curves.jsonl; then <PY> $E/analyze_relcensus.py p0 --archived-runs experiments/EXP-PFDR-1b78f7/runs --bundles $B --curves RUN_DIR/curves.jsonl --out RUN_DIR (design.json, power.json, p0x-report.json)"
echo "[$(date -u +%FT%TZ)] R11 attempt-2 start"
$PY $W exec --run-dir $RD --run-id $RID --exp EXP-PFDR-011cd0 --spec-command "$SPEC" --watchdog 86400 --rss-cap-bytes 3.5e9 -- bash -c "$PY $E/design_curves.py --spec $E/specification.yaml --out $RD/curves.jsonl --workers 4 && $PY $E/analyze_relcensus.py p0 --archived-runs experiments/EXP-PFDR-1b78f7/runs --bundles $B --curves $RD/curves.jsonl --out $RD"
$PY $W post --run-dir $RD -- gzip -n $RD/curves.jsonl
echo "[$(date -u +%FT%TZ)] R11 attempt-2 done"
