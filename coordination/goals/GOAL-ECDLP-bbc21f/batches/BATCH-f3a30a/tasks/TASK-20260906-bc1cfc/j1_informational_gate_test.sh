#!/usr/bin/env bash
# J1, THIRD check (finding, not in the original attack plan but surfaced by
# it): does the N=2^30 "informational, non-binding" G3 reading actually
# behave as non-binding in the real, unmodified analysis.py -- i.e. does an
# informational G3 FAIL at a 2^30 cell leave S1_v2/F1_v2 alone there, as the
# executor's own execution_report.yaml protocol_deviations text claims
# ("This reading remains explicitly INFORMATIONAL and non-binding at
# N=2^30 ... it is never used to gate S1/F1")?
#
# Method: same synthetic-negative-injection technique as
# j1_untestable_branch_test.sh, applied to the STAGE 2v2 (N=2^30) run
# directories instead: flip `g3_pass_this_seed_informational` to false for
# the "0.65T" cell on 3 of 5 seeds (forcing n_pass=2 < 4, a genuine
# informational G3 FAIL), run the real analysis.py, and inspect whether
# S1_v2/F1_v2 at that (informational) cell become UNTESTABLE or are left
# alone.
set -euo pipefail
REPO="/home/user/crypto-autoresearcher"
SCRATCH="${1:-/tmp/j1_informational_gate_test}"
rm -rf "$SCRATCH"
mkdir -p "$SCRATCH/synthetic_runs" "$SCRATCH/synthetic_out"

for s in 1 2 3 4 5; do
  cp -r "$REPO/experiments/EXP-ECDLP-612fb1/runs/RUN-ECDLP-612fb1-v2-2v2-s${s}" \
        "$SCRATCH/synthetic_runs/RUN-ECDLP-612fb1-v2-2v2-s${s}"
done

python3 - "$SCRATCH/synthetic_runs" <<'PYEOF'
import json, sys
base = sys.argv[1]
for s in (1, 2, 3):
    p = f"{base}/RUN-ECDLP-612fb1-v2-2v2-s{s}/summary.json"
    d = json.load(open(p))
    cell = d["G3_gate"]["0.65T"]
    cell["g3_pass_this_seed_informational"] = False
    cell["margin_informational"] = -0.01
    json.dump(d, open(p, "w"), indent=2)
    print(f"seed {s}: flipped 0.65T g3_pass_this_seed_informational -> False", file=sys.stderr)
PYEOF

cd "$REPO"
python3 experiments/EXP-ECDLP-612fb1/source_v2/analysis.py \
  --runs-dir "$SCRATCH/synthetic_runs" \
  --stages 2v2 \
  --outdir "$SCRATCH/synthetic_out"

echo "=== ci_tables.json G3_gate / S1_v2 / F1_v2 for 2^30 (informational cell) ==="
python3 -c "
import json
d = json.load(open('$SCRATCH/synthetic_out/ci_tables.json'))
print(json.dumps(d['gates']['2^30']['G3_gate'], indent=2))
cell = d['cells']['2^30']['per_T_sel']
for lab in ('0.65T', '0.75T'):
    print(lab, 'S1_v2=', cell[lab]['S1_v2'])
    print(lab, 'F1_v2=', cell[lab]['F1_v2'])
"
echo ""
echo "FINDING: if 0.65T's S1_v2/F1_v2 above read UNTESTABLE despite binding=false"
echo "(informational), this CONTRADICTS the executor's execution_report.yaml claim"
echo "that the N=2^30 informational reading 'is never used to gate S1/F1'."
