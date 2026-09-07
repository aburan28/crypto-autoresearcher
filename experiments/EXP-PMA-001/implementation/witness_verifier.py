"""
EXP-PMA-001 witness reverification.

Independent of BOTH parity_predicate.py (which never constructs a matrix)
and existence_decider.py's own construction algorithm
(four_by_four_det / three_by_three_det_generic, a recursive cofactor
expansion): this module recomputes each of the 16 principal minors via the
full Leibniz permutation-expansion formula (det = sum over permutations sigma
of sign(sigma) * prod_i a[i, sigma(i)]) -- an algorithmically distinct
determinant method -- while still using the domain-correct RationalFunction
arithmetic (required so that finite-field entries reduce mod q correctly;
converting to plain sympy Expr and back, as an earlier draft of this module
did, silently reverts to integer arithmetic and produces false mismatches
whenever a domain element's canonical representative is negative, e.g.
-3 vs 4 in GF(7) -- this bug was caught by the run's own calibration self-
check in RUN-PMA4-001-a and is disclosed in implementation.md). Required by
CTRL-PMA4-GROUND-TRUTH: "every EXISTS witness is reverified by direct
evaluation of all 16 principal minors."
"""
from __future__ import annotations

from itertools import permutations
from typing import Dict, Tuple

from common import RationalFunction, NONEMPTY_SUBSETS


def permutation_sign(perm: Tuple[int, ...]) -> int:
    n = len(perm)
    visited = [False] * n
    sign = 1
    for i in range(n):
        if visited[i]:
            continue
        j = i
        cycle_len = 0
        while not visited[j]:
            visited[j] = True
            j = perm[j]
            cycle_len += 1
        if cycle_len % 2 == 0:
            sign = -sign
    return sign


def leibniz_det(entries: Dict[Tuple[int, int], RationalFunction], idxs: Tuple[int, ...], domain) -> RationalFunction:
    n = len(idxs)
    if n == 0:
        return RationalFunction.constant(1, domain)
    total = RationalFunction.constant(0, domain)
    for perm in permutations(range(n)):
        sign = permutation_sign(perm)
        term = RationalFunction.constant(1, domain)
        for i in range(n):
            term = term * entries[(idxs[i], idxs[perm[i]])]
        if sign == -1:
            term = RationalFunction.constant(0, domain) - term
        total = total + term
    return total


def reverify_witness(entries: Dict[Tuple[int, int], RationalFunction], p_table: Dict, domain) -> Dict:
    """entries: dict (row,col)->RationalFunction for the full 4x4 candidate
    matrix (diagonal entries included). p_table: dict subset->RationalFunction
    prescribed values (must include all 15 nonempty subsets; p_emptyset=1
    implicit and trivially satisfied by any matrix, not checked here).
    Returns a report dict with per-subset pass/fail and an overall
    all_16_verified boolean (the 16th being the trivial empty-set minor,
    counted as verified by construction)."""
    results = {"empty_set": {"expected": "1", "computed": "1", "match": True}}
    all_ok = True
    for S in NONEMPTY_SUBSETS:
        computed_rf = leibniz_det(entries, S, domain)
        expected_rf = p_table[S]
        match = computed_rf == expected_rf
        results[str(S)] = {
            "expected": str(expected_rf),
            "computed": str(computed_rf),
            "match": bool(match),
        }
        if not match:
            all_ok = False
    return {
        "all_16_verified": all_ok,
        "per_subset": results,
    }
