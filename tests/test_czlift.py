"""Tests for harness/czlift.py (GOAL-CZLIFT-1516d5 instruments)."""
import random

from harness import czlift
from harness.czlift import ZpCurve
from harness.toycurve import EllipticCurve


def test_self_test_passes():
    assert czlift.self_test(seed=3)["ok"]


def test_cm_models_have_cm_j():
    czlift.cm_self_test()


def test_anomalous_curves_are_anomalous():
    for D, p, A, B, j in czlift.anomalous_cm_curves(200):
        assert EllipticCurve(p, A % p, B % p).order() == p
        assert czlift.j_invariant_q(A, B) == j


def test_torsion_section_is_homomorphic_and_degenerate():
    rng = random.Random(5)
    p, a, b = 101, 57, 60  # #E = 99 = 9 * 11, subgroup of order 11
    Efp = EllipticCurve(p, a, b)
    N = Efp.order()
    n = czlift.largest_prime_factor(N)
    E = ZpCurve(p, 4, a, b)
    P = czlift.point_of_order(Efp, n, N // n, rng)
    tP, _ = E.torsion_section(E.hensel_lift(*P, eps=rng.randrange(p)), n)
    tP2, _ = E.torsion_section(E.hensel_lift(*P, eps=rng.randrange(p)), n)
    assert E.eq(tP, tP2)
    assert E.is_zero(E.mul(n, tP))
    Q = Efp.mul(3, P)
    tQ, _ = E.torsion_section(E.hensel_lift(*Q, eps=rng.randrange(p)), n)
    assert E.eq(tQ, E.mul(3, tP))


def test_smart_recovers_on_nonsplit_lift_and_fails_on_canonical():
    rng = random.Random(11)
    D, p, A, B, j = next(c for c in czlift.anomalous_cm_curves(200) if c[1] == 127)
    Efp = EllipticCurve(p, A % p, B % p)
    P = czlift.random_point(Efp, rng)
    d = 57
    Q = Efp.mul(d, P)
    canonical = ZpCurve(p, 6, A, B)
    perturbed = ZpCurve(p, 6, A + p * 3, B + p * 5)
    for E, expect_v in ((canonical, 2), (perturbed, 1)):
        Ph = E.hensel_lift(*P, eps=rng.randrange(p))
        Qh = E.hensel_lift(*Q, eps=rng.randrange(p))
        ratio, vP, vQ = czlift.smart_ratio(E, Ph, Qh, p)
        if expect_v == 1:
            assert vP == 1 and ratio == d
        else:
            assert vP >= 2
