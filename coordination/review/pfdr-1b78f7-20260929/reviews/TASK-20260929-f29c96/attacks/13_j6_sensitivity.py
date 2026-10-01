"""J6(a) sensitivity of the family-wise calibration to the dispersion inputs (added after 04; the
choice of these two variants was made before running them and is stated here):
  G-NB-med  gamma-Poisson with D per (class, m) = the MEDIAN of D_rung over the eleven rungs
            (removes rungs whose D is inflated by one large bundle);
  G-CP-0    compound Poisson with the measured multiplicity distribution and NO relation-level
            frailty (phi = 0): the lightest-tailed version of G-CP.
R = 20000; numpy default_rng(20260939 + k).  Output: attacks/out/13_j6_sensitivity.json
"""
import json
import os
import statistics
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rtlib import OUT, RUNGS  # noqa: E402
import j6design  # noqa: E402
from j6design import Design  # noqa: E402

import importlib.util  # noqa: E402
spec = importlib.util.spec_from_file_location("fam04", os.path.join(os.path.dirname(os.path.abspath(__file__)), "04_j6_family_null.py"))
fam04 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fam04)


def run(des, gen, rng, R):
    cols = fam04.simulate(des, gen, rng, R)
    exc = np.zeros(R, dtype=int)
    pos = np.zeros(R, dtype=int)
    maxz = np.zeros(R)
    for key, z, res in cols:
        if z is None:
            continue
        res = res & ~np.isnan(z)
        za = np.where(res, z, 0.0)
        exc += res & (np.abs(za) > 3)
        pos += res & (za > 3)
        maxz = np.maximum(maxz, np.abs(za))
    return {"E_excursions": float(exc.mean()), "P_ge_4": float((exc >= 4).mean()),
            "P_ge_4_all_positive": float(((exc >= 4) & (pos == exc)).mean()),
            "P_max_absz_ge_4p75": float((maxz >= 4.7515).mean())}


def main():
    des = Design()
    out = {}
    D0 = dict(des.D)
    med = {}
    for cl in ("TT", "SS"):
        for m in (3, 4, 5):
            md = statistics.median(D0[(cl, m, b)] for b in RUNGS)
            med[f"{cl}|{m}"] = md
            for b in RUNGS:
                des.D[(cl, m, b)] = md
    out["G-NB-med"] = run(des, "G-NB", np.random.default_rng(20260939), 20000) | {"D_median_by_class_m": med}
    des.D = D0
    phi0 = dict(des.phi)
    for k in des.phi:
        des.phi[k] = 0.0
    out["G-CP-0"] = run(des, "G-CP", np.random.default_rng(20260940), 20000)
    des.phi = phi0
    with open(os.path.join(OUT, "out", "13_j6_sensitivity.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
