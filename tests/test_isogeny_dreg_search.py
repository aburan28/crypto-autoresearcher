"""Tests for tools/isogeny_dreg_search.py.

Every check here is against an INDEPENDENT computation: brute-force root
counts, brute-force enumeration of all curves over a small field, the
classical modular polynomials, and closed-form predictions the design
pre-registers (docs in analysis/isogeny-dreg-search/DESIGN.md).
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import isogeny_dreg_search as S  # noqa: E402


P = 1009


def test_polynomial_divmod_and_gcd_roundtrip():
    rng = random.Random(1)
    for _ in range(50):
        f = S._trim([rng.randrange(P) for _ in range(rng.randrange(1, 12))])
        g = S._trim([rng.randrange(P) for _ in range(rng.randrange(1, 8))])
        if not g:
            continue
        q, r = S.pdivmod(f, g, P)
        assert S.padd(S.pmul(q, g, P), r, P) == f
        assert len(r) < len(g)


def test_count_roots_matches_brute_force():
    rng = random.Random(2)
    for _ in range(40):
        f = S._trim([rng.randrange(P) for _ in range(rng.randrange(2, 10))])
        if len(f) < 2:
            continue
        brute = sum(1 for x in range(P) if S.peval(f, x, P) == 0)
        assert S.count_roots(f, P) == brute


def test_factoring_recovers_irreducible_factors():
    rng = random.Random(3)
    # product of three distinct random monic quadratics/cubics, squarefree
    facs = []
    while len(facs) < 3:
        d = rng.choice([2, 3])
        f = [rng.randrange(P) for _ in range(d)] + [1]
        if S.count_roots(f, P) == 0 and (d == 2 or all(
                len(S.pgcd(f, S.psub(S.ppowmod([0, 1], P ** i, f, P), [0, 1], P), P)) == 1
                for i in (1,))):
            if f not in facs:
                facs.append(f)
    prod = [1]
    for f in facs:
        prod = S.pmul(prod, f, P)
    found = []
    for d, g in S.distinct_degree_factor(prod, P):
        if d is None:
            continue
        found.extend(S.equal_degree_factor(g, d, P, rng))
    assert sorted(found) == sorted(S.pmonic(f, P) for f in facs)


def test_division_polynomial_degree_and_leading_coefficient():
    dp = S.DivisionPolynomials(3, 7, P)
    for ell in (3, 5, 7, 11, 13):
        f = dp(ell)
        assert len(f) - 1 == (ell * ell - 1) // 2
        assert f[-1] == ell % P


def test_division_polynomial_roots_are_torsion_x_coordinates():
    # every rational x-root of psi_ell whose lift is on the curve is an
    # ell-torsion point, checked by scalar multiplication
    a, b = 3, 7
    dp = S.DivisionPolynomials(a, b, P)
    for ell in (3, 5, 7):
        f = dp(ell)
        for x in range(P):
            if S.peval(f, x, P) == 0:
                y = S.sqrt_mod((x ** 3 + a * x + b) % P, P)
                if y is not None:
                    assert S.ec_mul(ell, (x, y), a, P) is None


def test_velu_codomain_preserves_trace_and_modular_relation():
    rng = random.Random(4)
    for (a, b) in [(3, 7), (11, 5), (100, 200), (1, 1)]:
        if S.is_singular(a, b, P):
            continue
        t = S.trace_exact(a, b, P)
        found_any = False
        for ell in (2, 3, 5, 7):
            for h in S.rational_subgroups(a, b, P, ell, rng):
                found_any = True
                a2, b2 = S.velu_from_kernel_polynomial(a, b, P, h)
                assert not S.is_singular(a2, b2, P)
                assert S.trace_exact(a2, b2, P) == t
                if ell in S.MODULAR:
                    assert S.MODULAR[ell](S.j_invariant(a, b, P), S.j_invariant(a2, b2, P), P) == 0
        assert found_any


def test_velu_agrees_with_harness_point_based_velu():
    harness_iso = pytest.importorskip("harness.isogeny_class")
    from harness.toycurve import EllipticCurve
    rng = random.Random(5)
    a, b = 3, 7
    E = EllipticCurve(P, a, b)
    dp = S.DivisionPolynomials(a, b, P)
    for ell in (3, 5, 7):
        for h in S.rational_subgroups(a, b, P, ell, rng):
            a2, b2 = S.velu_from_kernel_polynomial(a, b, P, h)
            # find a kernel generator over F_p if the kernel is pointwise rational
            x0 = next((x for x in range(P) if S.peval(h, x, P) == 0), None)
            if x0 is None:
                continue
            y0 = S.sqrt_mod((x0 ** 3 + a * x0 + b) % P, P)
            if y0 is None:
                continue
            ref = harness_iso.velu_odd(E, (x0, y0), ell)
            assert (ref[0], ref[1]) == (a2, b2)


def test_class_enumeration_matches_brute_force_small_field():
    p = 211
    rng = random.Random(6)
    classes: dict[int, set] = {}
    rep: dict[int, tuple[int, int]] = {}
    for a in range(p):
        for b in range(p):
            if S.is_singular(a, b, p):
                continue
            t = S.trace_exact(a, b, p)
            classes.setdefault(t, set()).add(S.iso_key(a, b, p))
            rep.setdefault(t, (a, b))
    checked = 0
    for t, keys in classes.items():
        if t % p == 0:
            continue
        a, b = rep[t]
        enum = S.enumerate_isogeny_class(a, b, p, rng, primes=(2, 3, 5, 7, 11, 13, 17, 19, 23))
        got = {S.iso_key(m.a, m.b, p) for m in enum.members}
        assert got == keys, (t, len(got), len(keys))
        assert enum.certified
        assert enum.observed_weighted == enum.predicted_weighted
        checked += 1
    assert checked > 40


def test_first_fall_degree_prereg_prediction_h_plus_2():
    # x1^{h-2} S_3 - (x2^2 coefficient) (x1^h - 1) drops degree at D = h + 2;
    # this is the closed-form prediction the design pre-registers and it must
    # be class-constant AND null-constant.
    for (a, b) in [(3, 7), (11, 5), (100, 200)]:
        for h in (2, 3, 4, 6):
            assert S.f2_first_fall_degree(a, b, P, h, 5, h + 10) == h + 2


def test_fibre_root_counts_are_multiples_of_k():
    rng = random.Random(7)
    k = 4
    res = S.f3_fibre_roots(3, 7, P, k, 100, rng)
    assert all(int(r) % k == 0 for r in res["histogram"])
    assert 0 <= res["mean"] <= 2 * k


def test_search_end_to_end_certified_and_no_survivors_on_generic_curve():
    rep = S.search(P, 3, 7, seed=1, k=4, samples=32, nulls=3, primes=(2, 3, 5, 7, 11, 13))
    assert rep["exhaustive"] is True
    assert rep["class_size"] == len(rep["members"])
    assert rep["summary"]["F1_support"]["min"] == rep["summary"]["F1_support"]["max"] == 13
    assert rep["summary"]["F2_dff"]["min"] == rep["summary"]["F2_dff"]["max"]
    assert rep["controls"]["order_checks_passed"] > 0
    assert rep["controls"]["modular_polynomial_checks_passed"] > 0


def test_search_flags_j_zero_member_as_survivor_when_present():
    # a class with D_0 = -3 contains j = 0 curves, whose S_3 support drops
    # below 13; the search must surface them as survivors (positive control).
    p = 1009
    rng = random.Random(8)
    assert p % 3 == 1
    a, b = 0, 7
    rep = S.search(p, a, b, seed=2, k=4, samples=16, nulls=2, with_f2=False)
    assert rep["exhaustive"] is True
    js = {r["j"] for r in rep["members"]}
    assert 0 in js
    assert any("F1 support" in f for s in rep["survivors"] for f in s["flags"])
