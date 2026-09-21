#!/usr/bin/env python3
"""RED-TEAM PROBE 2 -- fine-grained boundary scan around the producer's own
reduced_m=236, and a reproducibility check (independent re-run of the exact
producer M2 call from scratch, in this session, per this task's THIRD
TARGET). Same construction as probe1 (Xs=Xe=base Kyber1024 CBD noise,
m varied); this probe narrows the step size to 2-5 around the region where
probe1 found a KeyError boundary (m<=200) and a large non-monotone jump
(m=236 -> m=240)."""
from __future__ import annotations

import json
import math
import sys

from estimator import RC, schemes
from estimator.lwe_primal import primal_bdd
from estimator.lwe_parameters import LWEParameters


def call_at(base, m):
    p = LWEParameters(n=base.n, q=base.q, Xs=base.Xs, Xe=base.Xe, m=m,
                       tag=f"Kyber1024-m{m}-cleanXe")
    try:
        r = primal_bdd(p, red_cost_model=RC.MATZOV)
        return {
            "m": m, "beta": int(r["beta"]), "eta": int(r["eta"]),
            "d": int(r["d"]), "log2_rop": math.log2(float(r["rop"])),
            "exception": None,
        }
    except Exception as e:  # noqa: BLE001
        return {"m": m, "beta": None, "eta": None, "d": None,
                "log2_rop": None, "exception": f"{type(e).__name__}: {e}"}


def main() -> int:
    base = schemes.Kyber1024

    print("--- coarse boundary search: where does the KeyError('beta') "
          "failure stop firing? ---", file=sys.stderr)
    boundary_rows = []
    for m in [190, 195, 200, 202, 204, 206, 208, 210, 212, 214, 216, 218,
              219, 220]:
        row = call_at(base, m)
        boundary_rows.append(row)
        print(json.dumps(row), file=sys.stderr)

    print("--- fine scan 220..260 step 2, bracketing the 236->240 jump ---",
          file=sys.stderr)
    fine_rows = []
    for m in range(220, 261, 2):
        row = call_at(base, m)
        fine_rows.append(row)
        print(json.dumps(row), file=sys.stderr)

    print("--- reproducibility check: repeat m=236 five times in this "
          "session, from scratch, to confirm determinism ---", file=sys.stderr)
    repro_rows = [call_at(base, 236) for _ in range(5)]
    for row in repro_rows:
        print(json.dumps(row), file=sys.stderr)
    repro_betas = {r["beta"] for r in repro_rows}

    out = {
        "purpose": "Fine boundary scan around producer's reduced_m=236 "
                   "(finds where the KeyError('beta') failure mode starts/"
                   "stops, and characterizes the 236->240 jump at step "
                   "granularity 2) plus a 5x reproducibility check on the "
                   "exact m=236 call.",
        "boundary_scan_190_to_220": boundary_rows,
        "fine_scan_220_to_260_step_2": fine_rows,
        "reproducibility_check_m236_x5": repro_rows,
        "reproducibility_beta_set": sorted(repro_betas),
        "reproducible": len(repro_betas) == 1,
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
