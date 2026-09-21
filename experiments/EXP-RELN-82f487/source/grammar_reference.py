"""Frozen-grammar reproduction fixture (specification.yaml's
sigma_one_and_frozen_grammar_reproduction_slices control, part (ii)):
depth-1 tree on the Legendre feature and depth-k trees on the top-k bits of
x, k in {1,2,3}, scored on the same count vectors, implemented here as a
direct, independent code path (c5c614 itself was never run, so its grammar
member formulas g1-g3 are not importable; this module is this contract's
own reconstruction from the hypothesis record's description "bit thresholds
and Legendre classes are depth-1 trees and one-layer readouts").

SCOPE NOTE (recorded as a deviation in the execution report): c5c614 was
read only PARTIALLY by the hypothesis author (lines 1-130, 355-515), so its
exact g1-g4 formulas are not fully available to this executor. The fixture
implemented here is therefore an INTERNAL self-consistency check: the same
grammar-slice selection rule (rank discrete feature-value groups by mean
count, take top groups until sigma density is reached, tie-break within the
boundary group by count then index) computed by two independently written
code paths (a scalar loop and a vectorised numpy path) inside this module,
checked for floating-point-exact agreement -- not a reproduction of
c5c614's unread exact reference values.
"""
from __future__ import annotations

import numpy as np

from scoring import lift_metrics


def _group_rank_slice_scalar(group_ids: np.ndarray, counts: np.ndarray, sigma: float) -> np.ndarray:
    n = len(counts)
    k = max(1, int(round(sigma * n)))
    groups = {}
    for idx in range(n):
        g = int(group_ids[idx])
        groups.setdefault(g, []).append(idx)
    group_means = []
    for g, idxs in groups.items():
        m = sum(counts[i] for i in idxs) / len(idxs)
        group_means.append((m, g))
    group_means.sort(key=lambda t: -t[0])
    mask = np.zeros(n, dtype=bool)
    remaining = k
    for (m, g) in group_means:
        idxs = groups[g]
        if len(idxs) <= remaining:
            for i in idxs:
                mask[i] = True
            remaining -= len(idxs)
        else:
            # tie-break within boundary group by count desc, then index
            ordered = sorted(idxs, key=lambda i: (-counts[i], i))
            for i in ordered[:remaining]:
                mask[i] = True
            remaining = 0
        if remaining <= 0:
            break
    return mask


def _group_rank_slice_vectorized(group_ids: np.ndarray, counts: np.ndarray, sigma: float) -> np.ndarray:
    n = len(counts)
    k = max(1, int(round(sigma * n)))
    uniq = np.unique(group_ids)
    means = np.array([counts[group_ids == g].mean() for g in uniq])
    order = np.argsort(-means)
    mask = np.zeros(n, dtype=bool)
    remaining = k
    for gi in order:
        g = uniq[gi]
        idxs = np.where(group_ids == g)[0]
        if len(idxs) <= remaining:
            mask[idxs] = True
            remaining -= len(idxs)
        else:
            ordered = idxs[np.lexsort((idxs, -counts[idxs]))]
            mask[ordered[:remaining]] = True
            remaining = 0
        if remaining <= 0:
            break
    return mask


def legendre_groups(xs, p):
    from features import legendre
    return np.array([legendre(x, p) + 1 for x in xs], dtype=np.int64)  # map {-1,0,1}->{0,1,2}


def topk_bit_groups(xs, k):
    return np.array([x & ((1 << k) - 1) for x in xs], dtype=np.int64)


def reproduction_check(xs, p, counts, sigma, k_bits=(1, 2, 3)):
    """Runs the scalar and vectorized paths for the Legendre grouping and
    each top-k-bit grouping; returns per-grammar-member equality verdicts."""
    counts = np.asarray(counts, dtype=np.float64)
    results = {}
    leg_groups = legendre_groups(xs, p)
    m_scalar = _group_rank_slice_scalar(leg_groups, counts, sigma)
    m_vec = _group_rank_slice_vectorized(leg_groups, counts, sigma)
    results["legendre"] = {
        "exact_match": bool(np.array_equal(m_scalar, m_vec)),
        "scalar_metrics": lift_metrics(counts, m_scalar),
        "vectorized_metrics": lift_metrics(counts, m_vec),
    }
    for k in k_bits:
        g = topk_bit_groups(xs, k)
        ms = _group_rank_slice_scalar(g, counts, sigma)
        mv = _group_rank_slice_vectorized(g, counts, sigma)
        results[f"top{k}bit"] = {
            "exact_match": bool(np.array_equal(ms, mv)),
            "scalar_metrics": lift_metrics(counts, ms),
            "vectorized_metrics": lift_metrics(counts, mv),
        }
    results["all_exact"] = all(v["exact_match"] for v in results.values())
    return results
