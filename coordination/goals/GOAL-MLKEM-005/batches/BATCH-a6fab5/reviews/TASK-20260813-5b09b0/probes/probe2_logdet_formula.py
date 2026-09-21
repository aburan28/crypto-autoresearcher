#!/usr/bin/env python3
"""
RED TEAM PROBE 1 -- tests whether ROUTE-P's actual "hkz" logdet formula is
really "the exact closed-form (d-k)*log(q)" as the lead producer's
INDEPENDENCE DECLARATION claims, or the GSO-summed empirical logdet that
measure_relvar.py (BATCH-9e3584, TASK-20260809-cda2f6) actually computes at
line 564 (`logdet = prof["logdet"]`, where `prof["logdet"]` is
`hkz_profile`'s own `0.5 * float(np.sum(np.log(r)))`, NOT
`x_null_of`'s closed form).

This probe DOES NOT build a ROUTE-I'' claim of its own -- it is a red-team
diagnostic, run once, to directly measure how much this formula
substitution (closed form vs GSO-summed empirical) can plausibly account
for the reported D_route'' magnitude, independent of any implementation
"independence" question.

We import ROUTE-P's own hkz_profile/build_basis directly (permitted for a
red-team diagnostic; this script makes no ROUTE-I'' independence claim).
"""
import sys, os, math
import numpy as np

REPO = "/home/user/crypto-autoresearcher"
sys.path.insert(0, os.path.join(REPO,
    "coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/TASK-20260809-cda2f6"))

import measure_relvar as MR  # noqa: E402

Q = 3329

CELLS = [
    ("L7", 20, 6, 5),
    ("L7", 20, 6, 15),
    ("L9", 30, 9, 7),
    ("L9", 30, 9, 22),
    ("L11", 40, 12, 10),
    ("L11", 40, 12, 30),
]

print("cell           closed_form(d-k)*ln(q)/d     empirical 0.5*sum(ln(r))/d    "
      "abs_diff_in_logdet/d     hkz_closed - hkz_empirical (basis 0)")
for lat, d, k, beta in CELLS:
    B = MR.build_basis(d, k, Q, 0)
    prof = MR.hkz_profile(B.astype(np.float64), d)
    if prof.get("status") != "ok":
        print(lat, "FAILED:", prof.get("status"))
        continue
    r = prof["r"]
    logdet_empirical = prof["logdet"]                 # ROUTE-P's actual formula
    logdet_closed = (d - k) * math.log(Q)              # what ROUTE-II actually used
    logb = 0.5 * np.log(r)
    hkz_empirical = float(np.mean(logb[d - beta:]) - logdet_empirical / d)
    hkz_closed = float(np.mean(logb[d - beta:]) - logdet_closed / d)
    print("%-6s d=%-3d b=%-3d  closed/d=%.17f  empirical/d=%.17f  "
          "diff=%.6e   hkz_closed-hkz_empirical=%.6e"
          % (lat, d, beta, logdet_closed / d, logdet_empirical / d,
             abs(logdet_closed - logdet_empirical) / d,
             hkz_closed - hkz_empirical))
