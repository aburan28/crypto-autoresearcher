#!/usr/bin/env python3
"""Driver for EXP-MONO-2a13d7: Stage 0 (enumeration + pre-registration),
Stage 1 (exhaustive dual-check), Stage 3 (matched-pair + controls).

Usage: python3 run_experiment.py <run_dir>

Pure Python 3 stdlib only (json, os, sys, time, platform, hashlib,
resource, csv, math -- no third-party import anywhere). Fully
deterministic / seed-free, per the frozen contract.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import platform
import resource
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fp_common import legendre  # noqa: E402
from stage0 import (  # noqa: E402
    enumerate_curves, group_by_tz, matched_pair_census,
    closed_form_seven_tuple,
)
from stage1 import classify_panel_curve  # noqa: E402

PRIMES = [101, 211]
SIBLING_PAIRS = [(1, 1), (2, 3), (4, 1)]


def now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def peak_rss_mb():
    ru = resource.getrusage(resource.RUSAGE_SELF)
    # ru_maxrss is KB on Linux, bytes on macOS (Darwin).
    if sys.platform == "darwin":
        return ru.ru_maxrss / (1024 * 1024)
    return ru.ru_maxrss / 1024


def write_csv(path, header, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def is_special(A, B, p):
    """j = 0 (A=0) or j = 1728 (B=0) -- excluded from Stage-1 PANEL
    SELECTION (curve_panel_note), not from Stage-0 enumeration."""
    return A == 0 or B == 0


def select_panel(p, table, cells, out_dir, timings):
    """Stage 0 steps 3-6: matched-pair census, panel selection,
    pre-registration transcript construction (the actual pre-registration
    WRITE happens per-curve in run_stage1_for_panel, strictly before that
    curve's base-point enumeration)."""

    # Sibling curves (verified non-singular, per curve_panel_committed_from_sibling).
    sibling_curves = []
    for (A, B) in SIBLING_PAIRS:
        rec = table.get((A, B))
        if rec is None:
            raise RuntimeError(
                f"sibling curve (A={A},B={B}) at p={p} failed disc_check "
                "(singular) -- infrastructure_error, construction failure"
            )
        sibling_curves.append((A, B, rec))

    sibling_z_covered = {rec["Z"] for (_, _, rec) in sibling_curves}

    # Step 5: Z-coverage curves -- lexicographically smallest (A,B) in the
    # FULL table with each uncovered Z value (any t).
    z_coverage_curves = []
    for Z_target in (0, 1, 3):
        if Z_target in sibling_z_covered:
            continue
        best = None
        for (A, B) in sorted(table.keys()):
            if is_special(A, B, p):
                # j=0/1728 curves are excluded from Stage-1 PANEL SELECTION
                # entirely (`curve_panel_note`), not merely from the
                # matched-pair role -- so Z-coverage selection skips them too.
                continue
            if table[(A, B)]["Z"] == Z_target:
                best = (A, B, table[(A, B)])
                break
        if best is not None:
            z_coverage_curves.append((best[0], best[1], best[2], Z_target))

    z_coverage_ab = {(A, B) for (A, B, _, _) in z_coverage_curves}
    sibling_ab = {(A, B) for (A, B, _) in sibling_curves}
    preferred_ab = z_coverage_ab | sibling_ab

    # Step 3+4: exhaustive pairwise isomorphism census over every (t,Z)
    # cell, with streaming (memory-bounded) tracking of the
    # lexicographically smallest qualifying matched-pair candidate,
    # overall and among those touching a preferred (sibling/Z-coverage)
    # curve. See stage0.matched_pair_census's docstring for the memory
    # deviation this streaming approach fixes (an earlier version
    # materialized ~14.7M pair tuples at p=211 and breached the 1GB budget).
    t0 = time.perf_counter()
    census, non_iso_pairs_total, best_overall, best_preferred = matched_pair_census(
        p, cells, table, preferred_ab
    )
    timings["stage0_matched_pair_census_seconds"] = time.perf_counter() - t0

    matched_pair = best_preferred if best_preferred is not None else best_overall

    matched_pair_curve_recs = []
    if matched_pair is not None:
        A1v, B1v, A2v, B2v, t_cell, Z_cell = matched_pair
        matched_pair_curve_recs = [
            (A1v, B1v, table[(A1v, B1v)]),
            (A2v, B2v, table[(A2v, B2v)]),
        ]

    # Panel = union of sibling, Z-coverage, matched-pair curves.
    panel = {}
    transcript = []
    for (A, B, rec) in sibling_curves:
        panel[(A, B)] = rec
        transcript.append({"A": A, "B": B, "role": "sibling", "t": rec["t"], "Z": rec["Z"]})
    for (A, B, rec, Zt) in z_coverage_curves:
        if (A, B) not in panel:
            transcript.append({"A": A, "B": B, "role": f"z_coverage(Z={Zt})", "t": rec["t"], "Z": rec["Z"]})
        else:
            transcript.append({"A": A, "B": B, "role": f"z_coverage(Z={Zt})[also sibling]", "t": rec["t"], "Z": rec["Z"]})
        panel[(A, B)] = rec
    for (A, B, rec) in matched_pair_curve_recs:
        role = "matched_pair"
        if (A, B) in panel:
            role += "[also selected above]"
        transcript.append({"A": A, "B": B, "role": role, "t": rec["t"], "Z": rec["Z"]})
        panel[(A, B)] = rec

    # Tail checks.
    sparsest_matched_cell = None
    if matched_pair is not None:
        t_cell, Z_cell = matched_pair[4], matched_pair[5]
        sparsest_matched_cell = {
            "t": t_cell, "Z": Z_cell,
            "curve_count": len(cells[(t_cell, Z_cell)]),
        }
    z_raw_counts = {0: 0, 1: 0, 2: 0, 3: 0}
    for rec in table.values():
        z_raw_counts[rec["Z"]] = z_raw_counts.get(rec["Z"], 0) + 1
    z_tail = {z: z_raw_counts.get(z, 0) for z in (0, 1, 3)}

    result = {
        "census": census,
        "non_iso_pairs_total": non_iso_pairs_total,
        "sibling_curves": [(A, B) for (A, B, _) in sibling_curves],
        "z_coverage_curves": [(A, B, Zt) for (A, B, _, Zt) in z_coverage_curves],
        "matched_pair": matched_pair,
        "panel": panel,
        "panel_transcript": transcript,
        "sparsest_matched_cell": sparsest_matched_cell,
        "z_tail_counts": z_tail,
        "instrument_outcome_no_matched_pair": matched_pair is None,
    }
    return result


def preregister_and_run_stage1(p, panel, out_dir, prereg_records, stage1_logs, timings):
    """Emit the pre-registered closed-form table for each panel curve
    STRICTLY BEFORE that curve's Stage-1 base-point enumeration, per-curve
    (not batched), and then run Stage 1 for that curve. Returns dict
    (A,B) -> {tallies, seven_tuple_measured, closed_form, residuals}."""
    results = {}
    for (A, B) in sorted(panel.keys()):
        rec = panel[(A, B)]
        t, Z = rec["t"], rec["Z"]

        # --- PRE-REGISTRATION (must happen before enumeration below) ---
        cf = closed_form_seven_tuple(p, t, Z)
        prereg_entry = {
            "p": p, "A": A, "B": B, "t": t, "Z": Z,
            "preregistered_at": now_iso(),
            "closed_form": cf,
            "ordering_marker": "PRE_ENUMERATION",
        }
        prereg_records.append(prereg_entry)
        # -----------------------------------------------------------------

        t0 = time.perf_counter()
        tallies, log = classify_panel_curve(p, A, B, log_rows=True)
        elapsed = time.perf_counter() - t0
        timings.setdefault("stage1_per_curve_seconds", {})[f"{A},{B}"] = elapsed

        stage1_logs[(A, B)] = log

        residuals = {
            "A1_identity": tallies["A1_identity"] - cf["A1_identity"],
            "A2_sigma_i": tallies["A2_sigma_i"] - cf["A2_sigma_i"],
            "A3_sigma1sigma2": tallies["A3_sigma1sigma2"] - cf["A3_sigma1sigma2"],
            "A4_ramified_A": tallies["A4_ramified_A"] - cf["A4_ramified_A"],
            "B1_block_swap": tallies["B1_block_swap"] - cf["B1_block_swap"],
            "B2_ramified_B": tallies["B2_ramified_B"] - cf["B2_ramified_B"],
            "B3_four_cycle": tallies["B3_four_cycle"] - cf["B3_four_cycle"],
        }

        sum_a = (tallies["A1_identity"] + tallies["A2_sigma_i"]
                 + tallies["A3_sigma1sigma2"] + tallies["A4_ramified_A"])
        sum_b = (tallies["B1_block_swap"] + tallies["B2_ramified_B"]
                 + tallies["B3_four_cycle"])
        r3 = {
            "case_A_sum": sum_a, "case_A_expected": p * (p - 1) // 2,
            "case_A_ok": sum_a == p * (p - 1) // 2,
            "case_B_sum": sum_b, "case_B_expected": p * (p - 1) // 2,
            "case_B_ok": sum_b == p * (p - 1) // 2,
            "double_root_count": tallies["double_root"], "double_root_expected": p,
            "double_root_ok": tallies["double_root"] == p,
        }

        results[(A, B)] = {
            "t": t, "Z": Z, "j": rec["j"], "order3_count": rec["order3_count"],
            "tallies": tallies, "closed_form": cf, "residuals": residuals,
            "r3": r3, "prereg_timestamp": prereg_entry["preregistered_at"],
        }
    return results


def baseline_reproduction_check(p, sibling_ab, stage1_results):
    """S^2+N^2-(p-Z) from measured (A1)+(A3), against KN-FIND-a8990a's
    Theorem B closed form (H-MONO-0f9170 proof_search_map.baseline_embedding).
    Measured value = 2*(A1_measured + A3_measured) (see implementation.md
    for the unordered-to-ordered derivation)."""
    out = []
    for (A, B) in sibling_ab:
        r = stage1_results[(A, B)]
        t, Z = r["t"], r["Z"]
        S = (p - t - Z) // 2
        N = (p + t - Z) // 2
        closed_form_value = ((p - Z) ** 2 + t * t) // 2 - (p - Z)
        measured_value = 2 * (r["tallies"]["A1_identity"] + r["tallies"]["A3_sigma1sigma2"])
        out.append({
            "A": A, "B": B, "t": t, "Z": Z, "S": S, "N": N,
            "closed_form_S2_N2_minus_pZ": closed_form_value,
            "measured_2x_A1_plus_A3": measured_value,
            "agree_exactly": closed_form_value == measured_value,
        })
    return out


def run_one_prime(p, run_dir):
    timings = {}
    t_start = time.perf_counter()

    t0 = time.perf_counter()
    table = enumerate_curves(p)
    timings["stage0_enumeration_seconds"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    cells = group_by_tz(table)
    timings["stage0_grouping_seconds"] = time.perf_counter() - t0

    anomalies = [
        {"A": A, "B": B, "anomaly_count": rec["anomaly_count"]}
        for (A, B), rec in table.items() if rec["anomaly_count"] > 0
    ]

    panel_sel = select_panel(p, table, cells, run_dir, timings)

    prereg_records = []
    stage1_logs = {}
    t0 = time.perf_counter()
    stage1_results = preregister_and_run_stage1(
        p, panel_sel["panel"], run_dir, prereg_records, stage1_logs, timings
    )
    timings["stage1_total_seconds"] = time.perf_counter() - t0

    sibling_ab = set(panel_sel["sibling_curves"])
    baseline = baseline_reproduction_check(p, sibling_ab, stage1_results)

    # Matched-pair equality test (R2) + non-vacuity control.
    matched_pair_report = None
    mp = panel_sel["matched_pair"]
    if mp is not None:
        A1v, B1v, A2v, B2v, t_cell, Z_cell = mp
        r1 = stage1_results[(A1v, B1v)]
        r2 = stage1_results[(A2v, B2v)]
        strata = ["A1_identity", "A2_sigma_i", "A3_sigma1sigma2", "A4_ramified_A",
                  "B1_block_swap", "B2_ramified_B", "B3_four_cycle"]
        diffs = {s: r1["tallies"][s] - r2["tallies"][s] for s in strata}
        j_differs = r1["j"] != r2["j"]
        order3_differs = r1["order3_count"] != r2["order3_count"]
        non_vacuous = j_differs or order3_differs
        matched_pair_report = {
            "curve1": {"A": A1v, "B": B1v, "j": r1["j"], "order3_count": r1["order3_count"]},
            "curve2": {"A": A2v, "B": B2v, "j": r2["j"], "order3_count": r2["order3_count"]},
            "t": t_cell, "Z": Z_cell,
            "seven_tuple_diffs": diffs,
            "all_seven_equal": all(v == 0 for v in diffs.values()),
            "non_vacuity_control": {
                "j_differs": j_differs, "order3_count_differs": order3_differs,
                "passes": non_vacuous,
            },
        }

    timings["prime_total_seconds"] = time.perf_counter() - t_start

    return {
        "p": p,
        "table": table,
        "cells": cells,
        "anomalies": anomalies,
        "panel_selection": panel_sel,
        "stage1_results": stage1_results,
        "baseline_reproduction": baseline,
        "matched_pair_report": matched_pair_report,
        "prereg_records": prereg_records,
        "stage1_logs": stage1_logs,
        "timings": timings,
        "curve_count": len(table),
    }


def write_artifacts(run_dir, all_results):
    os.makedirs(run_dir, exist_ok=True)
    for p_res in all_results:
        p = p_res["p"]
        pdir = os.path.join(run_dir, f"p{p}")
        os.makedirs(pdir, exist_ok=True)

        # Curve-invariant table (full, not summarized).
        rows = []
        for (A, B), rec in sorted(p_res["table"].items()):
            rows.append([A, B, rec["t"], rec["Z"], rec["j"],
                         rec["order3_count"], rec["anomaly_count"], rec["disc"]])
        write_csv(os.path.join(pdir, "curve_invariant_table.csv"),
                  ["A", "B", "t", "Z", "j", "order3_count", "anomaly_count", "disc"],
                  rows)

        # Matched-pair census.
        census_out = {
            f"t={t},Z={Z}": v for (t, Z), v in p_res["panel_selection"]["census"].items()
        }
        with open(os.path.join(pdir, "matched_pair_census.json"), "w") as f:
            json.dump({
                "cells_with_ge2_curves": census_out,
                "non_iso_pairs_total": p_res["panel_selection"]["non_iso_pairs_total"],
                "matched_pair_selected": p_res["panel_selection"]["matched_pair"],
                "instrument_outcome_no_matched_pair":
                    p_res["panel_selection"]["instrument_outcome_no_matched_pair"],
                "sparsest_matched_cell": p_res["panel_selection"]["sparsest_matched_cell"],
                "z_tail_counts": p_res["panel_selection"]["z_tail_counts"],
            }, f, indent=2)

        # Panel selection transcript.
        with open(os.path.join(pdir, "panel_selection_transcript.json"), "w") as f:
            json.dump(p_res["panel_selection"]["panel_transcript"], f, indent=2)

        # Curve construction transcript (p, A, B, disc_check) per panel curve.
        constr = []
        for (A, B), rec in sorted(p_res["panel_selection"]["panel"].items()):
            constr.append({"p": p, "A": A, "B": B, "disc": rec["disc"],
                            "non_singular": rec["disc"] != 0})
        with open(os.path.join(pdir, "curve_construction_transcript.json"), "w") as f:
            json.dump(constr, f, indent=2)

        # Pre-registered closed-form table (with ordering marker).
        with open(os.path.join(pdir, "preregistration.json"), "w") as f:
            json.dump(p_res["prereg_records"], f, indent=2)

        # Per-base-point classification log per panel curve.
        for (A, B), log in p_res["stage1_logs"].items():
            fname = os.path.join(pdir, f"stage1_log_A{A}_B{B}.csv")
            write_csv(fname, ["e1", "e2", "D", "chi_D", "stratum", "char1", "char2"], log)

        # Seven-count tables + residuals + R3 per panel curve.
        seven_count = {}
        for (A, B), r in p_res["stage1_results"].items():
            seven_count[f"A={A},B={B}"] = {
                "t": r["t"], "Z": r["Z"], "j": r["j"], "order3_count": r["order3_count"],
                "measured": r["tallies"], "closed_form": r["closed_form"],
                "residuals": r["residuals"], "r3": r["r3"],
            }
        with open(os.path.join(pdir, "seven_count_tables.json"), "w") as f:
            json.dump(seven_count, f, indent=2)

        # Matched-pair equality report.
        with open(os.path.join(pdir, "matched_pair_equality_report.json"), "w") as f:
            json.dump(p_res["matched_pair_report"], f, indent=2)

        # Baseline reproduction.
        with open(os.path.join(pdir, "baseline_reproduction.json"), "w") as f:
            json.dump(p_res["baseline_reproduction"], f, indent=2)

        # Anomalies (order-3 root coinciding with 2-torsion).
        with open(os.path.join(pdir, "anomalies.json"), "w") as f:
            json.dump(p_res["anomalies"], f, indent=2)

        # Timings.
        with open(os.path.join(pdir, "timings.json"), "w") as f:
            json.dump(p_res["timings"], f, indent=2)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def main():
    run_dir = sys.argv[1]
    os.makedirs(run_dir, exist_ok=True)

    wall_start = time.perf_counter()
    all_results = []
    for p in PRIMES:
        all_results.append(run_one_prime(p, run_dir))
    wall_elapsed = time.perf_counter() - wall_start

    write_artifacts(run_dir, all_results)

    summary = {
        "primes": PRIMES,
        "wall_clock_seconds_total": wall_elapsed,
        "peak_rss_mb": peak_rss_mb(),
        "sqrt_method": "general_tonelli_shanks_unconditional",
        "per_prime": [],
    }
    for r in all_results:
        p = r["p"]
        r3_all_ok = all(
            v["r3"]["case_A_ok"] and v["r3"]["case_B_ok"] and v["r3"]["double_root_ok"]
            for v in r["stage1_results"].values()
        )
        r1_all_zero = all(
            all(res == 0 for res in v["residuals"].values())
            for v in r["stage1_results"].values()
        )
        baseline_all_ok = all(b["agree_exactly"] for b in r["baseline_reproduction"])
        mp_report = r["matched_pair_report"]
        summary["per_prime"].append({
            "p": p,
            "curve_count": r["curve_count"],
            "timings": r["timings"],
            "r1_all_residuals_zero": r1_all_zero,
            "r3_all_sum_checks_ok": r3_all_ok,
            "baseline_reproduction_all_ok": baseline_all_ok,
            "matched_pair_found": mp_report is not None,
            "matched_pair_all_seven_equal": (mp_report or {}).get("all_seven_equal"),
            "matched_pair_non_vacuity_passes":
                (mp_report or {}).get("non_vacuity_control", {}).get("passes"),
            "anomaly_count_total": sum(a["anomaly_count"] for a in r["anomalies"]),
            "z_tail_counts": r["panel_selection"]["z_tail_counts"],
            "sparsest_matched_cell": r["panel_selection"]["sparsest_matched_cell"],
        })

    with open(os.path.join(run_dir, "raw-result.json"), "w") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
