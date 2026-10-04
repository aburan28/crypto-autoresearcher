"""09 -- F6 (c) refinement, descriptive only: the aggregate statistic T per rung (on mode,
generic arms = random + structured, per m) under r_frozen and r_rank, with a 99% curve
bootstrap per rung (5 curves; all generic arms of a curve move together; 20000 replicates,
seed 0). No slope is fitted: the trend in N is joint F7's (the validator's).
"""
import json
import os
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib575 import OUT, dump  # noqa: E402

xs = [json.loads(l) for l in open(os.path.join(OUT, "instances.jsonl"))]
ev = [x for x in xs if x["evaluable"] and x["src"] != "stage-r" and x["mode"] == "on"
      and x["cls"] in ("random", "structured")]
res = {}
for m in (3, 4, 5):
    for b in range(12, 33, 2):
        rows = [x for x in ev if x["m"] == m and x["bits"] == b]
        for conv, key in (("frozen", "r_frozen"), ("rank", "rank")):
            A = defaultdict(float)
            D = defaultdict(float)
            for x in rows:
                w = 1.0 / (x["N"] * x["B"])
                A[x["curve"]] += w * x["S"] ** 2
                D[x["curve"]] += w * x[key] * x["N"] / 4
            cs = sorted(A)
            a = np.array([A[c] for c in cs])
            d = np.array([D[c] for c in cs])
            T = a.sum() / d.sum()
            rng = np.random.default_rng(0)
            idx = rng.integers(0, len(cs), size=(20000, len(cs)))
            Tb = a[idx].sum(axis=1) / d[idx].sum(axis=1)
            res[f"m{m}|b{b}|{conv}"] = {"n": len(rows), "T": float(T),
                                        "ci99": [float(np.quantile(Tb, 0.005)), float(np.quantile(Tb, 0.995))]}
dump("09_agg_by_rung.json", res)
for m in (3, 4, 5):
    print(m, " ".join("b%d:%.2f[%.2f]/%.1f" % (b, res[f"m{m}|b{b}|frozen"]["T"], res[f"m{m}|b{b}|frozen"]["ci99"][0],
                                              res[f"m{m}|b{b}|rank"]["T"]) for b in range(12, 33, 2)))
