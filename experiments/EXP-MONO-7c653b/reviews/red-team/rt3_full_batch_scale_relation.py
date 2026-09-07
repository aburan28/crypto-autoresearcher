#!/usr/bin/env python3
"""RT-20260905-340bf1, joint 2 -- full-batch corroboration beyond the single
hand-worked trial in rt1_mutant_reconstruction.py.

For ALL 50 trials in each official run's stage4a block, checks the pure
arithmetic identity

    mutant_twist_route_xset == { (delta * inverse(delta_prime) * c) mod p
                                   : c in direct_route_xset }

directly against the values ALREADY RECORDED in each run's own
raw-result.json (no re-execution of the group law needed for this check).
This relation can hold for all 50 trials only if the pre-rescaling
accumulator X(R) is IDENTICAL between the "correct" and "mutant" route in
every trial -- i.e. only if delta_prime enters nowhere except the single
final division -- which is a full algebraic confirmation across the whole
sample, not merely the one trial reconstructed by hand.

Run: python3 rt3_full_batch_scale_relation.py
"""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]

for run_id, seed in [("RUN-MONO-7c653b-1", 20260905), ("RUN-MONO-7c653b-2", 20260906)]:
    path = REPO_ROOT / f"experiments/EXP-MONO-7c653b/runs/{run_id}/raw-result.json"
    d = json.load(open(path))
    s4a = d["stage4a"]
    p = s4a["p"]
    delta = s4a["delta"]
    delta_prime = s4a["delta_prime"]
    scale = (delta * pow(delta_prime, -1, p)) % p
    trials = s4a["trials"]
    ok = 0
    mismatches = []
    for i, t in enumerate(trials):
        correct = t["direct_route_xset"]
        mutant = t["mutant_twist_route_xset"]
        predicted = sorted((c * scale) % p for c in correct)
        if predicted == mutant:
            ok += 1
        else:
            mismatches.append((i, correct, mutant, predicted))
    all_false = all(not t["match"] for t in trials)
    print(f"{run_id} (seed={seed}): delta={delta} delta_prime={delta_prime} "
          f"scale=delta*inv(delta_prime) mod p={scale} (!=1: {scale != 1})")
    print(f"  {ok}/{len(trials)} trials satisfy mutant == scale*correct elementwise")
    print(f"  reported n_mutant_reproduces_direct_route = "
          f"{s4a['n_mutant_reproduces_direct_route']}; "
          f"all 'match' flags false: {all_false}")
    if mismatches:
        print("  MISMATCHES:", mismatches)
    assert ok == len(trials), "algebraic relation failed to hold for all trials"
    assert scale != 1
    assert all_false

print("\nALL CHECKS PASSED for both official runs.")
