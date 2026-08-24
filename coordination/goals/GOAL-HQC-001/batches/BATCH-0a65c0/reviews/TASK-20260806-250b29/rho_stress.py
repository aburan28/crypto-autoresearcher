#!/usr/bin/env python3
"""RED TEAM: q-sensitivity at the PHYSICAL MAXIMUM of the nuisance.
TASK-20260806-250b29.  Output of record: rho_stress.txt.

amendment_v3.yaml correctly records that SE(q_hat)/q_hat = sqrt((1-q)/failures)
is the rho = 0 (independent-blocks) VALUE and a LOWER bound under the positive
block correlation the experiment exists to detect.  It defends the reduced sets
with the validator's MEASURED inflation factors (1.00/1.34/1.69/2.35).  Nobody
asked what happens at rho = 1, where Var(q_hat) = q(1-q)(1+(n_e-1))/(n_e T) and
the inflation is sqrt(n_e).  Measured here.

Claim tier TOY.  Every draw is from S ~ Binomial(n_e, q) under an explicit null.
"""
import math, sys
sys.path.insert(0, ".")
from resize import load_cfgs, measure, BLOCK_FAILURES, myseed, ACCEPT
import numpy as np

cfgs = load_cfgs()
for w, (s, a) in (("PS-R3@1e7", ("PS-R3", "1e7")), ("PS-R1@1e8", ("PS-R1", "1e8")),
                  ("PS-R5@2e7", ("PS-R5", "2e7"))):
    F = cfgs[(s, a)]
    n_e, q0, T = F["n_e"], F["q_hat"], F["T"]
    ks = sorted(F["cells"])
    lo = np.array([F["cells"][k][0] for k in ks])
    hi = np.array([F["cells"][k][1] for k in ks])
    se0 = math.sqrt((1 - q0) / BLOCK_FAILURES[s])
    infl = math.sqrt(1.0 + (n_e - 1) * 1.0)          # rho = 1, the physical maximum
    print("== %s  n_e=%d  3SE(rho=0)=%.6f  max inflation sqrt(1+(n_e-1)) = %.3f  3SE(rho=1)=%.6f"
          % (w, n_e, 3 * se0, infl, 3 * se0 * infl))
    worst_in = True
    for d in (-3 * se0 * infl, +3 * se0 * infl):
        fr, fi, _, _ = measure(n_e, q0 * (1 + d), T, ks, lo, hi, 400000,
                               myseed(s, a, "rho1", repr(d)))
        sz = [fr[j] / fi[j] for j in range(len(ks))]
        ok = all(ACCEPT[0] <= x <= ACCEPT[1] for x in sz)
        worst_in &= ok
        print("   shift %+9.6f (%+6.1f nominal SE): min %.5f  max %.5f  all 17 in [0.002,0.004]: %s"
              % (d, d / se0, min(sz), max(sz), ok))
    print("   -> robust across +-3 SE even at rho = 1 (worst case): %s\n" % worst_in)
