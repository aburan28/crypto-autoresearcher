#!/usr/bin/env python3
"""TASK-20260929-c40e48 J2 comparison supplement: Monte Carlo spread of the P6
2000-rep percentile endpoints (own numpy bootstrap, 50 seeds), and the z-score of
the archived raw-result P6 endpoints against it. Rows from the sealed blind
rederivation/j2-floor-rows.jsonl.gz."""
import gzip, json, math, sys
import numpy as np
rows = [json.loads(l) for l in gzip.open("rederivation/j2-floor-rows.jsonl.gz", "rt")]
raw = json.load(open(sys.argv[1]))
out = {}
for fb in ("small_x", "random", "subgroup"):
    sel = [x for x in rows if x["file"] == "sweep-minfill-20260926" and x["m"] == 3 and x["fb"] == fb
           and x["engine"] == "mitm" and 20 <= x["bits"] <= 32]
    by = {}
    for x in sel:
        by.setdefault(x["bits"], []).append(math.log(x["ratio"]))
    lo, hi = [], []
    for s in range(50):
        g = np.random.Generator(np.random.PCG64(5_000_000 + s))
        cols = [np.asarray(by[b])[g.integers(0, len(by[b]), size=(2000, len(by[b])))] for b in sorted(by)]
        bb = np.sort(np.exp(np.concatenate(cols, axis=1).mean(axis=1)))
        lo.append(bb[int(math.floor(0.025 * 1999))]); hi.append(bb[int(math.ceil(0.975 * 1999))])
    a = raw["P6_bases"]["per_base"][fb]["ci95"]
    out[fb] = {"lo_mean": float(np.mean(lo)), "lo_sd": float(np.std(lo, ddof=1)), "hi_mean": float(np.mean(hi)),
               "hi_sd": float(np.std(hi, ddof=1)), "archived": a,
               "z_archived_lo": (a[0] - np.mean(lo)) / np.std(lo, ddof=1), "z_archived_hi": (a[1] - np.mean(hi)) / np.std(hi, ddof=1)}
print(json.dumps(out, indent=1, default=float))
json.dump(out, open("checks/j2-p6-mc.json", "w"), indent=1, default=float)
