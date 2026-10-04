#!/usr/bin/env python3
"""RT-20260905-340bf1, joint 3 (499-vs-500 independent_sample_check discrepancy).

Re-executes the IMPLEMENTATION'S OWN deterministic draw functions
(SeedStream, draw_distinct, twisted_factor_base -- imported directly from
implementation/run_experiment.py, since this is an investigative
reproduction of an already-executed, fully-deterministic PRNG stream, not
the from-scratch blind re-derivation assigned to the other joint) to find
the EXACT mechanism behind:

    RUN-MONO-7c653b-1 raw-result.json:
        independent_sample_check.stage3_m4_p211_tuple_count == 499
        stage3.cells.m4_p211.n_completed == 500

for every (seed, m, p) cell in both official runs, to check whether the
same class of discrepancy appears anywhere else.

Run: python3 rt2_tuple_count_discrepancy.py
(run from the repo root, or adjust sys.path below)
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "experiments/EXP-MONO-7c653b/implementation"))

import run_experiment as R  # noqa: E402

CURVES = R.CURVES
STAGE3_N_PER_CELL = R.STAGE3_N_PER_CELL
STAGE3_M_VALUES = R.STAGE3_M_VALUES

print("=" * 78)
print("Per-cell duplicate-value-set audit, both official seeds, all 4 cells")
print("=" * 78)
any_dup_outside_target = False
for seed in [20260905, 20260906]:
    domain = f"EXP-MONO-7c653b/v1/run-{seed}"
    for m in STAGE3_M_VALUES:
        n = STAGE3_N_PER_CELL[m]
        k = m - 1
        for name, c in CURVES.items():
            p, a, b = c["p"], c["a"], c["b"]
            tfb = R.twisted_factor_base(p, a, b)
            stream = R.SeedStream(domain, "twisted-fb-tuple", p, m)
            seen = {}
            dups = []
            for i in range(n):
                t = R.draw_distinct(stream, tfb["xs"], k)
                key = tuple(sorted(t))
                if key in seen:
                    dups.append((i, seen[key], t))
                else:
                    seen[key] = i
            tag = "  <-- DUPLICATE(S) FOUND" if dups else ""
            print(f"seed={seed} m{m}_{name}: n={n} fb_size={tfb['size']:>4} "
                  f"distinct={len(seen)}{tag}")
            if dups and not (seed == 20260905 and m == 4 and name == "p211"):
                any_dup_outside_target = True
            for (i, j, t) in dups:
                print(f"    trial {i} repeats trial {j}'s value-set: draw={t}")

print()
print("Any duplicate OUTSIDE seed=20260905/m4_p211?", any_dup_outside_target)

print()
print("=" * 78)
print("Reproducing the exact colliding pair for RUN-1 (seed 20260905), m4_p211")
print("=" * 78)
p, a, b, m = 211, 37, 57, 4
tfb = R.twisted_factor_base(p, a, b)
domain = "EXP-MONO-7c653b/v1/run-20260905"
stream = R.SeedStream(domain, "twisted-fb-tuple", p, m)
draws = [R.draw_distinct(stream, tfb["xs"], 3) for _ in range(500)]
seen = {}
collisions = []
for i, t in enumerate(draws):
    key = tuple(sorted(t))
    if key in seen:
        collisions.append((seen[key], i, draws[seen[key]], t, key))
    else:
        seen[key] = i
print("twisted_factor_base(p=211) size:", tfb["size"], "(C(100,3) =", 100*99*98//6, "possible triples)")
print("all collisions (trial_a, trial_b, draw_a, draw_b, shared_sorted_key):", collisions)
print("distinct sorted-tuple count among all 500 draws:", len(seen), "(500 - len(collisions) =", 500 - len(collisions), ")")

# Birthday-bound sanity check for plausibility (not a proof, a plausibility gate)
import math
Npool = 100 * 99 * 98 // 6
ndraw = 500
p_collision = 1 - math.exp(-ndraw * (ndraw - 1) / (2 * Npool))
print(f"birthday-approx P(>=1 collision in {ndraw} draws from {Npool} triples) = {p_collision:.3f}")

print()
print("=" * 78)
print("Does stage3_cell's own n_completed counter double-count or drop this?")
print("=" * 78)
print("stage3_cell increments trials_completed by exactly 1 per loop iteration,")
print("unconditionally (implementation/run_experiment.py lines 458-500,")
print("'trials_completed += 1' at line 500, inside 'for i in range(n)'),")
print("regardless of whether the drawn tuple_x value-set repeats an earlier")
print("iteration's. Both the direct-route poly_split_analysis call and the")
print("twist-route build_points_delta/twist_route_xset call are executed AGAIN")
print("in full for the colliding trial -- nothing is skipped, cached, or reused")
print("across iterations. n_completed=500 therefore counts 500 independently")
print("executed and independently match-checked trials, exactly as claimed.")
