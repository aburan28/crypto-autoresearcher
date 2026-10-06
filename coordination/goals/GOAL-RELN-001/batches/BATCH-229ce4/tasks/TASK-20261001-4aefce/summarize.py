#!/usr/bin/env python3
"""Summarize raw_b16-s13_all_readings.json: ranges per graph reading and
budget, delta_proof under both L readings, and an informational
Erdos-Renyi G(|V|,|E|) comparison (non-protocol seed, see report)."""
import json
import math
import random
import sys
from collections import defaultdict


def er_cycle_rank(n, m, rng):
    if m > n * (n - 1) // 2:
        return None
    edges = set()
    while len(edges) < m:
        u, v = rng.randrange(n), rng.randrange(n)
        if u != v:
            edges.add((min(u, v), max(u, v)))
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u, v in edges:
        parent[find(u)] = find(v)
    c = len({find(i) for i in range(n)})
    return m - n + c


def dp(cr, L):
    return math.log(cr) / math.log(L) - 1 if cr and cr > 0 else None


def main(path, out):
    d = json.load(open(path))
    L_count = d["readings"][0]["params"]["L_liftable_classes_below_B"]
    L_ceil = d["readings"][0]["params"]["ceil_q_1_5"]
    rng = random.Random("TASK-20261001-4aefce|informational-ER|not-a-protocol-seed")
    rows = []
    for r in d["readings"]:
        rd = r["reading"]
        for ch, bud in r["results"].items():
            for b, st in bud.items():
                for gk, g in st["graphs"].items():
                    ers = [er_cycle_rank(g["V"], g["E"], rng) for _ in range(32)] if g["V"] > 1 else []
                    ers = [x for x in ers if x is not None]
                    row = {
                        "prefix": rd["prefix"], "scheme": rd["scheme"], "j0": rd["attempt_index_base"],
                        "choice": ch, "budget": b, "graph": gk,
                        "full": st["full"], "1LP": st["1LP"], "2LP": st["2LP"],
                        **{k: g[k] for k in ("V", "E", "components", "components_with_cycle",
                                             "cycle_rank", "giant_fraction", "cell_subcritical_condition")},
                        "delta_proof_L_count": dp(g["cycle_rank"], L_count),
                        "delta_proof_L_ceil_q15": dp(g["cycle_rank"], L_ceil),
                        "er_feasible_replicates": len(ers),
                        "er_mean_cycle_rank": (sum(ers) / len(ers) if ers else None),
                    }
                    vals = [dp(x, L_count) for x in ers]
                    row["er_mean_delta_proof_L_count"] = (
                        sum(v for v in vals if v is not None) / len(vals)
                        if vals and all(v is not None for v in vals) else None)
                    rows.append(row)
    agg = defaultdict(lambda: defaultdict(list))
    for row in rows:
        key = f"{row['budget']}|{row['graph']}"
        for k in ("V", "E", "components", "components_with_cycle", "cycle_rank", "giant_fraction",
                  "delta_proof_L_count", "delta_proof_L_ceil_q15"):
            agg[key][k].append(row[k])
        agg[key]["subcritical"].append(row["cell_subcritical_condition"])
    summary = {}
    for key, kv in sorted(agg.items()):
        s = {}
        for k, vs in kv.items():
            if k == "subcritical":
                s["cell_subcritical_condition_true_count"] = sum(vs)
                s["n_readings"] = len(vs)
                continue
            num = [v for v in vs if v is not None]
            s[k] = {"min": min(num) if num else None, "max": max(num) if num else None,
                    "n_undefined": len(vs) - len(num)}
        dps = kv["delta_proof_L_count"]
        s["delta_proof_L_count_gt_quarter"] = sum(1 for v in dps if v is not None and v > 0.25)
        dps9 = kv["delta_proof_L_ceil_q15"]
        s["delta_proof_L_ceil_q15_gt_quarter"] = sum(1 for v in dps9 if v is not None and v > 0.25)
        summary[key] = s
    json.dump({"L_count": L_count, "L_ceil_q15": L_ceil, "summary": summary, "rows": rows},
              open(out, "w"), indent=1)
    for key, s in summary.items():
        print(key, json.dumps({k: (v if not isinstance(v, dict) else [v["min"], v["max"], v["n_undefined"]])
                               for k, v in s.items()}))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
