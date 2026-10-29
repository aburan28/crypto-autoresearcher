#!/usr/bin/env python3
"""Check that V/20 is the variance of the per-curve null mean (TASK-20261029-e5fe6b, joint J4).

The spec's z uses V = sum of per-curve sample variances of the 20 null replicates and the factor
(1 + 1/20), i.e. it assumes the 20 replicates of a curve are independent draws (Var(mean) = sigma^2/20).
z_cal cannot detect equicorrelated replicates (rep 0 minus the mean of 1..19 has variance
sigma^2 (1 - rho)(1 + 1/19), which s^2 of the 19 estimates without bias). The three r-cells at the same
(bits, n) and curve carry three null sets of the same object built from different cell seeds, so the
spread of their three per-curve means measures Var(mean) directly.

Per (bits, n): ratio = [sum_c sum_r (m_cr - mbar_c)^2 / 2] / [sum_c mean_r(s2_cr) / 20]; expect 1 under
independence (approximately chi-square / dof with dof = 2 x curves). Also the pairwise pooled z
(M_ri - M_rj) / sqrt((V_ri + V_rj)/20) over curves present in both cells.

Usage: python3 -I null_variance_check.py <repo_root> <out_json>
"""
import json
import math
import os
import sys
from collections import defaultdict

import numpy as np

repo, out = sys.argv[1], sys.argv[2]
jobs = os.path.join(repo, "experiments/EXP-PFDR-bb0d26/runs/RUN-PFDR-4d8c71/toy-main-jobs.jsonl")
by = defaultdict(dict)  # (bits, n) -> {(c, r): (mean, s2)}
within_r0 = defaultdict(list)
for line in open(jobs):
    d = json.loads(line)
    if d["status"] != "ok":
        continue
    xs = np.array(d["null_C"], dtype=np.float64)
    by[(d["bits"], d["n"])][(d["c"], d["r"])] = (xs.mean(), xs.var(ddof=1))

res = []
for (bits, n) in sorted(by):
    D = by[(bits, n)]
    cs = sorted({c for (c, r) in D if all((c, rr) in D for rr in (1, 2, 3))})
    num = 0.0
    den = 0.0
    for c in cs:
        ms = np.array([D[(c, r)][0] for r in (1, 2, 3)])
        s2 = np.array([D[(c, r)][1] for r in (1, 2, 3)])
        num += ((ms - ms.mean()) ** 2).sum() / 2.0
        den += s2.mean() / 20.0
    ratio = num / den
    dof = 2 * len(cs)
    zr = (ratio - 1.0) / math.sqrt(2.0 / dof)  # normal approx of chi2/dof
    pair = {}
    for (i, j) in ((1, 2), (1, 3), (2, 3)):
        Mi = sum(D[(c, i)][0] for c in cs); Mj = sum(D[(c, j)][0] for c in cs)
        Vi = sum(D[(c, i)][1] for c in cs); Vj = sum(D[(c, j)][1] for c in cs)
        pair[f"r{i}-r{j}"] = (Mi - Mj) / math.sqrt((Vi + Vj) / 20.0)
    res.append({"bits": bits, "n": n, "curves": len(cs), "var_ratio": ratio, "dof": dof, "z_ratio": zr,
                "pair_z": pair})
    print(f"b{bits} n{n:5d} curves {len(cs):5d} var_ratio {ratio:6.3f} (dof {dof:5d}, z {zr:6.2f})  pair z "
          + " ".join(f"{k}:{v:6.2f}" for k, v in pair.items()))
num_all = sum(r["var_ratio"] * r["dof"] for r in res); dof_all = sum(r["dof"] for r in res)
allp = [v for r in res for v in r["pair_z"].values()]
summary = {"pooled_var_ratio": num_all / dof_all, "dof": dof_all,
           "pair_z_mean": float(np.mean(allp)), "pair_z_sd_pop": float(np.std(allp)), "pair_z_max_abs": float(max(map(abs, allp)))}
print(json.dumps(summary))
with open(out, "w") as fh:
    json.dump({"groups": res, "summary": summary}, fh, separators=(",", ":"))
    fh.write("\n")
