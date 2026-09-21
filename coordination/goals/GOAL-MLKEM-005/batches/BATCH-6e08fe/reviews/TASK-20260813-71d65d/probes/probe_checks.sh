#!/bin/bash
# TASK-20260813-71d65d (Validator) -- probe_checks.sh
#
# Git-plumbing notarization/change-set checks, RC-3 verbatim check, ROUTE-P
# exclusion check, no-reduction-above-d=40 check, hash verification. Runs
# entirely from committed history via git plumbing (never the working tree
# for anything already archived). Read-only; commits nothing.
cd "$(git rev-parse --show-toplevel)"

NOTARIZE_COMMIT=1e1acf08b151dd31b4d41b8afd287d261adce1e5
NOTARIZE_PARENT=d2ee472a4913e2b0b4a71d26ac481ca7c3624c88
LEAD_COMMIT=6ad64048dfee5b87b9df7ebcd9d7f7b80baf44cb
LEAD_PARENT=dcfa099d4309049bf14e0f22cfaa753e8fbe85c3

echo "=== A. notarization commit change-set (declared 3, all additions) ==="
git diff --name-status "$NOTARIZE_PARENT" "$NOTARIZE_COMMIT"
echo "count: $(git diff --name-status "$NOTARIZE_PARENT" "$NOTARIZE_COMMIT" | wc -l) (expect 3)"

echo
echo "=== B. prereg.md ABSENT at notarization commit's parent (expect: not found among prereg.md, only task_card.md) ==="
git ls-tree -r "$NOTARIZE_PARENT" --name-only | grep "TASK-20260813-cdcd88"

echo
echo "=== C. lead commit change-set (declared 8, all additions) ==="
git diff --name-status "$LEAD_PARENT" "$LEAD_COMMIT"
echo "count: $(git diff --name-status "$LEAD_PARENT" "$LEAD_COMMIT" | wc -l) (expect 8)"

echo
echo "=== D. ZERO producer artifacts at lead commit's parent (expect: only task_card.md) ==="
git ls-tree -r "$LEAD_PARENT" --name-only | grep "TASK-20260813-ea2e96"

echo
echo "=== E. hash verification: committed bytes vs declared path_sha256 (both commits) ==="
for f in \
  "coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/archives/TASK-20260813-e24ad9/snapshot-receipt.json" \
  "coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/tasks/TASK-20260813-cdcd88/prereg.md" \
  "coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/tasks/TASK-20260813-cdcd88/prereg_sha256.txt" ; do
  h=$(git show "$NOTARIZE_COMMIT":"$f" | sha256sum | cut -d' ' -f1)
  echo "$f -> $h"
done
for f in \
  "coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/archives/TASK-20260813-2d6b5e/snapshot-receipt.json" \
  "coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/tasks/TASK-20260813-ea2e96/command.txt" \
  "coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/tasks/TASK-20260813-ea2e96/measure_route_reimpl.py" \
  "coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/tasks/TASK-20260813-ea2e96/report_route_reimpl.md" \
  "coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/tasks/TASK-20260813-ea2e96/results_route_reimpl.json" \
  "coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/tasks/TASK-20260813-ea2e96/run_manifest.yaml" \
  "coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/tasks/TASK-20260813-ea2e96/stderr.log" \
  "coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/tasks/TASK-20260813-ea2e96/stdout.log" ; do
  h=$(git show "$LEAD_COMMIT":"$f" | sha256sum | cut -d' ' -f1)
  echo "$f -> $h"
done

echo
echo "=== F. RC-3 verbatim check: PREREG-4 section 1 blockquote vs report_route_reimpl.md's carried paragraph (backtick-formatting differences ignored) ==="
python3 - <<'PYEOF'
prereg = open('coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/tasks/TASK-20260813-cdcd88/prereg.md').read()
report = open('coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/tasks/TASK-20260813-ea2e96/report_route_reimpl.md').read()

def extract_blockquote(text, start_marker):
    idx = text.find(start_marker)
    sub = text[idx:idx+3000]
    lines, out, started = sub.split('\n'), [], False
    for l in lines:
        if l.startswith('> '):
            started = True
            out.append(l[2:])
        elif started and l.strip() == '':
            break
    return ' '.join(out)

pq = extract_blockquote(prereg, "FROZEN CORRECTION TEXT")
rq = extract_blockquote(report, "> BATCH-fbb639")

pq_stripped = pq.replace('`', '').replace('**', '')
rq_stripped = rq.replace('`', '').replace('**', '')
print("PREREG length:", len(pq), " REPORT length:", len(rq))
print("EQUAL after stripping markdown emphasis/code backticks:", pq_stripped.strip() == rq_stripped.strip())
if pq_stripped.strip() != rq_stripped.strip():
    print("MISMATCH DETECTED -- see below")
    print(repr(pq_stripped[:200]))
    print(repr(rq_stripped[:200]))
PYEOF

echo
echo "=== G. RC-3 numbers vs probe_coverage_beta_mismatch_output.json (primary source, re-read directly) ==="
python3 - <<'PYEOF'
import json
d = json.load(open('coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/reviews/TASK-20260813-6ab893/probes/probe_coverage_beta_mismatch_output.json'))
pc = d['per_cell_beta_coverage_audit']
for k in ['hkz/L9_b22', 'hkz/L11_b30']:
    v = pc[k]['TRUE_beta_hi_comparison']['true_abs_deviation']
    print(k, 'true_abs_deviation =', v, '(expect 0.0)')
PYEOF

echo
echo "=== H. independent coverage-table re-derivation from results_relvar.json's OWN G_REL1 block (read directly) ==="
python3 - <<'PYEOF'
import json
d = json.load(open('coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/TASK-20260809-cda2f6/results_relvar.json'))
g = d['G_REL1']
LATTICES = {"L7": (20, 6), "L9": (30, 9), "L11": (40, 12)}
BETA_GRID = {20: [5, 10, 15], 30: [7, 15, 22], 40: [10, 20, 30]}
n_covered = 0
for cand in ["lam1n", "hkz"]:
    for lat, (dd, kk) in LATTICES.items():
        e = g[cand][lat]
        beta_lo, beta_hi = e["beta_lo"], e["beta_hi"]
        n_bases = len(e["per_basis"])
        for beta in BETA_GRID[dd]:
            covered = beta in (beta_lo, beta_hi)
            if covered:
                n_covered += 1
            mid = "MIDDLE-BETA-UNCOVERED" if not covered else ("COVERED@beta_lo" if beta == beta_lo else "COVERED@beta_hi")
            print(f"{cand}/{lat}_b{beta}: beta_lo={beta_lo} beta_hi={beta_hi} n_bases={n_bases} -> {mid}")
print("TOTAL COVERED:", n_covered, "of 18 (expect 12)")
PYEOF

echo
echo "=== I. no-reduction-above-d=40 check (lead's committed script) ==="
grep -n "LATTICES = " coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/tasks/TASK-20260813-ea2e96/measure_route_reimpl.py
grep -c "lll_reduce(\|enumerate_svp(\|build_basis_indep(" coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/tasks/TASK-20260813-ea2e96/measure_route_reimpl.py
echo "(all three functions are called only inside the 'for lat in lattices_with_coverage: d,k=LATTICES[lat]' loop -- d,k always come from the fixed LATTICES dict {L7:(20,6),L9:(30,9),L11:(40,12)}, confirmed by direct reading)"

echo
echo "=== J. L11 timeout exclusion check ==="
python3 - <<'PYEOF'
import json
d = json.load(open('coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/tasks/TASK-20260813-ea2e96/results_route_reimpl.json'))
log = d['route_i_prime_per_basis_log']
for i in range(8):
    v = log[f'L11/i{i}']
    print(f"L11/i{i}: svp_exact={v.get('svp_exact')} enum_secs={v.get('enum_secs'):.2f} enum_nodes={v.get('enum_nodes')}")
matched_lam = [m['basis'] for m in d['R_IV_OUT_2_per_cell']['lam1n/L11_b10']['matched_bases_detail']]
matched_hkz = [m['basis'] for m in d['R_IV_OUT_2_per_cell']['hkz/L11_b10']['matched_bases_detail']]
print("lam1n/L11_b10 matched bases:", matched_lam, "(expect [0,2,3,4,7] -- excludes 1,5,6)")
print("hkz/L11_b10 matched bases:", matched_hkz, "(expect all 8 -- hkz uses the LLL-reduced GSO tail directly, not gated on exact SVP)")
PYEOF

echo
echo "END OF probe_checks.sh"
