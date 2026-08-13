#!/usr/bin/env python3
"""Independent recomputation from raw_scores.json only.

This script intentionally does not read results.json.  It verifies seeded
instance/candidate/target generation, serialized score arrays, all array
lengths, report-table statistics, modular ranks, and what can be recovered
about the omitted (x,y) vectors from the phase table.
"""

import argparse
import json
import math
from pathlib import Path

import numpy as np


def centered_binomial(rng, eta, size):
    a = rng.integers(0, 2, size=(size, eta), dtype=np.int64).sum(axis=1)
    b = rng.integers(0, 2, size=(size, eta), dtype=np.int64).sum(axis=1)
    return (a - b).astype(np.int64)


def rounded_gaussian(rng, sigma, size):
    return np.rint(rng.normal(0.0, sigma, size=size)).astype(np.int64)


def center_mod(v, q):
    r = np.mod(v, q)
    return np.where(r > q // 2, r - q, r).astype(np.int64)


def rref_mod(matrix, q):
    a = np.asarray(matrix, dtype=np.int64).copy() % q
    rows, cols = a.shape
    pivots = []
    r = 0
    for c in range(cols):
        pivot = next((i for i in range(r, rows) if a[i, c] % q), None)
        if pivot is None:
            continue
        if pivot != r:
            a[[r, pivot]] = a[[pivot, r]]
        a[r] = (a[r] * pow(int(a[r, c]), -1, q)) % q
        for i in range(rows):
            if i != r and a[i, c]:
                a[i] = (a[i] - a[i, c] * a[r]) % q
        pivots.append(c)
        r += 1
        if r == rows:
            break
    return a, pivots


def rank_mod(matrix, q):
    return len(rref_mod(matrix, q)[1])


def inverse_mod(matrix, q):
    a = np.asarray(matrix, dtype=np.int64) % q
    n, m = a.shape
    if n != m:
        raise ValueError("matrix must be square")
    aug = np.concatenate([a.copy(), np.eye(n, dtype=np.int64)], axis=1)
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, n) if aug[i, c] % q), None)
        if pivot is None:
            raise ValueError("matrix is singular")
        if pivot != r:
            aug[[r, pivot]] = aug[[pivot, r]]
        aug[r] = (aug[r] * pow(int(aug[r, c]), -1, q)) % q
        for i in range(n):
            if i != r and aug[i, c]:
                aug[i] = (aug[i] - aug[i, c] * aug[r]) % q
        r += 1
    if not np.array_equal(aug[:, :n], np.eye(n, dtype=np.int64)):
        raise AssertionError("inverse reduction failed")
    return aug[:, n:]


def group_summary(means, indices):
    x = np.asarray([means[i] for i in indices], dtype=np.float64)
    return {
        "n": int(len(x)),
        "mean": float(x.mean()),
        "min": float(x.min()),
        "max": float(x.max()),
        "sd_ddof1": float(x.std(ddof=1)) if len(x) > 1 else None,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw_scores", type=Path)
    args = ap.parse_args()
    with args.raw_scores.open() as f:
        raw = json.load(f)

    p = raw["parameters"]
    m, n, d, q, n_vectors = (
        int(p["m"]),
        int(p["n"]),
        int(p["d"]),
        int(p["q"]),
        int(p["n_sieve_vectors"]),
    )
    a = np.asarray(raw["A"], dtype=np.int64)
    secret = np.asarray(raw["secret"], dtype=np.int64)
    candidates = np.asarray([c["vector"] for c in raw["candidates"]], dtype=np.int64)
    labels = [c["label"] for c in raw["candidates"]]
    types = [c["type"] for c in raw["candidates"]]
    targets = raw["targets"]

    # Reconstruct every numpy-generated value from the recorded seeds.
    seeds = p["seeds"]
    rng_inst = np.random.default_rng(int(seeds["instance"]))
    a_re = rng_inst.integers(0, q, size=(m, n), dtype=np.int64)
    s_re = centered_binomial(rng_inst, 2, n)
    e_main_re = rounded_gaussian(rng_inst, 2.0, m)
    b_main_re = (a_re @ s_re + e_main_re) % q

    rng_cand = np.random.default_rng(int(seeds["candidates"]))
    c_re = [s_re.copy()]
    c_re.extend(rng_cand.integers(0, q, size=n, dtype=np.int64) for _ in range(16))
    c_re.extend(centered_binomial(rng_cand, 2, n) for _ in range(8))
    for i in range(8):
        c = s_re.copy()
        c[i] += 1
        c_re.append(c)
    c_re = np.asarray(c_re, dtype=np.int64)

    rng_null = np.random.default_rng(int(seeds["null_target"]))
    b_null_re = rng_null.integers(0, q, size=m, dtype=np.int64)

    rng_decay = np.random.default_rng(int(seeds["decay_errors"]))
    decay_error_re = {}
    for sigma in [0.5, 1.0, 4.0, 8.0, 16.0]:
        decay_error_re[f"DECAY_sigma{sigma:g}"] = rounded_gaussian(rng_decay, sigma, m)
    decay_error_re["DECAY_uniform_error"] = center_mod(
        rng_decay.integers(0, q, size=m, dtype=np.int64), q
    )

    seeded_checks = {
        "A": bool(np.array_equal(a, a_re)),
        "secret": bool(np.array_equal(secret, s_re)),
        "main_error": bool(
            np.array_equal(
                np.asarray(targets[0]["error_vector"], dtype=np.int64), e_main_re
            )
        ),
        "main_b": bool(
            np.array_equal(np.asarray(targets[0]["b"], dtype=np.int64), b_main_re)
        ),
        "candidates": bool(np.array_equal(candidates, c_re)),
        "null_b": bool(
            np.array_equal(np.asarray(targets[1]["b"], dtype=np.int64), b_null_re)
        ),
    }
    for tg in targets[2:]:
        name = tg["name"]
        expected_e = decay_error_re[name]
        seeded_checks[f"{name}_error"] = bool(
            np.array_equal(np.asarray(tg["error_vector"], dtype=np.int64), expected_e)
        )
        seeded_checks[f"{name}_b"] = bool(
            np.array_equal(
                np.asarray(tg["b"], dtype=np.int64),
                (a @ secret + expected_e) % q,
            )
        )

    # Exhaustively verify emitted array lengths and serialized cosine values.
    length_failures = []
    phase_arrays = 0
    score_arrays = 0
    score_value_count = 0
    max_serialized_cosine_error = 0.0
    serialized_cosine_mismatches = 0
    target_data = {}
    for tg in targets:
        per = sorted(tg["per_candidate"], key=lambda x: int(x["candidate_index"]))
        by_index = {}
        for item in per:
            ci = int(item["candidate_index"])
            t = np.asarray(item["phases_t"], dtype=np.int64)
            by_index[ci] = t
            phase_arrays += 1
            if len(t) != n_vectors:
                length_failures.append(f"{tg['name']}:phase:{ci}:{len(t)}")
            if "scores_cos" in item:
                observed = np.asarray(item["scores_cos"], dtype=np.float64)
                expected = np.round(np.cos(2.0 * np.pi * t / q), 6)
                score_arrays += 1
                score_value_count += len(observed)
                if len(observed) != n_vectors:
                    length_failures.append(
                        f"{tg['name']}:score:{ci}:{len(observed)}"
                    )
                if len(observed):
                    max_serialized_cosine_error = max(
                        max_serialized_cosine_error,
                        float(np.max(np.abs(observed - expected))),
                    )
                    serialized_cosine_mismatches += int(
                        np.count_nonzero(observed != expected)
                    )
        target_data[tg["name"]] = by_index

    for key, values in raw["per_vector"].items():
        if isinstance(values, list) and len(values) != n_vectors:
            length_failures.append(f"per_vector:{key}:{len(values)}")

    # Recompute all target means and ranks from integer phases, never serialized
    # scores and never results.json.
    target_metrics = {}
    for tg in targets:
        by_index = target_data[tg["name"]]
        ordered_indices = sorted(by_index)
        means = {
            ci: float(np.cos(2.0 * np.pi * by_index[ci] / q).mean())
            for ci in ordered_indices
        }
        correct = means[0]
        rank = 1 + sum(means[ci] > correct for ci in ordered_indices if ci != 0)
        target_metrics[tg["name"]] = {
            "n_candidates": len(ordered_indices),
            "correct_mean": correct,
            "rank": int(rank),
            "wrong_mean": float(
                np.mean([means[i] for i in ordered_indices if i != 0])
            ),
            "candidate_means": {labels[i]: means[i] for i in ordered_indices},
        }

    main_means = {
        i: target_metrics["MAIN_lwe_sigma2"]["candidate_means"][labels[i]]
        for i in range(len(candidates))
    }
    null_means = {
        i: target_metrics["NULL_uniform_target"]["candidate_means"][labels[i]]
        for i in range(len(candidates))
    }
    groups = {
        "uniform": list(range(1, 17)),
        "centered_binomial": list(range(17, 25)),
        "near_miss": list(range(25, 33)),
    }
    report_tables = {
        "main": {name: group_summary(main_means, idx) for name, idx in groups.items()},
        "null": {name: group_summary(null_means, idx) for name, idx in groups.items()},
    }
    null_wrong = np.asarray([null_means[i] for i in range(1, 33)])
    report_tables["null_nominal_z_wrong_sd"] = float(
        (null_means[0] - null_wrong.mean()) / null_wrong.std(ddof=1)
    )

    x_dot_e = np.asarray(raw["per_vector"]["x_dot_e_main"], dtype=np.int64)
    report_tables["x_dot_e_main"] = {
        "sd_ddof0": float(x_dot_e.std()),
        "min": int(x_dot_e.min()),
        "max": int(x_dot_e.max()),
        "fraction_abs_lt_q_over_4": float(np.mean(np.abs(x_dot_e) < q / 4.0)),
        "main_correct_phase_equal": bool(
            np.array_equal(target_data["MAIN_lwe_sigma2"][0], x_dot_e)
        ),
    }
    report_tables["error_main"] = {
        "sd_ddof0": float(e_main_re.std()),
        "infinity_norm": int(np.max(np.abs(e_main_re))),
    }
    norm2_v = np.asarray(raw["per_vector"]["norm2_v"], dtype=np.int64)
    norm2_x = np.asarray(raw["per_vector"]["norm2_x"], dtype=np.int64)
    norm2_y = np.asarray(raw["per_vector"]["norm2_y"], dtype=np.int64)
    report_tables["norm2_v"] = {
        "min": int(norm2_v.min()),
        "median": float(np.median(norm2_v)),
        "max": int(norm2_v.max()),
        "equals_x_plus_y_all": bool(np.array_equal(norm2_v, norm2_x + norm2_y)),
    }

    finite_decay_names = [
        "DECAY_sigma0.5",
        "DECAY_sigma1",
        "MAIN_lwe_sigma2",
        "DECAY_sigma4",
        "DECAY_sigma8",
        "DECAY_sigma16",
    ]
    finite_decay_means = [
        target_metrics[name]["correct_mean"] for name in finite_decay_names
    ]
    report_tables["decay"] = {
        "target_order": finite_decay_names + ["DECAY_uniform_error"],
        "correct_means": finite_decay_means
        + [target_metrics["DECAY_uniform_error"]["correct_mean"]],
        "wrong_means": [
            target_metrics[name]["wrong_mean"]
            for name in finite_decay_names + ["DECAY_uniform_error"]
        ],
        "ranks": [
            target_metrics[name]["rank"]
            for name in finite_decay_names + ["DECAY_uniform_error"]
        ],
        "strictly_monotone_over_finite_sigma": bool(
            all(a0 > a1 for a0, a1 in zip(finite_decay_means, finite_decay_means[1:]))
        ),
    }

    # Recover y mod q from phase differences across the 33 candidates.
    # D_j y = -(t_j-t_0), where D_j = candidate_j-candidate_0.
    diff_candidates = (candidates[1:] - candidates[0]) % q
    _, pivot_candidate_rows = rref_mod(diff_candidates.T, q)
    selected = pivot_candidate_rows[:n]
    d_square = diff_candidates[selected]
    d_inverse = inverse_mod(d_square, q)
    main_t = target_data["MAIN_lwe_sigma2"]
    rhs_main = np.asarray(
        [-(main_t[j + 1] - main_t[0]) for j in selected], dtype=np.int64
    ) % q
    y_mod = (d_inverse @ rhs_main).T % q
    all_main_rhs = np.asarray(
        [-(main_t[j] - main_t[0]) for j in range(1, len(candidates))],
        dtype=np.int64,
    ) % q
    main_phase_difference_failures = int(
        np.count_nonzero((diff_candidates @ y_mod.T) % q != all_main_rhs)
    )

    cross_target_y_failures = 0
    recovered_xb = {}
    for tg in targets:
        by_index = target_data[tg["name"]]
        for ci, phases in by_index.items():
            expected_delta = (y_mod @ (candidates[ci] - candidates[0])) % q
            observed_delta = (by_index[0] - phases) % q
            cross_target_y_failures += int(
                np.count_nonzero(expected_delta != observed_delta)
            )
        recovered_xb[tg["name"]] = (
            by_index[0] + y_mod @ candidates[0]
        ) % q

    y_center = center_mod(y_mod, q)
    y_norm_match = np.sum(y_center * y_center, axis=1) == norm2_y

    # Ranks quantify what the omitted vectors leave falsifiable.
    a_transpose_rank = rank_mod(a.T, q)
    b_rows = np.asarray([tg["b"] for tg in targets], dtype=np.int64)
    b_row_rank = rank_mod(b_rows, q)
    x_observation_matrix = np.vstack([a.T, b_rows])
    x_observation_rank = rank_mod(x_observation_matrix, q)

    output = {
        "input": str(args.raw_scores),
        "parameters": {
            "m": m,
            "n": n,
            "d": d,
            "q": q,
            "N": n_vectors,
            "A_shape": list(a.shape),
            "candidate_count": len(candidates),
            "candidate_class_counts": {
                "correct": types.count("correct_secret"),
                "uniform_Zq": types.count("uniform_Zq"),
                "centered_binomial_eta2": types.count("centered_binomial_eta2"),
                "near_miss": sum(t.startswith("correct_secret_plus_1") for t in types),
            },
            "secret_min": int(secret.min()),
            "secret_max": int(secret.max()),
        },
        "seeded_reconstruction": {
            "checks": seeded_checks,
            "all_pass": bool(all(seeded_checks.values())),
        },
        "array_and_score_checks": {
            "phase_arrays_checked": phase_arrays,
            "score_arrays_checked": score_arrays,
            "serialized_score_values_checked": score_value_count,
            "serialized_cosine_mismatches_at_6dp": serialized_cosine_mismatches,
            "max_serialized_cosine_error": max_serialized_cosine_error,
            "length_failures": length_failures,
        },
        "report_tables": report_tables,
        "target_metrics": target_metrics,
        "recoverability_and_certificate": {
            "rank_A_transpose_mod_q": a_transpose_rank,
            "A_transpose_surjective_to_Zq_n": bool(a_transpose_rank == n),
            "rank_candidate_difference_matrix_mod_q": rank_mod(diff_candidates, q),
            "selected_independent_candidate_rows": [int(x + 1) for x in selected],
            "y_mod_q_recovered_for_all_vectors": bool(
                main_phase_difference_failures == 0
                and cross_target_y_failures == 0
            ),
            "main_phase_difference_failures": main_phase_difference_failures,
            "cross_target_phase_difference_failures": cross_target_y_failures,
            "centered_y_norm_matches_archived_norm2_y_count": int(
                np.count_nonzero(y_norm_match)
            ),
            "centered_y_norm_mismatch_count": int(
                np.count_nonzero(~y_norm_match)
            ),
            "max_abs_centered_y": int(np.max(np.abs(y_center))),
            "rank_archived_b_rows_mod_q": b_row_rank,
            "rank_combined_A_transpose_and_b_rows_mod_q": x_observation_rank,
            "x_residue_linear_nullity": int(m - x_observation_rank),
            "interpretation": (
                "The phase table determines y modulo q, and the tiny archived "
                "norm determines its centered integer lift. It supplies only "
                f"{b_row_rank} target equations for the {m} x coordinates. "
                "Even after imposing A^T x=y, the combined linear system has "
                f"nullity {m - x_observation_rank}; x is not emitted or uniquely "
                "recoverable by these linear observations. Because A^T has full "
                "row rank, arbitrary y residues have some x preimage, so "
                "membership is not independently falsifiable without x (or a "
                "binding reconstruction artifact)."
            ),
        },
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
