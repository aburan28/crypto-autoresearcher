#!/usr/bin/env python3
"""Reader costmodel (SHF-20261021-477d51): tabulate every saved ecbench comparison
(ops ratio + interval, wall ratio + interval, verdict string) for the six sessions
of research/ic_planner_validation_20261020 at crypto b4f056101. Read-only."""
import json, sys, pathlib
root = pathlib.Path(sys.argv[1])  # .../research/ic_planner_validation_20261020
out = {}
for c in ["r24", "r26", "r28", "c24", "c28", "c30"]:
    for f in sorted((root / "sessions" / c / "comparisons").glob("*.json")):
        d = json.loads(f.read_text())
        key = f"{c}:{d['a']['arm']}->{d['b']['arm']}"
        w = d.get("wall", {})
        out[key] = {
            "ops_ratio": round(d["ops"]["ratio_b_over_a"], 4),
            "ops_ci95": [round(x, 4) for x in d["ops"]["ci95"]],
            "ops_status": d["ops"]["status"],
            "wall_status": w.get("status"),
            "wall_median_ratio": None if w.get("median_ratio") is None else round(w["median_ratio"], 4),
            "wall_ci95": None if w.get("ci95") is None else [round(x, 4) for x in w["ci95"]],
            "wall_outside_noise": w.get("outside_noise"),
            "a_lower_bound": d["a"]["lower_bound"], "b_lower_bound": d["b"]["lower_bound"],
            "verdict": d.get("verdict"),
        }
json.dump(out, sys.stdout, indent=1)
