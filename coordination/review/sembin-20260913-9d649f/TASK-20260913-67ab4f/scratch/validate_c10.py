#!/usr/bin/env python3
"""Validator TASK-20260913-67ab4f -- joint M3(3): C10 residuals recomputed from
inputs/SEMAEV-2015-310/tables.yaml with my own arithmetic.

Readings of the Tables 1-2 MB column, as the run declares them:
  A  the printed MB is a per-system PEAK          -> log2 bits = log2(MB * 8 * 2^20)
  B  the printed MB is the TOTAL over 100 systems -> reading A minus log2(100)
Neither is picked here either; both are reported (contract C10).

Model memory per row: the same four storage readings as the surface, at the row's
own (n, t, k), with the chain-variable count N = (t - 2) n + k t (the run's column
is labelled t, and t is the chain length; where t < m this substitutes t for m,
which is a modelling choice and is reported as such).
"""
import json
import math
import os
from math import comb, log2

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = "/workspace/experiments/EXP-SEMBIN-2c40bb/runs/RUN-SEMBIN-3ae91c"
TABLES = "/workspace/inputs/SEMAEV-2015-310/tables.yaml"
INF = float("inf")


def log2_add(a, b):
    if a == -INF:
        return b
    if b == -INF:
        return a
    hi, lo = max(a, b), min(a, b)
    return hi if hi - lo > 60 else hi + log2(1.0 + 2.0 ** (lo - hi))


def parse_tables():
    """Minimal parser for the inline-mapping rows of tables.yaml (no yaml dependency)."""
    rows = {"table_1": [], "table_2": []}
    cur = None
    for line in open(TABLES):
        s = line.strip()
        if s.startswith("table_1:"):
            cur = "table_1"
            continue
        if s.startswith("table_2:"):
            cur = "table_2"
            continue
        if s.startswith("table_3:") or s.startswith("derived_checks:"):
            cur = None
            continue
        if cur and s.startswith("- {") and s.endswith("}"):
            body = s[3:-1]
            d = {}
            for part in body.split(","):
                k, v = part.split(":", 1)
                k, v = k.strip(), v.strip()
                if v in ("true", "false"):
                    d[k] = v == "true"
                else:
                    try:
                        d[k] = int(v)
                    except ValueError:
                        d[k] = float(v)
            rows[cur].append(d)
    return rows


def model_mem_log2(n, t, k):
    nvars = (t - 2) * n + k * t
    wl = log2(sum(comb(nvars, d) for d in range(5)))
    rel = k + log2(t * k + 2 * n)
    out = {}
    out["dense_row_echelon"] = 2.0 * wl
    out["semaev_sparse"] = (4.0 * log2(n * t) - log2(24.0)) + (3.0 * log2(n) - log2(t))
    rows_log2 = log2(n * (t - 1)) + log2(nvars + 1)
    out["rows_times_cols_dense"] = rows_log2 + wl
    v = 2 * n + k
    out["nonzeros_with_index_sparse"] = rows_log2 + log2(sum(comb(v, d) for d in range(4))) + log2(wl)
    return {"nvars": nvars, "macaulay_width_log2": wl, "relation_store_log2": rel,
            "working_sets": out,
            "totals": {kk: log2_add(rel, vv) for kk, vv in out.items()},
            "working_set_only": out}


tabs = parse_tables()
mine = []
for tname in ("table_1", "table_2"):
    for r in tabs[tname]:
        n = r["n"]
        t = r.get("t", r.get("t_eq_m"))
        k = r["k"]
        MB = r["total_MB"]
        A = log2(MB * 8.0 * (2 ** 20))
        B = A - log2(100.0)
        mm = model_mem_log2(n, t, k)
        mine.append({"table": tname, "n": n, "t": t, "k": k, "total_MB_printed": MB,
                     "nvars": mm["nvars"], "macaulay_width_log2": round(mm["macaulay_width_log2"], 4),
                     "reading_A_log2_bits": round(A, 4), "reading_B_log2_bits": round(B, 4),
                     "model_working_set_only": {kk: round(vv, 4) for kk, vv in mm["working_set_only"].items()},
                     "model_total_with_relation_store": {kk: round(vv, 4) for kk, vv in mm["totals"].items()},
                     "residual_A_working_set_only": {kk: round(vv - A, 4) for kk, vv in mm["working_set_only"].items()},
                     "residual_B_working_set_only": {kk: round(vv - B, 4) for kk, vv in mm["working_set_only"].items()}})

run = json.load(open(os.path.join(RUN, "measurement-comparison.json")))
runrows = {(r["table"], r["n"], r["t"], r["k"]): r for r in run["rows"]}
cmp_rows, worst = [], 0.0
missing = []
for r in mine:
    key = (r["table"], r["n"], r["t"], r["k"])
    if key not in runrows:
        missing.append(key)
        continue
    rr = runrows[key]
    d = {"key": key,
         "nvars_agree": rr["nvars"] == r["nvars"],
         "width_diff": round(rr["macaulay_width_log2"] - r["macaulay_width_log2"], 5),
         "reading_A_diff": round(rr["measured_log2_bits_reading_A_peak_per_system"] - r["reading_A_log2_bits"], 5),
         "reading_B_diff": round(rr["measured_log2_bits_reading_B_total_over_100_systems_per_system"] - r["reading_B_log2_bits"], 5),
         "model_diff": {kk: round(rr["model_log2_bits"][kk] - r["model_working_set_only"][kk], 5)
                        for kk in r["model_working_set_only"]},
         "residual_A_diff": {kk: round(rr["model_minus_measured_bits_reading_A"][kk] - r["residual_A_working_set_only"][kk], 5)
                             for kk in r["model_working_set_only"]},
         "residual_B_diff": {kk: round(rr["model_minus_measured_bits_reading_B"][kk] - r["residual_B_working_set_only"][kk], 5)
                             for kk in r["model_working_set_only"]}}
    for v in list(d["model_diff"].values()) + list(d["residual_A_diff"].values()) + list(d["residual_B_diff"].values()) + [d["width_diff"], d["reading_A_diff"], d["reading_B_diff"]]:
        worst = max(worst, abs(v))
    cmp_rows.append(d)

# upper-bound verdicts recomputed from my own residuals
verdicts = {}
for kk in ["dense_row_echelon", "semaev_sparse", "rows_times_cols_dense", "nonzeros_with_index_sparse"]:
    resA = [r["residual_A_working_set_only"][kk] for r in mine]
    resB = [r["residual_B_working_set_only"][kk] for r in mine]
    verdicts[kk] = {"reading_A_upper_bounds_every_row": all(x >= 0 for x in resA),
                    "reading_A_rows_exceeded": sum(1 for x in resA if x < 0),
                    "reading_B_upper_bounds_every_row": all(x >= 0 for x in resB),
                    "reading_B_rows_exceeded": sum(1 for x in resB if x < 0),
                    "min_residual_A": min(resA), "max_residual_A": max(resA),
                    "min_residual_B": min(resB), "max_residual_B": max(resB)}

# dense-minus-sparse gap: measured scale vs FIPS labels (my own arithmetic)
gap_small = [{"n": r["n"], "t": r["t"],
              "dense_minus_sparse_bits": round(r["model_working_set_only"]["dense_row_echelon"]
                                               - r["model_working_set_only"]["semaev_sparse"], 4)}
             for r in mine]
gap_labels = {}
for n, m in [(163, 7), (233, 9), (283, 9), (409, 11), (571, 12)]:
    k = -(-n // m)
    mm = model_mem_log2(n, m, k)
    gap_labels[n] = {"m": m, "dense_minus_sparse_bits": round(
        mm["working_set_only"]["dense_row_echelon"] - mm["working_set_only"]["semaev_sparse"], 4)}

out = {"rows_in_tables_yaml": {"table_1": len(tabs["table_1"]), "table_2": len(tabs["table_2"]),
                               "total": len(tabs["table_1"]) + len(tabs["table_2"])},
       "run_rows_compared": run["rows_compared"],
       "contract_C10_says": "34 MAGMA memory measurements",
       "my_rows": mine, "row_by_row_vs_run": cmp_rows,
       "rows_present_in_mine_absent_from_run": missing,
       "worst_disagreement_bits_any_field": worst,
       "upper_bound_verdicts_mine": verdicts,
       "upper_bound_verdicts_run": run["upper_bound_check_per_reading"],
       "gap_at_measured_scale": gap_small[:6] + gap_small[-3:],
       "gap_at_measured_scale_min_max": {"min": min(g["dense_minus_sparse_bits"] for g in gap_small),
                                         "max": max(g["dense_minus_sparse_bits"] for g in gap_small)},
       "gap_at_labels": gap_labels}
with open(os.path.join(HERE, "validate_c10.json"), "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps({k: v for k, v in out.items() if k not in ("my_rows", "row_by_row_vs_run")}, indent=1))
print("rows compared:", len(cmp_rows), "worst field disagreement bits:", worst)
