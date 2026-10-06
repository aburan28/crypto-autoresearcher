#!/usr/bin/env python3
"""TASK-20260929-c40e48 J2 supplement (blind): per-seed JOINT outcome id under
the frozen stats.bootstrap_slope, seeds 0..199, for the two series whose
seed-0 intervals sit within Monte Carlo error of their model value (S6 vs 1/12,
S7 vs 0; 12..32). The other six primary series never excluded their model value
at any of seeds 0..199 (rederive.py seed scan), min ratio >= 1 and the P6 base
intervals overlap, so for each seed the outcome id is determined by these two.
Also: the same for SORTED (bits, curve) row order. Descriptive only; the
frozen outcome id is defined on seed 0.

Usage: python seed_joint.py <j2-floor-rows.jsonl.gz> <stats.py> <out.json>
"""
import collections
import gzip
import importlib.util
import json
import math
import sys


def main(rows_path, stats_path, out_path):
    spec = importlib.util.spec_from_file_location("frozen_stats_7c8bf2", stats_path)
    stats = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(stats)
    rows = [json.loads(l) for l in gzip.open(rows_path, "rt")]
    series = {"S6-smallx": ("sweep-arity67-20260928", 6, 1 / 12),
              "S7-smallx": ("sweep-arity67-20260928", 7, 0.0)}
    res = {}
    for order in ("file", "sorted_bits_curve"):
        per = {}
        for name, (f, m, model) in series.items():
            sel = [x for x in rows if x["file"] == f and x["m"] == m and x["engine"] == "mitm"]
            if order == "sorted_bits_curve":
                sel = sorted(sel, key=lambda x: (x["bits"], x["curve"]))
            xs = [x["log2N"] for x in sel]
            ys = [math.log2(x["ratio"]) for x in sel]
            gs = [x["bits"] for x in sel]
            per[name] = []
            for s in range(200):
                o = stats.bootstrap_slope(xs, ys, groups=gs, reps=2000, level=0.95, seed=s)
                per[name].append(o["lo"] > model or o["hi"] < model)
        joint = collections.Counter()
        for s in range(200):
            e6, e7 = per["S6-smallx"][s], per["S7-smallx"][s]
            if e6 and e7:
                joint["OUT-SLOPE-INTERVAL via S6 and S7"] += 1
            elif e6:
                joint["OUT-SLOPE-INTERVAL via S6 alone"] += 1
            elif e7:
                joint["OUT-SLOPE-INTERVAL via S7 alone"] += 1
            else:
                joint["OUT-CONSISTENT (no F-2/F-3)"] += 1
        res[order] = {"seed0": {"S6_excludes": per["S6-smallx"][0], "S7_excludes": per["S7-smallx"][0]},
                      "counts_over_seeds_0_199": dict(joint),
                      "fraction_S6_excludes": sum(per["S6-smallx"]) / 200,
                      "fraction_S7_excludes": sum(per["S7-smallx"]) / 200}
    json.dump(res, open(out_path, "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:4])
