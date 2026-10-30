#!/usr/bin/env python3
"""Cell-level versus curve-level dispersion of the log-GAP deviations (TASK-20261029-e5fe6b, joint J4).

Per powered valid cell, D_c = gap_C - m_c (m_c = mean of the 20 null replicates on curve c). Reports
  z      = sum D / sqrt(1.05 sum s2_c)                  (the spec's z; null variance)
  t      = sum D / sqrt(k/(k-1) sum (D - Dbar)^2)       (empirical across-curve dispersion of D)
  R_gap  = sum D^2 / (1.05 sum s2_c)                    (per-curve variance ratio)
and the same three for the A/A arm (replicate 0 against 1..19, factor 1 + 1/19). Equal-weight summaries
over the 44 cells. Descriptive only.
Usage: python3 -I celllevel_check.py <repo_root> <out_json>
"""
import json, math, os, sys
from collections import defaultdict
import numpy as np
repo, out = sys.argv[1], sys.argv[2]
jobs = os.path.join(repo, "experiments/EXP-PFDR-bb0d26/runs/RUN-PFDR-4d8c71/toy-main-jobs.jsonl")
rows = defaultdict(list)
for line in open(jobs):
    d = json.loads(line)
    if d["status"] != "ok" or d["cell"] == "b20-r3-n4096":
        continue
    x = np.array(d["null_C"], dtype=np.float64)
    rows[d["cell"]].append((d["c"], d["gap_C"] - x.mean(), x.var(ddof=1), x[0] - x[1:].mean(), x[1:].var(ddof=1)))
res = {}
for cell, R in rows.items():
    a = np.array(sorted(R))
    k = len(a)
    D, s2, A, s219 = a[:, 1], a[:, 2], a[:, 3], a[:, 4]
    z = D.sum() / math.sqrt(1.05 * s2.sum())
    t = D.sum() / math.sqrt(k / (k - 1) * ((D - D.mean()) ** 2).sum())
    Rg = (D ** 2).sum() / (1.05 * s2.sum())
    za = A.sum() / math.sqrt((1 + 1 / 19) * s219.sum())
    ta = A.sum() / math.sqrt(k / (k - 1) * ((A - A.mean()) ** 2).sum())
    Ra = (A ** 2).sum() / ((1 + 1 / 19) * s219.sum())
    # even/odd A/A on the gap deviations: lag-1 correlation of D in curve order (cross-curve dependence probe)
    Ds = D / np.sqrt(1.05 * s2)
    lag1 = float(np.corrcoef(Ds[:-1], Ds[1:])[0, 1])
    res[cell] = {"k": k, "z": z, "t": t, "R_gap": Rg, "z_aa": za, "t_aa": ta, "R_aa": Ra, "lag1_std_D": lag1}
def summ(key):
    v = np.array([r[key] for r in res.values()])
    return {"mean": float(v.mean()), "sd_pop": float(v.std()), "sum_sq": float((v ** 2).sum()), "n": int(len(v)),
            "max_abs": float(np.abs(v).max())}
S = {k: summ(k) for k in ("z", "t", "R_gap", "z_aa", "t_aa", "R_aa", "lag1_std_D")}
print(json.dumps(S, indent=1))
print("cells with |t|>2:", sorted([(c, round(r["t"], 2), round(r["z"], 2), round(r["R_gap"], 2)) for c, r in res.items() if abs(r["t"]) > 2]))
with open(out, "w") as fh:
    json.dump({"cells": res, "summary": S}, fh, separators=(",", ":")); fh.write("\n")
