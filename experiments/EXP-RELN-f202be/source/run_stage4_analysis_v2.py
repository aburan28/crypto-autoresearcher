#!/usr/bin/env python3
"""Stage 4 re-analysis under protocol amendment v1
(experiments/EXP-RELN-f202be/amendments/v1.yaml, version_to 2,
DEC-20260907-432a39): applies the AMENDED forced_negation_gap_trap_control
tolerance

    |measured - expected| <= max(0.1, 3*(m/B_1)*(B_1^3/(4M)))   m = 3

per cell (in place of the frozen v1 fixed absolute 0.1), everywhere the
tolerance is evaluated -- reading directly from each rung's own recorded
forced_negation_gap_measured / forced_negation_gap_expected / B values in
curve_results.json, not from the old accounting.json boolean (which recorded
only the OLD tolerance's verdict).

Consumes RUN-RELN-f202be-N14v2 and RUN-RELN-f202be-N16v2 (full re-execution
of stages 2-3 for the two affected rungs, same deterministic seeds, path (a)
of the amendment's reanalysis_authorization -- see those runs' manifests and
the bit-for-bit reproducibility check recorded in
reanalysis-provenance.json) for rungs 14 and 16, and the EXISTING, UNEDITED
RUN-RELN-f202be-N18 / RUN-RELN-f202be-N20 for rungs 18 and 20 (the amendment
states the new tolerance is inert there; this script recomputes that claim
from the recorded data rather than asserting it).

All other statistics (Delta bootstrap CIs, NULL-A bands, growth fit, k-rich,
predicate lifts, other controls) are computed by the SAME unmodified
analysis.py functions used by run_stage4_analysis.py; only the
forced-negation-gap tolerance formula differs. Diff against
run_stage4_analysis.py to confirm the only substantive change is the
tolerance formula and the per-rung source-directory mapping.

Writes RUN-RELN-f202be-stage4v2.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import analysis as an
import runutil as ru

RUNS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "runs"))
STAGE0_DIR = os.path.join(RUNS_DIR, "RUN-RELN-f202be-stage0")
STAGE1_DIR = os.path.join(RUNS_DIR, "RUN-RELN-f202be-stage1")
RUN_ID = "RUN-RELN-f202be-stage4v2"
RUN_DIR = os.path.join(RUNS_DIR, RUN_ID)

# Amendment v1 (version_to 2), change G1: rungs 14/16 read from the NEW
# re-analysis run directories (full re-execution, path (a)); rungs 18/20 read
# from the EXISTING, UNEDITED run directories (no re-execution -- the
# amendment's reanalysis_authorization does not require or permit touching
# those two rungs' data, only re-evaluating the tolerance against it).
RUNG_SOURCE_DIR = {
    14: "RUN-RELN-f202be-N14v2",
    16: "RUN-RELN-f202be-N16v2",
    18: "RUN-RELN-f202be-N18",
    20: "RUN-RELN-f202be-N20",
}

ALL_RUNGS = [14, 16, 18, 20]
OBJECT_ARMS = ["x_interval_low", "x_interval_mid", "qr_class"]
K_RANGE = list(range(1, 9))
HOLM_ALPHA = 0.05
PREDICATE_IDS = ["P1", "P2", "P3", "P4", "P5", "P6", "P7"]
PREDICATE_SIGMA = {"P1": 0.5, "P2": 0.25, "P3": 0.5, "P4": 0.5, "P5": 0.5, "P6": 0.125, "P7": 0.125,
                   "ANCHOR-LOG": 0.125}

AMENDMENT_M = 3  # fixed arity, unchanged by the amendment


def load_json(path):
    with open(path) as f:
        return json.load(f)


def rung_run_dir(rung):
    return os.path.join(RUNS_DIR, RUNG_SOURCE_DIR[rung])


def amended_tolerance(B: float, forced_gap_expected: float) -> float:
    """max(0.1, 3*(m/B)*(B_1^3/(4M))) -- amendment v1 change G1. B and
    forced_gap_expected (= B_1^3/(4M), the cell's own recorded leading-order
    forced value) are read per cell from the already-measured record; m=3 is
    the contract's frozen arity."""
    return max(0.1, 3.0 * (AMENDMENT_M / B) * forced_gap_expected)


def available_rungs():
    out = []
    for k in ALL_RUNGS:
        d = rung_run_dir(k)
        cr = os.path.join(d, "curve_results.json")
        man = os.path.join(d, "manifest.json")
        if os.path.exists(cr) and os.path.exists(man):
            manifest = load_json(man)
            if manifest["run"].get("status") == "completed_valid":
                out.append(k)
    return out


def main():
    t_start = time.time()
    os.makedirs(RUN_DIR, exist_ok=True)
    log_lines = []

    def log(msg):
        print(msg)
        log_lines.append(msg)

    log(f"stage4v2 (amended forced-gap tolerance, amendment v1 / DEC-20260907-432a39) start {ru.now_iso()}")
    rungs_done = available_rungs()
    missing = [k for k in ALL_RUNGS if k not in rungs_done]
    log(f"rungs available (completed_valid stage2/3, per-rung source dir): "
        f"{ {k: RUNG_SOURCE_DIR[k] for k in rungs_done} }")
    log(f"rungs missing/not_run/partial: {missing}")

    curve_results_by_rung = {k: load_json(os.path.join(rung_run_dir(k), "curve_results.json"))
                              for k in rungs_done}

    bands = {}
    metrics = {"per_rung": {}}
    predicate_lifts = {}

    # ---- per-rung, per-arm, per-B-conv: object-cell deltas, NULL-A band, verdicts
    # (identical computation to run_stage4_analysis.py; the amendment does not
    # touch Delta, the NULL-A band, or the growth fit)
    growth_series = {arm: {"logN": [], "log_excess": [], "rungs": []} for arm in OBJECT_ARMS}

    for k in rungs_done:
        cr = curve_results_by_rung[k]
        metrics["per_rung"][k] = {}
        for arm in OBJECT_ARMS:
            arm_key = f"{arm}_B1"
            per_curve_delta = []
            per_curve_z = []
            in_band_flags = []
            null_band_ref = None
            for seed, rec in cr.items():
                oa = rec["object_arms"].get(arm_key)
                na = rec["NULL_A"].get("B1")
                if oa is None or na is None:
                    continue
                delta_red = oa["delta_reduced"]
                band = na["band_reduced"]
                null_band_ref = band
                z = an.z_delta(delta_red, band)
                per_curve_delta.append(delta_red)
                per_curve_z.append(z)
                in_band_flags.append(an.in_band(delta_red, band))
            if not per_curve_delta:
                continue
            ci = an.bootstrap_ci(per_curve_delta, n_boot=2000, seed=k)
            excess = [max(d - null_band_ref["mean"], null_band_ref["sd"] if null_band_ref["sd"] > 0 else 1e-12)
                      for d in per_curve_delta]
            mean_excess = sum(excess) / len(excess)
            N_example = list(cr.values())[0]["N"]
            growth_series[arm]["logN"].append(math.log(N_example))
            growth_series[arm]["log_excess"].append(math.log(mean_excess))
            growth_series[arm]["rungs"].append(k)
            verdict = {
                "arm": arm, "B_conv": "B1", "rung": k,
                "per_curve_delta_reduced": per_curve_delta,
                "per_curve_z_vs_NULL_A": per_curve_z,
                "in_band_all_curves": all(in_band_flags),
                "bootstrap_ci_delta": ci,
                "null_a_band_reduced": null_band_ref,
            }
            metrics["per_rung"][k][arm_key] = verdict
            log(f"rung{k} {arm_key}: deltas={['%.4f'%d for d in per_curve_delta]} "
                f"z={['%.2f'%z if z is not None else None for z in per_curve_z]} "
                f"in_band_all={verdict['in_band_all_curves']}")

    # ---- growth fit per object geometry (B1, reduced) -- unchanged computation
    growth_fits = {}
    for arm in OBJECT_ARMS:
        gs = growth_series[arm]
        fit = an.growth_fit(gs["logN"], gs["log_excess"], seed=hash(arm) % (2**31))
        fit["rungs_used"] = gs["rungs"]
        growth_fits[arm] = fit
        log(f"growth_fit {arm}: {fit}")
    metrics["growth_fits"] = growth_fits

    # ---- k-rich / Chebyshev / predicate lifts (object arms, B1, from stored T_S sums)
    # -- unchanged computation
    for k in rungs_done:
        cr = curve_results_by_rung[k]
        predicate_lifts[k] = {}
        for arm in OBJECT_ARMS:
            arm_key = f"{arm}_B1"
            predicate_lifts[k][arm_key] = {}
            for seed, rec in cr.items():
                oa = rec["object_arms"].get(arm_key)
                if oa is None:
                    continue
                Mred = oa["M_red"]
                T = oa["predicate_T_S_reduced"]
                pvals = []
                zs = {}
                for pid in PREDICATE_IDS:
                    sigma = PREDICATE_SIGMA[pid]
                    T_S = T.get(pid, 0)
                    rho = T_S / (sigma * Mred) if sigma * Mred != 0 else None
                    z = an.z_analytic(rho, sigma, Mred) if rho is not None else None
                    p = an.two_sided_pvalue_from_z(z) if z is not None else 1.0
                    zs[pid] = {"rho": rho, "z_analytic_null": z, "p": p}
                    pvals.append(p)
                holm = an.holm_correction(pvals, alpha=HOLM_ALPHA)
                for i, pid in enumerate(PREDICATE_IDS):
                    zs[pid]["holm_adjusted_p"] = holm["adjusted_pvalues"][i]
                    zs[pid]["holm_reject_at_0.05"] = holm["reject"][i]
                T_anchor = T.get("ANCHOR-LOG", 0)
                sigma_a = PREDICATE_SIGMA["ANCHOR-LOG"]
                rho_a = T_anchor / (sigma_a * Mred) if sigma_a * Mred != 0 else None
                zs["ANCHOR-LOG"] = {"rho": rho_a, "note": "unrealizable anchor, sensitivity check only"}
                predicate_lifts[k][arm_key][seed] = zs
                max_holm_z_reject = any(zs[pid]["holm_reject_at_0.05"] for pid in PREDICATE_IDS)
                log(f"rung{k} seed{seed} {arm_key} predicate max|z| holm-reject any: {max_holm_z_reject}")

    # ---- control verdicts consolidation ----
    # ZN_interval / bose_chowla / q_decay: NOT touched by the amendment, reused
    # unchanged from stage1 (frozen, common to all rungs).
    control_summary = {}
    stage1_accounting = load_json(os.path.join(STAGE1_DIR, "accounting.json"))["rows"]
    for row in stage1_accounting:
        if row.get("cell") == "ZN_interval":
            control_summary.setdefault("ZN_interval", []).append(row)
        if row.get("cell") == "bose_chowla":
            control_summary.setdefault("bose_chowla", []).append(row)
        if row.get("cell") == "q_decay_ladder":
            control_summary.setdefault("q_decay_ladder", []).append(row)

    all_controls_pass = True
    for row in control_summary.get("ZN_interval", []):
        if not row.get("pass_threshold", False) or not row.get("INV1_ok", False) or not row.get("INV2_ok", False):
            all_controls_pass = False
    for row in control_summary.get("bose_chowla", []):
        if row.get("skipped"):
            continue
        if not row.get("E3_equals_M2", False):
            all_controls_pass = False
    for row in control_summary.get("q_decay_ladder", []):
        if not row.get("monotone_decreasing", False):
            all_controls_pass = False

    # ---- forced-negation-gap trap control: AMENDED tolerance ----
    # Recomputed directly from each rung's own recorded
    # forced_negation_gap_measured / forced_negation_gap_expected / B per
    # object cell, per curve -- for ALL FOUR rungs, not just 14/16 -- so the
    # amendment's claim that the new formula is inert at 18/20 is verified
    # here by computation, not merely asserted.
    forced_gap_cells = []
    forced_gap_failures = []
    forced_gap_rungs_failed = set()
    inv1_inv2_failures = []
    for k in rungs_done:
        cr = curve_results_by_rung[k]
        for seed, rec in cr.items():
            for cell_key, oa in rec["object_arms"].items():
                B = oa["B"]
                measured = oa["forced_negation_gap_measured"]
                expected = oa["forced_negation_gap_expected"]
                old_tol_pass = oa["forced_gap_within_0.1"]  # frozen v1 tolerance, unedited
                tol = amended_tolerance(B, expected)
                new_pass = abs(measured - expected) <= tol
                abs_dev = abs(measured - expected)
                rel_dev = abs_dev / expected if expected else None
                cell_row = {
                    "rung": k, "seed": seed, "cell": cell_key, "B": B,
                    "forced_negation_gap_measured": measured,
                    "forced_negation_gap_expected": expected,
                    "abs_deviation": abs_dev,
                    "relative_deviation": rel_dev,
                    "old_absolute_tolerance_0.1_pass": old_tol_pass,
                    "amended_tolerance_value": tol,
                    "amended_tolerance_pass": new_pass,
                    "INV1_ok": oa["INV1_ok"], "INV2_ok": oa["INV2_ok"],
                }
                forced_gap_cells.append(cell_row)
                if not new_pass:
                    forced_gap_failures.append(cell_row)
                    forced_gap_rungs_failed.add(k)
                if not (oa["INV1_ok"] and oa["INV2_ok"]):
                    inv1_inv2_failures.append(cell_row)
    forced_gap_control_pass = len(forced_gap_failures) == 0
    inv1_inv2_all_pass = len(inv1_inv2_failures) == 0
    if not forced_gap_control_pass or not inv1_inv2_all_pass:
        all_controls_pass = False

    log(f"forced_negation_gap_control_pass (AMENDED tolerance): {forced_gap_control_pass} "
        f"({len(forced_gap_failures)} of {len(forced_gap_cells)} cells fail, "
        f"rungs {sorted(forced_gap_rungs_failed)})")
    log(f"INV1/INV2 all pass across all recomputed cells: {inv1_inv2_all_pass} "
        f"({len(inv1_inv2_failures)} failures)")

    # per-rung worst-case summary (mirrors the amendment's validation table,
    # recomputed here rather than copied from the amendment text)
    per_rung_worst = {}
    for k in rungs_done:
        rows_k = [r for r in forced_gap_cells if r["rung"] == k]
        worst = max(rows_k, key=lambda r: r["relative_deviation"] or 0.0)
        per_rung_worst[k] = {
            "B": worst["B"],
            "worst_abs_deviation": worst["abs_deviation"],
            "worst_relative_deviation": worst["relative_deviation"],
            "amended_relative_tolerance_at_worst_cell": 3.0 * (AMENDMENT_M / worst["B"]),
            "amended_tolerance_value_at_worst_cell": worst["amended_tolerance_value"],
            "old_tolerance_pass_at_worst_cell": worst["old_absolute_tolerance_0.1_pass"],
            "amended_tolerance_pass_at_worst_cell": worst["amended_tolerance_pass"],
            "n_cells_failing_amended_at_this_rung": sum(1 for r in rows_k if not r["amended_tolerance_pass"]),
            "n_cells_total_at_this_rung": len(rows_k),
        }
        log(f"rung{k} worst forced-gap cell: {per_rung_worst[k]}")

    ru.write_json(os.path.join(RUN_DIR, "bands.json"), {"per_rung": metrics["per_rung"]})
    ru.write_json(os.path.join(RUN_DIR, "metrics.json"), metrics)
    ru.write_json(os.path.join(RUN_DIR, "predicate-lifts.json"), predicate_lifts)
    ru.write_json(os.path.join(RUN_DIR, "control-verdicts.json"), {
        "amendment": "experiments/EXP-RELN-f202be/amendments/v1.yaml (version_to 2), DEC-20260907-432a39",
        "tolerance_formula": "max(0.1, 3*(m/B_1)*(B_1^3/(4M))), m=3, per cell from that cell's own B and forced_negation_gap_expected",
        "all_blocking_controls_pass": all_controls_pass,
        "forced_negation_gap_control_pass": forced_gap_control_pass,
        "forced_negation_gap_n_cells_checked": len(forced_gap_cells),
        "forced_negation_gap_n_cells_failing": len(forced_gap_failures),
        "forced_negation_gap_failures": forced_gap_failures,
        "forced_negation_gap_rungs_failed": sorted(forced_gap_rungs_failed),
        "forced_negation_gap_per_rung_worst_cell": per_rung_worst,
        "forced_negation_gap_all_cells": forced_gap_cells,
        "inv1_inv2_all_pass": inv1_inv2_all_pass,
        "inv1_inv2_failures": inv1_inv2_failures,
        "detail": {
            k: v for k, v in control_summary.items()
        }
    })

    # ---- mechanical classification (success_criterion / falsification_criterion
    # UNCHANGED by the amendment -- same logic as run_stage4_analysis.py) ----
    complete_run_set = (len(rungs_done) == 4)
    all_in_band = True
    for k in rungs_done:
        for arm_key, verdict in metrics["per_rung"][k].items():
            if not verdict["in_band_all_curves"]:
                all_in_band = False

    slope_status = {}
    for arm in OBJECT_ARMS:
        gf = growth_fits[arm]
        if gf.get("insufficient_rungs"):
            slope_status[arm] = "insufficient_rungs"
        elif gf.get("contains_zero"):
            slope_status[arm] = "contains_zero"
        elif gf["slope"] > 0 and gf["lo"] is not None and gf["lo"] > 0:
            slope_status[arm] = "excludes_zero_positive"
        elif gf["slope"] < 0 and gf["hi"] is not None and gf["hi"] < 0:
            slope_status[arm] = "excludes_zero_negative"
        else:
            slope_status[arm] = "excludes_zero_ambiguous_sign"
    slopes_all_contain_zero = all(v == "contains_zero" for v in slope_status.values())

    two_largest = [r for r in [18, 20] if r in rungs_done]
    alive_geometries = []
    if len(two_largest) == 2:
        for arm in OBJECT_ARMS:
            ok = True
            for r in two_largest:
                verdict = metrics["per_rung"].get(r, {}).get(f"{arm}_B1")
                if verdict is None:
                    ok = False
                    break
                zs = verdict["per_curve_z_vs_NULL_A"]
                if not all((z is not None and z > 3.0) for z in zs):
                    ok = False
                    break
            if ok and slope_status[arm] == "excludes_zero_positive":
                alive_geometries.append(arm)

    if not complete_run_set:
        classification = "INCOMPLETE_NO_CLASSIFICATION"
        reason = f"rungs missing/not completed: {missing}; success_criterion requires all four rungs."
    elif not all_controls_pass:
        classification = "INSTRUMENT_FAILURE_NO_VERDICT"
        reason = (
            "A blocking control still fails even under the amended forced-negation-gap tolerance "
            f"and/or the recomputed INV1/INV2 accounting: forced_gap_control_pass="
            f"{forced_gap_control_pass} ({len(forced_gap_failures)}/{len(forced_gap_cells)} cells), "
            f"inv1_inv2_all_pass={inv1_inv2_all_pass} ({len(inv1_inv2_failures)} failures). "
            "See control-verdicts.json for the exact cells."
        )
    elif all_in_band and slopes_all_contain_zero:
        classification = "NULL_OUTCOME"
        reason = ("every object cell inside NULL-A band at every rung on every curve; "
                   "growth slope intervals contain 0 for every object geometry")
    elif alive_geometries:
        classification = "ALIVE_OUTCOME_CANDIDATE"
        reason = (f"geometries meeting the literal competing-outcome test (z>3 SD on every "
                  f"curve at rungs {two_largest} AND slope excludes 0 positive): {alive_geometries}")
    elif all_in_band and not slopes_all_contain_zero:
        classification = "UNANTICIPATED_PATTERN_NOT_NULL_NOT_ALIVE"
        reason = (
            "Every object cell (x_interval_low/mid, qr_class; reduced, B1) is inside the "
            "NULL-A band (mean +/- 3 SD) at every rung on every curve -- the Delta "
            "band-inclusion part of the pre-committed NULL outcome holds. But the growth-fit "
            "slope of log(max(Delta - Delta_null_mean, SD_null)) vs log(N) does NOT contain 0 "
            "for one or more of the three object geometries; measured slopes are "
            f"{ {arm: growth_fits[arm]['slope'] for arm in OBJECT_ARMS} }. This is neither the "
            "pre-committed NULL outcome (which requires the slope interval to contain 0) nor the "
            "competing ALIVE outcome (z>3 SD on every curve at the two largest rungs, increasing "
            "with N -- not observed here). Reported as an unanticipated observation for "
            "Coordinator/reviewer characterization, not resolved by this Executor report."
        )
    else:
        classification = "INCONCLUSIVE"
        reason = f"mixed signal across geometries/rungs; per-geometry slope status: {slope_status}"

    result = {
        "slope_status_per_geometry": slope_status,
        "alive_geometries_meeting_literal_test": alive_geometries,
        "complete_run_set": complete_run_set,
        "rungs_completed": rungs_done,
        "rungs_missing": missing,
        "all_blocking_controls_pass": all_controls_pass,
        "all_object_cells_in_null_a_band": all_in_band,
        "growth_slope_contains_zero_all_geometries": slopes_all_contain_zero,
        "mechanical_classification": classification,
        "classification_reason": reason,
    }
    ru.write_json(os.path.join(RUN_DIR, "classification.json"), result)
    log(f"CLASSIFICATION: {classification} -- {reason}")

    manifest = {
        "run": {
            "id": RUN_ID, "experiment_id": "EXP-RELN-f202be", "stage": "stage4_analysis_amended_v2",
            "status": "completed_valid" if rungs_done else "not_run",
            "amendment_applied": "experiments/EXP-RELN-f202be/amendments/v1.yaml (version_to 2)",
            "decision": "DEC-20260907-432a39",
            "rung_source_directories": {k: RUNG_SOURCE_DIR[k] for k in rungs_done},
            "code": {"commit": ru.git_commit(), "dirty": ru.git_dirty(),
                     "command": "python3 source/run_stage4_analysis_v2.py"},
            "environment": ru.environment_info(),
            "timing": {"started_at_epoch": t_start, "finished_at_epoch": time.time(),
                       "wall_seconds": time.time() - t_start},
            "rungs_completed": rungs_done, "rungs_missing": missing,
        }
    }
    ru.write_json(os.path.join(RUN_DIR, "manifest.json"), manifest)
    with open(os.path.join(RUN_DIR, "command.txt"), "w") as f:
        f.write("python3 source/run_stage4_analysis_v2.py\n")
    with open(os.path.join(RUN_DIR, "environment.json"), "w") as f:
        json.dump(ru.environment_info(), f, indent=2)
    with open(os.path.join(RUN_DIR, "stdout.log"), "w") as f:
        f.write("\n".join(log_lines))
    with open(os.path.join(RUN_DIR, "stderr.log"), "w") as f:
        f.write("")
    log(f"stage4v2 done, wall={time.time()-t_start:.2f}s")


if __name__ == "__main__":
    main()
