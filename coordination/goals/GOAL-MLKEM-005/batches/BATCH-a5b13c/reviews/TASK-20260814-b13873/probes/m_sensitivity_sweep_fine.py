#!/usr/bin/env python3
"""Finer m-sweep, step 5, bracketing the M2 point (m=236) and the region
where primal_bdd's beta went non-monotonic (300 -> 260 -> 236 -> 220) and
then broke down entirely (rop=inf) at m<=200, per m_sensitivity_sweep.py's
coarser first pass. Validator-built control, TASK-20260814-b13873 target #2."""
import math
import json

from estimator import RC, schemes
from estimator.lwe_primal import primal_bdd

M_VALUES = list(range(200, 305, 5))


def main():
    out = []
    for m in M_VALUES:
        params = schemes.Kyber1024.updated(m=m, tag=f"fine-m{m}")
        r = primal_bdd(params, red_cost_model=RC.MATZOV)
        d = dict(r)
        entry = {"m": m}
        if "beta" in d:
            entry["beta"] = int(d["beta"])
            entry["eta"] = int(d["eta"])
            entry["d"] = int(d["d"])
            entry["log2_rop"] = math.log2(float(d["rop"])) if math.isfinite(float(d["rop"])) else "inf"
        else:
            entry["raw_repr"] = repr(r)
        out.append(entry)
    print(json.dumps(out, indent=2))
    return out


if __name__ == "__main__":
    main()
