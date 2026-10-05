"""Route A: pair-count envelope P_n from class cardinalities only.

Forgets alphas and the target. Dual meter to covered.py |C_n|.
No Magma/Sage/AUXIN/Bedrock. Toy Z/l arithmetic only.
"""
from __future__ import annotations


def class_counts(n_add: int, rates: tuple[int, ...], n_free: int) -> list[int]:
    """n_free starting elements, one per leading class; then n_add by rates."""
    if n_add < 0:
        raise ValueError("n_add")
    k = len(rates)
    counts = [0] * k
    for i in range(min(n_free, k)):
        counts[i] = 1
    added = 0
    turn = 0
    while added < n_add:
        cls = turn % k
        take = rates[cls]
        for _ in range(take):
            if added >= n_add:
                break
            counts[cls] += 1
            added += 1
        turn += 1
    return counts


def pair_count(counts: list[int]) -> int:
    p = 0
    for i, ci in enumerate(counts):
        for cj in counts[i + 1 :]:
            p += ci * cj
    return p


def envelope_amqm_bound(n_add: int, k: int, n_free: int) -> int:
    """AM-QM envelope: k=2 -> (n+n_free)^2/4; k=3 -> (n+n_free)^2/3."""
    s = n_add + n_free
    if k == 2:
        return (s * s) // 4
    if k == 3:
        return (s * s) // 3
    raise ValueError("k")


def floor_survival_terms(ell: int, k: int, n_free: int, n_max: int) -> list[dict]:
    """List rows with integer n. term_num = max(0, ell - bound) for F = sum term_num/ell."""
    rows = []
    for n in range(0, n_max + 1):
        bound = envelope_amqm_bound(n, k, n_free)
        term = ell - bound
        if term < 0:
            term = 0
        rows.append(
            {
                "l": int(ell),
                "n": int(n),
                "k": int(k),
                "n_free": int(n_free),
                "envelope_bound": int(bound),
                "term_num": int(term),
            }
        )
        if bound >= ell:
            break
    return rows


def floor_numerator(rows: list[dict]) -> int:
    return sum(int(r["term_num"]) for r in rows)
