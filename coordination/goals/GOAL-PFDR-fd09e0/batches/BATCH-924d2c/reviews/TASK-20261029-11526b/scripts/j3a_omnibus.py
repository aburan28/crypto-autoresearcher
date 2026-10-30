"""J3a omnibus checks with matched null-object controls.

For each statistic computed on the log-GAP arm, the identical statistic is computed with each null replicate k
(k = 0..19) as the structured arm against the other 19 replicates of the same curve (variance factor 1 + 1/19):
  (1) sum over the 44 powered cells of z^2 (cell-to-cell dispersion of z; two-sided effects cancel in Stouffer);
  (2) per (bits, r) stratum rank-location z (each curve weighted equally; complements the count-weighted kappa);
  (3) per cell sign test: fraction of curves whose structured count lies below its null mean.
Writes outputs/omnibus-null-controls.json.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import math  # noqa: E402

import numpy as np  # noqa: E402

import common as C  # noqa: E402


def binom_two_sided(k, n):
    """Exact two-sided binomial(n, 1/2) p-value (doubling the smaller tail, capped at 1)."""
    lo = min(k, n - k)
    tail = sum(math.comb(n, i) for i in range(0, lo + 1)) / 2 ** n
    return min(1.0, 2 * tail)


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
        rows.append((d, g, m, s2, nulls))
    K = len(rows)
    # (1) sum of z^2
    zg = np.array([(g - m).sum() / math.sqrt(1.05 * s2.sum()) for d, g, m, s2, nulls in rows])
    zk = np.zeros((20, K))
    for j, (d, g, m, s2, nulls) in enumerate(rows):
        for k in range(20):
            o = np.delete(nulls, k, axis=1)
            zk[k, j] = (nulls[:, k] - o.mean(axis=1)).sum() / math.sqrt(o.var(axis=1, ddof=1).sum() * (1 + 1 / 19))
    ss_gap = float((zg ** 2).sum())
    ss_null = (zk ** 2).sum(axis=1)
    # (2) stratum rank-location z
    strata = sorted(set((d["bits"], d["r"]) for d, *_ in rows))
    loc_gap, loc_null = {}, {k: {} for k in range(20)}
    prng = C.review_np_rng("omnibus-pit")
    for (bits, r) in strata:
        sel = [x for x in rows if x[0]["bits"] == bits and x[0]["r"] == r]
        Rg, Rn = [], [[] for _ in range(20)]
        for d, g, m, s2, nulls in sel:
            below = (nulls < g[:, None]).sum(axis=1)
            ties = (nulls == g[:, None]).sum(axis=1)
            Rg.append(below + np.floor(prng.random(len(g)) * (ties + 1)))
            for k in range(20):
                o = np.delete(nulls, k, axis=1)
                b_ = (o < nulls[:, k:k + 1]).sum(axis=1)
                t_ = (o == nulls[:, k:k + 1]).sum(axis=1)
                Rn[k].append(b_ + np.floor(prng.random(len(g)) * (t_ + 1)))
        Rg = np.concatenate(Rg)
        J = len(Rg)
        loc_gap[f"{bits}-{r}"] = float((Rg.mean() - 10) / math.sqrt(((21 ** 2 - 1) / 12) / J))
        for k in range(20):
            Rk = np.concatenate(Rn[k])
            loc_null[k][f"{bits}-{r}"] = float((Rk.mean() - 9.5) / math.sqrt(((20 ** 2 - 1) / 12) / J))
    max_loc_gap = max(abs(v) for v in loc_gap.values())
    max_loc_null = [max(abs(v) for v in loc_null[k].values()) for k in range(20)]
    all_null_loc = np.array([v for k in range(20) for v in loc_null[k].values()])
    # (3) sign tests
    sign_rows = []
    sign_null_min_p = []
    for k in range(20):
        ps = []
        for d, g, m, s2, nulls in rows:
            o = np.delete(nulls, k, axis=1)
            below = int((nulls[:, k] < o.mean(axis=1)).sum())
            ps.append(binom_two_sided(below, len(g)))
        sign_null_min_p.append(min(ps))
    for d, g, m, s2, nulls in rows:
        below = int((g < m).sum())
        frac_null = float(np.mean([(nulls[:, k] < np.delete(nulls, k, axis=1).mean(axis=1)).mean() for k in range(20)]))
        sign_rows.append({"cell": d["cell"], "curves": int(len(g)), "below": below, "frac_below": below / len(g),
                          "frac_below_null_loo_mean": frac_null, "p_two_sided_binomial_half": binom_two_sided(below, len(g))})
    min_sign = min(sign_rows, key=lambda r: r["p_two_sided_binomial_half"])
    C.write_json("omnibus-null-controls.json", {
        "task": "TASK-20261029-11526b", "joint": "J3a items (3)-(5), matched null-object controls",
        "inputs": [C.rel(C.JOBS), C.rel(C.DESIGN)],
        "method": __doc__.strip(),
        "sum_z2": {"gap": ss_gap, "cells": K, "null_loo_per_k": [float(x) for x in ss_null],
                   "null_loo_mean": float(ss_null.mean()), "null_loo_sd": float(ss_null.std(ddof=1)),
                   "gap_rank_among_null_k_ascending": int((ss_null < ss_gap).sum()),
                   "chi2_p_unit_normal": None,
                   "gap_z_values": [float(x) for x in zg]},
        "stratum_rank_location": {"gap": loc_gap, "gap_max_abs": max_loc_gap,
                                  "null_k_max_abs_over_strata": max_loc_null,
                                  "fraction_null_k_with_max_ge_gap": float(np.mean([x >= max_loc_gap for x in max_loc_null])),
                                  "null_all_strata_sd": float(all_null_loc.std(ddof=1)),
                                  "null_all_strata_max_abs": float(np.abs(all_null_loc).max()),
                                  "null_values_ge_3_count": int((np.abs(all_null_loc) >= 3).sum()),
                                  "null_values_total": int(all_null_loc.size)},
        "sign_test": {"min_gap": min_sign, "null_k_min_p_over_cells": sign_null_min_p,
                      "fraction_null_k_min_p_le_gap_min": float(np.mean([x <= min_sign["p_two_sided_binomial_half"] for x in sign_null_min_p])),
                      "cells": sign_rows},
    }, sig=6)
    print("sum z2 gap", ss_gap, "null", ss_null.mean(), ss_null.std(ddof=1), sorted(ss_null.round(1)))
    print("loc gap", loc_gap, "max", max_loc_gap, "null max", sorted(np.round(max_loc_null, 2)))
    print("null loc sd", all_null_loc.std(ddof=1), "max", np.abs(all_null_loc).max(), "n>=3", int((np.abs(all_null_loc) >= 3).sum()))
    print("sign min", min_sign, "null min p", sorted(np.round(sign_null_min_p, 5)))


if __name__ == "__main__":
    main()
