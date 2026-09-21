#!/usr/bin/env python3
"""Fresh uniform-vs-CBD candidate control on the archived NULL target."""

import argparse
import json
from pathlib import Path

import numpy as np

from recompute_raw import center_mod, centered_binomial, inverse_mod, rref_mod


def summarize(values):
    x = np.asarray(values, dtype=np.float64)
    return {
        "n_candidates": int(len(x)),
        "mean_of_candidate_means": float(x.mean()),
        "sd_of_candidate_means_ddof1": float(x.std(ddof=1)),
        "min": float(x.min()),
        "q05": float(np.quantile(x, 0.05)),
        "median": float(np.median(x)),
        "q95": float(np.quantile(x, 0.95)),
        "max": float(x.max()),
        "mean_standard_error": float(x.std(ddof=1) / np.sqrt(len(x))),
    }


def score_candidates(y_mod, xb_mod, candidates, q, chunk_size):
    out = np.empty(len(candidates), dtype=np.float64)
    for start in range(0, len(candidates), chunk_size):
        stop = min(start + chunk_size, len(candidates))
        phases = (xb_mod[:, None] - y_mod @ candidates[start:stop].T) % q
        out[start:stop] = np.cos(2 * np.pi * phases / q).mean(axis=0)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw_scores", type=Path)
    ap.add_argument("--seed", type=int, default=5351520260813)
    ap.add_argument("--n-per-class", type=int, default=4096)
    ap.add_argument("--chunk-size", type=int, default=128)
    args = ap.parse_args()
    raw = json.loads(args.raw_scores.read_text())
    q, n = int(raw["parameters"]["q"]), int(raw["parameters"]["n"])
    archived_candidates = np.asarray(
        [c["vector"] for c in raw["candidates"]], dtype=np.int64
    )
    null = next(t for t in raw["targets"] if t["name"] == "NULL_uniform_target")
    phases = {
        int(item["candidate_index"]): np.asarray(item["phases_t"], dtype=np.int64)
        for item in null["per_candidate"]
    }

    diff = (archived_candidates[1:] - archived_candidates[0]) % q
    _, pivot_rows = rref_mod(diff.T, q)
    selected = pivot_rows[:n]
    rhs = np.asarray(
        [-(phases[j + 1] - phases[0]) for j in selected], dtype=np.int64
    ) % q
    y_mod = (inverse_mod(diff[selected], q) @ rhs).T % q
    xb_mod = (phases[0] + y_mod @ archived_candidates[0]) % q
    archived_mismatches = 0
    for ci, observed in phases.items():
        expected = center_mod(xb_mod - y_mod @ archived_candidates[ci], q)
        archived_mismatches += int(np.count_nonzero(expected != observed))

    rng = np.random.default_rng(args.seed)
    uniform = rng.integers(0, q, size=(args.n_per_class, n), dtype=np.int64)
    cbd = np.asarray(
        [centered_binomial(rng, 2, n) for _ in range(args.n_per_class)],
        dtype=np.int64,
    )
    us = score_candidates(y_mod, xb_mod, uniform, q, args.chunk_size)
    cs = score_candidates(y_mod, xb_mod, cbd, q, args.chunk_size)
    u, c = summarize(us), summarize(cs)
    difference = c["mean_of_candidate_means"] - u["mean_of_candidate_means"]
    difference_se = float(
        np.sqrt(
            u["sd_of_candidate_means_ddof1"] ** 2 / len(us)
            + c["sd_of_candidate_means_ddof1"] ** 2 / len(cs)
        )
    )
    result = {
        "input": str(args.raw_scores),
        "null_target": "NULL_uniform_target",
        "candidate_seed": args.seed,
        "n_per_class": args.n_per_class,
        "chunk_size": args.chunk_size,
        "q": q,
        "candidate_dimension": n,
        "recovery_check": {
            "archived_null_phase_values_recomputed": len(phases) * len(phases[0]),
            "mismatches": archived_mismatches,
            "max_abs_centered_y": int(np.abs(center_mod(y_mod, q)).max()),
        },
        "uniform_Zq": u,
        "centered_binomial_eta2": c,
        "class_difference_cbd_minus_uniform": difference,
        "class_difference_standard_error": difference_se,
        "class_difference_over_standard_error": difference / difference_se,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
