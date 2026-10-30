"""J3a internal split-half replication of the cell-level heterogeneity (no new curves).

If the excess spread of gap z across cells (omnibus-null-controls.json) is a real cell-specific effect, the z of
the even-index curves and the z of the odd-index curves of the same cell estimate the same effect, so they are
positively correlated across the 44 powered cells; under pure noise the correlation is ~0. The identical
statistic with null replicate k as the structured arm against the other 19 (k = 0..19) is the matched null.
Also reported: per (bits, r) Stouffer z on each half for the three strata with the largest pooled |z|.
Writes outputs/split-half.json.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import math  # noqa: E402

import numpy as np  # noqa: E402

import common as C  # noqa: E402


def main():
    recs = C.load_jobs()
    design = C.load_design()["toy_cells"]
    cells = C.by_cell(recs)
    rows = []
    for d in design:
        rs = cells.get(d["cell"], [])
        if len(rs) < d["n_curves"]:
            continue
        g, m, s2, nulls = C.curve_arrays(rs)
        cidx = np.array([r["c"] for r in rs])
        rows.append((d, g, m, s2, nulls, cidx % 2 == 0))

    def zhalf(x, mu, var, sel, fac):
        return float((x[sel] - mu[sel]).sum() / math.sqrt(fac * var[sel].sum()))

    ze = np.array([zhalf(g, m, s2, ev, 1.05) for d, g, m, s2, nulls, ev in rows])
    zo = np.array([zhalf(g, m, s2, ~ev, 1.05) for d, g, m, s2, nulls, ev in rows])
    corr_gap = float(np.corrcoef(ze, zo)[0, 1])
    corr_null = []
    for k in range(20):
        a, b = [], []
        for d, g, m, s2, nulls, ev in rows:
            o = np.delete(nulls, k, axis=1)
            mo, vo = o.mean(axis=1), o.var(axis=1, ddof=1)
            a.append(zhalf(nulls[:, k], mo, vo, ev, 1 + 1 / 19))
            b.append(zhalf(nulls[:, k], mo, vo, ~ev, 1 + 1 / 19))
        corr_null.append(float(np.corrcoef(a, b)[0, 1]))
    K = len(rows)
    # Fisher z test of corr_gap against 0
    fz = math.atanh(corr_gap) * math.sqrt(K - 3)
    strata = {}
    for bits, r in ((20, 3), (28, 1), (24, 1), (20, 1), (24, 3), (28, 2)):
        sel = [i for i, x in enumerate(rows) if x[0]["bits"] == bits and x[0]["r"] == r]
        strata[f"bits={bits},r={r}"] = {"cells": [rows[i][0]["cell"] for i in sel],
                                        "z_even": [float(ze[i]) for i in sel], "z_odd": [float(zo[i]) for i in sel],
                                        "stouffer_even": float(ze[sel].sum() / math.sqrt(len(sel))),
                                        "stouffer_odd": float(zo[sel].sum() / math.sqrt(len(sel)))}
    out = {"task": "TASK-20261029-11526b", "joint": "J3a item (5) follow-up",
           "inputs": [C.rel(C.JOBS), C.rel(C.DESIGN)], "method": __doc__.strip(),
           "cells": K, "corr_z_even_z_odd_gap": corr_gap, "fisher_z_gap": fz,
           "two_sided_p_gap": 2 * C.phi(-abs(fz)),
           "corr_null_k": corr_null, "null_mean": float(np.mean(corr_null)), "null_sd": float(np.std(corr_null, ddof=1)),
           "null_k_with_corr_ge_gap": int(sum(c >= corr_gap for c in corr_null)),
           "sum_z2_even_gap": float((ze ** 2).sum()), "sum_z2_odd_gap": float((zo ** 2).sum()),
           "strata": strata}
    C.write_json("split-half.json", out, sig=6)
    print({k: v for k, v in out.items() if k not in ("strata", "method", "corr_null_k")})
    print(sorted(np.round(corr_null, 3)))
    for k, v in strata.items():
        print(k, round(v["stouffer_even"], 2), round(v["stouffer_odd"], 2), [round(x, 2) for x in v["z_even"]], [round(x, 2) for x in v["z_odd"]])


if __name__ == "__main__":
    main()
