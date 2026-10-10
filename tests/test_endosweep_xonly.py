"""Tests for harness/endosweep/xonly.py: x-only XZ formulas, the ladder,
Bernstein's binary chain, and the conjugate chain as the 2-D difference."""
from __future__ import annotations

import random

import pytest

from harness.endosweep import costmodel as CM
from harness.endosweep import quadorder as QO
from harness.endosweep import xonly as XO
from harness.endosweep.targets import deployed_targets, verify
from harness.endosweep.toyverify import Curve


def _cryptopro_b():
    T = next(t for t in deployed_targets() if t.name == "GOST CryptoPro-B")
    verify(T)
    return T


def _curves():
    T = _cryptopro_b()
    p, a, b = T.p, T.coeffs["a"] % T.p, T.coeffs["b"] % T.p
    return T, Curve(p, a, b), XO.XCurve(p, a, b)


def _scale(P, rng, p):
    z = rng.randrange(1, p)
    return (P[0] * z % p, z)


def test_xz_formulas_agree_with_affine_and_count_what_the_efd_says():
    T, E, C = _curves()
    p = T.p
    rng = random.Random(1)
    F = C.F
    for _ in range(4):
        P, Q = E.point(rng.randrange(1 << 30)), E.point(rng.randrange(1 << 30))
        F.reset()
        assert C.normalise(C.xdbl(_scale(P, rng, p))) == E.add(P, P)[0]
        assert (F.M, F.S, F.Mc_full + F.Mc_small) == (2, 5, 3)            # dbl-2002-bj-3
        diff = E.add(P, E.neg(Q))
        F.reset()
        R = C.xadd(_scale(P, rng, p), _scale(Q, rng, p), _scale(diff, rng, p))
        assert (F.M, F.S, F.Mc_full + F.Mc_small) == (7, 2, 2)            # dadd-2002-it-3
        assert C.normalise(R) == E.add(P, Q)[0]
        F.reset()
        R = C.xadd(_scale(P, rng, p), _scale(Q, rng, p), (diff[0], 1), affine_diff=True)
        assert (F.M, F.S, F.Mc_full + F.Mc_small) == (6, 2, 2)            # mdadd-2002-it-3
        assert C.normalise(R) == E.add(P, Q)[0]
    # the identity (1 : 0) passes through both formulas
    P = E.point(7)
    assert C.xdbl((1, 0))[1] == 0
    assert C.normalise(C.xadd((1, 0), (P[0], 1), (P[0], 1))) == P[0]
    # the cost row reproduces the counts, with a = -3 small and b full-size on CryptoPro-B
    assert CM.xonly_op("xDBL", C.a, C.b, p) == {"M": 2, "S": 5, "Mc_full": 2, "M_eq": 9}
    assert CM.xonly_op("xADD", C.a, C.b, p)["M_eq"] == 10
    assert CM.xonly_op("mxADD", C.a, C.b, p)["M_eq"] == 9


def test_ladder_is_correct_and_uniform():
    T, E, C = _curves()
    rng = random.Random(2)
    bits = T.n.bit_length()
    counts = set()
    for k in (1, 2, 3, T.n - 1, rng.randrange(T.n), rng.randrange(1 << 20)):
        P = XO.EX.point_of_order(E, T.n, T.h, 3 + k % 5)
        C.F.reset()
        R = XO.ladder(C, k, P[0], bits)
        counts.add(C.F.snapshot()["M_eq"])
        ref = XO.jacobian_mul(T.p, C.a, k, P)
        assert C.normalise(R) == ref[0]
    assert counts == {CM.xonly_ladder_cost(bits, C.a, C.b, T.p)["M_eq"]}


def test_jacobian_reference_agrees_with_affine():
    T, E, C = _curves()
    P = E.point(11)
    for k in (0, 1, 2, 5, 12345678901234567890, T.n - 1):
        assert XO.jacobian_mul(T.p, C.a, k, P) == E.mul(k, P)


def test_bernstein_levels_reproduce_the_papers_example():
    # Bernstein 2006, section 4: the example chain's lines, ending with (73, 59), (74, 58), (74, 59)
    lines = [XO.line_pairs(*lv) for lv in XO.bernstein_levels(73, 58, 7, D_final=0)[1:]]
    assert [sorted(l) for l in lines] == [sorted(x) for x in (
        [(1, 1), (2, 0), (2, 1)], [(3, 1), (2, 2), (3, 2)], [(5, 3), (4, 4), (5, 4)],
        [(9, 7), (10, 8), (9, 8)], [(19, 15), (18, 14), (18, 15)], [(37, 29), (36, 30), (37, 30)],
        [(73, 59), (74, 58), (74, 59)])]


def test_chain_plan_is_add_double_add_with_small_differences():
    rng = random.Random(3)
    L = 12
    pairs = [(0, 0), (1, 0), (0, 1), (1, 1), ((1 << L) - 1, (1 << L) - 1), (0, (1 << L) - 1)]
    pairs += [(rng.randrange(1 << L), rng.randrange(1 << L)) for _ in range(300)]
    for A, B in pairs:
        plan = XO.chain_plan(A, B, L)
        assert len(plan) == L
        for ops in plan:
            assert [op[0] for op in ops] == ["add", "dbl", "add"]
            for op in ops:
                if op[0] == "add":
                    d = op[4]
                    assert d in XO.DIFFS or (-d[0], -d[1]) in XO.DIFFS
    with pytest.raises(ValueError):
        XO.chain_plan(1 << L, 0, L)


def test_chain_2d_matches_scalar_multiplication_with_independent_points():
    T, E, C = _curves()
    p, n = T.p, T.n
    rng = random.Random(4)
    P = XO.EX.point_of_order(E, n, T.h, 21)
    Q = XO.EX.point_of_order(E, n, T.h, 500)
    assert Q[0] != P[0]
    xs = {(1, 0): (P[0], 1, False), (0, 1): (Q[0], 1, False),
          (1, 1): (E.add(P, Q)[0], 1, False), (1, -1): (E.add(P, E.neg(Q))[0], 1, False)}
    L = 16
    per_level = CM.xonly_op("xDBL", C.a, C.b, p)["M_eq"] + 2 * CM.xonly_op("xADD", C.a, C.b, p)["M_eq"]
    for k1, k2 in [(0, 1), (1, 0), (5, 0), (0, 7), (3, 3)] + [(rng.randrange(1 << L), rng.randrange(1 << L))
                                                              for _ in range(6)]:
        C.F.reset()
        R = C.normalise(XO.chain_2d(C, k1, k2, xs, L))
        assert C.F.snapshot()["M_eq"] == L * per_level            # same work for every multiscalar
        assert R == E.add(E.mul(k1, P), E.mul(k2, Q))[0]


def test_trace_one_elements():
    for D in (-619, -339, -4155, -3, -7):
        rows = XO.trace_one_elements(D, 9)
        assert rows[0]["element"] == [0, 1] and rows[0]["norm"] == (1 - D) // 4
        for r in rows:
            assert QO.trace(D, *r["element"]) == 1
            assert 4 * r["norm"] == 1 + r["m"] ** 2 * (-D)
    assert XO.trace_one_elements(-4) == [] and XO.trace_one_elements(-20) == []
    # omega - 1 = -conj(omega): the identity the construction rests on
    for D in (-619, -339, -4155):
        assert QO.conjugate(D, 0, 1) == (1, -1)
    # D = -3: omega is the unit zeta_6, and 1 - omega = zeta_6^-1 is a unit too
    assert QO.norm(-3, 0, 1) == 1 and QO.norm(-3, 1, -1) == 1


def test_chain_cost_closed_form():
    assert CM.xonly_chain_cost([31, 5])["M_eq"] == 64
    assert CM.xonly_chain_cost([5, 31])["M_eq"] > CM.xonly_chain_cost([31, 5])["M_eq"]
    assert CM.xonly_chain_cost([17, 5])["M_eq"] == 43
    assert CM.xonly_chain_cost([1039])["M_eq"] == 1558


def test_omega_and_its_conjugate_chain_on_cryptopro_b():
    pytest.importorskip("flint")
    T = _cryptopro_b()
    r = XO.run_curve(T, "targets.py", m=1, scalars=2, map_points=1)
    assert r["map_checks"] == {"x_beta_P": 1, "x_beta_bar_P": 1, "x_betaP_minus_P_eq_x_beta_bar_P": 1}
    assert r["beta"]["steps"] == [31, 5] and r["beta"]["norm"] == 155
    assert r["endomorphism_ops"]["beta"]["M_eq"] == r["endomorphism_ops"]["beta_bar"]["M_eq"] == 64
    assert r["endomorphism_ops"]["beta"]["M_eq"] == r["endomorphism_ops_model"]["M_eq"]
    for v, c in r["chain_2d"].items():
        assert c["ops_total"]["M_eq"]["mean"] == c["model"]["M_eq"]
        assert c["ops_total"]["M_eq"]["sd"] == 0
    assert r["ladder"]["ops"]["M_eq"]["mean"] == r["ladder"]["model"]["M_eq"] == 4608
    assert 1.18 <= r["R"] <= 1.28
