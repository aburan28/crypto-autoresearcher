#!/usr/bin/env bash
# Pre-pin exercise of run_jobs.py (dummy command, no solver) and merge_census.py (synthetic
# fixtures only), TASK-20260929-89c123.  Output: exercise.log beside this file.
set -u
REPO=/home/user/crypto-autoresearcher
PY=/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/venv-ci/bin/python
FC=experiments/EXP-PFDR-1b78f7/amd-430f44/fixture-check
RJ=experiments/EXP-PFDR-1b78f7/amd-430f44/run_jobs.py
MC=experiments/EXP-PFDR-1b78f7/amd-430f44/merge_census.py
F=$FC/fixtures
O=$FC/out
cd "$REPO"
run() { echo; echo "### $1"; shift; echo "\$ $*"; "$@"; echo "[exit $?]"; }

echo "# exercise started $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "# run_jobs.py sha256 $(sha256sum $RJ | cut -d' ' -f1)"
echo "# merge_census.py sha256 $(sha256sum $MC | cut -d' ' -f1)"
run "fixture generation" $PY $FC/make_fixtures.py

# ---------------- run_jobs.py (dummy command; no solver) ----------------
run "D1 order, concurrency (max 2), ascap + crash flags, finalize (expect failed_infrastructure; m4 triggers b22-c1, b18-c0)" \
  $PY $RJ run --run-id RUN-FIXTURE-D1 --attempt-dir $O/D1 --panel main --m 4 --dummy --max-procs 2 --poll 1 \
  --jobs b20-c1,b24-c1,b22-c0,b22-c1,b20-c0,b18-c0 \
  --dummy-behaviour-json '{"b24-c1":"sleep","b22-c1":"ascap","b18-c0":"crash"}' \
  --trigger "fixture D1" --finalize
run "D2 run-stop rule (max 1; b28-c0 invalid; expect b26-* not_started_after_run_stop; status invalid)" \
  $PY $RJ run --run-id RUN-FIXTURE-D2 --attempt-dir $O/D2 --panel main --m 4 --dummy --max-procs 1 --poll 1 \
  --jobs b30-c0,b28-c0,b26-c0,b26-c1 --dummy-behaviour-json '{"b28-c0":"invalid"}' --trigger "fixture D2" --finalize
run "D3 RLIMIT_AS cap through run_wrapper.py (hog allocates 4e9 B; expect MemoryError, abnormal end)" \
  $PY $RJ run --run-id RUN-FIXTURE-D3 --attempt-dir $O/D3 --panel main --m 4 --dummy --poll 1 \
  --jobs b24-c0 --dummy-behaviour-json '{"b24-c0":"hog"}' --trigger "fixture D3" --finalize
run "D4 j0 jobs with rho rows, jobs-subdir '' (expect completed_valid; rho rows claimed and verified)" \
  $PY $RJ run --run-id RUN-FIXTURE-D4 --attempt-dir $O/D4 --jobs-subdir "" --panel j0 --rho-curves 5 --dummy --poll 1 \
  --jobs b24-c0,b22-c4 --trigger "fixture D4" --finalize
run "D6 M-4 per-arm job layout (b24-c1:subgroup, b24-c1:dickson; expect completed_valid, 2 keys per job)" \
  $PY $RJ run --run-id RUN-FIXTURE-D6 --attempt-dir $O/D6 --panel main --m 4 --dummy --poll 1 \
  --jobs b24-c1:subgroup,b24-c1:dickson --trigger "fixture D6" --finalize
run "D5 MemAvailable gate (gate 1000 GB, attempt watchdog 8 s; expect no job started, not_started_attempt_watchdog)" \
  $PY $RJ run --run-id RUN-FIXTURE-D5 --attempt-dir $O/D5 --panel main --m 4 --dummy --poll 1 \
  --min-mem-avail-gb 1000 --watchdog 8 --jobs b24-c0 --trigger "fixture D5" --finalize
for d in D1 D2 D3 D4 D6 D5; do
  echo "--- $d jobs-index summary"
  $PY - "$O/$d/jobs-index.json" <<'EOF'
import json, sys
x = json.load(open(sys.argv[1]))
print("run_stop_at_job", x["run_stop_at_job"], "not_started", x["not_started"], x["not_started_reason"], "mem_gate_wait_polls", x["mem_gate_wait_polls"])
for j in sorted(x["jobs"], key=lambda j: j["started_at"]):
    print(j["job"], "start", j["started_at"][11:19], "end", j["ended_at"][11:19], "exit", j["exit_code"], "signal", j["signal"],
          "rows", j["rows_written"], j["status_counts"], "missing", len(j["missing_keys"]), "ascap", len(j["address_space_cap_instances"]),
          "invalid", len(j["invalid_instances"]), "abnormal", j["abnormal_end"], "m4", j["m4_trigger"])
EOF
  grep -E "^  status:|^  location_kind" $O/$d/manifest.yaml
done

# ---------------- merge_census.py (synthetic fixtures only) ----------------
run "C1 compare: equal up to excluded keys (expect pass)" \
  $PY $MC compare --check-id FIXTURE-C1 --m 4 --bits 26 --curve 0 --a-rows $F/compare/attempt1/rows.jsonl.gz \
  --a-stairs $F/compare/attempt1/staircase.jsonl.gz --a-harvest $F/compare/attempt1/harvest-rows.jsonl.gz \
  --b-dir $F/compare/check/b26-c0 --out $O/C1-compare.json
run "C2 compare: one staircase record differs in a non-excluded key (expect fail, key name 'stair')" \
  $PY $MC compare --check-id FIXTURE-C2 --m 4 --bits 26 --curve 0 --a-rows $F/compare-diff/attempt1/rows.jsonl.gz \
  --a-stairs $F/compare-diff/attempt1/staircase.jsonl.gz --a-harvest $F/compare-diff/attempt1/harvest-rows.jsonl.gz \
  --b-dir $F/compare-diff/check/b26-c0 --out $O/C2-compare.json
run "R1 resume-set on F1 (expect equal, 33 jobs)" \
  $PY $MC resume-set --rows $F/r11like/runs/RUN-PFDR-1b78f7-census-m4/rows.jsonl.gz --out $O/R1-resume.json
run "R2 resume-set on F1r (extra crashed job; expect NOT equal, exit 1)" \
  $PY $MC resume-set --rows $F/r11resume/runs/RUN-PFDR-1b78f7-census-m4/rows.jsonl.gz --out $O/R2-resume.json
M11="--panel main --m 4 --bits 12 14 16 18 20 22 24 26 28 30 32 --root-attempt1 --assert-r11-resume-set --attempts attempt-2"
run "M1 merge F1 (expect 990 canonical, 0 placeholders, 67 non-cell, 594 superseded, completed_valid)" \
  $PY $MC merge --run-id RUN-FIXTURE-F1 --run-dir $F/r11like/runs/RUN-PFDR-1b78f7-census-m4 \
  --out $O/F1-merged $M11
run "M2 merge F1d (duplicate key in one attempt; expect STOP exit 4)" \
  $PY $MC merge --run-id RUN-FIXTURE-F1d --run-dir $F/r11dup/runs/RUN-PFDR-1b78f7-census-m4 --out $O/F1d-merged $M11
run "M3 merge F1r (resume set differs; expect STOP exit 4)" \
  $PY $MC merge --run-id RUN-FIXTURE-F1r --run-dir $F/r11resume/runs/RUN-PFDR-1b78f7-census-m4 --out $O/F1r-merged $M11
run "M4 merge F1o (attempt-2 job outside resume set; expect STOP exit 4)" \
  $PY $MC merge --run-id RUN-FIXTURE-F1o --run-dir $F/r11outside/runs/RUN-PFDR-1b78f7-census-m4 --out $O/F1o-merged $M11
M12="--panel main --m 5 --bits 12 14 16 18 20 22 24 26 28 30 32 --attempts attempt-1 attempt-2"
run "M5 merge F2 (expect 17 placeholders: b20-c3 small_x on + 8 arms x 2 of b18-c1; 2 equal determinism comparisons)" \
  $PY $MC merge --run-id RUN-FIXTURE-F2 --run-dir $F/r12like/runs/RUN-PFDR-1b78f7-census-m5 --out $O/F2-root $M12
run "M6 merge F2n (per-arm re-run differs from completed_valid row; expect STOP exit 4 I-5)" \
  $PY $MC merge --run-id RUN-FIXTURE-F2n --run-dir $F/r12nondet/runs/RUN-PFDR-1b78f7-census-m5 --out $O/F2n-root $M12
run "M7 merge F3 j0 (expect 315 canonical incl. 35 rho rows)" \
  $PY $MC merge --run-id RUN-FIXTURE-F3 --run-dir $F/j0like/runs/RUN-PFDR-1b78f7-j0 --out $O/F3-root \
  --panel j0 --bits 12 14 16 18 20 22 24 --rho-curves 5 --attempts attempt-1
run "M8 merge F3c (planted rho certificate failure; expect CERTIFICATE FAILURE, no manifest, exit 1)" \
  $PY $MC merge --run-id RUN-FIXTURE-F3c --run-dir $F/j0cert/runs/RUN-PFDR-1b78f7-j0 --out $O/F3c-root \
  --panel j0 --bits 12 14 16 18 20 22 24 --rho-curves 5 --attempts attempt-1
echo "F3c manifest present: $(test -e $O/F3c-root/manifest.yaml && echo yes || echo no)"
echo "--- merge-report checks"
$PY - "$REPO/$O" <<'EOF'
import gzip, json, os, sys
o = sys.argv[1]
for n in ("F1-merged", "F2-root", "F3-root"):
    r = json.load(open(os.path.join(o, n, "merge-report.json")))
    rows = [json.loads(l) for l in gzip.open(os.path.join(o, n, "rows.jsonl.gz"), "rt")]
    def sk(x):
        if x.get("method") == "rho": return (x["bits"], x["curve"], 0, "", "")
        m = x.get("m") if x.get("m") is not None else int(x["method"][4:])
        return (x["bits"], x["curve"], m, x.get("arm") or "", x.get("mode") or "")
    print(n, "U", r["U_size"], "canonical", r["canonical_rows"], "one-per-key", r["keys_with_exactly_one_canonical_row"],
          "placeholders", len(r["placeholders"]), "non-cell", len(r["non_cell_rows_excluded"]),
          "superseded", len(r["superseded_rows"]), "determinism", [(d["key"], d["equal_after_M3_exclusions"]) for d in r["determinism_comparisons"]],
          "sorted", [sk(x) for x in rows] == sorted(sk(x) for x in rows), "status_counts", r["counts_by_status"],
          "stairs", r["canonical_staircase_records"])
    print("   placeholder reasons:", sorted({p["status_reason"] for p in r["placeholders"]}))
    print("   non-cell keys:", sorted({(tuple(x["key"])[4], x["attempt"]) for x in r["non_cell_rows_excluded"]}))
    print("   manifest status:", [l.strip() for l in open(os.path.join(o, n, "manifest.yaml")) if l.startswith("  status:")])
    if n == "F3-root":
        print("   first rows:", [(x["bits"], x["curve"], x.get("method"), x.get("arm"), x.get("mode")) for x in rows[:3]])
EOF
for n in F1d-merged F1r-merged F1o-merged F2n-root; do echo "$n stop: $(cat $O/$n/merge-stop.json 2>/dev/null)"; done
run "V1 view (expect census-m4 -> merged, census-m3 -> root, NOT-A-RUN skipped)" \
  $PY $MC view --runs-root $F/viewroot/runs --view /tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/89c123/fixture-view --map-out $O/V1-view-map.json
echo "# exercise finished $(date -u +%Y-%m-%dT%H:%M:%SZ)"
