#!/usr/bin/env python3
"""Per-curve dispersion of the log-GAP count against the matched null (TASK-20261029-e5fe6b, joint J4).

The spec's z = (S - M)/sqrt(V (1 + 1/20)) treats gap_C on each curve as one more draw of the null
distribution: E[(gap_C - m_c)^2] = sigma_c^2 (1 + 1/20). This checks that assumption curve by curve:

  R_gap = sum_c (gap_C - m_c)^2 / ((1 + 1/20) sum_c s2_c)          m_c, s2_c over the 20 null replicates
  R_aa  = sum_c (null_0 - m19_c)^2 / ((1 + 1/19) sum_c s2_19_c)     A/A: replicate 0 against 1..19

Both are ~1 when the respective set behaves like a null draw. R_gap > R_aa means the log-GAP counts vary
more from curve to curve than uniform subsets do (their mean may still match). Uncertainty: curve
bootstrap (2000 resamples, seed declared below) of each pooled ratio, per bits and overall; per-cell ratios
are listed. Descriptive only; the frozen class rule reads the pooled mean, not this.
Usage: python3 -I dispersion_check.py <repo_root> <out_json>
"""
import hashlib
import json
import os
import sys
from collections import defaultdict

import numpy as np

repo, out = sys.argv[1], sys.argv[2]
jobs = os.path.join(repo, "experiments/EXP-PFDR-bb0d26/runs/RUN-PFDR-4d8c71/toy-main-jobs.jsonl")
rows = defaultdict(list)  # cell -> list of (dgap2, s2x1.05, daa2, s2_19x(1+1/19), bits)
for line in open(jobs):
    d = json.loads(line)
    if d["status"] != "ok":
        continue
    x = np.array(d["null_C"], dtype=np.float64)
    m, s2 = x.mean(), x.var(ddof=1)
    x19 = x[1:]
    m19, s219 = x19.mean(), x19.var(ddof=1)
    rows[d["cell"]].append(((d["gap_C"] - m) ** 2, s2 * 1.05, (x[0] - m19) ** 2, s219 * (1 + 1 / 19), d["bits"], d["n"]))


def pooled(sel):
    a = np.array(sel)
    return a[:, 0].sum() / a[:, 1].sum(), a[:, 2].sum() / a[:, 3].sum()


def boot(sel, seed, B=2000):
    a = np.array(sel)
    rng = np.random.Generator(np.random.PCG64(seed))
    k = len(a)
    rg = np.empty(B); ra = np.empty(B)
    for i in range(B):
        idx = rng.integers(0, k, size=k)
        b = a[idx]
        rg[i] = b[:, 0].sum() / b[:, 1].sum(); ra[i] = b[:, 2].sum() / b[:, 3].sum()
    return [float(v) for v in np.percentile(rg, [2.5, 97.5])], [float(v) for v in np.percentile(ra, [2.5, 97.5])]


def seed_of(tag):
    return int.from_bytes(hashlib.sha256(f"TASK-20261029-e5fe6b|disp|{tag}".encode()).digest()[:8], "big")


res = {"seed_rule": "int(sha256('TASK-20261029-e5fe6b|disp|<tag>')[:8], big), numpy PCG64, 2000 curve resamples",
       "cells": {}, "groups": {}}
for cell, sel in rows.items():
    g, aa = pooled(sel)
    res["cells"][cell] = {"curves": len(sel), "R_gap": float(g), "R_aa": float(aa)}
# Groups. Within a group, cells are pooled as separate (cell, curve) units; curves shared across cells at
# the same bits make the units correlated only through curve-level effects (null and gap sets are drawn per cell).
groups = {"all_valid": [r for c, s in rows.items() if c != "b20-r3-n4096" for r in s]}
for b in (20, 24, 28):
    groups[f"bits{b}"] = [r for c, s in rows.items() if c != "b20-r3-n4096" for r in s if r[4] == b]
for n in (256, 512, 1024, 2048, 4096):
    groups[f"n{n}"] = [r for c, s in rows.items() if c != "b20-r3-n4096" for r in s if r[5] == n]
for name, sel in groups.items():
    g, aa = pooled(sel)
    cg, ca = boot(sel, seed_of(name))
    res["groups"][name] = {"units": len(sel), "R_gap": float(g), "R_gap_ci95": cg, "R_aa": float(aa), "R_aa_ci95": ca}
    print(f"{name:10s} units {len(sel):5d}  R_gap {g:6.3f} [{cg[0]:.3f},{cg[1]:.3f}]   R_aa {aa:6.3f} [{ca[0]:.3f},{ca[1]:.3f}]")
top = sorted(res["cells"].items(), key=lambda kv: -kv[1]["R_gap"])[:8]
print("largest per-cell R_gap:", [(k, round(v["R_gap"], 2), round(v["R_aa"], 2)) for k, v in top])
with open(out, "w") as fh:
    json.dump(res, fh, separators=(",", ":"))
    fh.write("\n")
