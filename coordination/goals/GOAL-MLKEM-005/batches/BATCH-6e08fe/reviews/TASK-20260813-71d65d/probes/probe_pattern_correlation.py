#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TASK-20260813-71d65d (Validator) -- probe_pattern_correlation.py

Uses ONLY already-committed data from the lead's own
results_route_reimpl.json (read directly, not imported as a module) to test
whether the hkz D_route' disagreement pattern correlates with beta/dimension
(a reduction-quality-confound signature) or looks like a fixed, dimension-
independent offset (which would be closer to what a code-sharing or fixed
numerical-bug artifact would look like). NO NEW REDUCTION; NO NEW COMPUTATION
of any lattice quantity -- this is a pure re-analysis of numbers the lead
already computed and committed.

CLAIM TIER: TOY.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def find_repo_root(start):
    cur = start
    for _ in range(20):
        if os.path.isdir(os.path.join(cur, ".git")):
            return cur
        cur = os.path.dirname(cur)
    raise SystemExit("no repo root")


REPO_ROOT = find_repo_root(HERE)
LEAD_RESULTS = os.path.join(
    REPO_ROOT, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/"
    "tasks/TASK-20260813-ea2e96/results_route_reimpl.json")

LATTICE_D = {"L7": 20, "L9": 30, "L11": 40}


def main():
    with open(LEAD_RESULTS) as fh:
        d = json.load(fh)
    pc = d["R_IV_OUT_2_per_cell"]

    out = {"probe": "probe_pattern_correlation.py",
           "source": "coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/"
                      "tasks/TASK-20260813-ea2e96/results_route_reimpl.json "
                      "(committed at 6ad64048d), read directly -- not imported "
                      "as a module, no producer code executed.",
           "cells": []}

    for key, v in pc.items():
        if not key.startswith("hkz") or v.get("status") != "COMPUTED":
            continue
        lat = key.split("/")[1].split("_")[0]
        beta = int(key.split("_b")[1])
        dd = LATTICE_D[lat]
        signs = []
        for m in v["matched_bases_detail"]:
            if m["route_i_prime"] < m["route_p"]:
                signs.append(1)   # route_i (LLL) MORE NEGATIVE than route_p
            elif m["route_i_prime"] > m["route_p"]:
                signs.append(-1)
            else:
                signs.append(0)
        n_more_neg = sum(1 for s in signs if s > 0)
        n_less_neg = sum(1 for s in signs if s < 0)
        out["cells"].append({
            "cell": key, "lattice": lat, "d": dd, "beta": beta,
            "beta_over_d": round(beta / dd, 3),
            "D_route_prime": v["D_route_prime"],
            "n_bases_route_i_MORE_negative_than_route_p": n_more_neg,
            "n_bases_route_i_LESS_negative_than_route_p": n_less_neg,
            "sign_consistency_fraction": max(n_more_neg, n_less_neg) / len(signs),
        })

    # dimension-scaling check at matched beta/d ratio
    beta_lo_cells = sorted([c for c in out["cells"] if c["beta"] == {
        "L7": 5, "L9": 7, "L11": 10}.get(c["lattice"])],
        key=lambda c: c["d"])
    beta_hi_cells = sorted([c for c in out["cells"] if c["beta"] == {
        "L7": 15, "L9": 22, "L11": 30}.get(c["lattice"])],
        key=lambda c: c["d"])
    out["dimension_scaling_beta_lo_endpoint"] = [
        {"d": c["d"], "D_route_prime": c["D_route_prime"]} for c in beta_lo_cells]
    out["dimension_scaling_beta_hi_endpoint"] = [
        {"d": c["d"], "D_route_prime": c["D_route_prime"]} for c in beta_hi_cells]

    # beta-window-size check within each lattice (does D_route shrink as the
    # averaging window widens at FIXED dimension?)
    per_lat = {}
    for c in out["cells"]:
        per_lat.setdefault(c["lattice"], []).append(c)
    out["beta_window_size_effect_within_lattice"] = {
        lat: sorted([{"beta": c["beta"], "D_route_prime": c["D_route_prime"]}
                    for c in cells], key=lambda x: x["beta"])
        for lat, cells in per_lat.items()}

    # overall sign consistency across all 48 basis-comparisons (6 cells x 8 bases)
    total_bases = sum(len(v["matched_bases_detail"])
                      for k, v in pc.items()
                      if k.startswith("hkz") and v.get("status") == "COMPUTED")
    total_more_neg = sum(c["n_bases_route_i_MORE_negative_than_route_p"]
                         for c in out["cells"])
    out["overall_sign_consistency"] = {
        "total_basis_comparisons": total_bases,
        "n_route_i_more_negative": total_more_neg,
        "n_route_i_less_negative_or_tied": total_bases - total_more_neg,
        "fraction_one_directional": total_more_neg / total_bases,
    }

    outpath = os.path.join(HERE, "probe_pattern_correlation_output.json")
    with open(outpath, "w") as fh:
        json.dump(out, fh, indent=1)
    print("wrote", outpath)
    print(json.dumps(out["dimension_scaling_beta_lo_endpoint"]))
    print(json.dumps(out["dimension_scaling_beta_hi_endpoint"]))
    print(json.dumps(out["overall_sign_consistency"]))


if __name__ == "__main__":
    main()
