#!/usr/bin/env python3
"""Per powered cell: the largest label-AP substructure (of the planted type: the AP terms that fall in L) that the
recorded interval still admits, scaled from the recorded plant.  internal(m) grows like m^3, the plant of m_pl
labels added an excess (plant_kappa - 1) of the null mean, so an embedded AP of m labels adds about
(plant_kappa - 1) * (m / m_pl)^3.  The bound uses delta95 = max(|ci95_lo - 1|, |ci95_hi - 1|) from analysis.json.
Recorded data only (analysis.json, job records); a scaling estimate, not a theorem.
"""
from __future__ import annotations

import json
import os
import statistics
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
RUNS = os.path.join(ROOT, "experiments", "EXP-PFDR-bb0d26", "runs")
ana = json.load(open(os.path.join(RUNS, "RUN-PFDR-089edc", "analysis.json")))
pm = defaultdict(list)
for line in open(os.path.join(RUNS, "RUN-PFDR-4d8c71", "toy-main-jobs.jsonl")):
    r = json.loads(line)
    if r["status"] == "ok":
        pm[r["cell"]].append(r["plant_m"])
rows = []
for c in ana["cells"]:
    if not c.get("powered"):
        continue
    d95 = max(abs(c["ci95"][0] - 1), abs(c["ci95"][1] - 1))
    m_pl = statistics.median(pm[c["cell"]])
    m_b = m_pl * (d95 / (c["plant_kappa"] - 1)) ** (1 / 3)
    rows.append({"cell": c["cell"], "n": c["n"], "delta95": round(d95, 6), "plant_m_median": m_pl,
                 "plant_kappa": round(c["plant_kappa"], 4), "ap_labels_bound": round(m_b, 1),
                 "ap_fraction_of_n": round(m_b / c["n"], 4)})
out = {"rows": rows,
       "max_fraction": max(rows, key=lambda r: r["ap_fraction_of_n"]),
       "min_fraction": min(rows, key=lambda r: r["ap_fraction_of_n"])}
json.dump(out, open(os.path.join(HERE, "rt_ap_bound.json"), "w"), indent=0)
for r in rows:
    print(r)
print("max", out["max_fraction"]); print("min", out["min_fraction"])
