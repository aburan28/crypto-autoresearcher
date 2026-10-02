#!/usr/bin/env python3
"""TASK-20260929-c40e48: J2 comparison (written AFTER the J2 section was sealed).

Compares the sealed blind re-derivation (rederivation/j2-results.json and
rederivation/j2-floor-rows.jsonl.gz) with the archived run outputs
(raw-result.json, fits.json, floor-rows.jsonl.gz). Exact float equality is
required where both sides call the same frozen function on the same rows in the
same order; Monte Carlo-level agreement is reported where the implementations
differ (P6).

Usage: python compare_j2.py <rederivation dir> <archived run dir> <out.json>
"""
import gzip
import json
import math
import sys


def main(rd, run, out_path):
    mine = json.load(open(f"{rd}/j2-results.json"))
    raw = json.load(open(f"{run}/raw-result.json"))
    fits = json.load(open(f"{run}/fits.json"))
    res = {"fits": {}, "P5": {}, "P6": {}, "outcome": {}, "floor_rows": {}}
    all_exact = True
    for name, v in mine["P4_fits"].items():
        a = raw["P3_P4_fits"][name]
        b = fits["series"][name]
        for mk, ak in (("12..32", "primary_12_32"), ("20..32", "sensitivity_20_32")):
            m = v[mk]["frozen_file_order"]
            A, B = a[ak], b[ak]
            exact = all(m[k] == A[k] == B[k] for k in ("slope", "lo", "hi", "n"))
            all_exact &= exact
            res["fits"][f"{name} {mk}"] = {
                "mine": [m["slope"], m["lo"], m["hi"], m["n"]],
                "raw_result": [A["slope"], A["lo"], A["hi"], A["n"]],
                "fits_json": [B["slope"], B["lo"], B["hi"], B["n"]],
                "exact_equal_all_three": exact}
    res["fits_all_16_exact"] = all_exact
    # P5
    res["P5"] = {"mine_min": mine["P5"]["min_ratio"], "raw_min": raw["P5_min"]["min_ratio"],
                 "fits_min": fits["min_ratio"],
                 "exact": mine["P5"]["min_ratio"] == raw["P5_min"]["min_ratio"] == fits["min_ratio"],
                 "mine_rows_below_1": mine["P5"]["rows_below_1"], "raw_rows_below_1": raw["P5_min"]["rows_below_1"],
                 "fits_rows_below_1": fits["rows_below_1"],
                 "mine_n": mine["P5"]["n_ic_rows"], "raw_n": raw["P5_min"]["n_rows"],
                 "min_row_mine": mine["P5"]["min_row"], "min_row_raw": raw["P5_min"]["min_row"]}
    # P6
    for fb in ("small_x", "random", "subgroup"):
        m = mine["P6"]["bases"][fb]
        a = raw["P6_bases"]["per_base"][fb]
        b = fits["m3_base_geometric_means"]["per_base"][fb]
        res["P6"][fb] = {"geo_mean_mine": m["geo_mean"], "geo_mean_raw": a["geometric_mean_ratio"],
                         "geo_mean_rel_diff": abs(m["geo_mean"] - a["geometric_mean_ratio"]) / a["geometric_mean_ratio"],
                         "ci_mine_random0": m["ci_random0_statspy"], "ci_mine_numpy200k": m["ci_numpy200k"],
                         "ci_raw": a["ci95"], "ci_fits": b["ci95"], "raw_equals_fits": a == b,
                         "raw_minus_mine200k": [a["ci95"][0] - m["ci_numpy200k"][0], a["ci95"][1] - m["ci_numpy200k"][1]]}
    res["P6"]["overlap_raw"] = raw["P6_bases"]["pairwise_overlap"]
    res["P6"]["overlap_mine"] = mine["P6"]["pairwise_overlap"]
    # outcome
    res["outcome"] = {"mine": mine["outcomes"]["first_true_in_stated_order_excluding_OUT-INVALID"],
                      "mine_F3": mine["outcomes"]["F-3_series"], "mine_F2": mine["outcomes"]["F-2_series"],
                      "raw": raw["outcome_id"], "raw_conditions": raw["outcome_conditions_met"],
                      "raw_exclusions": raw["condition_details"]["slope_interval_exclusions"]}
    # floor rows, IC part, keyed
    arch = [json.loads(l) for l in gzip.open(f"{run}/floor-rows.jsonl.gz", "rt")]
    arch_ic = [x for x in arch if x.get("kind") != "rho"]
    mrows = [json.loads(l) for l in gzip.open(f"{rd}/j2-floor-rows.jsonl.gz", "rt")]

    def k(x):
        f = x["file"].replace(".jsonl.gz", "")
        return (f, x["bits"], x["curve"], x["method"], x["fb"], x["engine"])
    A = {k(x): x for x in arch_ic}
    M = {k(x): x for x in mrows}
    diffs = []
    for key in sorted(set(A) | set(M), key=str):
        a, m = A.get(key), M.get(key)
        if a is None or m is None:
            diffs.append({"key": key, "missing_in": "archive" if a is None else "mine"})
            continue
        for mf, af in (("S", "S"), ("T", "T"), ("search", "search"), ("r", "relations"), ("N", "N"),
                       ("floor", "floor"), ("ratio", "ratio"), ("table_share", "table_share"), ("log2N", "log2N")):
            if m[mf] != a[af]:
                diffs.append({"key": key, "field": af, "mine": m[mf], "archive": a[af]})
    order_same = [k(x) for x in arch_ic] == [k(x) for x in mrows]
    res["floor_rows"] = {"archive_ic_rows": len(arch_ic), "mine_ic_rows": len(mrows),
                         "archive_rho_rows": len(arch) - len(arch_ic),
                         "fields_compared": 9, "differences": diffs[:50], "n_differences": len(diffs),
                         "ic_row_order_identical": order_same}
    json.dump(res, open(out_path, "w"), indent=1, default=str)
    print(json.dumps({"fits_all_16_exact": all_exact, "P5_exact": res["P5"]["exact"],
                      "floor_row_differences": len(diffs), "order_same": order_same,
                      "outcome": res["outcome"]}, indent=1, default=str))


if __name__ == "__main__":
    main(*sys.argv[1:4])
