#!/usr/bin/env python3
"""
RED TEAM PROBE 2 -- "same-code rerun" null-object baseline.

Runs ROUTE-P's OWN hkz_profile/build_basis code (measure_relvar.py, BATCH-9e3584,
imported directly and UNMODIFIED) IN THIS RED-TEAM SESSION, at a different time
than the original archived run, and compares the freshly-computed hkz value
DIRECTLY against the ARCHIVED value in results_relvar.json (i.e. against
route_p_values as read by the lead producer).

Purpose: establish how much floating-point drift a REEXECUTION of the IDENTICAL
code produces, as the most conservative possible baseline for "should match
exactly." If even a same-code rerun shows a nonzero delta of similar magnitude
to the lead's reported cross-implementation D_route'', that tells us the
observed ~1e-15 scale is close to the noise floor of fpylll's own
determinism/reproducibility, not distinctively informative about
cross-implementation independence. If the same-code rerun is BIT-IDENTICAL
(delta=0) while the cross-implementation D_route'' is systematically nonzero
at the SAME scale, that is also informative (points to some genuine, if tiny,
cross-implementation numerical difference beyond pure nondeterminism).
"""
import sys, os, math, json
import numpy as np

REPO = "/home/user/crypto-autoresearcher"
sys.path.insert(0, os.path.join(REPO,
    "coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/TASK-20260809-cda2f6"))
import measure_relvar as MR  # noqa: E402

RESULTS_HKZ_INDEP = os.path.join(REPO,
    "coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/tasks/"
    "TASK-20260813-c0ec71/results_hkz_indep.json")

Q = 3329
CELLS = [
    ("hkz/L7_b5",   "L7", 20, 6, 5),
    ("hkz/L7_b15",  "L7", 20, 6, 15),
    ("hkz/L9_b7",   "L9", 30, 9, 7),
    ("hkz/L9_b22",  "L9", 30, 9, 22),
    ("hkz/L11_b10", "L11", 40, 12, 10),
    ("hkz/L11_b30", "L11", 40, 12, 30),
]

with open(RESULTS_HKZ_INDEP) as fh:
    hkz_indep = json.load(fh)

print("%-14s %-3s  archived_route_p        same-code-rerun         "
      "delta(rerun-archived)   |delta| vs reported D_route''" % (
          "cell", "i"))
for cell_name, lat, d, k, beta in CELLS:
    cell = hkz_indep["R_V_OUT_2_per_cell"][cell_name]
    route_p_archived = cell["route_p_values"]
    d_route_reported = cell["D_route_pp"]
    for i in range(len(route_p_archived)):
        B = MR.build_basis(d, k, Q, i)
        prof = MR.hkz_profile(B.astype(np.float64), d)
        if prof.get("status") != "ok":
            print(cell_name, i, "FAILED:", prof.get("status"))
            continue
        r = prof["r"]
        logdet = prof["logdet"]
        logb = 0.5 * np.log(r)
        hkz_rerun = float(np.mean(logb[d - beta:]) - logdet / d)
        archived = route_p_archived[i]
        delta = hkz_rerun - archived
        print("%-14s %-3d  %.17f  %.17f  %+.6e  (reported D_route''=%.6e)"
              % (cell_name, i, archived, hkz_rerun, delta, d_route_reported))
