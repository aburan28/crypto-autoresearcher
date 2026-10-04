#!/usr/bin/env bash
# Exercise of the run_jobs.py / merge_census.py edit for R16 (deviation DEV-A in
# implementation-notes-amd430f44.yaml), TASK-20260929-89c123.  Dummy command (no solver) and
# synthetic fixtures only.  Output: exercise-r16.log beside this file.
set -u
REPO=/home/user/crypto-autoresearcher
PY=/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/venv-ci/bin/python
FC=experiments/EXP-PFDR-1b78f7/amd-430f44/fixture-check
RJ=experiments/EXP-PFDR-1b78f7/amd-430f44/run_jobs.py
MC=experiments/EXP-PFDR-1b78f7/amd-430f44/merge_census.py
F=$FC/fixtures
O=$FC/out-r16
cd "$REPO"
run() { echo; echo "### $1"; shift; echo "\$ $*"; "$@"; echo "[exit $?]"; }
echo "# exercise-r16 started $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "# run_jobs.py sha256 $(sha256sum $RJ | cut -d' ' -f1)"
echo "# merge_census.py sha256 $(sha256sum $MC | cut -d' ' -f1)"
echo "# dummy_job.py sha256 $(sha256sum $FC/dummy_job.py | cut -d' ' -f1)"
A="subgroup+random_sub_r0+random_sub_r1+random_sub_r2"
J="m3-b28-c5:$A,m3-b28-c6:$A,m4-b20-c5:small_x+random_sub_r0+random_sub_r1+random_sub_r2,m4-b26-c5:dickson+random_dick_r0+random_dick_r1+random_dick_r2,m5-b16-c5:$A"
run "D7 R16-like attempt: per-job m and frozen --arms lists; m4-b20-c5 crashes (expect 8 missing keys, failed_infrastructure)" \
  $PY $RJ run --run-id RUN-FIXTURE-D7 --attempt-dir $O/RUN-FIXTURE-stage-r/attempt-1 --panel main --dummy --poll 1 \
  --jobs "$J" --dummy-behaviour-json '{"m4-b20-c5":"crash"}' --trigger "fixture D7" --finalize
echo "--- D7 jobs"; $PY -c "
import json; x=json.load(open('$O/RUN-FIXTURE-stage-r/attempt-1/jobs-index.json'))
for j in x['jobs']: print(j['job'], 'm', j['m'], 'arms', j['arms'], 'rows', j['rows_written'], 'expected', j['expected_keys'], 'missing', len(j['missing_keys']), 'nonjob', len(j['non_job_keys']), 'abnormal', j['abnormal_end'], 'cmd_arms', j['command'][j['command'].index('--arm')+1] if '--arm' in j['command'] else None)
"
grep -E "^  status:" $O/RUN-FIXTURE-stage-r/attempt-1/manifest.yaml
run "D8 R16-like run-stop: m5-b16-c5 invalid, max 1 process (expect not_started with specs, summarize expects 8 keys per unstarted job)" \
  $PY $RJ run --run-id RUN-FIXTURE-D8 --attempt-dir $O/D8 --panel main --dummy --max-procs 1 --poll 1 \
  --jobs "m5-b16-c5:$A,m3-b14-c5:$A,m3-b12-c5:$A" --dummy-behaviour-json '{"m5-b16-c5":"invalid"}' --trigger "fixture D8" --finalize
$PY -c "
import json; x=json.load(open('$O/D8/jobs-index.json')); r=json.load(open('$O/D8/raw-result.json'))
print('not_started', x['not_started'], x['not_started_specs'], 'expected_keys', r['completeness']['expected_keys'], 'missing', r['completeness']['keys_missing'])"
grep -E "^  status:" $O/D8/manifest.yaml
C="3:28:$A:5+6 4:20:small_x+random_sub_r0+random_sub_r1+random_sub_r2:5 4:26:dickson+random_dick_r0+random_dick_r1+random_dick_r2:5 5:16:$A:5"
run "M9 merge R16-like with --cells and --post-command (expect U 40, 8 placeholders for m4-b20-c5, post step output covered)" \
  $PY $MC merge --run-id RUN-FIXTURE-stage-r --run-dir $O/RUN-FIXTURE-stage-r --out $O/RUN-FIXTURE-stage-r --panel main \
  --bits 0 --attempts attempt-1 --cells $C --location-kind canonical_run_root \
  --post-command "$PY -c \"import gzip,json; n=sum(1 for _ in gzip.open('$O/RUN-FIXTURE-stage-r/rows.jsonl.gz','rt')); json.dump({'fixture_post_step_rows_seen': n}, open('$O/RUN-FIXTURE-stage-r/analysis.json','w'))\""
$PY - "$REPO/$O/RUN-FIXTURE-stage-r" <<'PYEOF'
import gzip, json, os, sys
d = sys.argv[1]
r = json.load(open(os.path.join(d, "merge-report.json")))
print("U", r["U_size"], "canonical", r["canonical_rows"], "one-per-key", r["keys_with_exactly_one_canonical_row"],
      "placeholders", len(r["placeholders"]), sorted({p["status_reason"] for p in r["placeholders"]}), "status", r["counts_by_status"])
print("analysis.json", json.load(open(os.path.join(d, "analysis.json"))))
cs = open(os.path.join(d, "checksums.sha256")).read()
print("checksums cover analysis.json:", "  analysis.json" in cs, "post-step logs:", "post-step.stdout.log" in cs)
print("raw-result by:", json.load(open(os.path.join(d, "raw-result.json")))["summarised_by"])
print([l.strip() for l in open(os.path.join(d, "manifest.yaml")) if l.startswith("  status:")])
PYEOF
echo "--- regression: edited merge on the original fixtures; canonical rows/staircases must equal the pre-edit outputs in out/"
M11="--panel main --m 4 --bits 12 14 16 18 20 22 24 26 28 30 32 --root-attempt1 --assert-r11-resume-set --attempts attempt-2"
M12="--panel main --m 5 --bits 12 14 16 18 20 22 24 26 28 30 32 --attempts attempt-1 attempt-2"
$PY $MC merge --run-id RUN-FIXTURE-F1 --run-dir $F/r11like/runs/RUN-PFDR-1b78f7-census-m4 --out $O/F1-merged $M11 >/dev/null 2>&1; echo "F1 exit $?"
$PY $MC merge --run-id RUN-FIXTURE-F1d --run-dir $F/r11dup/runs/RUN-PFDR-1b78f7-census-m4 --out $O/F1d-merged $M11 >/dev/null 2>&1; echo "F1d exit $? $(cat $O/F1d-merged/merge-stop.json | tr -d '\n')"
$PY $MC merge --run-id RUN-FIXTURE-F1o --run-dir $F/r11outside/runs/RUN-PFDR-1b78f7-census-m4 --out $O/F1o-merged $M11 >/dev/null 2>&1; echo "F1o exit $? $(cat $O/F1o-merged/merge-stop.json | tr -d '\n')"
$PY $MC merge --run-id RUN-FIXTURE-F2 --run-dir $F/r12like/runs/RUN-PFDR-1b78f7-census-m5 --out $O/F2-root $M12 >/dev/null 2>&1; echo "F2 exit $?"
$PY $MC merge --run-id RUN-FIXTURE-F2n --run-dir $F/r12nondet/runs/RUN-PFDR-1b78f7-census-m5 --out $O/F2n-root $M12 >/dev/null 2>&1; echo "F2n exit $? $(cat $O/F2n-root/merge-stop.json | tr -d '\n')"
$PY $MC merge --run-id RUN-FIXTURE-F3 --run-dir $F/j0like/runs/RUN-PFDR-1b78f7-j0 --out $O/F3-root --panel j0 --bits 12 14 16 18 20 22 24 --rho-curves 5 --attempts attempt-1 >/dev/null 2>&1; echo "F3 exit $?"
for n in F1-merged F2-root F3-root; do
  for f in rows.jsonl.gz staircase.jsonl.gz; do
    a=$(sha256sum $FC/out/$n/$f | cut -d' ' -f1); b=$(sha256sum $O/$n/$f | cut -d' ' -f1)
    echo "$n/$f pre-edit $a post-edit $b equal $([ "$a" = "$b" ] && echo yes || echo NO)"
  done
  $PY -c "
import json
a=json.load(open('$FC/out/$n/merge-report.json')); b=json.load(open('$O/$n/merge-report.json'))
ks=('per_key_source','placeholders','non_cell_rows_excluded','superseded_rows','determinism_comparisons','counts_by_status','U_size')
print('$n merge-report fields equal:', {k: a[k]==b[k] for k in ks})"
done
echo "# exercise-r16 finished $(date -u +%Y-%m-%dT%H:%M:%SZ)"
