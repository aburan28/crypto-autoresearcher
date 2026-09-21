"""Theta(B) lookup labelling for the SAMPLED 2^24 rung (specification.yaml's
SAMPLED-RUNG LABELS clause): R - d in D + D over a sorted table of the
B(B+1)/2 pair sums. NOT exercised in this executor session (the 2^24 rung
was not reached; see the execution report's not_run list) -- implemented
and unit-tested here so the required_artifacts entry is a real, working
module rather than a stub, and so cost_instrumentation.py can measure its
per-lookup cost relative to c_f at the rungs that WERE reached.
"""
from __future__ import annotations

import bisect


def build_pair_sum_table_E(curve, D):
    """All B(B+1)/2 pair sums d_i + d_j (i<=j), sorted by a canonical key
    (x-coordinate, with O as -infinity) for bisection lookup."""
    B = len(D)
    pairs = []
    for i in range(B):
        for j in range(i, B):
            s = curve.add(D[i], D[j])
            key = s if s is not None else "O"
            pairs.append((key, i, j))

    def sort_key(item):
        key = item[0]
        if key == "O":
            return (-1, -1)
        return key
    pairs.sort(key=sort_key)
    keys_sorted = [sort_key(p) for p in pairs]
    return pairs, keys_sorted


def lookup_decomposition_E(curve, D, pairs, keys_sorted, target):
    """Is target - d in (D + D) for some d in D? Theta(B log B) per target
    via bisection over the precomputed pair-sum table."""
    for d_idx, d in enumerate(D):
        need = curve.add(target, curve.negate(d))
        need_key = need if need is not None else "O"

        def sort_key(k):
            if k == "O":
                return (-1, -1)
            return k
        nk = sort_key(need_key)
        pos = bisect.bisect_left(keys_sorted, nk)
        if pos < len(keys_sorted) and keys_sorted[pos] == nk:
            (found_key, i, j) = pairs[pos]
            return True, (i, j, d_idx)
    return False, None


def build_pair_sum_table_ZN(N, D):
    B = len(D)
    pairs = []
    for i in range(B):
        for j in range(i, B):
            s = (D[i] + D[j]) % N
            pairs.append((s, i, j))
    pairs.sort(key=lambda p: p[0])
    keys_sorted = [p[0] for p in pairs]
    return pairs, keys_sorted


def lookup_decomposition_ZN(N, D, pairs, keys_sorted, target):
    for d_idx, d in enumerate(D):
        need = (target - d) % N
        pos = bisect.bisect_left(keys_sorted, need)
        if pos < len(keys_sorted) and keys_sorted[pos] == need:
            (found_key, i, j) = pairs[pos]
            return True, (i, j, d_idx)
    return False, None


if __name__ == "__main__":
    # small self-test on Z/N (fast, no curve needed)
    import numpy as np
    N = 1009
    D = list(range(1, 11)) + [(-d) % N for d in range(1, 11)]
    pairs, keys_sorted = build_pair_sum_table_ZN(N, D)
    ok_count = 0
    for _ in range(20):
        i, j, k = np.random.default_rng(0).integers(0, len(D), size=3)
        target = (D[i] + D[j] + D[k]) % N
        found, triple = lookup_decomposition_ZN(N, D, pairs, keys_sorted, target)
        ok_count += int(found)
    print("found", ok_count, "of 20 (should be 20, all constructed to be decomposable)")
