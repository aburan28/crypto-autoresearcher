#!/usr/bin/env python3
"""Typed families, their admissibility guards, and the four invalid inputs.

EVERY TYPED NUMBER IN THIS RUN PASSES THROUGH `validate_typed_draw`. Invalidation
rule 4 of the frozen contract makes a typed cost number computed from a draw
whose representatives are not pairwise distinct modulo V invalid, because the
types collapse and the m! is then not removed; a "random" v_i can land in V or
in a coset already used, so distinctness is CHECKED rather than assumed, and a
failed check raises instead of returning a small saving.
"""
from __future__ import annotations

import numpy as np

from image_enum import is_independent, is_subspace, span


class InvalidInput(Exception):
    """Raised for an input the contract requires be REJECTED, not scored."""

    def __init__(self, kind: str, detail: str):
        super().__init__(f"{kind}: {detail}")
        self.kind = kind
        self.detail = detail


# ---------------------------------------------------------------------------
# Guards
# ---------------------------------------------------------------------------
def validate_parameters(n: int, m: int, k: int, t: int | None = None) -> None:
    if m > n:
        raise InvalidInput("m_greater_than_n",
                           f"m = {m} exceeds n = {n}: fewer than m independent "
                           f"summands exist and eq. (5) is not defined")
    if k < 1:
        raise InvalidInput("k_below_one",
                           f"k = {k} < 1: V would be the zero subspace or "
                           f"smaller and |V| = 2^k is not a factor base")
    if t is not None and t < 2:
        raise InvalidInput("t_equals_one",
                           f"t = {t}: eq. (5) consists of t - 1 = {t - 1} "
                           f"equations, so there is no system to solve")


def validate_subspace(elements, k: int) -> None:
    els = set(int(e) for e in elements)
    if len(els) != 1 << k:
        raise InvalidInput("not_a_subspace",
                           f"claimed dimension {k} but the set has {len(els)} "
                           f"elements, not 2^{k} = {1 << k}")
    if not is_subspace(els):
        raise InvalidInput("not_a_subspace",
                           "the set is not closed under xor / does not contain "
                           "0, so it is not an F_2-subspace")


def validate_typed_draw(reps: list[int], vspace: set[int]) -> None:
    """v_i pairwise distinct modulo V, i.e. v_i + v_j not in V for i != j."""
    for i in range(len(reps)):
        for j in range(i + 1, len(reps)):
            if (reps[i] ^ reps[j]) in vspace:
                raise InvalidInput(
                    "collapsed_types",
                    f"v_{i + 1} and v_{j + 1} lie in the same coset of V "
                    f"(v_{i + 1} + v_{j + 1} = {reps[i] ^ reps[j]} in V): the "
                    f"types collapse and the m! is not removed")


def validate_multiplicative_draw(gens: list[int], vbasis: list[int],
                                 field) -> None:
    """g_i V pairwise distinct as SETS, and each of full dimension k."""
    sets = []
    for g in gens:
        if g == 0:
            raise InvalidInput("zero_multiplier",
                              "g = 0 collapses gV to {0}")
        img = [field.mul(g, w) for w in span(vbasis)]
        if len(set(img)) != 1 << len(vbasis):
            raise InvalidInput("degenerate_multiplier",
                               f"g = {g} does not act injectively on V")
        sets.append(frozenset(img))
    for i in range(len(sets)):
        for j in range(i + 1, len(sets)):
            if sets[i] == sets[j]:
                raise InvalidInput(
                    "collapsed_translates",
                    f"g_{i + 1} V and g_{j + 1} V are the same subspace: the "
                    f"types collapse")


# ---------------------------------------------------------------------------
# Draws
# ---------------------------------------------------------------------------
def draw_additive_cosets(rng, n: int, m: int, vspace: set[int],
                         degenerate: bool = False) -> tuple[list[int], int]:
    """m representatives in pairwise distinct cosets of V. Returns (reps, redraws).

    Rejection sampling with the guard as the acceptance test, so the number of
    rejected candidates is recorded rather than hidden; `degenerate` returns
    v_1 = ... = v_m = 0 for the matched null and does not pass the guard.
    """
    if degenerate:
        return [0] * m, 0
    redraws = 0
    reps: list[int] = []
    while len(reps) < m:
        cand = int(rng.integers(0, 1 << n))
        if any((cand ^ r) in vspace for r in reps):
            redraws += 1
            continue
        reps.append(cand)
    validate_typed_draw(reps, vspace)
    return reps, redraws


def draw_multiplicative_translates(rng, field, n: int, m: int,
                                   vbasis: list[int]) -> tuple[list[int], int]:
    """m multipliers g_i with g_i V pairwise distinct subspaces of dimension k."""
    redraws = 0
    gens: list[int] = []
    while len(gens) < m:
        cand = int(rng.integers(1, 1 << n))
        trial = gens + [cand]
        try:
            validate_multiplicative_draw(trial, vbasis, field)
        except InvalidInput:
            redraws += 1
            continue
        gens.append(cand)
    return gens, redraws


def typed_xsets(kind: str, vbasis: list[int], reps: list[int], field):
    """The m x-coordinate sets of the typed family, as explicit lists."""
    base = span(vbasis)
    if kind == "additive_cosets":
        return [[v ^ w for w in base] for v in reps]
    if kind == "multiplicative_translates":
        return [[field.mul(g, w) for w in base] for g in reps]
    raise ValueError(f"unknown translate family {kind}")


def check_multiplicative_are_subspaces(xsets, k: int) -> None:
    for s in xsets:
        validate_subspace(s, k)


def random_nonsubspace(rng, n: int, k: int) -> list[int]:
    """A size-2^k set that is NOT an F_2-subspace, for the invalid-input control."""
    while True:
        cand = set()
        while len(cand) < (1 << k):
            cand.add(int(rng.integers(0, 1 << n)))
        if not is_subspace(cand):
            return sorted(cand)


__all__ = [
    "InvalidInput", "validate_parameters", "validate_subspace",
    "validate_typed_draw", "validate_multiplicative_draw",
    "draw_additive_cosets", "draw_multiplicative_translates", "typed_xsets",
    "check_multiplicative_are_subspaces", "random_nonsubspace",
    "is_independent", "span",
]
