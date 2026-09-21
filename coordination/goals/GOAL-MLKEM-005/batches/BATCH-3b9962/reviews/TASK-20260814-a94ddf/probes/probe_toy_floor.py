#!/usr/bin/env python3
"""
Independent Validator probe: reproduce TASK-20260814-ffd791's own
worker_toy_floor() logic (PREREG-8 section 2.2's toy-floor sweep) for a
chosen d, from an independent re-implementation (same construction/seed
formula, own code -- not imported from stage0_feasibility.py), to confirm
the reported COMPLETED/NOT_COMPUTED outcome, elapsed time, and
r_min_over_evaluated_subset value for that point.

Usage: python3 probe_toy_floor.py <d> <cap_seconds>
"""
import json
import sys
import time

import numpy as np

SEED_ROOT = 715923
TOY_ETA = 2
TOY_CHUNK = 4_000_000


def gram_schmidt(B):
    d = B.shape[0]
    Bstar = np.zeros_like(B, dtype=np.float64)
    mu = np.zeros((d, d), dtype=np.float64)
    for i in range(d):
        Bstar[i] = B[i].astype(np.float64)
        for j in range(i):
            mu[i, j] = np.dot(B[i], Bstar[j]) / np.dot(Bstar[j], Bstar[j])
            Bstar[i] = Bstar[i] - mu[i, j] * Bstar[j]
    r = np.array([np.dot(Bstar[i], Bstar[i]) for i in range(d)])
    return Bstar, mu, r


def main(d, cap_seconds):
    from fpylll import IntegerMatrix, LLL, BKZ, FPLLL
    import os

    beta_toy = max(0, d // 2)
    eta = TOY_ETA
    seed = int(np.random.default_rng([SEED_ROOT, 0, d, beta_toy, 2, 0]).integers(0, 2 ** 31 - 1))
    FPLLL.set_random_seed(seed)
    result = {"d": d, "eta": eta, "beta_toy": beta_toy, "seed_used": seed}

    A = IntegerMatrix.random(d, "qary", k=d // 2, q=3329)
    LLL.reduction(A)
    strategies_path = "/usr/share/libfplll8/strategies/default.json"
    if not os.path.exists(strategies_path):
        strategies_path = BKZ.DEFAULT_STRATEGY
    if beta_toy >= 2:
        par = BKZ.Param(block_size=beta_toy, strategies=strategies_path, flags=BKZ.AUTO_ABORT)
        BKZ.reduction(A, par)

    B = np.array([[A[i, j] for j in range(d)] for i in range(d)], dtype=np.int64)
    Bstar, mu, r = gram_schmidt(B)
    k = d - beta_toy
    P = np.zeros((d, d), dtype=np.float64)
    for i in range(k, d):
        P += np.outer(Bstar[i], Bstar[i]) / r[i]

    base = 2 * eta + 1
    total_points = base ** d
    result["alphabet_size_total"] = total_points if total_points < 10 ** 18 else "OVERFLOW_TOO_LARGE"

    t0 = time.time()
    best_r = None
    n_evaluated = 0
    idx = 0
    completed = False
    while idx < total_points:
        if time.time() - t0 >= cap_seconds:
            break
        chunk_end = min(idx + TOY_CHUNK, total_points)
        n = chunk_end - idx
        ids = np.arange(idx, chunk_end, dtype=np.int64)
        digits = np.zeros((n, d), dtype=np.int64)
        tmp = ids.copy()
        for pos in range(d):
            digits[:, pos] = tmp % base
            tmp //= base
        E = digits - eta
        norms_sq = np.einsum("ij,ij->i", E, E)
        nonzero = norms_sq > 0
        if np.any(nonzero):
            proj = E[nonzero] @ P
            proj_sq = np.einsum("ij,ij->i", proj, E[nonzero])
            ratio = proj_sq / norms_sq[nonzero]
            chunk_min = float(np.min(ratio))
            if best_r is None or chunk_min < best_r:
                best_r = chunk_min
        n_evaluated += n
        idx = chunk_end
    else:
        completed = True

    result.update({
        "status": "COMPLETED" if completed else "NOT_COMPUTED",
        "elapsed_seconds": time.time() - t0,
        "n_points_evaluated": n_evaluated,
        "fraction_of_alphabet_evaluated": n_evaluated / total_points if isinstance(result["alphabet_size_total"], int) else None,
        "r_min_over_evaluated_subset": best_r,
    })
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    d = int(sys.argv[1])
    cap = float(sys.argv[2])
    out = main(d, cap)
    with open("probe_toy_floor_d%d.json" % d, "w") as f:
        json.dump(out, f, indent=2)
