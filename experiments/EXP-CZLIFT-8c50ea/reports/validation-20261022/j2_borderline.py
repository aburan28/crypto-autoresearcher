#!/usr/bin/env python3
"""Borderline probes for J2 (written after the implementation was read).

1. For each K-point that the specification's box contains but the recorded
   counts omit, show with the PRODUCER's own primitives (harness/czlift_cubic.py
   g_value / exact_sqrt / mul) that its minimal representation (alpha, d) is an
   exact square, and that the only reason it is not counted is the
   gcd(c0, c1, c2, d) != 1 skip in search_points (or d^2 > H in height()).
2. The two cells straddling the coverage median in each run.

Usage: python3 j2_borderline.py RUN_DIR_MAIN RUN_DIR_REPL J2_OUTPUT.json OUT.json
"""
import json
import math
import os
import sys

sys.dont_write_bytecode = True
REPO = "/home/user/crypto-autoresearcher"
sys.path.insert(0, REPO)
from harness import czlift_cubic as C  # noqa: E402


def main():
    rd_main, rd_repl, j2_path, outpath = sys.argv[1:5]
    j2 = json.load(open(j2_path))
    out = {"dropped_points": [], "median_cells": {}}
    for tag, rd in (("main", rd_main), ("replication", rd_repl)):
        raw = json.load(open(os.path.join(rd, "raw-result.json")))
        hmax = raw["metrics"]["hmax"]
        ai_by = {c["label"]: c["ainvs"] for c in raw["raw"]["curves"]}
        for label, row in j2["part2_enumeration"][tag]["curves"].items():
            a1, a2, a3, a4, a6 = ai_by[label]
            b2 = a1 * a1 + 4 * a2; b4 = 2 * a4 + a1 * a3; b6 = a3 * a3 + 4 * a6
            for x in row["x_in_spec_not_inferred_at_hmax"]:
                alpha, d = tuple(x["min_alpha"]), x["min_d"]
                G = C.g_value(alpha, d, b2, b4, b6)
                gamma = C.exact_sqrt(G)
                g = math.gcd(math.gcd(abs(alpha[0]), abs(alpha[1])), math.gcd(abs(alpha[2]), d))
                ht = C.height((alpha, d, gamma))
                reason = []
                if g != 1:
                    reason.append(f"gcd(c0,c1,c2,d) = {g} != 1: skipped by search_points line 97")
                if ht > hmax:
                    reason.append(f"height() = max(|coords|, d^2) = {ht} > H = {hmax}: never counted")
                out["dropped_points"].append({
                    "run": tag, "curve": label, "x": x["x"], "rational": x["rational"],
                    "alpha": list(alpha), "d": d, "producer_exact_sqrt": list(gamma) if gamma else None,
                    "producer_exact_square": gamma is not None and C.mul(gamma, gamma) == G,
                    "producer_height": ht, "reason_not_counted": reason})
        cells = sorted(((c["ratio_to_model"], cv["label"], c["p"], c["H"], c["n_points"], c["distinct"], c["N_p"])
                        for cv in raw["raw"]["curves"] for c in cv["coverage"]
                        if c["n_points"] >= 20 and c["model_distinct"] <= 0.9 * c["N_p"]))
        n = len(cells)
        out["median_cells"][tag] = {"n": n, "lower_middle_index": n // 2 - 1, "lower_middle": cells[n // 2 - 1],
                                    "upper_middle_index": n // 2, "upper_middle": cells[n // 2],
                                    "statistical_median": (cells[n // 2 - 1][0] + cells[n // 2][0]) / 2,
                                    "recorded": raw["metrics"]["coverage_ratio_median"]}
    with open(outpath, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
