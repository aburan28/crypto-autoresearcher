#!/usr/bin/env python3
"""Addendum to j2_recompute.py, written after check.py, run.py and the harness were read.

(a) runs the producer's checker on both run dirs (no bytecode written);
(b) evaluates the frozen invalidation rule as written (the checker's re-run
    subset must REPRODUCE the recorded value, i.e. equality, not <=);
(c) re-runs the producer's measure_curve for 11a1 and 37a1 on the smallest
    box (hmax 24, dmax 6) with the recorded primes and compares with raw;
(d) recomputes the growth slope with the producer's stated fit rule;
(e) tabulates metric-definition variants (code / hypothesis / statistical
    median) on recorded counts and on the specification-box counts;
(f) the coverage ratio's structural ceiling per counted cell.

Usage: python3 j2_addendum.py RUN_DIR_MAIN RUN_DIR_REPL J2_OUTPUT.json OUT.json
"""
import contextlib
import io
import json
import math
import os
import statistics
import sys

sys.dont_write_bytecode = True
REPO = "/home/user/crypto-autoresearcher"
IMPL = os.path.join(REPO, "experiments/EXP-CZLIFT-8c50ea/implementation")
sys.path.insert(0, IMPL)
sys.path.insert(0, REPO)
import check as producer_check  # noqa: E402
import run as driver  # noqa: E402


def model(n, N):
    return N * (1 - (1 - 1 / N) ** n)


def main():
    rd_main, rd_repl, j2_path, outpath = sys.argv[1:5]
    j2 = json.load(open(j2_path))
    out = {}
    raws = {"main": json.load(open(os.path.join(rd_main, "raw-result.json"))),
            "replication": json.load(open(os.path.join(rd_repl, "raw-result.json")))}
    # (a) checker
    for tag, rd in (("main", rd_main), ("replication", rd_repl)):
        so, se = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(so), contextlib.redirect_stderr(se):
            rc = producer_check.main([rd])
        out[f"checker_{tag}"] = {"returncode": rc, "stdout": so.getvalue().strip(), "stderr": se.getvalue().strip()}
    # (b) invalidation rule as written: equality of the re-run subset
    for tag, raw in raws.items():
        cv = raw["raw"]["curves"][1]
        fresh = driver.measure_curve(cv["label"], cv["ainvs"], cv["rank_recalled_over_Q"], hmax=4,
                                     dmax=min(2, cv["dmax"]), primes=[])
        out[f"rerun_subset_{tag}"] = {"curve": cv["label"], "fresh_counts_K": fresh["counts_K"],
                                      "fresh_counts_Q": fresh["counts_Q"],
                                      "recorded_counts_K_4": cv["counts_K"]["4"], "recorded_counts_Q_4": cv["counts_Q"]["4"],
                                      "reproduces_exactly": fresh["counts_K"]["4"] == cv["counts_K"]["4"]
                                      and fresh["counts_Q"]["4"] == cv["counts_Q"]["4"],
                                      "checker_test_used": "fresh <= recorded"}
    # (c) producer re-run on the smallest box for the two blind curves
    raw = raws["replication"]
    primes = raw["raw"]["curves"][0]["primes"]
    out["split_primes_rederived_by_driver"] = driver.split_primes(101, 5000, 12) == primes
    for cv in raw["raw"]["curves"][:2]:
        fresh = driver.measure_curve(cv["label"], cv["ainvs"], cv["rank_recalled_over_Q"], hmax=24, dmax=6, primes=primes)
        fresh_j = json.loads(json.dumps(fresh))
        out[f"producer_rerun_{cv['label']}_h24_d6_equals_raw"] = fresh_j == cv
    # (d) slope with the producer's rule (H >= 4 and N_K(H) >= 3, log N vs log log H)
    for tag, raw in raws.items():
        sl = {}
        for cv in raw["raw"]["curves"]:
            Hs = sorted(int(h) for h in cv["counts_K"])
            pts = [(math.log(math.log(h)), math.log(cv["counts_K"][str(h)])) for h in Hs if h >= 4 and cv["counts_K"][str(h)] >= 3]
            mx = statistics.fmean(p[0] for p in pts)
            my = statistics.fmean(p[1] for p in pts)
            s = sum((x - mx) * (y - my) for x, y in pts) / sum((x - mx) ** 2 for x, _ in pts)
            sl[cv["label"]] = {"own": s, "recorded": cv["growth_slope_K"], "abs_diff": abs(s - cv["growth_slope_K"])}
        out[f"slope_{tag}"] = sl
    # (e) metric-definition variants
    for tag, raw in raws.items():
        hm = raw["metrics"]["hmax"]
        rec = {cv["label"]: (cv["counts_K"][str(hm)], cv["counts_Q"][str(hm)]) for cv in raw["raw"]["curves"]}
        spec = {k: tuple(v) for k, v in j2["part2_enumeration"][tag]["spec_definition_metrics"]["N_K_N_Q_at_hmax"].items()}
        var = {}
        for name, tab in (("recorded_counts", rec), ("spec_box_counts", spec)):
            g_all = sorted(k / max(1, q) for k, q in tab.values())
            g_10 = sorted(k / q for k, q in tab.values() if q >= 10)
            var[name] = {"per_curve": {c: [k, q, k / q] for c, (k, q) in tab.items()},
                         "code_upper_median_all6": g_all[len(g_all) // 2],
                         "statistical_median_all6": statistics.median(g_all),
                         "hypothesis_median_NQ_ge_10": statistics.median(g_10),
                         "max_gain_NQ_ge_10": max(g_10)}
        cells = [c for cv in raw["raw"]["curves"] for c in cv["coverage"] if c["n_points"] >= 20 and c["model_distinct"] <= 0.9 * c["N_p"]]
        r = sorted(c["ratio_to_model"] for c in cells)
        ceil = sorted(c["n_points"] / model(c["n_points"], c["N_p"]) for c in cells)
        var["coverage"] = {"cells": len(cells), "code_upper_element": r[len(r) // 2], "statistical_median": statistics.median(r),
                           "recorded": raw["metrics"]["coverage_ratio_median"],
                           "ceiling_max": ceil[-1], "ceiling_median_max_attainable": statistics.median(ceil),
                           "cells_at_ceiling": sum(1 for c in cells if c["distinct"] == c["n_points"]),
                           "min_ratio": r[0], "max_ratio": r[-1]}
        out[f"variants_{tag}"] = var
    with open(outpath, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)
    print(json.dumps(out, indent=1, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
