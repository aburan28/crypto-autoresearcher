"""Red-team check A (TASK-20261023-326d39, joint R1): anatomy of the coverage-ratio excess.

Reads only raw-result.json of the two runs, by key. No producer code is imported.

For the frozen coverage cells (n_points >= 30 and model_distinct <= 0.9 N_p) it reports,
overall and per curve:
  * median and mean of ratio = distinct / (N_p (1 - (1 - 1/N_p)^N)),
  * the fraction of cells that are collision-free (distinct == min(N, N_p)),
  * the expected collision-free fraction under (i) N independent uniform draws and
    (ii) the negation-paired null (O plus (N-1)/2 pairs {R, -R}, R uniform),
  * observed versus modelled lost residues sum(N - distinct) against sum(N - model),
  * exact per-cell upper/lower tail probabilities of `distinct` under the paired null
    (occupancy DP over x-classes), and the count of cells beyond 1e-6 on each side,
  * three seeded same-shape nulls for the median: independent per cell (the validator's),
    nested in H per (curve, p), and nested + negation-paired.
Seed: numpy default_rng(20261023). 200 replicates per null.
"""
from __future__ import annotations

import json
import math
import os
import statistics
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
RUNS = {"main": "RUN-CZLIFT-74f172", "replication": "RUN-CZLIFT-490b33"}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rt_a_coverage_anatomy_output.json")


def load(run_id):
    path = os.path.join(ROOT, "experiments", "EXP-CZLIFT-a255fc", "runs", run_id, "raw-result.json")
    return json.load(open(path))["raw"]["curves"]


def model(Np, n):
    return Np * (1 - (1 - 1 / Np) ** n)


def frozen(c):
    return c["n_points"] >= 30 and c["model_distinct"] <= 0.9 * c["N_p"]


def upper_median(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2]


def p_no_collision_indep(Np, n):
    if n > Np:
        return 0.0
    lp = sum(math.log1p(-i / Np) for i in range(n))
    return math.exp(lp)


def paired_classes(Np):
    # x-classes {R, -R} of size 2 among the N_p - 1 non-identity residues (2-torsion ignored)
    return max(1, (Np - 1) // 2)


def p_no_collision_paired(Np, n):
    k = (n - 1) // 2
    M = paired_classes(Np)
    if k > M:
        return 0.0
    return math.exp(sum(math.log1p(-i / M) for i in range(k)))


def occupancy_dist(M, k):
    """Distribution of the number of distinct classes hit by k uniform draws from M classes."""
    P = np.zeros(k + 1)
    P[0] = 1.0
    for j in range(k):
        D = np.arange(k + 1)
        new = P * (D / M)
        new[1:] += P[:-1] * ((M - D[:-1]) / M)
        P = new
    return P


def tails_paired(Np, n, distinct):
    """Exact tails of `distinct` under the cyclic negation-paired null.

    Model: E(F_p) ~ Z/N_p (cyclic assumption); O is always present; k = (n-1)//2 draws R uniform
    in Z/N_p each contribute the class {R, -R}. Classes: {0} (already present), {N_p/2} if N_p is
    even (a singleton), and M = (N_p - 1 - e)//2 pairs, e = 1 if N_p even else 0.
    distinct = 1 + 2 D + s, with D pair classes hit and s = 1 if the singleton is hit.
    """
    k = (n - 1) // 2
    e = 1 if Np % 2 == 0 else 0
    M = (Np - 1 - e) // 2
    # P[s][D]
    P = np.zeros((2, k + 1))
    P[0, 0] = 1.0
    p_zero = 1 / Np
    p_single = e / Np
    for _ in range(k):
        D = np.arange(k + 1)
        p_pair_new = 2 * (M - D) / Np
        p_pair_old = 2 * D / Np
        new = np.zeros_like(P)
        for s in (0, 1):
            stay = P[s] * (p_zero + p_pair_old + (p_single if s == 1 else 0.0))
            new[s] += stay
            new[s, 1:] += P[s, :-1] * p_pair_new[:-1]
        new[1] += P[0] * p_single
        P = new
    D = np.arange(k + 1)
    dist = {}
    for s in (0, 1):
        for d_, pr in zip(1 + 2 * D + s, P[s]):
            dist[int(d_)] = dist.get(int(d_), 0.0) + float(pr)
    upper = sum(pr for d_, pr in dist.items() if d_ >= distinct)
    lower = sum(pr for d_, pr in dist.items() if d_ <= distinct)
    return upper, lower


def stats_block(cells):
    ratios = [c["ratio_to_model"] for c in cells]
    maxspread = [c["distinct"] == min(c["n_points"], c["N_p"]) for c in cells]
    exp_ms_ind = [p_no_collision_indep(c["N_p"], c["n_points"]) for c in cells]
    exp_ms_pair = [p_no_collision_paired(c["N_p"], c["n_points"]) for c in cells]
    lost_obs = sum(c["n_points"] - c["distinct"] for c in cells)
    lost_mod = sum(c["n_points"] - c["model_distinct"] for c in cells)
    xs = [c["n_points"] / c["N_p"] for c in cells]
    ceil = [min(x, 1) / (1 - math.exp(-x)) for x in xs]
    return {
        "cells": len(cells),
        "median_ratio_upper": upper_median(ratios) if ratios else None,
        "mean_ratio": statistics.fmean(ratios) if ratios else None,
        "min_ratio": min(ratios) if ratios else None,
        "max_ratio": max(ratios) if ratios else None,
        "median_N_over_Np": statistics.median(xs) if xs else None,
        "median_pigeonhole_ceiling": statistics.median(ceil) if ceil else None,
        "frac_collision_free_observed": sum(maxspread) / len(cells) if cells else None,
        "frac_collision_free_expected_indep": statistics.fmean(exp_ms_ind) if cells else None,
        "frac_collision_free_expected_paired": statistics.fmean(exp_ms_pair) if cells else None,
        "lost_residues_observed": lost_obs,
        "lost_residues_model": round(lost_mod, 1),
        "lost_ratio_obs_over_model": (lost_obs / lost_mod) if lost_mod else None,
    }


def null_medians(curves, rng, reps, nested, paired):
    """Median of the frozen-cell ratio under a uniform null of the same shape."""
    meds = []
    keys = []
    for cv in curves:
        for p in cv["primes"]:
            rows = sorted([c for c in cv["coverage"] if c["p"] == p], key=lambda c: c["H"])
            keys.append((cv["label"], p, rows))
    for _ in range(reps):
        ratios = []
        for _, p, rows in keys:
            Np = rows[0]["N_p"]
            if nested:
                nmax = max(c["n_points"] for c in rows)
                if paired:
                    k = (nmax - 1) // 2
                    R = rng.integers(0, Np, size=k)
                    seq = np.empty(2 * k + 1, dtype=np.int64)
                    seq[0] = 0
                    seq[1::2] = R
                    seq[2::2] = (-R) % Np
                else:
                    seq = rng.integers(0, Np, size=nmax)
                    seq[0] = 0
                for c in rows:
                    if not frozen(c):
                        continue
                    d = len(np.unique(seq[: c["n_points"]]))
                    ratios.append(d / c["model_distinct"])
            else:
                for c in rows:
                    if not frozen(c):
                        continue
                    d = len(np.unique(rng.integers(0, Np, size=c["n_points"])))
                    ratios.append(d / c["model_distinct"])
        meds.append(upper_median(ratios))
    meds.sort()
    return {"median_of_medians": float(np.median(meds)),
            "band_2p5_97p5": [float(np.percentile(meds, 2.5)), float(np.percentile(meds, 97.5))],
            "max": float(max(meds)), "reps": reps}


def main():
    rng = np.random.default_rng(20261023)
    out = {"seed": 20261023, "runs": {}}
    for tag, run in RUNS.items():
        curves = load(run)
        cells = [c for cv in curves for c in cv["coverage"] if frozen(c)]
        block = {"overall": stats_block(cells), "per_curve": {}, "per_rank_tail_counts": {}}
        # recompute the producer's median to make sure the cell set is the frozen one
        block["overall"]["median_check_vs_manifest"] = upper_median([c["ratio_to_model"] for c in cells])
        for cv in curves:
            cc = [dict(c, label=cv["label"]) for c in cv["coverage"] if frozen(c)]
            if cc:
                block["per_curve"][cv["label"]] = dict(stats_block(cc), rank_recalled=cv["rank_recalled"])
        # per-cell exact tails under the paired null
        n_up = n_lo = 0
        extreme = []
        for cv in curves:
            for c in cv["coverage"]:
                if not frozen(c):
                    continue
                up, lo = tails_paired(c["N_p"], c["n_points"], c["distinct"])
                if up < 1e-6:
                    n_up += 1
                if lo < 1e-6:
                    n_lo += 1
                extreme.append((min(up, lo), "excess" if up < lo else "deficit", cv["label"], c["p"], c["H"],
                                c["N_p"], c["n_points"], c["distinct"], round(c["ratio_to_model"], 4)))
        extreme.sort()
        block["paired_null_cell_tails"] = {
            "cells_upper_tail_below_1e-6": n_up,
            "cells_lower_tail_below_1e-6": n_lo,
            "most_extreme_20": [
                {"tail_prob": t[0], "side": t[1], "curve": t[2], "p": t[3], "H": t[4], "N_p": t[5],
                 "N": t[6], "distinct": t[7], "ratio": t[8]} for t in extreme[:20]],
            "note": "cells are nested in H, so counts over cells are not independent tests; a single cell "
                    "below 1e-6 is already a refutation of the paired-uniform model at that (curve, p)",
        }
        block["nulls"] = {
            "independent_per_cell": null_medians(curves, rng, 200, nested=False, paired=False),
            "nested_in_H": null_medians(curves, rng, 200, nested=True, paired=False),
            "nested_and_negation_paired": null_medians(curves, rng, 200, nested=True, paired=True),
        }
        out["runs"][run] = block
    json.dump(out, open(OUT, "w"), indent=1)
    print(json.dumps({r: {"overall": b["overall"], "nulls": b["nulls"],
                          "tails": {k: v for k, v in b["paired_null_cell_tails"].items() if k != "most_extreme_20"}}
                      for r, b in out["runs"].items()}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
