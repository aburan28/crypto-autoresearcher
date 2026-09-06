#!/usr/bin/env python3
"""rt_r4_extras.py -- RED TEAM derivation aid for TASK-20260904-6681da (R4).

(a) the two standardized sizes docs/evidence-and-reproducibility.md names that
    the frozen 64/128/256 grid omits (384, 512), for the headline cell;
(b) the time-memory interpolation the artifact declares absent: within the
    model, choosing a factor base B BELOW the balance gives
        time = m! 2^m C N / B^{m-1},  memory = B,
    so the minimum memory at which the route still matches rho on time is
        log2 B = (log2 m! + log2(2^m C) + log2 N - log2 rho) / (m - 1).

Imports the primitives of rt_cost_recheck.py (same directory).  Not an
experiment.  Standard library only.
"""
import os
from math import log2, factorial

_here = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(_here, "rt_cost_recheck.py")).read().split("import sys as _sys")[0]
exec(_src)  # noqa: S102 -- primitives only (ncols, d_reg_pkg, balance, log2_rho)

print("--- (a) larger standardized sizes, m = 5, D_0 = 4 ---")
for L in (256, 384, 512):
    for om in OMEGAS:
        b = balance(5, 4, om, L, dreg_pkg_wrapper)
        print(f"log2N={L} omega={om} T={b['log2T']:.2f} rho={log2_rho(L):.2f} "
              f"T-rho={b['log2T'] - log2_rho(L):+.2f} mem={b['log2_mem']:.2f}")

print("--- (b) minimum memory at which the route still matches rho on time "
      "(256 bits) ---")
for (m, D0, om) in ((5, 4, 2.0), (5, 4, 2.807), (5, 6, 2.0), (5, 8, 2.0)):
    b = balance(m, D0, om, 256, dreg_pkg_wrapper)
    n = b["n"]
    lC = m + om * log2(ncols(n, min(D0, d_reg_pkg(n, m))))
    lB = (log2(factorial(m)) + lC + 256 - log2_rho(256)) / (m - 1)
    print(f"m={m} D_0={D0} omega={om}: log2 C0(with 2^m)={lC:.2f}, "
          f"balanced mem={b['log2_mem']:.2f}, min mem to match rho = {lB:.2f}")
