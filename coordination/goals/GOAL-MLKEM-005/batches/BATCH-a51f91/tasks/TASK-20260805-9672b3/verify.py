#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Independent verification pass over TASK-20260805-9672b3/results.json.

Makes NO estimator call and imports nothing from the estimator or the shim: it
re-reads the raw arrays already recorded by the protocol run and recomputes
every summary from them.  It therefore adds no run to the budget and cannot
change a number -- it can only agree or disagree with one.

It also carries the corrections for two labelling defects in results.json.
results.json is an immutable run record and is NOT edited; the corrections live
here and in receipt.json, computed from results.json's own raw `points` arrays.

    python3 verify.py            # writes verification.json next to this file
"""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results.json")
OUT = os.path.join(HERE, "verification.json")
SETS = ["Kyber512", "Kyber768", "Kyber1024"]


def ols(xs, ys):
    """Ordinary least squares slope/intercept, pure Python."""
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx
    icpt = my - slope * mx
    resid = [y - (slope * x + icpt) for x, y in zip(xs, ys)]
    sd = math.sqrt(sum(r * r for r in resid) / (n - 2)) if n > 2 else float("nan")
    se = sd / math.sqrt(sxx) if n > 2 else float("nan")
    return slope, icpt, sd, max(abs(r) for r in resid), se


def main():
    r = json.load(open(RES))
    v = {"schema": "crypto.autoresearch.task_verification.v1",
         "task_id": r["task_id"], "verifies": "results.json",
         "estimator_calls_made": 0,
         "method": "re-reads the recorded raw arrays; recomputes every summary from them",
         "checks": {}}
    C = v["checks"]

    # V1 -- the table's delta_beta_fd is the difference of its own recorded betas
    bad = [(row["set"], row["c"]) for row in r["finite_difference_table"]["rows"]
           if row["delta_beta_fd"] != row["scaled"]["beta"] - row["baseline"]["beta"]]
    C["V1_table_delta_beta_matches_its_own_raw_betas"] = {"pass": not bad, "mismatches": bad}

    # V2 -- the table cells and the scan (computed by SEPARATE calls in the run)
    #       must agree at the same c
    scan = r["scan_staircase"]["by_set"]
    mism = []
    for row in r["finite_difference_table"]["rows"]:
        pts = [p for p in scan[row["set"]]["points"] if p["c"] == row["c"]]
        if not pts:
            mism.append({"set": row["set"], "c": row["c"], "why": "no scan point"})
            continue
        p = pts[0]
        if (p["beta"] != row["scaled"]["beta"] or p["d"] != row["scaled"]["d"]
                or p["log2_rop"] != row["scaled"]["log2_rop"]):
            mism.append({"set": row["set"], "c": row["c"], "scan": p, "table": row["scaled"]})
    C["V2_table_and_scan_agree_at_shared_c"] = {
        "what": "two independent invocations inside the run land on the same cell",
        "pass": not mism, "mismatches": mism}

    # V3 -- 0.292 column
    bad = [(row["set"], row["c"]) for row in r["finite_difference_table"]["rows"]
           if abs(row["bits_0292_x_delta_beta_fd"] - 0.292 * row["delta_beta_fd"]) > 1e-12]
    C["V3_bits_column_is_0292_times_delta_beta"] = {"pass": not bad, "mismatches": bad}

    # V4 -- Arm A vs Arm B delta_beta
    a = {(x["set"], x["c"]): x["delta_beta_fd"] for x in r["finite_difference_table"]["rows"]}
    b = {(x["set"], x["c"]): x["delta_beta_fd"] for x in r["arm_b_d_not_reoptimised"]["rows"]}
    same = {f"{k[0]}@{k[1]}": [a[k], b[k]] for k in sorted(a)}
    C["V4_delta_beta_identical_with_and_without_d_reoptimisation"] = {
        "what": ("Whether re-optimising d (hence m) moves the FINITE DIFFERENCE at all. "
                 "Mechanism, from estimator/lwe_primal.py cost_zeta: step 1 optimises beta "
                 "with d taken from the closed-form heuristic d(beta); step 2 then "
                 "re-optimises d at that FIXED beta. The optimiser is sequential, never "
                 "joint, so step 2 cannot feed back into beta."),
        "identical_in_all_cells": all(a[k] == b[k] for k in a),
        "cells_armA_armB": same}

    # V5 -- corrected staircase statistics (results.json defect D2: the key
    #       `non_monotone_pairs_beta_rises_when_norm_grows` actually holds the
    #       EXPECTED steps, and the anomalous pairs were never listed)
    corr = {}
    for s in SETS:
        pts = scan[s]["points"]
        down = [{"c_lo": pts[i]["c"], "c_hi": pts[i + 1]["c"],
                 "beta_lo": pts[i]["beta"], "beta_hi": pts[i + 1]["beta"],
                 "drop": pts[i]["beta"] - pts[i + 1]["beta"]}
                for i in range(len(pts) - 1) if pts[i + 1]["beta"] < pts[i]["beta"]]
        up = sum(1 for i in range(len(pts) - 1) if pts[i + 1]["beta"] > pts[i]["beta"])
        flat = sum(1 for i in range(len(pts) - 1) if pts[i + 1]["beta"] == pts[i]["beta"])
        corr[s] = {
            "intervals": len(pts) - 1,
            "beta_rises_with_c_expected_direction": up,
            "beta_flat": flat,
            "beta_FALLS_with_c_ANOMALOUS": len(down),
            "anomalous_pairs": down,
            "max_anomalous_drop_blocks": max((x["drop"] for x in down), default=0),
        }
    C["V5_staircase_monotonicity_corrected"] = {
        "what": ("beta*(c) should be non-decreasing in c: a larger target norm is a harder "
                 "instance. Where it is not, the optimiser's selection is noisy at that "
                 "resolution. This is the corrected version of results.json's mislabelled key."),
        "by_set": corr}

    # V6 -- slope of beta in ln c, from all 41 recorded points, vs the linearisation
    slopes = {}
    for s in SETS:
        pts = scan[s]["points"]
        xs = [math.log(p["c"]) for p in pts]
        ys = [float(p["beta"]) for p in pts]
        slope, icpt, sd, mx, se = ols(xs, ys)
        lnd = r["baselines"][s]["ln_delta"]
        lin = 1.0 / (2.0 * lnd)
        endpoint = (pts[-1]["beta"] - pts[0]["beta"]) / (xs[-1] - xs[0])
        slopes[s] = {
            "ols_dbeta_per_dlnc_over_41_points": slope,
            "ols_residual_sd_blocks": sd,
            "ols_max_abs_residual_blocks": mx,
            "ols_slope_standard_error": se,
            "ols_slope_standard_error_caveat": (
                "DESCRIPTIVE ONLY. The residuals are deterministic integer quantisation of a "
                "deterministic optimiser, not random error, so this is not an inferential "
                "confidence statement."),
            "endpoint_secant_dbeta_per_dlnc": endpoint,
            "linearised_slope_one_over_2lndelta": lin,
            "ols_minus_linearised": slope - lin,
            "ols_over_linearised": slope / lin,
            "ols_minus_linearised_in_slope_standard_errors": (slope - lin) / se if se else None,
            "implied_beta_difference_over_the_scan_window": (slope - lin) * (xs[-1] - xs[0]),
        }
    C["V6_slope_of_the_optimiser_vs_the_linearised_slope"] = {
        "LABEL": ("The slope comparison is part of the DESIGN AUDIT and is NOT A FINDING. "
                  "It is reported because the cellwise differences at |delta_beta| of 1-6 "
                  "are dominated by the integer staircase, and a reader deserves the "
                  "better-conditioned readout rather than the noisier one."),
        "estimator_note": ("OLS of the recorded beta on ln c across the whole scan window. "
                           "The residual sd is the size of the optimiser's own selection "
                           "scatter about a straight line, in blocks."),
        "by_set": slopes}

    # V7 -- the estimator's own bits-per-block, against the card's 0.292
    bpb = {}
    for s in SETS:
        pts = scan[s]["points"]
        xs = [float(p["beta"]) for p in pts]
        ys = [p["log2_rop"] for p in pts]
        slope, icpt, sd, mx, se = ols(xs, ys)
        bpb[s] = {"ols_dlog2rop_per_dbeta": slope, "ols_residual_sd_bits": sd,
                  "card_constant": 0.292, "card_over_measured": 0.292 / slope,
                  "card_overstates_by_percent": 100.0 * (0.292 / slope - 1.0)}
    C["V7_estimator_own_bits_per_block_vs_card_0292"] = {
        "what": ("0.292 is the card's conversion constant (classical core-sieve exponent). "
                 "The betas it multiplies came from RC.MATZOV. This is what RC.MATZOV's own "
                 "cost actually moves per block over the scanned range. Both are MODELLED."),
        "by_set": bpb}

    # V8 -- controls and the known-answer control text
    kac = r["step0_known_answer_control"]
    need = ["Kyber512   140.1994731076     140.1994731076   0.00e+00   389   422   1005",
            "Kyber768   200.9587149141     200.9587149141   0.00e+00   606   640   1420"]
    C["V8_step0_control"] = {
        "exit_code": kac["exit_code"], "passed_flag": kac["passed"],
        "required_lines_present_verbatim": all(x in kac["stdout_verbatim"] for x in need),
        "pass_line_present": "PASS: every reference reproduced" in kac["stdout_verbatim"],
        "stderr_empty": kac["stderr_verbatim"] == "",
        "pass": (kac["exit_code"] == 0 and kac["passed"]
                 and all(x in kac["stdout_verbatim"] for x in need))}
    C["V9_run_controls"] = {k: r["controls"][k]["pass"] for k in r["controls"]}

    # V10 -- the toy n=100 cell is FORCED by the estimator's beta search floor
    toy = r["toy_shape_arm_NOT_CRYPTO_SCALE"]["sets"]
    t100 = [t for t in toy if t["n"] == 100][0]
    C["V10_toy_n100_is_at_the_search_floor_FORCED"] = {
        "what": ("estimator/lwe_primal.py cost_zeta step 1 searches beta over "
                 "local_minimum(40, max_beta + 2), so beta = 40 is the FLOOR of the search, "
                 "not an optimum. The toy n=100 baseline sits exactly on it, so its "
                 "delta_beta_fd = 0 is FORCED and carries no information about the "
                 "conversion. Reported as forced, per the batch's forced-quantity screen."),
        "baseline_beta": t100["baseline"]["beta"], "search_floor": 40,
        "is_pinned_at_floor": t100["baseline"]["beta"] == 40,
        "all_delta_beta_zero": [row["delta_beta_fd"] for row in t100["rows"]],
        "delta_log2_rop_still_moves": [row["delta_log2_rop_matzov"] for row in t100["rows"]]}

    # V11 -- budget
    bud = r["budget"]
    C["V11_budget"] = {"wall_clock_within": bud["within_wall_clock_budget"],
                       "wall_clock_seconds_used": bud["wall_clock_seconds_used"],
                       "peak_rss_gb": bud["peak_rss_gb_measured"],
                       "memory_within": bud["peak_rss_gb_measured"] <= bud["memory_gb_budget"],
                       "pass": bud["within_wall_clock_budget"]
                       and bud["peak_rss_gb_measured"] <= bud["memory_gb_budget"]}

    hard = ["V1_table_delta_beta_matches_its_own_raw_betas",
            "V2_table_and_scan_agree_at_shared_c",
            "V3_bits_column_is_0292_times_delta_beta",
            "V8_step0_control", "V11_budget"]
    v["all_hard_checks_pass"] = all(C[k]["pass"] for k in hard)
    with open(OUT, "w") as fh:
        json.dump(v, fh, indent=2)

    print(json.dumps({k: (C[k].get("pass", "n/a")) for k in C}, indent=2))
    print("\nV4 identical delta_beta with/without d re-optimisation:",
          C["V4_delta_beta_identical_with_and_without_d_reoptimisation"]["identical_in_all_cells"])
    for s in SETS:
        x = C["V6_slope_of_the_optimiser_vs_the_linearised_slope"]["by_set"][s]
        y = C["V7_estimator_own_bits_per_block_vs_card_0292"]["by_set"][s]
        z = C["V5_staircase_monotonicity_corrected"]["by_set"][s]
        print(f"{s:10} OLS dbeta/dlnc = {x['ols_dbeta_per_dlnc_over_41_points']:8.2f} "
              f"(sd {x['ols_residual_sd_blocks']:.2f} blocks)  linearised {x['linearised_slope_one_over_2lndelta']:8.2f} "
              f"ratio {x['ols_over_linearised']:.4f} ({x['ols_minus_linearised']:+.2f} +/- {x['ols_slope_standard_error']:.2f})  | bits/block {y['ols_dlog2rop_per_dbeta']:.4f} "
              f"vs 0.292 (+{y['card_overstates_by_percent']:.1f}%)  | anomalous drops {z['beta_FALLS_with_c_ANOMALOUS']}"
              f"/{z['intervals']}, max {z['max_anomalous_drop_blocks']}")
    print(f"\nall hard checks pass: {v['all_hard_checks_pass']}  -> {OUT}")
    return 0 if v["all_hard_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
