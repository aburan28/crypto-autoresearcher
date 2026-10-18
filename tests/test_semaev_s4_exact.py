"""Exact regression for harness.semaev.s4_expr (KN-OPEN-5b3a08, Q1).

S4(x1, x2, x3, x4) must vanish at a tuple of abscissae exactly when some
choice of signs gives +-P1 +-P2 +-P3 +-P4 = O.  The test enumerates every
x-tuple over a toy prime, decides the group relation by direct point
arithmetic (independent of any polynomial), and compares.  It also rebuilds
the former non-simultaneous construction and requires the same comparison to
FAIL on it, so the test is shown to see the defect (positive control).
"""
from __future__ import annotations

import itertools

import pytest
import sympy

from harness import semaev
from harness.toycurve import EllipticCurve

x4 = sympy.symbols("x4")


def _legacy_s4(a: int, b: int):
    """The pre-repair construction: sequential, non-simultaneous .subs()."""
    left = semaev.s3_expr(a, b).subs(semaev.x3, semaev._t)
    right = semaev.s3_expr(a, b).subs(
        {semaev.x1: semaev.x3, semaev.x2: x4, semaev.x3: semaev._t}
    )
    return sympy.resultant(left, right, semaev._t)


def _points(E: EllipticCurve):
    return [
        (x, y)
        for x in range(E.p)
        for y in range(E.p)
        if (y * y - (x ** 3 + E.a * x + E.b)) % E.p == 0
    ]


def _relation_tuples(E: EllipticCurve, pts):
    """x-tuples admitting signs with +-P1+-P2+-P3+-P4 = O (pair-sum meet)."""
    pair_sums: dict[tuple[int, int], set] = {}
    for P, Q in itertools.product(pts, repeat=2):
        key = (P[0], Q[0])
        sums = pair_sums.setdefault(key, set())
        sums.add(E.add(P, Q))
        sums.add(E.add(P, E.negate(Q)))
    xs = sorted({P[0] for P in pts})
    out = set()
    for k12, k34 in itertools.product(pair_sums, repeat=2):
        s34 = pair_sums[k34]
        s34 = s34 | {E.negate(R) for R in s34}
        if pair_sums[k12] & s34:
            out.add(k12 + k34)
    return xs, out


def _mismatches(S4, E: EllipticCurve):
    pts = _points(E)
    xs, relation = _relation_tuples(E, pts)
    f = sympy.lambdify((semaev.x1, semaev.x2, semaev.x3, x4), S4, "math")
    wrong = 0
    for t in itertools.product(xs, repeat=4):
        vanishes = int(f(*t)) % E.p == 0
        if vanishes != (t in relation):
            wrong += 1
    return wrong


CURVES = [(13, 2, 3), (11, 1, 6)]


@pytest.mark.parametrize("p,a,b", CURVES)
def test_s4_vanishes_exactly_on_group_relations(p, a, b):
    E = EllipticCurve(p, a, b)
    assert _mismatches(semaev.s4_expr(a, b), E) == 0


@pytest.mark.parametrize("p,a,b", CURVES)
def test_exact_check_detects_legacy_nonsimultaneous_defect(p, a, b):
    E = EllipticCurve(p, a, b)
    legacy = _legacy_s4(a, b)
    # the defect drops x3 entirely from the resultant
    assert semaev.x3 not in legacy.free_symbols
    assert _mismatches(legacy, E) > 0


def test_default_factor_base_is_whole_curve_not_subgroup():
    """Q2 is a documented scope choice, not a bug: the legacy default draws
    from E(F_p); the subgroup scope is opt-in.  Pin both so a silent change
    of the default (which would alter archived full_curve bytes) is caught."""
    from harness.toycurve import generate_instance

    inst = generate_instance(seed=1, field_bits=6)
    E = inst.curve()
    assert E.order() // inst.n > 1
    outside = [
        x for x in semaev.build_factor_base(inst, 5)
        if E.mul(inst.n, E.lift_x(x)) is not None
    ]
    assert outside, "default scope should include non-subgroup abscissae here"
    assert all(
        E.mul(inst.n, E.lift_x(x)) is None
        for x in semaev.build_factor_base(inst, 5, scope="target_subgroup")
    )
