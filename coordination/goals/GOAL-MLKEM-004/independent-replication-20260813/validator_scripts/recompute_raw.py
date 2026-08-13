#!/usr/bin/env python3
"""Independent raw-only metric, seed, score, and recoverability checks."""

import argparse
import json
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
    aug = np.concatenate([a, np.eye(n, dtype=np.int64)], axis=1)
    for c in range(n):
        pivot = next((i for i in range(c, n) if aug[i, c] % q), None)
        if pivot is None:
            raise ValueError("singular matrix")
        if pivot != c:
            aug[[c, pivot]] = aug[[pivot, c]]
        aug[c] = (aug[c] * pow(int(aug[c, c]), -1, q)) % q
        for i in range(n):
            if i != c and aug[i, c]:
                aug[i] = (aug[i] - aug[i, c] * aug[c]) % q
    return aug[:, n:]


def summary(values):
    x = np.asarray(values, dtype=np.float64)
    return {
        "n": int(len(x)),
        "mean": float(x.mean()),
        "min": float(x.min()),
        "max": float(x.max()),
        "sd_ddof1": float(x.std(ddof=1)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw_scores", type=Path)
    args = ap.parse_args()
    raw = json.loads(args.raw_scores.read_text())
    p = raw["parameters"]
    m, n, d, q, N = (int(p[k]) for k in ("m", "n", "d", "q", "n_sieve_vectors"))
    A = np.asarray(raw["A"], dtype=np.int64)
    s = np.asarray(raw["secret"], dtype=np.int64)
    C = np.asarray([c["vector"] for c in raw["candidates"]], dtype=np.int64)
    labels = [c["label"] for c in raw["candidates"]]
    types = [c["type"] for c in raw["candidates"]]
    targets = raw["targets"]
    seeds = p["seeds"]

    # Exact seeded input reconstruction.
    rng = np.random.default_rng(int(seeds["instance"]))
    A2 = rng.integers(0, q, size=(m, n), dtype=np.int64)
    s2 = centered_binomial(rng, 2, n)
    e2 = rounded_gaussian(rng, 2.0, m)
    rngc = np.random.default_rng(int(seeds["candidates"]))
    C2 = [s2.copy()]
    C2 += [rngc.integers(0, q, size=n, dtype=np.int64) for _ in range(16)]
    C2 += [centered_binomial(rngc, 2, n) for _ in range(8)]
    for i in range(8):
        c = s2.copy()
        c[i] += 1
        C2.append(c)
    rngn = np.random.default_rng(int(seeds["null_target"]))
    bnull = rngn.integers(0, q, size=m, dtype=np.int64)
    seed_checks = {
        "A": np.array_equal(A, A2),
        "secret": np.array_equal(s, s2),
        "main_error": np.array_equal(targets[0]["error_vector"], e2),
        "main_b": np.array_equal(targets[0]["b"], (A2 @ s2 + e2) % q),
        "candidates": np.array_equal(C, np.asarray(C2)),
        "null_b": np.array_equal(targets[1]["b"], bnull),
    }
    rngd = np.random.default_rng(int(seeds["decay_errors"]))
    expected_errors = {}
    for sigma in (0.5, 1.0, 4.0, 8.0, 16.0):
        expected_errors[f"DECAY_sigma{sigma:g}"] = rounded_gaussian(rngd, sigma, m)
    expected_errors["DECAY_uniform_error"] = center_mod(
        rngd.integers(0, q, size=m, dtype=np.int64), q
    )
    for tg in targets[2:]:
        e = expected_errors[tg["name"]]
        seed_checks[tg["name"] + "_error"] = np.array_equal(tg["error_vector"], e)
        seed_checks[tg["name"] + "_b"] = np.array_equal(tg["b"], (A @ s + e) % q)

    # Raw lengths, score serialization, candidate means, and ranks.
    length_failures = []
    phase_arrays = score_arrays = score_values = score_mismatches = 0
    max_score_error = 0.0
    phase = {}
    metrics = {}
    for tg in targets:
        by_index = {}
        for item in tg["per_candidate"]:
            ci = int(item["candidate_index"])
            t = np.asarray(item["phases_t"], dtype=np.int64)
            by_index[ci] = t
            phase_arrays += 1
            if len(t) != N:
                length_failures.append([tg["name"], "phase", ci, len(t)])
            if "scores_cos" in item:
                got = np.asarray(item["scores_cos"], dtype=np.float64)
                want = np.round(np.cos(2 * np.pi * t / q), 6)
                score_arrays += 1
                score_values += len(got)
                if len(got) != N:
                    length_failures.append([tg["name"], "score", ci, len(got)])
                score_mismatches += int(np.count_nonzero(got != want))
                max_score_error = max(max_score_error, float(np.max(np.abs(got - want))))
        phase[tg["name"]] = by_index
        means = {i: float(np.cos(2 * np.pi * t / q).mean()) for i, t in by_index.items()}
        metrics[tg["name"]] = {
            "correct_mean": means[0],
            "wrong_mean": float(np.mean([v for i, v in means.items() if i])),
            "rank": 1 + sum(v > means[0] for i, v in means.items() if i),
            "candidate_means": {labels[i]: v for i, v in means.items()},
        }
    for key, values in raw["per_vector"].items():
        if isinstance(values, list) and len(values) != N:
            length_failures.append(["per_vector", key, len(values)])

    main = {i: metrics["MAIN_lwe_sigma2"]["candidate_means"][labels[i]] for i in range(33)}
    null = {i: metrics["NULL_uniform_target"]["candidate_means"][labels[i]] for i in range(33)}
    groups = {"uniform": range(1, 17), "centered_binomial": range(17, 25), "near_miss": range(25, 33)}
    tables = {
        "main": {k: summary([main[i] for i in v]) for k, v in groups.items()},
        "null": {k: summary([null[i] for i in v]) for k, v in groups.items()},
    }
    wrong_null = np.asarray([null[i] for i in range(1, 33)])
    tables["null_nominal_z_wrong_sd"] = float(
        (null[0] - wrong_null.mean()) / wrong_null.std(ddof=1)
    )
    xdot = np.asarray(raw["per_vector"]["x_dot_e_main"], dtype=np.int64)
    tables["x_dot_e_main"] = {
        "sd_ddof0": float(xdot.std()),
        "min": int(xdot.min()),
        "max": int(xdot.max()),
        "fraction_abs_lt_q_over_4": float(np.mean(np.abs(xdot) < q / 4)),
        "main_correct_phase_equal": np.array_equal(phase["MAIN_lwe_sigma2"][0], xdot),
    }
    normv = np.asarray(raw["per_vector"]["norm2_v"], dtype=np.int64)
    normx = np.asarray(raw["per_vector"]["norm2_x"], dtype=np.int64)
    normy = np.asarray(raw["per_vector"]["norm2_y"], dtype=np.int64)
    tables["norm2_v"] = {
        "min": int(normv.min()),
        "median": float(np.median(normv)),
        "max": int(normv.max()),
        "equals_x_plus_y_all": np.array_equal(normv, normx + normy),
    }
    order = [
        "DECAY_sigma0.5", "DECAY_sigma1", "MAIN_lwe_sigma2",
        "DECAY_sigma4", "DECAY_sigma8", "DECAY_sigma16", "DECAY_uniform_error",
    ]
    correct_decay = [metrics[k]["correct_mean"] for k in order]
    tables["decay"] = {
        "target_order": order,
        "correct_means": correct_decay,
        "wrong_means": [
            metrics[order[0]]["wrong_mean"], metrics[order[1]]["wrong_mean"],
            tables["main"]["uniform"]["mean"], metrics[order[3]]["wrong_mean"],
            metrics[order[4]]["wrong_mean"], metrics[order[5]]["wrong_mean"],
            metrics[order[6]]["wrong_mean"],
        ],
        "ranks": [metrics[k]["rank"] for k in order],
        "strictly_monotone_over_finite_sigma": all(
            x > y for x, y in zip(correct_decay[:6], correct_decay[1:6])
        ),
    }

    # Recover y from candidate phase differences.
    D = (C[1:] - C[0]) % q
    _, pivot_rows = rref_mod(D.T, q)
    selected = pivot_rows[:n]
    rhs = np.asarray(
        [-(phase["MAIN_lwe_sigma2"][j + 1] - phase["MAIN_lwe_sigma2"][0]) for j in selected]
    ) % q
    ymod = (inverse_mod(D[selected], q) @ rhs).T % q
    phase_failures = 0
    for tg in targets:
        by = phase[tg["name"]]
        for ci, t in by.items():
            phase_failures += int(
                np.count_nonzero((by[0] - t) % q != (ymod @ (C[ci] - C[0])) % q)
            )
    ycenter = center_mod(ymod, q)
    ynorm_match = np.sum(ycenter * ycenter, axis=1) == normy
    brows = np.asarray([tg["b"] for tg in targets], dtype=np.int64)

    out = {
        "parameters": {
            "m": m, "n": n, "d": d, "q": q, "N": N, "A_shape": list(A.shape),
            "candidate_count": len(C),
            "candidate_class_counts": {
                "correct": types.count("correct_secret"),
                "uniform_Zq": types.count("uniform_Zq"),
                "centered_binomial_eta2": types.count("centered_binomial_eta2"),
                "near_miss": sum(t.startswith("correct_secret_plus_1") for t in types),
            },
            "secret_min": int(s.min()), "secret_max": int(s.max()),
        },
        "seeded_reconstruction": {
            "checks": {k: bool(v) for k, v in seed_checks.items()},
            "all_pass": bool(all(seed_checks.values())),
        },
        "array_and_score_checks": {
            "phase_arrays_checked": phase_arrays,
            "score_arrays_checked": score_arrays,
            "serialized_score_values_checked": score_values,
            "serialized_cosine_mismatches_at_6dp": score_mismatches,
            "max_serialized_cosine_error": max_score_error,
            "length_failures": length_failures,
        },
        "report_tables": tables,
        "target_metrics": metrics,
        "recoverability_and_certificate": {
            "rank_A_transpose_mod_q": rank_mod(A.T, q),
            "A_transpose_surjective_to_Zq_n": rank_mod(A.T, q) == n,
            "rank_candidate_difference_matrix_mod_q": rank_mod(D, q),
            "y_mod_q_recovered_for_all_vectors": phase_failures == 0,
            "cross_target_phase_difference_failures": phase_failures,
            "centered_y_norm_matches_archived_norm2_y_count": int(ynorm_match.sum()),
            "centered_y_norm_mismatch_count": int((~ynorm_match).sum()),
            "max_abs_centered_y": int(np.abs(ycenter).max()),
            "rank_archived_b_rows_mod_q": rank_mod(brows, q),
            "rank_combined_A_transpose_and_b_rows_mod_q": rank_mod(np.vstack([A.T, brows]), q),
            "x_residue_linear_nullity": m - rank_mod(np.vstack([A.T, brows]), q),
        },
    }
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
