"""07 -- PTM-5 analysis: the predicate's null rate on an exactly generic engine (choices PTM-5,
MC-2, MC-4). Reads out/ptm5_results.jsonl (written by ptm5_engine.py via run_ptm5.sh).

Per (m, rung, mode) and pooled: firing rate of ratio < 0.9 under frozen, rank, rank1 and
X_total at the PRIMARY stop (first row determining k) and frozen/rank at the VARIANT stop
(full rank); binomial MC s.e. (each instance is one seed). Aggregate T = sum w S^2 /
sum w r N/4, w = 1/(N B), per (m, mode) -- the lemma's testable form in the exact generic
model. First-moment check of the replica: SS pairs against C(X', 2)*2/N. Matched comparison
with the census (MC-4): the census's generic evaluable instances at 12..24 bits, expected
firings = sum over instances of the PTM-5 rate of the same (m, rung, mode), P(>= observed) by
exact Poisson-binomial; family-wise P(>= 1).
"""
import json
import math
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib575 import OUT, dump  # noqa: E402
from numlib import poisson_binomial_tail  # noqa: E402


def ratios(rec, stop):
    p = rec[stop]
    if p is None:
        return None
    N, B = rec["N"], rec["B"]
    S, rf, rk = p["S"], p["r_frozen"], p["rank"]
    out = {"frozen": S / (0.5 * math.sqrt(rf * N)) if rf > 0 else None,
           "rank": S / (0.5 * math.sqrt(rk * N)) if rk > 0 else None,
           "rank1": S / (0.5 * math.sqrt((rk + 1) * N)),
           "Xtotal": (2 * S + B + p["attempts"] + 2) / math.sqrt(rf * N) if rf > 0 else None}
    return out


def main():
    recs = [json.loads(l) for l in open(os.path.join(OUT, "ptm5_results.jsonl"))]
    cells = defaultdict(list)
    for r in recs:
        cells[(r["m"], r["bits"], r["mode"])].append(r)
    res = {"instances": len(recs), "cells": {}, "pooled": {}, "aggregate_T": {}, "first_moment_SS": {}}
    conv = ("frozen", "rank", "rank1", "Xtotal")
    rate = {}
    for (m, bits, mode), rs in sorted(cells.items()):
        blk = {"n": len(rs), "cap_hit": sum(1 for r in rs if r["primary"] is None),
               "full_missing": sum(1 for r in rs if r["full"] is None)}
        ok = [r for r in rs if r["primary"] is not None]
        for c in conv:
            vals = [ratios(r, "primary")[c] for r in ok]
            vals = [v for v in vals if v is not None]
            f = sum(1 for v in vals if v < 0.9)
            p = f / len(vals) if vals else None
            blk[f"primary_{c}"] = {"n": len(vals), "fire": f, "rate": p,
                                   "mc_se": math.sqrt(p * (1 - p) / len(vals)) if vals else None,
                                   "median": sorted(vals)[len(vals) // 2] if vals else None,
                                   "min": min(vals) if vals else None}
            rate[(m, bits, mode, c)] = p
        okf = [r for r in rs if r["full"] is not None]
        for c in ("frozen", "rank"):
            vals = [ratios(r, "full")[c] for r in okf]
            vals = [v for v in vals if v is not None]
            f = sum(1 for v in vals if v < 0.9)
            blk[f"full_{c}"] = {"n": len(vals), "fire": f, "rate": f / len(vals) if vals else None}
        res["cells"][f"m{m}|b{bits}|{mode}"] = blk
    for m in (3, 4, 5):
        for mode in ("census", "on"):
            rs = [r for r in recs if r["m"] == m and r["mode"] == mode and r["primary"] is not None]
            blk = {"n": len(rs)}
            for c in conv:
                vals = [v for v in (ratios(r, "primary")[c] for r in rs) if v is not None]
                f = sum(1 for v in vals if v < 0.9)
                p = f / len(vals)
                blk[c] = {"fire": f, "rate": p, "mc_se": math.sqrt(p * (1 - p) / len(vals)),
                          "below_1_rate": sum(1 for v in vals if v < 1.0) / len(vals),
                          "median": sorted(vals)[len(vals) // 2]}
            rf = [r for r in recs if r["m"] == m and r["mode"] == mode and r["full"] is not None]
            for c in ("frozen", "rank"):
                vals = [v for v in (ratios(r, "full")[c] for r in rf) if v is not None]
                f = sum(1 for v in vals if v < 0.9)
                blk[f"full_{c}"] = {"fire": f, "n": len(vals), "rate": f / len(vals) if vals else None}
            res["pooled"][f"m{m}|{mode}"] = blk
            for stop in ("primary", "full"):
                items = [r for r in recs if r["m"] == m and r["mode"] == mode and r[stop] is not None]
                for c, key in (("frozen", "r_frozen"), ("rank", "rank")):
                    num = sum(r[stop]["S"] ** 2 / (r["N"] * r["B"]) for r in items)
                    den = sum(r[stop][key] * r["N"] / 4 / (r["N"] * r["B"]) for r in items)
                    res["aggregate_T"][f"m{m}|{mode}|{stop}|{c}"] = num / den if den else None
            if mode == "on":
                tot_p = sum(r["primary"]["ss_pairs"] for r in rs)
                tot_mu = sum((r["primary"]["enc_recorded"] - r["primary"]["ss_dup"]) *
                             (r["primary"]["enc_recorded"] - r["primary"]["ss_dup"] - 1) / r["N"] for r in rs)
                res["first_moment_SS"][f"m{m}"] = {"sum_pairs": tot_p, "sum_H1_mean": tot_mu,
                                                   "ratio": tot_p / tot_mu if tot_mu else None}
    # matched comparison with the census at 12..24 bits (MC-4)
    xs = [json.loads(l) for l in open(os.path.join(OUT, "instances.jsonl"))]
    ev = [x for x in xs if x["evaluable"] and x["src"] != "stage-r" and x["bits"] <= 24]
    comp = {}
    for c in ("frozen", "rank", "Xtotal"):
        for m in (3, 4, 5):
            for mode in ("on", "census"):
                for cl in ("random", "structured", "j0_random", "generic"):
                    items = [x for x in ev if x["m"] == m and x["mode"] == mode and
                             (x["cls"] == cl if cl != "generic" else x["cls"] in ("random", "structured", "j0_random"))]
                    if not items:
                        continue
                    def obs_fire(x):
                        S, N = x["S"], x["N"]
                        if c == "frozen":
                            v = x["ratio"]
                        elif c == "rank":
                            v = S / (0.5 * math.sqrt(x["rank"] * N))
                        else:
                            v = (2 * S + x["B"] + x["attempts"] + 2) / math.sqrt(x["r_frozen"] * N)
                        return v < 0.9
                    obs = sum(1 for x in items if obs_fire(x))
                    ps = [rate.get((m, x["bits"], mode, c)) or 0.0 for x in items]
                    comp[f"{c}|m{m}|{mode}|{cl}"] = {"n": len(items), "observed": obs, "expected_ptm5": sum(ps),
                                                    "P_ge_observed": poisson_binomial_tail(ps, obs),
                                                    "P_le_observed": 1 - poisson_binomial_tail(ps, obs + 1),
                                                    "familywise_P_ge_1": 1 - math.prod(1 - p for p in ps)}
    res["census_vs_ptm5_12_24"] = comp
    dump("07_ptm5_analysis.json", res)
    print(json.dumps(res["pooled"], indent=0))
    print(json.dumps(res["aggregate_T"], indent=0))
    print(json.dumps(res["first_moment_SS"], indent=0))
    print(json.dumps({k: v for k, v in comp.items() if k.startswith("frozen|") or k.startswith("rank|")}, indent=0)[:6000])


if __name__ == "__main__":
    main()
