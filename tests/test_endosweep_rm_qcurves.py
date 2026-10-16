"""Tests for the RM-Kummer survey (rmkummer.py) and the Q-curve sweep (qcurves.py)."""
from __future__ import annotations

import random

import pytest
from sympy import isprime, primerange

from harness.endosweep import genus2 as G2
from harness.endosweep import quadorder as QO
from harness.endosweep import rmkummer as RK
from harness.endosweep import qcurves as QC


# --- rmkummer -----------------------------------------------------------------

def test_fft_family_counts_match_bruteforce_orders():
    rng = random.Random(3)
    for p in (101, 109):
        for g in (RK.D5, RK._random_quintic(p, rng)):
            fc = RK.family_counts(p, g)
            good = sorted(RK._nonsingular_ts(p, g))
            for t in rng.sample(good, 3):
                f = [(c + (t if i == 0 else 0)) % p for i, c in enumerate(g)]
                assert G2.jacobian_order(p, f) == fc.order(t)


def test_member_counter_matches_bruteforce():
    rng = random.Random(4)
    mc = RK.MemberCounter(103)
    for _ in range(3):
        f = RK.split_quintic(103, rng)
        assert len(RK._roots_fp(103, f)) == 5
        N, Nt, s1, s2 = mc.orders(f)
        assert N == G2.jacobian_order(103, f)
        assert N % 16 == 0 and Nt % 16 == 0          # full rational 2-torsion on both sides


def test_split_criterion_and_permutation_property():
    for p in primerange(7, 260):
        if p % 5 in (1, 4):
            fc = RK.family_counts(p, RK.D5)
            for t in range(p):
                if t in (2, p - 2):
                    continue
                assert (fc.roots[t] == 5) == RK.split_criterion(p, t), (p, t)
        elif p % 5 in (2, 3):
            vals = {(x**5 - 5 * x**3 + 5 * x) % p for x in range(p)}
            assert len(vals) == p                      # D_5 permutes F_p: one root for every t
    assert (2**127 - 1) % 5 == 2


def test_rm_charpoly_factors_over_q_sqrt5_only_for_the_family():
    p = 131
    fc = RK.family_counts(p, RK.D5)
    good = RK._nonsingular_ts(p, RK.D5)
    assert all(RK.rm_factorization(p, *fc.s1_s2(t)) is not None for t in good)
    g = [0, 7, 11, 13, 0, 1]
    fg = RK.family_counts(p, g)
    frac = sum(RK.rm_factorization(p, *fg.s1_s2(t)) is not None for t in range(p)) / p
    assert frac < 0.2


def test_explicit_rm_endomorphism_on_points():
    r = RK.verify_rm_member(109, 44)
    assert r["ok"] and r["order"] == 16 * r["l"] and isprime(r["l"])
    lam, l = r["eigenvalue_on_J[l]"], r["l"]
    assert (lam * lam + lam - 1) % l == 0
    r = RK.verify_rm_member(131, 8)
    assert r["ok"] and r["p_mod_5"] == 1


def test_ladder_ceiling():
    assert RK.ladder_vs_2d_chain(1.0)["speedup"] == pytest.approx(4 / 3)
    assert RK.ladder_vs_2d_chain(0.0)["speedup"] == pytest.approx(2.0)


# --- qcurves ------------------------------------------------------------------

def test_all_elements_of_norm_agree_with_search():
    for D in (-40, -15, -23):
        for M in (6, 14, 21, 35, 46):
            got = {e for e in QC.all_elements_of_norm(D, M)}
            want = {(e.a, e.b) for e in QO.elements_of_norm(D, M, primitive_only=False,
                                                            up_to_units_and_conjugation=False)
                    if e.b != 0 and __import__("math").gcd(e.b, M) == 1}
            want |= {(-a, -b) for a, b in want}          # elements_of_norm lists b > 0 only
            assert got == want, (D, M)


@pytest.mark.parametrize("d", [2, 3])
def test_explicit_qcurve_psi_squared(d):
    r = QC.explicit_qcurve(d, seed=1 + d, want_order=False)
    assert r.psi_sign in (1, -1)
    assert all(r.checks.values()), r.checks


def test_builder_on_fourq_w_finds_psi_with_eigenvalue():
    r = QC.fourq_w_crosscheck(3)
    assert r.psi_sign == 1 and r.cofactor == 392 and r.eigenvalue is not None
    assert all(r.checks.values()), r.checks


def test_cm_sweep_reproduces_fourq():
    out = QC.cm_sweep(Dmax=41, max_norm=7)
    fq = [c for c in out["candidates"] if c["is_fourq"]]
    assert len(fq) == 1
    c = fq[0]
    assert c["cofactor"] == 392 and c["D"] == -40
    assert "4 * psi_a with N(a) = 2" in c["fourq_crosscheck"]["psi (fourq.py)"]
    assert "4 * psi_a with N(a) = 5" in c["fourq_crosscheck"]["phi (fourq.py)"]
    assert c["best_4d"]["coeff_bits"] <= 63 and c["best_2d"]["coeff_bits"] >= 121


def test_map_cost_monotone():
    costs = [QC.map_cost(d) for d in (2, 3, 5, 7, 11, 13)]
    assert costs == sorted(costs) and costs[0] == pytest.approx(78.0)
