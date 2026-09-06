#!/usr/bin/env python3
"""EXP-PFDR-20ee58 -- Stage 5 analysis (zero compute; observations only).

Reads ONLY experiments/EXP-PFDR-20ee58/runs/*/raw-result.json (+ manifest status)
and writes analysis.md and analysis.json.  Every deficit, residual and fit value
below is recomputed from the raw per-cell records (rows, ncols, rank, koszul),
never copied from a summary.  The frozen prediction is copied here for the
comparison only and is never adjusted.  No verdict on H-PFDR-9aadc0 is stated:
the pre-registered branch is DECLARED by the frozen rule, not interpreted.

    python3 experiments/EXP-PFDR-20ee58/analyze.py                 # full analysis
    python3 experiments/EXP-PFDR-20ee58/analyze.py --stop-check-only  # stopping rule 3 at the deciding cell
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys
from fractions import Fraction
from typing import Dict, List

import yaml

EXP_ID = "EXP-PFDR-20ee58"
HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "runs")

# ---------------------------------------------------------------------------
# Frozen prediction and criteria (copied from specification.yaml; read-only)
# ---------------------------------------------------------------------------
FROZEN = {
    "calibration": {"deficit_graded_D3": 1, "deficit_graded_D4": 31, "null": 0},
    "null_support": "deficit(D) = 0 for all D <= 8 at every cell (up to the small-p rank-drop budget)",
    "M1": "deficit(D) = 0 for all D <= 8 at every s, p and curve (prior 0.75)",
    "M2": "deficit(8) - deficit_topology(8) = alpha s + beta with alpha's CI excluding 0 and residuals p-independent (prior 0.10)",
    "M3_or_constant": "an s-independent positive constant at some D in {5, 6, 7} (prior 0.15) reads as M2's constant term or M3",
    "resolution": "one integer per s point; an interval spanning branches is unresolved",
    "artifact_budget": "EXP-PFDR-fd901a rank-drop rate at p = 4099: 0/40, exact 95% CI [0, 0.0881]; criterion 'below 0.1 per draw'",
    "stopping_rule_3": "stop Stage 3 at the deciding cell (s = 3, D = 8) if NULL-SUPPORT shows a nonzero deficit beyond the small-p budget on more than one seed",
}
PLANNED_CELLS = [(s, p) for s in (3, 4, 5, 6) for p in (4099, 16411, 65537)]
S_MAIN = (3, 4, 5)
FD901A_BUDGET_RATE = 0.1     # frozen criterion (4) of EXP-PFDR-fd901a: rank-drop rate below 0.1 per draw
FD901A_OBSERVED = {"rate": 0.0, "events": 0, "draws": 40, "ci95": [0.0, 0.0881]}


def load_runs() -> Dict[str, dict]:
    out = {}
    for d in sorted(glob.glob(os.path.join(RUNS, "RUN-*"))):
        rid = os.path.basename(d)
        with open(os.path.join(d, "manifest.yaml")) as fh:
            man = yaml.safe_load(fh)["run"]
        with open(os.path.join(d, "raw-result.json")) as fh:
            raw = json.load(fh)
        out[rid] = {"manifest": man, "raw": raw, "status": man["status"]}
    return out


def recompute_deficit(cum: dict, D: int) -> int:
    """deficit(D) = rows - rank - koszul, from the raw per-cell layer record."""
    L = cum[str(D)]
    return L["row_count"] - L["full_rank"] - L["koszul_pairwise"]


def clopper_pearson(k: int, n: int, alpha: float = 0.05):
    """Exact binomial CI by bisection on the regularised incomplete beta (Fraction-free floats are fine here: a bound, not a metric)."""
    from math import comb

    def cdf(x, n, p):
        return sum(comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(x + 1))

    def solve(target, f, lo=0.0, hi=1.0):
        # f is increasing in p; find p with f(p) = target by bisection
        for _ in range(60):
            mid = (lo + hi) / 2
            if f(mid) < target:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
    if n == 0:
        return [None, None]
    # lower: P(X >= k) = alpha/2  <=>  1 - cdf(k-1) = alpha/2 ; upper: P(X <= k) = alpha/2  <=>  1 - cdf(k) = 1 - alpha/2
    lower = 0.0 if k == 0 else solve(alpha / 2, lambda p: 1 - cdf(k - 1, n, p), 0.0, 1.0)
    upper = 1.0 if k == n else solve(1 - alpha / 2, lambda p: 1 - cdf(k, n, p), 0.0, 1.0)
    return [round(lower, 4), round(upper, 4)]


def ols(points: List[tuple]):
    """Least squares y = alpha x + beta with a t-based 95% CI on alpha (exact zero variance -> CI [0, 0])."""
    n = len(points)
    if n < 3:
        return None
    xs = [Fraction(x) for x, _ in points]
    ys = [Fraction(y) for _, y in points]
    xbar = sum(xs) / n
    ybar = sum(ys) / n
    sxx = sum((x - xbar) ** 2 for x in xs)
    if sxx == 0:
        return None
    sxy = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys))
    alpha = sxy / sxx
    beta = ybar - alpha * xbar
    rss = sum((y - (alpha * x + beta)) ** 2 for x, y in zip(xs, ys))
    dof = n - 2
    if rss == 0:
        return {"alpha": float(alpha), "beta": float(beta), "n": n, "rss": 0, "alpha_ci95": [float(alpha), float(alpha)],
                "alpha_se": 0.0, "note": "zero residual variance: every observation lies on the fitted line exactly; the CI is a point"}
    se = math.sqrt(float(rss / dof) / float(sxx))
    # t_{0.975, dof}: dof >= 52 here; use the normal quantile with a conservative small-dof table
    t = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}.get(dof, 2.01 if dof < 60 else 1.98)
    return {"alpha": float(alpha), "beta": float(beta), "n": n, "rss": float(rss), "alpha_se": se,
            "alpha_ci95": [float(alpha) - t * se, float(alpha) + t * se], "t_quantile": t}


def analyse(runs: Dict[str, dict]) -> dict:
    A: dict = {"runs": {rid: r["status"] for rid, r in runs.items()}, "frozen": FROZEN}

    # ---- calibration ------------------------------------------------------
    cal = runs.get("RUN-PFDR-20ee58-calib-gf2-n12")
    if cal:
        m = cal["raw"]["metrics"]
        sem = cal["raw"]["raw"]["result"]["semaev_arm"]["cumulative"]
        recomputed = {D: recompute_deficit(sem, D) for D in (2, 3, 4, 5)}
        graded = [recomputed[2], recomputed[3] - recomputed[2], recomputed[4] - recomputed[3], recomputed[5] - recomputed[4]]
        A["calibration"] = {
            "status": cal["status"], "fixture_sha256_matches": m["fixture_sha256_matches"],
            "rows": m["rows_D2_D3_D4_D5"], "rank": m["rank_D2_D3_D4_D5"], "koszul": m["koszul_pairwise_D2_D3_D4_D5"],
            "deficit_cumulative_recomputed_D2_D5": [recomputed[D] for D in (2, 3, 4, 5)],
            "deficit_graded_recomputed_D2_D5": graded,
            "deficit_graded_reported": m["deficit_graded_D2_D3_D4_D5"],
            "agree_raw_vs_metrics": graded == m["deficit_graded_D2_D3_D4_D5"],
            "frozen_expected": FROZEN["calibration"],
            "D3_equals_1": graded[1] == 1, "D4_equals_31": graded[2] == 31, "cumulative_D4_equals_32_8k": recomputed[4] == 32,
            "D5_cumulative_archived_1322": recomputed[5] == 1322,
            "null_dreg_boolean_deficit_cumulative": cal["raw"]["raw"]["result"]["null_dreg_boolean"]["profile"]["deficit_cumulative"],
            "null_histogram_matched_deficit_cumulative": {k: v["profile"]["deficit_cumulative"] for k, v in cal["raw"]["raw"]["result"]["null_histogram_matched"].items()},
            "nulls_all_zero": m["null_deficits_all_zero"],
            "mixed_mode_code_path": {"deficit_pairwise_D2_D4": m["mixed_mode_deficit_pairwise_D2_D3_D4"], "derived_expectation": [0, 1, 33],
                                     "matches": m["mixed_mode_matches_derived_expectation"]},
            "stage0_mechanical_checks_pass": m["stage0_checks_all_pass"],
            "calibration_reproduced": m["calibration_reproduced"],
        }

    # ---- s = 1 slice -------------------------------------------------------
    s1 = runs.get("RUN-PFDR-20ee58-s1-slice")
    if s1:
        m = s1["raw"]["metrics"]
        cells = s1["raw"]["raw"]["cells"]
        A["s1_slice"] = {"status": s1["status"], "symbolic_identity_all_cells": m["symbolic_identity_all_cells"],
                         "per_cell": {f"p{c['p']}-B{c['B']}": {
                             "identity": c["symbolic_identity"], "per_generator_equal": c["per_generator_equal"],
                             "generator_degrees": c["generator_degrees"],
                             "cumulative_rank_D4_D10": c["cumulative_rank"], "cumulative_rows_D4_D10": c["cumulative_rows"],
                             "cumulative_deficit_recomputed_D4_D10": [recompute_deficit(c["cumulative"], D) for D in range(4, 11)],
                             "per_layer_rank_D4_D10": c["per_layer_rank"], "per_layer_top_rank_D4_D10": c["per_layer_top_rank"],
                             "certificate_verified": c["certificate_verified"]} for c in cells}}

    # ---- Stage 3 / 4 cells -------------------------------------------------
    cells: dict = {}
    for rid, r in runs.items():
        if "-s" not in rid or "-p" not in rid or rid.endswith("s1-slice"):
            continue
        m = r["raw"]["metrics"]
        s, p = m["s"], m["p"]
        degrees = m["degrees"]
        draws = r["raw"]["raw"]["draws"]
        by_arm: dict = {}
        for d in draws:
            if "cumulative" not in d:
                continue
            vec = [recompute_deficit(d["cumulative"], D) for D in degrees]
            assert vec == d["deficit_vector"], (rid, d["arm"], vec, d["deficit_vector"])  # raw and summary agree
            rec = {"deficit": vec, "valid": d.get("valid"), "quotient_dim": d["quotient"]["dimension"],
                   "sol": d.get("sol"), "generator_degrees": d["generator_degrees"],
                   "rows": d["rows"], "ncols": d["ncols"], "rank": d["rank"], "koszul": d["koszul"],
                   "zero_product_rows": [d["cumulative"][str(D)]["zero_product_rows"] for D in degrees],
                   "peak_preflight": d["preflight"][str(max(degrees))]}
            for key in ("curve_seed", "target_seed", "null_seed", "cubic_seed"):
                if key in d:
                    rec[key] = d[key]
            if "certificate_verified" in d:
                rec["certificate_verified"] = d["certificate_verified"]
            by_arm.setdefault(d["arm"], []).append(rec)
        cells[f"s{s}-p{p}"] = {"run_id": rid, "status": r["status"], "s": s, "p": p, "degrees": degrees,
                               "stopped": m.get("stopped"), "preflight_aborted": m.get("preflight_aborted"),
                               "certificates": {"total": m["planted_certificates_total"], "failed": m["planted_certificates_failed"]},
                               "wall_seconds": r["manifest"]["timing"]["wall_seconds"],
                               "peak_rss_bytes": r["manifest"]["resources"]["peak_rss_bytes"],
                               "arms": by_arm}
    A["cells"] = cells
    A["cells_missing"] = [f"s{s}-p{p}" for s, p in PLANNED_CELLS if f"s{s}-p{p}" not in cells]

    # per-arm deficit tables: per (s, p, D): list of deficits over draws, min/max
    table: dict = {}
    for key, c in cells.items():
        if c["status"] != "completed_valid":
            continue
        for arm, recs in c["arms"].items():
            for i, D in enumerate(c["degrees"]):
                vals = [r["deficit"][i] for r in recs if r.get("valid", True)]
                table.setdefault(arm, {}).setdefault(key, {})[str(D)] = {"values": vals, "min": min(vals), "max": max(vals), "n": len(vals)}
    A["deficit_tables"] = table

    # ---- NULL-SUPPORT check against the small-p budget --------------------
    ns_events = []
    ns_total = 0
    for key, c in cells.items():
        if c["status"] != "completed_valid":
            continue
        for r in c["arms"].get("null_support", []):
            ns_total += 1
            if any(v != 0 for v in r["deficit"]):
                ns_events.append({"cell": key, "null_seed": r["null_seed"], "deficit": r["deficit"], "generator_degrees": r["generator_degrees"]})
    A["null_support_check"] = {"draws": ns_total, "nonzero_events": len(ns_events), "events": ns_events,
                               "rate": (len(ns_events) / ns_total) if ns_total else None,
                               "rate_ci95_exact": clopper_pearson(len(ns_events), ns_total) if ns_total else None,
                               "budget_rate": FD901A_BUDGET_RATE, "budget_reference": FD901A_OBSERVED,
                               "within_budget": (ns_total > 0 and len(ns_events) / ns_total < FD901A_BUDGET_RATE),
                               "all_exactly_zero": ns_total > 0 and not ns_events}
    dec = cells.get("s3-p4099")
    if dec and dec["status"] == "completed_valid":
        seeds_nonzero = [r["null_seed"] for r in dec["arms"].get("null_support", []) if any(v != 0 for v in r["deficit"])]
        A["stopping_rule_3"] = {"deciding_cell": "s3-p4099", "null_support_seeds_with_nonzero_deficit": seeds_nonzero,
                                "triggered": len(seeds_nonzero) > 1}
        sem_nonzero = [r for r in dec["arms"].get("semaev", []) if any(v != 0 for v in r["deficit"])]
        A["stopping_rule_4"] = {"deciding_cell": "s3-p4099", "sem_draws_with_nonzero_deficit": len(sem_nonzero),
                                "p_ladder_and_curve_spread_at_s3_required_first": len(sem_nonzero) > 0}

    # ---- deciding cell per arm ---------------------------------------------
    if dec and dec["status"] == "completed_valid":
        A["deciding_cell"] = {arm: {"D8_deficits": [r["deficit"][-1] for r in recs], "vectors": [r["deficit"] for r in recs],
                                    "rows_D8": sorted({r["rows"][-1] for r in recs}), "ncols_D8": sorted({r["ncols"][-1] for r in recs}),
                                    "rank_D8": sorted({r["rank"][-1] for r in recs}), "koszul_D8": sorted({r["koszul"][-1] for r in recs})}
                              for arm, recs in dec["arms"].items()}

    # ---- residuals at D = 8, affine fit in s, p-ladder, curve spread ------
    residual_points = []      # (s, residual) pooled over p and curves
    per_s: dict = {}
    per_sp: dict = {}
    topo_band: dict = {}
    for key, c in cells.items():
        if c["status"] != "completed_valid" or c["s"] not in S_MAIN or 8 not in c["degrees"]:
            continue
        i8 = c["degrees"].index(8)
        topo = [r["deficit"][i8] for r in c["arms"].get("null_topology", [])]
        supp = [r["deficit"][i8] for r in c["arms"].get("null_support", [])]
        if not topo:
            continue
        topo_ref = sorted(topo)[len(topo) // 2]   # median of the 5 seeds
        topo_band[key] = {"values": topo, "median": topo_ref, "min": min(topo), "max": max(topo), "support_values": supp}
        sems = [r for r in c["arms"].get("semaev", []) if r.get("valid", True)]
        res = [r["deficit"][i8] - topo_ref for r in sems]
        per_sp[key] = {"s": c["s"], "p": c["p"], "sem_D8": [r["deficit"][i8] for r in sems], "residuals": res,
                       "curve_seeds": [r["curve_seed"] for r in sems], "target_seeds": [r["target_seed"] for r in sems],
                       "curve_spread": (max(res) - min(res)) if res else None,
                       "max_abs_deviation_across_curves": (max(abs(x - sorted(res)[len(res) // 2]) for x in res)) if res else None,
                       "null_band_width": max(topo) - min(topo)}
        per_s.setdefault(c["s"], []).extend(res)
        residual_points.extend((c["s"], x) for x in res)
    A["residuals_D8"] = {"per_cell": per_sp, "topology_band": topo_band,
                         "per_s": {str(s): {"values": v, "min": min(v), "max": max(v), "integer_per_point": (v[0] if len(set(v)) == 1 else None)}
                                   for s, v in per_s.items()}}
    fit = ols(residual_points) if len({s for s, _ in residual_points}) >= 3 else None
    A["affine_fit_D8"] = fit if fit else {"note": "fewer than three s points with valid residuals; no fit"}

    # p-ladder at s = 4 (CTRL-P-LADDER) and s = 3 (if the stopping rule required it)
    ladder: dict = {}
    for s in S_MAIN:
        vals = {}
        for key, v in per_sp.items():
            if v["s"] == s:
                vals[str(v["p"])] = {"sem_D8": v["sem_D8"], "residuals": v["residuals"], "null_band": [topo_band[key]["min"], topo_band[key]["max"]]}
        if vals:
            allres = [x for v in vals.values() for x in v["residuals"]]
            ladder[str(s)] = {"per_p": vals, "p_spread_of_residuals": max(allres) - min(allres),
                              "p_independent_within_null_band": (max(allres) - min(allres)) <= max(topo_band[k]["max"] - topo_band[k]["min"] for k, v in per_sp.items() if v["s"] == s)}
    A["p_ladder"] = ladder

    # ---- constant-in-s deficits at D in {5, 6, 7} (P3) --------------------
    p3: dict = {}
    for key, c in cells.items():
        if c["status"] != "completed_valid" or c["s"] not in S_MAIN:
            continue
        for D in (5, 6, 7):
            if D in c["degrees"]:
                i = c["degrees"].index(D)
                p3.setdefault(str(D), {})[key] = sorted({r["deficit"][i] for r in c["arms"].get("semaev", []) if r.get("valid", True)})
    A["sem_deficits_D5_D7_distinct_values_per_cell"] = p3

    # ---- branch declaration by the pre-registered rule ---------------------
    have_all = all(f"s{s}-p{p}" in cells and cells[f"s{s}-p{p}"]["status"] == "completed_valid" for s in S_MAIN for p in (4099, 16411, 65537))
    branch = "unresolved"
    reasons = []
    if not have_all:
        reasons.append("not every main (s, p) cell is completed_valid")
    elif not A["null_support_check"]["within_budget"]:
        branch = "F2 (NULL-SUPPORT beyond budget; nothing else is read)"
    else:
        all_zero = (all(r == 0 for _, r in residual_points)
                    and all(all(v == 0 for v in vals) for D in p3.values() for vals in D.values()))
        topo_zero = all(b["min"] == 0 and b["max"] == 0 for b in topo_band.values())
        if all_zero:
            branch = "M1"
            reasons.append("every SEM residual at D = 8 is 0 and every SEM deficit at D in {5, 6, 7} is 0, at every s, p and curve; "
                           f"NULL-TOPOLOGY band {'is exactly 0' if topo_zero else 'is ' + str({k: [b['min'], b['max']] for k, b in topo_band.items()})}")
        elif fit and (fit["alpha_ci95"][0] > 0 or fit["alpha_ci95"][1] < 0):
            p_ok = all(v["p_independent_within_null_band"] for v in ladder.values())
            c_ok = all(v["curve_spread"] <= v["null_band_width"] for v in per_sp.values())
            branch = "M2" if (p_ok and c_ok) else "M3 (slope CI excludes 0 but residuals vary with p or curve)"
        else:
            branch = "M3 (nonzero residual with slope CI containing 0, or constant in s)"
    A["branch_declaration"] = {"branch": branch, "rule": "pre-registered (specification.preregistered_prediction / success_criterion)",
                               "reasons": reasons, "priors_for_the_record": {"M1": 0.75, "M2": 0.10, "constant_or_M3": 0.15}}

    # ---- tail checks -------------------------------------------------------
    tails: dict = {}
    worst = None
    for key, c in cells.items():
        if c["status"] != "completed_valid":
            continue
        for r in c["arms"].get("null_support", []):
            mx = max(abs(v) for v in r["deficit"])
            if worst is None or mx > worst["max_abs_deficit"]:
                worst = {"cell": key, "null_seed": r["null_seed"], "deficit": r["deficit"], "max_abs_deficit": mx,
                         "generator_degrees": r["generator_degrees"]}
    tails["T1_largest_null_support_deficit"] = {**(worst or {}), "budget": FD901A_OBSERVED, "within_budget": A["null_support_check"]["within_budget"]}
    tails["T2_max_sem_D8_deviation_across_curves_vs_null_band"] = {k: {"max_abs_deviation": v["max_abs_deviation_across_curves"], "null_band_width": v["null_band_width"],
                                                                     "inside_band": v["max_abs_deviation_across_curves"] <= v["null_band_width"]} for k, v in per_sp.items()}
    largest = {k: c for k, c in cells.items() if c["s"] == 5}
    tails["T3_largest_cell_s5_D8"] = {k: {"status": c["status"], "wall_seconds": c["wall_seconds"], "peak_rss_bytes": c["peak_rss_bytes"],
                                         "preflight_D8": {arm: recs[0]["peak_preflight"] for arm, recs in c["arms"].items() if recs},
                                         "sem_D8_deficits": [r["deficit"][-1] for r in c["arms"].get("semaev", [])]} for k, c in largest.items()}
    A["tail_checks"] = tails

    # ---- covariates --------------------------------------------------------
    A["covariates"] = {key: {arm: {"quotient_dims": [r["quotient_dim"] for r in recs], "sol": [r["sol"] for r in recs][:1],
                                   "sol_all_identical": len({str(r["sol"]) for r in recs}) == 1,
                                   "zero_product_rows_max": max(max(r["zero_product_rows"]) for r in recs)}
                             for arm, recs in c["arms"].items()} for key, c in cells.items() if c["status"] == "completed_valid"}
    A["null_generator_degrees"] = {key: {arm: sorted({str(r["generator_degrees"]) for r in recs}) for arm, recs in c["arms"].items() if arm.startswith("null")}
                                   for key, c in cells.items() if c["status"] == "completed_valid"}
    return A


def render(A: dict) -> str:
    L = [f"# {EXP_ID} -- Stage 5 analysis (observations only)", "",
         "Generated by `analyze.py` from `runs/*/raw-result.json`; every deficit below is recomputed as "
         "rows(D) - rank(Mac_D) - koszul(D) from the raw per-cell layer record and asserted equal to the run's own "
         "summary (`analysis.json` holds the full tables). This file reports measured values against the frozen "
         "criteria of the specification as OBSERVATIONS and declares the pre-registered branch by the frozen rule. "
         "It states no verdict on H-PFDR-9aadc0; that judgement belongs to the Reviewer and Coordinator.", "",
         "## Run status / censoring table", "", "| run | terminal status |", "|---|---|"]
    for rid, st in A["runs"].items():
        L.append(f"| {rid} | {st} |")
    if A.get("cells_missing"):
        L.append(f"\nPlanned cells without a run directory: {A['cells_missing']}")
    c = A.get("calibration")
    if c:
        L += ["", "## CTRL-BINARY-CALIBRATION (Stage 1, blocking)", "",
              f"Fixture sha256 matches the meter's committed fixture: {c['fixture_sha256_matches']}; status {c['status']}.", "",
              "| D | rows | rank | koszul (pairs + Frobenius) | deficit cumulative (rows - rank - koszul) | deficit graded (increment) |", "|---|---|---|---|---|---|"]
        for i, D in enumerate((2, 3, 4, 5)):
            L.append(f"| {D} | {c['rows'][i]} | {c['rank'][i]} | {c['koszul'][i]} | {c['deficit_cumulative_recomputed_D2_D5'][i]} | {c['deficit_graded_recomputed_D2_D5'][i]} |")
        L += ["", f"Frozen expectation: graded deficit(3) = 1, deficit(4) = 31, null 0 (KN-FIND-006; cumulative at D = 4 is 8k = 32).",
              f"Observed: deficit(3) = 1: **{c['D3_equals_1']}**; deficit(4) = 31: **{c['D4_equals_31']}**; cumulative D = 4 = 32: {c['cumulative_D4_equals_32_8k']}; "
              f"cumulative D = 5 = 1322 (archived RUN-DREG-001-VALIDATE-N12-A): {c['D5_cumulative_archived_1322']}.",
              f"Nulls (KN-FIND-006's DREG boolean_null with continued RNG, and histogram-matched at seeds 7, 11, 13, 17, 19): all zero: **{c['nulls_all_zero']}** "
              f"(DREG null cumulative {c['null_dreg_boolean_deficit_cumulative']}; histogram-matched {c['null_histogram_matched_deficit_cumulative']}).",
              f"Mixed-mode code path (unused u, Frobenius count on): deficit_pairwise D = 2..4 = {c['mixed_mode_code_path']['deficit_pairwise_D2_D4']} against the derived expectation "
              f"{c['mixed_mode_code_path']['derived_expectation']}: {c['mixed_mode_code_path']['matches']}.",
              f"Stage 0 mechanical checks (degree-4 parts, f^2 != f): {c['stage0_mechanical_checks_pass']}. Calibration reproduced: **{c['calibration_reproduced']}**."]
    s1 = A.get("s1_slice")
    if s1:
        L += ["", "## CTRL-S1-SLICE (Stage 2, blocking)", "", f"Symbolic identity with cb8e46's chained J at every (p, B): **{s1['symbolic_identity_all_cells']}** (status {s1['status']}).", "",
              "| cell | identity | generator degrees | cumulative rank D = 4..10 | cumulative deficit D = 4..10 | per-layer rank D = 4..10 | per-layer top rank |", "|---|---|---|---|---|---|---|"]
        for k, v in s1["per_cell"].items():
            L.append(f"| {k} | {v['identity']} | {v['generator_degrees']} | {v['cumulative_rank_D4_D10']} | {v['cumulative_deficit_recomputed_D4_D10']} | {v['per_layer_rank_D4_D10']} | {v['per_layer_top_rank_D4_D10']} |")
        L.append("\nThese graded ranks are recorded as the frozen fixture (CTRL-S1-SLICE forced disposition); no prime-field chained instrument exists to compare against.")
    L += ["", "## Stage 3 / 4 cells: deficit tables per arm", "",
          "deficit(D) = rows(D) - rank(Mac_D) - koszul(D), cumulative multipliers; one entry per draw; `[min, max]` over draws.", ""]
    for arm, cellsd in A.get("deficit_tables", {}).items():
        L += [f"### {arm}", "", "| cell | D | n | values | min | max |", "|---|---|---|---|---|---|"]
        for key, byD in cellsd.items():
            for D, v in byD.items():
                L.append(f"| {key} | {D} | {v['n']} | {v['values']} | {v['min']} | {v['max']} |")
        L.append("")
    ns = A["null_support_check"]
    L += ["## NULL-SUPPORT against the small-p budget (P1, blocking)", "",
          f"Draws: {ns['draws']}; nonzero-deficit events: {ns['nonzero_events']}; rate {ns['rate']}; exact 95% CI {ns['rate_ci95_exact']}; "
          f"budget: EXP-PFDR-fd901a criterion (4), rate below {ns['budget_rate']} per draw (observed there {ns['budget_reference']}). "
          f"Within budget: **{ns['within_budget']}**; all exactly zero: **{ns['all_exactly_zero']}**."]
    if ns["events"]:
        L.append(f"Events: {ns['events']}")
    if "stopping_rule_3" in A:
        L += ["", f"Stopping rule 3 at the deciding cell: null seeds with nonzero deficit {A['stopping_rule_3']['null_support_seeds_with_nonzero_deficit']}; triggered: **{A['stopping_rule_3']['triggered']}**.",
              f"Stopping rule 4 (SEM nonzero at the deciding cell -> p-ladder and curve spread at s = 3 first): SEM draws with nonzero deficit {A['stopping_rule_4']['sem_draws_with_nonzero_deficit']}; "
              f"required: {A['stopping_rule_4']['p_ladder_and_curve_spread_at_s3_required_first']} (the s = 3 cells at all three primes were run before s = 4 in any case)."]
    if "deciding_cell" in A:
        L += ["", "## Deciding cell (s = 3, p = 4099, D = 8) per arm", "", "| arm | rows | ncols | rank | koszul | deficit(8) per draw |", "|---|---|---|---|---|---|"]
        for arm, v in A["deciding_cell"].items():
            L.append(f"| {arm} | {v['rows_D8']} | {v['ncols_D8']} | {v['rank_D8']} | {v['koszul_D8']} | {v['D8_deficits']} |")
    R = A.get("residuals_D8", {})
    L += ["", "## P4: residual deficit(8) on SEM minus deficit(8) on NULL-TOPOLOGY, per (s, p)", "",
          "| cell | SEM deficit(8) per curve | topology null values (5 seeds) | residuals | curve spread | null band width |", "|---|---|---|---|---|---|"]
    for k, v in R.get("per_cell", {}).items():
        b = R["topology_band"][k]
        L.append(f"| {k} | {v['sem_D8']} | {b['values']} | {v['residuals']} | {v['curve_spread']} | {v['null_band_width']} |")
    L += ["", f"Per s (pooled over p and curves): {R.get('per_s')}", "",
          f"Affine fit of the residual against s in {{3, 4, 5}} (OLS over all (s, residual) observations): {A.get('affine_fit_D8')}", "",
          "## CTRL-P-LADDER / CTRL-CURVE-SPREAD (Stage 4)", ""]
    for s, v in A.get("p_ladder", {}).items():
        L.append(f"- s = {s}: residuals per p {{p: residuals}} = { {p: w['residuals'] for p, w in v['per_p'].items()} }; p-spread {v['p_spread_of_residuals']}; p-independent within the null band: {v['p_independent_within_null_band']}")
    L += ["", f"P3: distinct SEM deficit values at D in {{5, 6, 7}} per cell: {A.get('sem_deficits_D5_D7_distinct_values_per_cell')}", "",
          "## Branch declaration (pre-registered rule; declared, not interpreted)", "",
          f"**{A['branch_declaration']['branch']}** -- {A['branch_declaration']['reasons']}", "",
          "## Tail checks", ""]
    for k, v in A.get("tail_checks", {}).items():
        L.append(f"- {k}: {json.dumps(v, default=str)}")
    L += ["", "## Covariates (not claims)", "",
          f"- quotient dimensions and sol(D) per arm and cell: see analysis.json `covariates`; sol(D) was False at every recorded (cell, arm, D) unless listed here: "
          f"{[(k, a) for k, arms in A.get('covariates', {}).items() for a, v in arms.items() if v['sol'] and any(v['sol'][0].values())] or 'none'}",
          f"- realised null generator degrees per cell and arm: {A.get('null_generator_degrees')}",
          f"- zero-product rows dropped by the cumulative convention: max over draws per cell/arm = "
          f"{ {k: {a: v['zero_product_rows_max'] for a, v in arms.items()} for k, arms in A.get('covariates', {}).items()} }",
          "", "## CTRL-CONFOUNDERS-NAMED", "",
          "(i) the CRT / complete-splitting degeneracy of IDEA-20260830-cb8e46 is inherited by the twin at every s (the quotient dimensions above are the point counts); "
          "a nonzero deficit here would be a generator-level fact, never an ideal invariant. (ii) No Groebner degree is read; sol(D) is a covariate. "
          "(iii) The multilinear reduction a^2 -> a is not homogeneous; the degree convention is the meter's cumulative convention, frozen and identical across arms and to the calibration arm. "
          "(iv) Two generators: deficits at D <= 8 concern multipliers of degree <= 4 only; nothing at D > 8 is measured or claimed."]
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stop-check-only", action="store_true")
    args = ap.parse_args()
    runs = load_runs()
    A = analyse(runs)
    if args.stop_check_only:
        print(json.dumps({"stopping_rule_3": A.get("stopping_rule_3"), "stopping_rule_4": A.get("stopping_rule_4"),
                          "null_support_check": {k: v for k, v in A["null_support_check"].items() if k != "events"}}, indent=2))
        return 0
    with open(os.path.join(HERE, "analysis.json"), "w") as fh:
        json.dump(A, fh, indent=2, sort_keys=True, default=str)
    with open(os.path.join(HERE, "analysis.md"), "w") as fh:
        fh.write(render(A))
    print(json.dumps(A["branch_declaration"], indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
