#!/usr/bin/env python3
"""Main driver for EXP-MONO-4c7479 Stage 0 + Stage 1.

Usage: python3 run_experiment.py <master_seed> <output_dir>

Pure Python 3 standard library only (sys, os, json, time, hashlib,
subprocess, platform, resource). No sympy/sage/numpy/g6k/fpylll anywhere
in this module or any module it imports.
"""
from __future__ import annotations

import json
import os
import sys
import time
import platform
import subprocess
import resource
from collections import Counter

import fp_common as fc
import arm_a
import arm_b
import recipe
import polymod as pm
import ordered_base_control
import random_quartic_control as rqc
import stage0 as stage0_mod

CURVE_PANEL = [
    {"p": 101, "A": 1, "B": 1},
    {"p": 101, "A": 2, "B": 3},
    {"p": 101, "A": 4, "B": 1},
    {"p": 211, "A": 1, "B": 1},
    {"p": 211, "A": 2, "B": 3},
    {"p": 211, "A": 4, "B": 1},
]

FIVE_CLASSES = ["identity", "sigma_i", "sigma1_sigma2", "block_swap_involution", "four_cycle"]
FORCED_DENSITY = {
    "identity": 1 / 8,
    "sigma_i": 1 / 4,
    "sigma1_sigma2": 1 / 8,
    "block_swap_involution": 1 / 4,
    "four_cycle": 1 / 4,
}
S4_FORCED_DENSITY = {"1^4": 1 / 24, "2.1.1": 1 / 4, "2^2": 1 / 8, "3+1": 1 / 3, "4": 1 / 4}


def verify_nonsingular(p, A, B):
    disc4 = (4 * pow(A, 3, p) + 27 * pow(B, 2, p)) % p
    return disc4 != 0, disc4


def count_f_roots(p, A, B):
    roots = [x for x in range(p) if (x ** 3 + A * x + B) % p == 0]
    return roots


def binomial_se(n, prob):
    return (n * prob * (1 - prob)) ** 0.5


def process_cell(p, A, B, fp2, fp4):
    stratum_counts = {"i": 0, "ii": 0, "iii": 0}
    stratum_ii_regime_counts = Counter()
    class_counts = Counter()
    perms_seen = set()
    perms_seen_split = set()
    perms_seen_inert = set()
    p1_disagree = 0
    p1_compared = 0
    p3_agree = 0
    p3_total = 0
    rows = []
    split_t_pairs = []
    fb_sublocus_total = 0
    fb_sublocus_identity = 0
    overlap_i_iii = 0
    overlap_ii_iii = 0

    for e1 in range(p):
        for e2 in range(p):
            ra = arm_a.classify_point(p, A, B, e1, e2, fp2, fp4)
            rb = arm_b.classify_point(p, A, B, e1, e2)
            is_iii = rb["stratum_iii"]
            if is_iii:
                stratum_counts["iii"] += 1

            if ra["stratum"] == "i":
                stratum_counts["i"] += 1
                if is_iii:
                    overlap_i_iii += 1
                rows.append({
                    "e1": e1, "e2": e2, "regime": ra["regime"], "stratum": "i",
                    "predicted_class": None, "arm_a_class": None, "arm_b_label": rb["label"],
                    "agree_recipe": None, "agree_arms": None,
                    "chi_D": None, "chi_f1": None, "chi_f2": None, "chi_c0": None,
                })
                continue

            if ra["stratum"] == "ii":
                stratum_counts["ii"] += 1
                stratum_ii_regime_counts[ra["regime"]] += 1
                if is_iii:
                    overlap_ii_iii += 1
                rows.append({
                    "e1": e1, "e2": e2, "regime": ra["regime"], "stratum": "ii",
                    "predicted_class": None, "arm_a_class": None, "arm_b_label": rb["label"],
                    "agree_recipe": None, "agree_arms": None,
                    "chi_D": None, "chi_f1": None, "chi_f2": None, "chi_c0": None,
                })
                continue

            arm_a_class = ra["class"]
            arm_a_shape = arm_b.CLASS_TO_SHAPE[arm_a_class]
            arm_b_label = rb["label"]
            class_counts[arm_a_class] += 1
            perms_seen.add(ra["perm"])
            D = (e1 * e1 - 4 * e2) % p
            chi_D = fc.legendre(D, p)

            if ra["regime"] == "split":
                perms_seen_split.add(ra["perm"])
                chi_f1 = fc.legendre(ra["f1"], p)
                chi_f2 = fc.legendre(ra["f2"], p)
                predicted = recipe.predict_split(ra["f1"], ra["f2"], p)
                chi_c0 = None
                split_t_pairs.append((ra["t1"], ra["t2"]))
                if chi_f1 == 1 and chi_f2 == 1:
                    fb_sublocus_total += 1
                    if arm_a_class == "identity":
                        fb_sublocus_identity += 1
            else:
                perms_seen_inert.add(ra["perm"])
                chi_f1 = None
                chi_f2 = None
                chi_c0 = fc.legendre(rb["c0"], p)
                predicted = recipe.predict_inert(rb["c0"], p)

            agree_recipe = predicted == arm_a_class
            p3_total += 1
            if agree_recipe:
                p3_agree += 1

            if not is_iii:
                p1_compared += 1
                agree_arms = arm_a_shape == arm_b_label
                if not agree_arms:
                    p1_disagree += 1
            else:
                agree_arms = None

            rows.append({
                "e1": e1, "e2": e2, "regime": ra["regime"], "stratum": "iii" if is_iii else "none",
                "predicted_class": predicted, "arm_a_class": arm_a_class, "arm_b_label": arm_b_label,
                "agree_recipe": agree_recipe, "agree_arms": agree_arms,
                "chi_D": chi_D, "chi_f1": chi_f1, "chi_f2": chi_f2, "chi_c0": chi_c0,
            })

    n = p * p
    density_report = {}
    for c in FIVE_CLASSES:
        observed = class_counts.get(c, 0)
        forced = FORCED_DENSITY[c]
        expected_count = n * forced
        se = binomial_se(n, forced)
        density_report[c] = {
            "observed_count": observed,
            "observed_density": observed / n,
            "forced_density": forced,
            "expected_count": expected_count,
            "binomial_se_count": se,
            "deviation_in_se": (observed - expected_count) / se if se > 0 else None,
            "within_3_se": abs(observed - expected_count) <= 3 * se,
        }

    ordered_ctrl = ordered_base_control.run(p, A, B, split_t_pairs, fp2, fp4)

    fb_sublocus = {
        "n_in_sublocus": fb_sublocus_total,
        "n_identity_in_sublocus": fb_sublocus_identity,
        "pct_identity": (fb_sublocus_identity / fb_sublocus_total * 100.0) if fb_sublocus_total else None,
        "declared_non_discriminating": True,
    }

    f_roots = count_f_roots(p, A, B)

    return {
        "p": p, "A": A, "B": B,
        "n_base_points": n,
        "stratum_counts": stratum_counts,
        "stratum_ii_regime_counts": dict(stratum_ii_regime_counts),
        "stratum_ii_f_root_count": len(f_roots),
        "stratum_ii_f_roots": f_roots,
        "overlap_i_and_iii": overlap_i_iii,
        "overlap_ii_and_iii": overlap_ii_iii,
        "P1_disagreement_count": p1_disagree,
        "P1_compared_count": p1_compared,
        "P1_forced": 0,
        "P2_distinct_permutations": len(perms_seen),
        "P2_forced": 8,
        "P2_distinct_permutations_split_regime": len(perms_seen_split),
        "P2_distinct_permutations_inert_regime": len(perms_seen_inert),
        "P2_split_inert_partition_disjoint": len(perms_seen_split & perms_seen_inert) == 0,
        "heur_wreath_2_check": {
            "note": "Declared interpretation (see implementation.md): realized-class "
                    "partition between the split-regime (F_p-rational t-values) and "
                    "inert-regime (genuinely F_{p^2} t-values) subpopulations of the "
                    "same F_p-base census, not a separate exhaustive F_{p^2}-base "
                    "census (infeasible within budget; not costed in the contract's "
                    "own cost_note).",
            "split_regime_perms": sorted(perms_seen_split),
            "inert_regime_perms": sorted(perms_seen_inert),
            "disjoint_as_expected": len(perms_seen_split & perms_seen_inert) == 0,
            "union_size": len(perms_seen_split | perms_seen_inert),
        },
        "P3_agreement_count": p3_agree,
        "P3_total": p3_total,
        "P3_ratio": (p3_agree / p3_total) if p3_total else None,
        "P3_forced": 1.0,
        "class_density_report": density_report,
        "matched_ordered_base_control": ordered_ctrl,
        "factor_base_sublocus_control": fb_sublocus,
        "rows": rows,
    }


def git_info(repo_root):
    def run(cmd):
        return subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True).stdout.strip()

    commit = run(["git", "rev-parse", "HEAD"])
    status = run(["git", "status", "--porcelain"])
    dirty = bool(status)
    return {"commit": commit, "dirty": dirty, "dirty_file_count": len(status.splitlines()) if dirty else 0}


def main():
    master_seed = sys.argv[1]
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    log_dir = os.path.join(out_dir, "per_base_point_log")
    os.makedirs(log_dir, exist_ok=True)
    rq_dir = os.path.join(out_dir, "random_quartic_control")
    os.makedirs(rq_dir, exist_ok=True)

    t_start = time.time()

    stage0_result = stage0_mod.run_stage0()
    with open(os.path.join(out_dir, "stage0_transcript.json"), "w") as fh:
        json.dump(stage0_result, fh, indent=2)

    if not stage0_result["all_pass"]:
        with open(os.path.join(out_dir, "raw-result.json"), "w") as fh:
            json.dump({"stage0": stage0_result, "stage1_executed": False,
                       "reason": "stage0 identity failure; stage 1 not run"}, fh, indent=2)
        print("STAGE 0 FAILED -- halting before Stage 1 compute.")
        return

    fp2_cache = {}
    fp4_cache = {}

    def get_fp2_fp4(p):
        if p not in fp2_cache:
            fp2_cache[p] = fc.Fp2(p)
            fp4_cache[p] = fc.Fp4(fp2_cache[p])
        return fp2_cache[p], fp4_cache[p]

    curve_transcript = []
    cell_summaries = []

    for cell in CURVE_PANEL:
        p, A, B = cell["p"], cell["A"], cell["B"]
        ok, disc4 = verify_nonsingular(p, A, B)
        curve_transcript.append({"p": p, "A": A, "B": B, "disc4_mod_p": disc4, "nonsingular": ok})
        if not ok:
            raise RuntimeError(f"FAILED_INFRASTRUCTURE: curve (p={p},A={A},B={B}) is singular "
                                f"(4A^3+27B^2 = 0 mod p) -- construction check failed.")
        fp2, fp4 = get_fp2_fp4(p)
        t0 = time.time()
        result = process_cell(p, A, B, fp2, fp4)
        elapsed = time.time() - t0
        result["wall_seconds"] = elapsed

        rows = result.pop("rows")
        log_path = os.path.join(log_dir, f"p{p}_A{A}_B{B}.ndjson")
        with open(log_path, "w") as fh:
            for row in rows:
                fh.write(json.dumps(row, sort_keys=True))
                fh.write("\n")
        result["per_base_point_log_path"] = os.path.relpath(log_path, out_dir)
        result["per_base_point_log_row_count"] = len(rows)
        cell_summaries.append(result)
        print(f"cell p={p} A={A} B={B}: P1={result['P1_disagreement_count']} "
              f"P2={result['P2_distinct_permutations']} P3={result['P3_ratio']} "
              f"({elapsed:.2f}s)")

    # Random-quartic null control, once per prime, per run (domain suffix
    # keys the two replication runs to genuinely different draws).
    domain_suffix = f"run-{master_seed}"
    rq_results = {}
    for p in sorted(set(c["p"] for c in CURVE_PANEL)):
        t0 = time.time()
        rq = rqc.run(p, domain_suffix, n_draws=2000)
        rq["wall_seconds"] = time.time() - t0
        rq_path = os.path.join(rq_dir, f"p{p}.json")
        with open(rq_path, "w") as fh:
            json.dump(rq, fh, indent=2)
        density_check = {}
        for label, forced in S4_FORCED_DENSITY.items():
            observed = rq["histogram"].get(label, 0)
            expected = rq["n_accepted"] * forced
            se = binomial_se(rq["n_accepted"], forced)
            density_check[label] = {
                "observed_count": observed,
                "expected_count": expected,
                "binomial_se_count": se,
                "within_3_se": abs(observed - expected) <= 3 * se,
            }
        rq_results[p] = {
            "n_accepted": rq["n_accepted"],
            "n_squarefree_discards": rq["n_squarefree_discards"],
            "histogram": rq["histogram"],
            "density_check": density_check,
            "emits_3plus1": rq["histogram"].get("3+1", 0) > 0,
            "raw_log_path": os.path.relpath(rq_path, out_dir),
            "wall_seconds": rq["wall_seconds"],
        }
        print(f"random-quartic control p={p}: histogram={rq['histogram']} "
              f"({rq_results[p]['wall_seconds']:.2f}s)")

    total_elapsed = time.time() - t_start

    with open(os.path.join(out_dir, "curve_construction_transcript.json"), "w") as fh:
        json.dump(curve_transcript, fh, indent=2)

    raw_result = {
        "master_seed": master_seed,
        "stage0": stage0_result,
        "stage1_executed": True,
        "curve_construction_transcript": curve_transcript,
        "cells": cell_summaries,
        "random_quartic_control": rq_results,
        "total_wall_seconds": total_elapsed,
        "peak_rss_bytes": (
            resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
            if platform.system() == "Linux"
            else resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        ),
    }
    with open(os.path.join(out_dir, "raw-result.json"), "w") as fh:
        json.dump(raw_result, fh, indent=2)

    print(f"TOTAL WALL TIME: {total_elapsed:.2f}s")
    print(f"PEAK RSS bytes: {raw_result['peak_rss_bytes']}")


if __name__ == "__main__":
    main()
