#!/bin/bash
# R10 fix check driver (TASK-20261001-7f7a33)
set -u
cd /home/user/crypto-autoresearcher
PY=/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/venv-ci/bin/python
S=/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/7f7a33
E=experiments/EXP-PFDR-011cd0
RID=RUN-PFDR-011cd0-fix-check
RD=$E/runs/$RID
export PYTHONDONTWRITEBYTECODE=1
SPEC='run_jobs.py over the 45 fix_check_panel jobs, each: <PY> -m crypto_autoresearcher.index_calculus census --panel main --m <m> --bits <B> --curve-offset <c> --curves 1 --known-log-max-bits <24 if m = 3 else 0> --relcount --solve-certs JOB/solve-certs.jsonl --workers 1 --out JOB/rows.jsonl --rows-out SCRATCH/<job>/harvest-rows.jsonl --staircase-out JOB/staircase.jsonl; then merge_relcensus.py fixcompare --old-runs experiments/EXP-PFDR-1b78f7/runs --new RUN_DIR --scratch SCRATCH --out RUN_DIR/fix-report.json'
echo "[$(date -u +%FT%TZ)] R10 start"
$PY $E/run_jobs.py jobs --run R10 --out $S/jobs-r10.json
$PY $E/run_jobs.py run --run-id $RID --attempt-dir $RD/attempt-1 --jobs-file $S/jobs-r10.json --trigger "R10: the 45 frozen fix_check_panel jobs" --spec-command "$SPEC"
$PY $E/run_jobs.py finalize-attempt --attempt-dir $RD/attempt-1 --run-id $RID --spec-command "$SPEC"
echo "# run-root steps (canonical location = run root), cwd /home/user/crypto-autoresearcher" > $RD/command.txt
$PY $S/root_env.py $RD/environment.json
$S/root_step.sh $RD -- $PY $E/merge_relcensus.py merge --run-dir $RD --run-id $RID --attempts attempt-1
$S/root_step.sh $RD -- $PY $E/merge_relcensus.py fixcompare --old-runs experiments/EXP-PFDR-1b78f7/runs --new $RD --scratch $S/r10-harvest-rows --out $RD/fix-report.json
$S/root_step.sh $RD -- $PY $E/verify_solves.py $RD/solve-certs.jsonl.gz --out $RD/solve-verify.json
echo "[$(date -u +%FT%TZ)] R10 steps done"
