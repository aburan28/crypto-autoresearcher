"""Exact q_maj / q_strict for the f558e4 estimator (Stage 2 gates).

q_maj is the maximum, over functions F: SxS -> S, of the fraction of
pairs (k, l) in (Z/n)^2 with v(k+l) = F(v(k), v(l)).

This module does not compute digit ADV and does not read a curve
statistic unless the caller supplies a label sequence v.
"""
from __future__ import annotations

from fractions import Fraction

import numpy as np


def interval_partition(n: int, s: int) -> np.ndarray:
    v = np.empty(n, dtype=np.int64)
    for k in range(n):
        v[k] = min(int(k * s / n), s - 1)
    return v


def x_bucket_labels(xs: list[int], p: int, s: int) -> np.ndarray:
    v = np.empty(len(xs), dtype=np.int64)
    for i, x in enumerate(xs):
        v[i] = min(int(int(x) * s / p), s - 1)
    return v


def _cyclic_convolution(f: np.ndarray, g: np.ndarray, n: int, label: str) -> np.ndarray:
    F = np.fft.fft(f.astype(np.float64))
    G = np.fft.fft(g.astype(np.float64))
    h = np.fft.ifft(F * G).real
    err = float(np.max(np.abs(h - np.round(h))))
    if err >= 0.25:
        raise AssertionError(
            f"integer-recovery failed for {label}: max |h-round(h)|={err}"
        )
    return np.round(h).astype(np.int64)


def pair_counts(v: np.ndarray, n: int) -> np.ndarray:
    s = int(v.max()) + 1
    F = np.zeros((s, n), dtype=np.float64)
    F[v.astype(np.int64), np.arange(n)] = 1.0
    N = np.zeros((s, s, s), dtype=np.int64)
    for i in range(s):
        for j in range(s):
            h = _cyclic_convolution(F[i], F[j], n, f"f_{i}*f_{j}")
            for m in range(s):
                N[i, j, m] = int(np.dot(h, F[m]))
    return N


def q_maj_exact(v: np.ndarray, n: int) -> Fraction:
    N = pair_counts(v, n)
    total = 0
    for i in range(N.shape[0]):
        for j in range(N.shape[1]):
            total += int(N[i, j, :].max())
    return Fraction(total, n * n)


def q_strict_exact(v: np.ndarray, n: int) -> Fraction:
    N = pair_counts(v, n)
    s = N.shape[0]
    sizes = [int((v == i).sum()) for i in range(s)]
    total = 0
    for i in range(s):
        for j in range(s):
            row = N[i, j, :]
            nz = int((row > 0).sum())
            if nz == 1 and int(row.max()) == sizes[i] * sizes[j]:
                total += sizes[i] * sizes[j]
    return Fraction(total, n * n)


def q_maj_brute_group(labels: list[int], add_index: np.ndarray) -> Fraction:
    """q_maj over a (possibly non-cyclic) group given addition table.

    add_index[i, j] is the index of g_i + g_j. Used only for the
    composite-order x-bucket fixture (N ~ 100).
    """
    n = len(labels)
    s = max(labels) + 1
    counts = np.zeros((s, s, s), dtype=np.int64)
    for i in range(n):
        for j in range(n):
            counts[labels[i], labels[j], labels[int(add_index[i, j])]] += 1
    total = 0
    for i in range(s):
        for j in range(s):
            total += int(counts[i, j, :].max())
    return Fraction(int(total), n * n)
