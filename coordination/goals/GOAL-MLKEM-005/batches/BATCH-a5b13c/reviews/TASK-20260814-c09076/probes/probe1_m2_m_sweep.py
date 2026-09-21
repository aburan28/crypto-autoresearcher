#!/usr/bin/env python3
"""RED-TEAM PROBE 1 (TASK-20260814-c09076, GOAL-MLKEM-005/BATCH-a5b13c).

ATTACK TARGET: the producer's M2 result (beta(M2)=617 at reduced_m=236,
255 bits below beta(M0)=872 at ML-KEM-1024, vs H-MLKEM-11aabf's own
predicted 2-4 bit minimum_effect).

QUESTION: is primal_bdd's beta/rop output TRUSTWORTHY in an m<<n regime this
extreme (m=236 vs n=1024, ~23% of the base sample count)? We sweep m across
several intermediate values between 236 and 1024 (and beyond/below) at the
SAME Kyber1024 noise construction the producer's own M2 used verbatim
(Xs=base.Xs, Xe=base.Xe, unmodified -- i.e. the "clean" key-side-identical
noise, only the sample count m is varied), and record beta/rop/eta/d at
each point to check for smoothness, monotonicity, an inflection, or a
discontinuity near m=236.

This probe deliberately reuses EXACTLY the producer's own M2 instance
construction (estimator.schemes.Kyber1024 base object; Xs=base.Xs,
Xe=base.Xe unmodified; only m varied) -- not a new noise model -- so any
anomaly found is attributable to the m-sweep alone, not to a construction
difference from the producer's own artifact.

Independent of the producer's ciphertext_noise_readout.py: this file does
NOT import it. It imports only the estimator itself (pinned commit
3e48ef421ec256afddb3e7d2249a77eab6e9ba12, PYTHONPATH set at invocation, see
command.txt in this probes/ directory's sibling run).

NO LATTICE REDUCTION OF ANY KIND (fpylll/BKZ/HKZ) -- primal_bdd is a
closed-form cost-model readout only, matching PREREG-7 section 5.4's
constraint, carried into this probe.
"""
from __future__ import annotations

import json
import math
import sys
import time

from estimator import RC, schemes
from estimator.lwe_primal import primal_bdd
from estimator.lwe_parameters import LWEParameters


def main() -> int:
    base = schemes.Kyber1024
    print(f"base: n={base.n} m={base.m} q={base.q} Xs={base.Xs} Xe={base.Xe}",
          file=sys.stderr)

    # Dense near the producer's own reduced_m=236 (the fibre-fraction value),
    # then coarser out to and beyond the base m=n=1024, plus below 236 to
    # bracket the whole regime.
    m_values = [10, 50, 100, 150, 200, 220, 230, 236, 240, 250, 260, 280,
                300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850,
                900, 950, 1000, 1024, 1100, 1200, 1400, 1600, 2000, 3000]

    rows = []
    t_start = time.time()
    for m in m_values:
        p = LWEParameters(n=base.n, q=base.q, Xs=base.Xs, Xe=base.Xe, m=m,
                           tag=f"Kyber1024-m{m}-cleanXe")
        t0 = time.time()
        exc = None
        try:
            r = primal_bdd(p, red_cost_model=RC.MATZOV)
            beta = int(r["beta"])
            eta = int(r["eta"])
            d = int(r["d"])
            log2_rop = math.log2(float(r["rop"]))
        except Exception as e:  # noqa: BLE001 -- deliberately broad: this IS the probe
            beta = eta = d = None
            log2_rop = None
            exc = f"{type(e).__name__}: {e}"
        dt = time.time() - t0
        row = {
            "m": m, "n": base.n, "m_over_n": round(m / base.n, 4),
            "beta": beta, "eta": eta, "d": d, "log2_rop": log2_rop,
            "exception": exc, "call_seconds": round(dt, 4),
        }
        rows.append(row)
        print(json.dumps(row), file=sys.stderr)

    total_dt = time.time() - t_start

    # Monotonicity / smoothness diagnostics -- exactly what the task asks:
    # does beta scale smoothly/monotonically, or does something qualitatively
    # break (inflection, discontinuity, instability) near m=236?
    ok_rows = [r for r in rows if r["beta"] is not None]
    diffs = []
    for a, b in zip(ok_rows, ok_rows[1:]):
        dbeta = b["beta"] - a["beta"]
        dm = b["m"] - a["m"]
        diffs.append({
            "m_from": a["m"], "m_to": b["m"], "delta_m": dm,
            "delta_beta": dbeta,
            "beta_per_100_m": round(100 * dbeta / dm, 3) if dm else None,
        })

    # Monotonic-decreasing check (beta should not INCREASE as m increases,
    # under the "more samples helps the attacker" intuition -- an increase
    # is the artifact tell this probe is built to catch).
    non_monotone = [d for d in diffs if d["delta_beta"] > 0]

    # Where does the producer's own reduced_m=236 fall on this curve, and
    # is there a large jump immediately around it relative to the typical
    # per-step change elsewhere on the curve?
    typical_step = sorted(abs(d["delta_beta"]) for d in diffs if d["delta_m"] <= 20)
    median_typical_step = (
        typical_step[len(typical_step) // 2] if typical_step else None
    )

    out = {
        "purpose": "m-sweep control for the M2 255-bit anomaly: same clean "
                   "Kyber1024 noise (Xs=Xe=base CBD(eta1)), m varied from 10 "
                   "to 3000 (n=1024 fixed). Tests whether beta degrades "
                   "smoothly as samples shrink toward the producer's own "
                   "reduced_m=236, or whether something qualitatively "
                   "breaks in that regime.",
        "producer_M2_reduced_m": 236,
        "producer_M2_beta": 617,
        "producer_M0_beta_kyber1024": 872,
        "producer_key_side_beta_kyber1024": 855,
        "rows": rows,
        "pairwise_diffs": diffs,
        "non_monotone_increases_found": non_monotone,
        "median_abs_delta_beta_per_step_where_delta_m_leq_20": median_typical_step,
        "total_wall_clock_seconds": round(total_dt, 3),
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
