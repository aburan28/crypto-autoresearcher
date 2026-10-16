"""Exact m = 3 coverage over Z_N for EXP-CMFB-cea1d2.

count_coverage is the spec's algorithm (pair sums, tail slices, uint8 seen[]); histogram is the
full-histogram recount (np.bincount in chunks); brute_force_counts is the literal itertools
enumeration used only by the instrument check.  Labels are integers in Z_N.
"""

from __future__ import annotations

import itertools
import math
from math import comb

import numpy as np


def binom3(B: int) -> int:
    """T = binomial(B+2, 3): the number of size-3 multisets of a B-element base."""
    return comb(B + 2, 3)


def base_size(N: int) -> int:
    """B = smallest integer with B^3 >= 6N, exactly."""
    B = round((6 * N) ** (1 / 3))
    while B ** 3 < 6 * N:
        B += 1
    while B > 1 and (B - 1) ** 3 >= 6 * N:
        B -= 1
    return B


def pair_sums(labels: np.ndarray, N: int) -> tuple[np.ndarray, np.ndarray]:
    """P = l_b + l_c mod N for b <= c ordered by b then c (int32) and the offset of each b."""
    l = np.asarray(labels, dtype=np.int32)
    B = len(l)
    parts = []
    for b in range(B):
        s = l[b:] + l[b]
        np.subtract(s, N, out=s, where=s >= N)
        parts.append(s)
    off = np.zeros(B + 1, dtype=np.int64)
    off[1:] = np.cumsum([B - b for b in range(B)])
    return np.concatenate(parts), off


def count_coverage(labels, N: int, seen: np.ndarray | None = None) -> tuple[int, int]:
    """(#{r : c(r) > 0}, number of enumerated sums).  The second must equal binomial(B+2, 3) (M0)."""
    l = np.asarray(labels, dtype=np.int32)
    B = len(l)
    P, off = pair_sums(l, N)
    if seen is None:
        seen = np.zeros(N, dtype=np.uint8)
    else:
        seen.fill(0)
    buf = np.empty(len(P), dtype=np.int32)
    enumerated = 0
    for a in range(B):
        tail = P[off[a]:]
        s = buf[:len(tail)]
        np.add(tail, l[a], out=s)
        np.subtract(s, N, out=s, where=s >= N)
        seen[s] = 1
        enumerated += len(tail)
    return int(np.count_nonzero(seen)), enumerated


def histogram(labels, N: int, chunk_target: int = 1 << 22) -> dict:
    """Full histogram c(r) of all size-3 multiset sums; returns the integers the spec records.

    total = sum_r c(r), nonzero = #{r : c(r) > 0}, collisions = sum_r c(r)(c(r)-1)/2, max_c."""
    l = np.asarray(labels, dtype=np.int32)
    B = len(l)
    P, off = pair_sums(l, N)
    hist = np.zeros(N, dtype=np.int64)
    pending, size = [], 0

    def flush():
        nonlocal pending, size
        if pending:
            hist.__iadd__(np.bincount(np.concatenate(pending), minlength=N))
            pending, size = [], 0

    for a in range(B):
        s = P[off[a]:] + l[a]
        np.subtract(s, N, out=s, where=s >= N)
        pending.append(s)
        size += len(s)
        if size >= max(chunk_target, N):
            flush()
    flush()
    return {"total": int(hist.sum()), "nonzero": int(np.count_nonzero(hist)),
            "collisions": int((hist * (hist - 1) // 2).sum()), "max_c": int(hist.max()),
            "vector": hist}


def brute_force_counts(labels, N: int) -> np.ndarray:
    """c(r) by literal itertools.combinations_with_replacement enumeration (instrument check)."""
    c = np.zeros(N, dtype=np.int64)
    for x, y, z in itertools.combinations_with_replacement([int(v) for v in labels], 3):
        c[(x + y + z) % N] += 1
    return c


def coverage_by_set(labels, N: int) -> int:
    """Second code path 1 (pure Python set), for checkers."""
    return len({(x + y + z) % N for x, y, z in
                itertools.combinations_with_replacement([int(v) for v in labels], 3)})


def coverage_by_sort(labels, N: int) -> int:
    """Second code path 2 (sort-based unique over all sums), for checkers at large N."""
    l = np.asarray(labels, dtype=np.int64)
    parts = []
    for a in range(len(l)):
        for b in range(a, len(l)):
            parts.append((l[a] + l[b] + l[b:]) % N)
    return int(len(np.unique(np.concatenate(parts).astype(np.int32))))


def random_labels(N: int, B: int, gen: np.random.Generator) -> list[int]:
    """B distinct classes {+-l} uniformly without replacement from the (N-1)/2 classes, independent signs.

    Stream recipe (fixed): c = integers(1, (N-1)/2 + 1, size=B); keep first occurrences; redraw the
    shortfall with the same call until B distinct; then s = integers(0, 2, size=B); label = c if s = 0
    else N - c."""
    half = (N - 1) // 2
    chosen: list[int] = []
    seen_c: set[int] = set()
    need = B
    while need > 0:
        for c in gen.integers(1, half + 1, size=need):
            c = int(c)
            if c not in seen_c:
                seen_c.add(c)
                chosen.append(c)
        need = B - len(chosen)
    signs = gen.integers(0, 2, size=B)
    return [c if int(s) == 0 else N - c for c, s in zip(chosen, signs)]


def poisson_mu(B: int, N: int) -> float:
    return binom3(B) / N


def poisson_coverage(B: int, N: int) -> float:
    return 1.0 - math.exp(-poisson_mu(B, N))


def sigma_rel_formula(B: int, N: int) -> float:
    """sqrt(e^-mu (1 - (1+mu) e^-mu)) / ((1 - e^-mu) sqrt(N))."""
    mu = poisson_mu(B, N)
    e = math.exp(-mu)
    return math.sqrt(e * (1.0 - (1.0 + mu) * e)) / ((1.0 - e) * math.sqrt(N))


def planted_known_ratio(B: int, N: int) -> float:
    """(1 - exp(-mu')) / (1 - exp(-mu)) with mu' = mu (B+3)/B: planted base of size B+1 vs random of size B."""
    mu = poisson_mu(B, N)
    return (1.0 - math.exp(-mu * (B + 3) / B)) / (1.0 - math.exp(-mu))
