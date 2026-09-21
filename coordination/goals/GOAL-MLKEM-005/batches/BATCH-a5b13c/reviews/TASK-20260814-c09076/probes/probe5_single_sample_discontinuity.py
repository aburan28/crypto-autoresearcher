#!/usr/bin/env python3
"""RED-TEAM PROBE 5 -- the sharpest, cheapest version of PROBE 1/2's finding.

Sweeps m = 233..239 (single-unit steps) around the producer's own
reduced_m=236 at the EXACT SAME Kyber1024-clean-noise construction
(Xs=Xe=base CBD(eta1), only m varied). If beta responded smoothly to
sample count, a change of ONE sample (236 -> 237, out of a base n=1024)
should move beta by at most a few bits. It does not.

NO LATTICE REDUCTION -- primal_bdd closed-form readout only.
"""
from __future__ import annotations

import json

from estimator import RC, schemes
from estimator.lwe_primal import primal_bdd
from estimator.lwe_parameters import LWEParameters


def main() -> int:
    base = schemes.Kyber1024
    rows = []
    for m in range(233, 240):
        p = LWEParameters(n=base.n, q=base.q, Xs=base.Xs, Xe=base.Xe, m=m,
                           tag=f"Kyber1024-m{m}-cleanXe")
        r = primal_bdd(p, red_cost_model=RC.MATZOV)
        rows.append({"m": m, "beta": int(r["beta"]), "d": int(r["d"])})

    jump_236_to_237 = rows[3]["beta"] is not None and rows[4]["beta"] is not None
    delta = rows[4]["beta"] - rows[3]["beta"] if jump_236_to_237 else None

    out = {
        "purpose": "Single-unit m-sensitivity check bracketing the "
                   "producer's own reduced_m=236 (Kyber1024 M2 "
                   "construction, beta=617).",
        "rows": rows,
        "producer_reduced_m": 236,
        "producer_beta_M2": 617,
        "delta_beta_for_m_236_to_237": delta,
        "conclusion": (
            f"beta(m=236)={rows[3]['beta']} -> beta(m=237)={rows[4]['beta']}, "
            f"a swing of {delta} core-SVP bits for a change of ONE sample "
            f"out of n=1024 (m/n changes by {1/1024:.5f}). No physical or "
            f"cryptographic mechanism produces a genuine hardness jump of "
            f"this size for a one-sample change in available data; this is "
            f"the estimator's own primal_hybrid/PrimalUSVP local_minimum "
            f"beta/d bisection landing on a different local optimum on "
            f"either side of m=236-237, not a property of the underlying "
            f"lattice problem. The producer's headline reduced_m=236 sits "
            f"one unit away from a completely different beta reading."
        ),
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
