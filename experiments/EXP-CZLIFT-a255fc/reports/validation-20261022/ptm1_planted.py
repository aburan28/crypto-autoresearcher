#!/usr/bin/env python3
"""PTM-1 proves-too-much control for TASK-20261022-3aca4b (EXP-CZLIFT-a255fc).

Object: a planted point set of N DISTINCT residues of E(F_p) (maximal spreading, the
opposite of uniform random reduction), fed to the producer's coverage-ratio instrument
(implementation/run.py: model_distinct, curve_order_mod_p, summarize -- imported, not
copied, so the instrument under test is exactly the one that produced the receipts).

Known-false conclusion: "any point set covers E(F_p) at the uniform-reduction rate".
Expected failure signature (review plan): ratio > 1.2 at small N/N_p; a ratio near 1
means the instrument cannot see excess coverage.

Parts
  A. concrete planted sets on 37a1 at p = 1009 (explicit E(F_p) points) over N/N_p;
  B. the planted (maximally spread) set and a clustered set placed on EXACTLY the frozen
     cells (same N, N_p) of both runs, summarized by the producer's summarize();
  C. a seeded uniform-random null object on the same cells (the instrument's null
     distribution), for calibration of A/B;
  D. the analytic ceiling: for any point set, ratio <= min(N, N_p) / model(N, N_p).

Usage: python3 -I ptm1_planted.py <repo-root>   (seed fixed below)
"""
import json
import math
import statistics
import sys

ROOT = sys.argv[1]
sys.path.insert(0, ROOT + "/experiments/EXP-CZLIFT-a255fc/implementation")
sys.path.insert(0, ROOT)
import numpy as np  # noqa: E402
import run as instrument  # noqa: E402  (producer's driver: the instrument under test)

SEED = 20261022
NULL_REPS = 200
EXP = ROOT + "/experiments/EXP-CZLIFT-a255fc"


def ratio_ceiling(x):
    """Planted max-spread ratio in the N, N_p -> infinity limit at x = N / N_p."""
    return min(x, 1.0) / (1.0 - math.exp(-x))


def solve(target, lo, hi):
    for _ in range(200):
        mid = (lo + hi) / 2
        if ratio_ceiling(mid) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def fake_curve(label, rows):
    return {"label": label, "coverage": rows, "growth_slope": None, "growth_slope_predicted": None,
            "rank_recalled": 0, "h_half": {}, "twists": []}


def main():
    out = {"seed": SEED, "null_reps": NULL_REPS}
    # ---------------- A: explicit planted sets on 37a1 at p = 1009 ----------------
    ai = [0, 0, 1, -1, 0]
    p = 1009
    Np = instrument.curve_order_mod_p(ai, p)
    pts = ["O"]
    for x in range(p):
        for y in range(p):
            if (y * y + y - (x ** 3 - x)) % p == 0:
                pts.append((x, y))
    assert len(pts) == Np
    rowsA = []
    for frac in (0.01, 0.03, 0.05, 0.1, 0.2, 0.3, 0.375, 0.5, 0.75, 0.874, 0.9, 1.0):
        N = max(1, round(frac * Np))
        planted = set(pts[:N])                       # N distinct residues
        m = instrument.model_distinct(Np, N)
        rowsA.append({"N": N, "N_over_Np": N / Np, "distinct": len(planted), "model": m,
                      "ratio": len(planted) / m,
                      "passes_frozen_cell_filter": N >= 30 and m <= 0.9 * Np})
    out["A_37a1_p1009"] = {"N_p": Np, "rows": rowsA}

    # ---------------- B/C: frozen cells of both runs ----------------
    rng = np.random.default_rng(SEED)
    for run in ("RUN-CZLIFT-74f172", "RUN-CZLIFT-490b33"):
        raw = json.load(open(f"{EXP}/runs/{run}/raw-result.json"))
        cells = [(cv["label"], c) for cv in raw["raw"]["curves"] for c in cv["coverage"]
                 if c["n_points"] >= 30 and c["model_distinct"] <= 0.9 * c["N_p"]]
        rec = raw["metrics"]

        def summarize_with(distinct_fn):
            by = {}
            for lab, c in cells:
                N, Np_ = c["n_points"], c["N_p"]
                d = distinct_fn(lab, c)
                m = instrument.model_distinct(Np_, N)
                by.setdefault(lab, []).append({"p": c["p"], "H": c["H"], "N_p": Np_, "n_points": N,
                                               "distinct": d, "model_distinct": m,
                                               "coverage": d / Np_, "ratio_to_model": d / m})
            s = instrument.summarize([fake_curve(k, v) for k, v in by.items()])
            return {k: s[k] for k in ("coverage_cells", "coverage_ratio_median",
                                      "coverage_ratio_frac_above_1p5", "coverage_ratio_frac_below_0p5")}

        planted = summarize_with(lambda lab, c: min(c["n_points"], c["N_p"]))
        clustered = summarize_with(lambda lab, c: 2)   # every point on one residue, plus O
        observed = {k: rec[k] for k in ("coverage_cells", "coverage_ratio_median",
                                        "coverage_ratio_frac_above_1p5", "coverage_ratio_frac_below_0p5")}
        # how many frozen cells could EVER show ratio > 1.2 / > 1.5, whatever the points
        ceil = [min(c["n_points"], c["N_p"]) / instrument.model_distinct(c["N_p"], c["n_points"]) for _, c in cells]
        # cells where the observed set is already maximally spread (distinct == min(N, N_p))
        maxspread = sum(1 for _, c in cells if c["distinct"] == min(c["n_points"], c["N_p"]))
        maxspread_by_curve = {}
        for lab, c in cells:
            t = maxspread_by_curve.setdefault(lab, [0, 0])
            t[1] += 1
            if c["distinct"] == min(c["n_points"], c["N_p"]):
                t[0] += 1
        # C: null object of the model's own shape -- N independent uniform draws from the
        # N_p residues per cell (E[distinct] = model exactly), same cells, same instrument.
        meds, ab15, be05 = [], [], []
        obs_rank = 0
        for _ in range(NULL_REPS):
            def null_distinct(lab, c):
                return int(len(np.unique(rng.integers(0, c["N_p"], c["n_points"]))))
            s = summarize_with(null_distinct)
            meds.append(s["coverage_ratio_median"])
            ab15.append(s["coverage_ratio_frac_above_1p5"])
            be05.append(s["coverage_ratio_frac_below_0p5"])
            if s["coverage_ratio_median"] >= observed["coverage_ratio_median"]:
                obs_rank += 1
        meds_sorted = sorted(meds)
        out[run] = {
            "frozen_cells": len(cells),
            "observed_instrument_output": observed,
            "planted_max_spread_instrument_output": planted,
            "planted_clustered_instrument_output": clustered,
            "null_uniform_instrument_output": {
                "median_of_medians": statistics.median(meds),
                "medians_2.5pct": meds_sorted[int(0.025 * NULL_REPS)],
                "medians_97.5pct": meds_sorted[int(0.975 * NULL_REPS) - 1],
                "max_frac_above_1p5": max(ab15), "max_frac_below_0p5": max(be05),
                "null_reps_with_median_ge_observed": obs_rank,
            },
            "cells_where_any_point_set_could_exceed_1p2": sum(1 for r in ceil if r > 1.2),
            "cells_where_any_point_set_could_exceed_1p5": sum(1 for r in ceil if r > 1.5),
            "max_possible_frac_above_1p5_for_any_point_set": sum(1 for r in ceil if r > 1.5) / len(cells),
            "observed_cells_already_max_spread": maxspread,
            "observed_cells_already_max_spread_by_curve": maxspread_by_curve,
        }
    # ---------------- D: analytic thresholds ----------------
    out["D_analytic"] = {
        "ratio_ceiling_formula": "min(x,1)/(1-exp(-x)), x = N/N_p (large-N_p limit); = 1 + x/2 + O(x^2) as x -> 0",
        "x_where_ceiling_reaches_1p2": solve(1.2, 1e-9, 1.0),
        "x_where_ceiling_reaches_1p5": solve(1.5, 1e-9, 1.0),
        "ceiling_max_at_x_eq_1": ratio_ceiling(1.0),
        "x_above_1_where_ceiling_falls_back_to_1p5": math.log(3.0),
        "ceiling_at_x_0p01": ratio_ceiling(0.01), "ceiling_at_x_0p1": ratio_ceiling(0.1),
    }
    json.dump(out, sys.stdout, indent=1)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
