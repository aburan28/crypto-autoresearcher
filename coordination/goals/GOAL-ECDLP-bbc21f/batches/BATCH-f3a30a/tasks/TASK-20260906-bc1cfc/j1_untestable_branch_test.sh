#!/usr/bin/env bash
# J1, second check: is the G3 FAIL -> UNTESTABLE branch in
# experiments/EXP-ECDLP-612fb1/source_v2/analysis.py actually reachable AND
# taken (not a silent fallthrough to a default PASS)?
#
# Method: copy the 5 real STAGE 1v2 (N=2^24) run directories into a scratch
# location, flip `g3_pass_this_seed` to false for the "0.65T" cell on 2 of
# the 5 seeds (forcing n_pass=3 < 4, i.e. a genuine G3 FAIL by the contract's
# own >=4-of-5 rule), leave the "0.75T" cell and all other data untouched,
# then run the REAL, UNMODIFIED experiments/EXP-ECDLP-612fb1/source_v2/analysis.py
# against this synthetic runs-dir and inspect its ci_tables.json output.
#
# This exercises the production code path directly (not a copy/paraphrase of
# its logic), with a fabricated-but-structurally-valid negative input. It is
# read-only with respect to the real experiment artifacts: everything is
# copied into a scratch directory first; nothing under experiments/ or
# coordination/.../TASK-20260906-5e78c7/ is modified.
#
# Expected (per specification.v2.yaml inputs.g3_gate_procedure /
# amendments/v1_to_v2.yaml item a): G3(0.65T) -> FAIL, S1_v2(0.65T) ->
# UNTESTABLE, F1_v2(0.65T) -> UNTESTABLE; G3(0.75T), S1_v2(0.75T), F1_v2(0.75T)
# unaffected (PASS / MET / does not fire), since the gate is per-(a,r,T_sel)
# cell, not global.
set -euo pipefail
REPO="/home/user/crypto-autoresearcher"
SCRATCH="${1:-/tmp/j1_untestable_test}"
rm -rf "$SCRATCH"
mkdir -p "$SCRATCH/synthetic_runs" "$SCRATCH/synthetic_out"

for s in 1 2 3 4 5; do
  cp -r "$REPO/experiments/EXP-ECDLP-612fb1/runs/RUN-ECDLP-612fb1-v2-1v2-s${s}" \
        "$SCRATCH/synthetic_runs/RUN-ECDLP-612fb1-v2-1v2-s${s}"
done

python3 - "$SCRATCH/synthetic_runs" <<'PYEOF'
import json, sys
base = sys.argv[1]
for s in (1, 2):
    p = f"{base}/RUN-ECDLP-612fb1-v2-1v2-s{s}/summary.json"
    d = json.load(open(p))
    cell = d["G3_gate"]["0.65T"]
    cell["g3_pass_this_seed"] = False
    cell["exact_top_T_sel_share"] = cell["static_T_exact_coverage"] - 0.01
    cell["margin"] = -0.01
    json.dump(d, open(p, "w"), indent=2)
    print(f"seed {s}: flipped 0.65T g3_pass_this_seed -> False", file=sys.stderr)
PYEOF

cd "$REPO"
python3 experiments/EXP-ECDLP-612fb1/source_v2/analysis.py \
  --runs-dir "$SCRATCH/synthetic_runs" \
  --stages 1v2 \
  --outdir "$SCRATCH/synthetic_out"

echo "=== ci_tables.json G3_gate / S1_v2 / F1_v2 for 2^24 ==="
python3 -c "
import json
d = json.load(open('$SCRATCH/synthetic_out/ci_tables.json'))
print(json.dumps(d['gates']['2^24']['G3_gate'], indent=2))
cell = d['cells']['2^24']['per_T_sel']
for lab in ('0.65T', '0.75T'):
    print(lab, 'S1_v2=', cell[lab]['S1_v2'])
    print(lab, 'F1_v2=', cell[lab]['F1_v2'])
"
