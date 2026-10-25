#!/usr/bin/env python3
"""Reader costmodel (SHF-20261021-477d51): check the planner's Table B citations
(E_LADDER, E_LADDER_JSON) against docs/ic/leaderboard.json at crypto b4f056101.
For every prime / random-binary board row: each recipe's base, target source, m,
S and ratio to rho; the planner's size rule round(#E^(1/3)/2) (prime) or
round(log2 #E / 3) (binary) beside the measured best; walked-vs-random and
m=2-vs-m=3 ratios. Read-only; argv[1] = path to leaderboard.json."""
import json, math, sys
d = json.load(open(sys.argv[1]))
out = []
for r in d["board"]:
    if r["regime"] not in ("prime", "char2"):
        continue
    E = 2 ** r["log2_r"] * r["cofactor"]
    rule = round(E ** (1 / 3) / 2) if r["regime"] == "prime" else round(math.log2(E) / 3)
    recs = []
    for x in r["recipes"]:
        recs.append({k: x.get(k) for k in ("variant", "label", "m", "base_points", "columns", "table", "targets", "s", "ratio_rho")})
    best = r["best"]
    walk = [x for x in r["recipes"] if x.get("targets") == "walk" and x.get("m") == 2]
    rand = [x for x in r["recipes"] if x.get("targets") != "walk" and x.get("m") == 2]
    m3 = [x for x in r["recipes"] if x.get("m") == 3]
    m2 = [x for x in r["recipes"] if x.get("m") == 2]
    out.append({
        "regime": r["regime"], "slug": r["slug"], "log2_r": round(r["log2_r"], 3), "cofactor": r["cofactor"],
        "planner_rule_size": rule, "best_variant": best["variant"], "best_columns": best.get("columns"),
        "best_base_points": best.get("base_points"), "best_ratio_rho": round(best["ratio_rho"], 3),
        "best_s": round(best["s"], 3), "reference_s": r["reference_s"],
        "min_ratio_walk_m2": round(min(x["ratio_rho"] for x in walk), 3) if walk else None,
        "min_ratio_nonwalk_m2": round(min(x["ratio_rho"] for x in rand), 3) if rand else None,
        "min_ratio_m3": round(min(x["ratio_rho"] for x in m3), 3) if m3 else None,
        "min_ratio_m2": round(min(x["ratio_rho"] for x in m2), 3) if m2 else None,
        "recipes": recs,
    })
json.dump(out, sys.stdout, indent=1)
