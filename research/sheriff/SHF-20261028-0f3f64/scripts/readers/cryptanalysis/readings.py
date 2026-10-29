#!/usr/bin/env python3
"""Red-team readings from the re-derived band (candidates, not evidence; sheriff SHF-20261028-0f3f64).

1. Where in the band the stacked row's wall-time gap sits: the uniform weight w at which the counted
   band reproduces the row's wall-time gap 94.4168 (baselines.json other_records stacked row).
2. Amortised regime (heuristic): T targets share one rank stage + setup + LA; per-target IC cost is
   the online interval. Against (a) a single-target rho with no reuse and (b) a rho that reuses its
   distinguished points across targets (Kuhn-Struik heuristic: total ~ sqrt(2 T n) against
   sqrt(pi n / 2) for one target, so mean per target ~ (2/sqrt(pi)) / sqrt(T) x one-target cost).
"""
import json
import math
import sys
from pathlib import Path

res = json.loads(Path(sys.argv[1]).read_text())
baselines = json.loads(Path(sys.argv[2]).read_text())
out = Path(sys.argv[3])
band = res["band"]
S, rT = band["arms"]["S"], band["arms"]["rT"]
ro = res["readouts"]
stacked = [r for r in baselines["other_records"] if "koblitz-n83-stacked-20261016" in r.get("experiment", "")][0]
wall_gap = stacked["gap_cold_ic_over_rho"]["value"]
lo, hi = stacked["gap_cold_ic_over_rho"]["ci95"]


def w_for_gap(g):
    # S_group + w S_un = g (rT_group + w rT_un)
    return (g * rT["mean_group"] - S["mean_group"]) / (S["mean_unpriced"] - g * rT["mean_unpriced"])


reading = {"stacked_wall_time_gap": [wall_gap, lo, hi],
           "implied_uniform_w_at_wall_gap": [w_for_gap(wall_gap), w_for_gap(lo), w_for_gap(hi)]}
fixed_un = ro["S_fixed_unpriced_per_cold_unit"]
fixed_g = S["mean_group"] - ro["cS_online_only_mean"]["group"]
on_un, on_g = ro["cS_online_only_mean"]["unpriced"], ro["cS_online_only_mean"]["group"]
am = {}
for w in (0.1, 1.0):
    a = fixed_g + w * fixed_un
    b = on_g + w * on_un
    c = rT["mean_group"] + w * rT["mean_unpriced"]
    k = 2 / math.sqrt(math.pi)
    am["w=%g" % w] = {
        "ic_fixed": a, "ic_per_target_online": b, "rho_one_target": c,
        "breakeven_T_vs_rho_without_reuse": a / (c - b) if c > b else None,
        "min_ratio_ic_over_reusing_rho": 2 * math.sqrt(a * b) / (k * c),
        "argmin_T": a / b,
    }
reading["amortised"] = am
out.write_text(json.dumps(reading, indent=1) + "\n")
print(json.dumps(reading, indent=1))
