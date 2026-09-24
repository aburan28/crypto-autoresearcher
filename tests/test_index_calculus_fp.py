"""Tests for crypto_autoresearcher.index_calculus (ECDLP index calculus over F_p)."""

from __future__ import annotations

import random

import pytest

from crypto_autoresearcher.index_calculus import (
    FactorBase,
    generate_prime_order_curve,
    pollard_rho,
    solve_index_calculus,
)
from crypto_autoresearcher.index_calculus.__main__ import main
from crypto_autoresearcher.index_calculus.curve import is_probable_prime, sqrt_mod
from crypto_autoresearcher.index_calculus.decompose import decompose
from crypto_autoresearcher.index_calculus.linalg import EliminationState
from crypto_autoresearcher.index_calculus.semaev import s3, s3_roots


@pytest.fixture(scope="module")
def curve14():
    return generate_prime_order_curve(14, seed=3)


def test_curve_order_is_certified_prime(curve14):
    E, P = curve14
    assert is_probable_prime(E.order)
    assert E.order != E.p
    assert E.a % E.p and E.b % E.p
    assert E.is_on_curve(P)
    assert E.mul(E.order, P) is None


def test_generation_is_deterministic():
    E1, P1 = generate_prime_order_curve(12, seed=7)
    E2, P2 = generate_prime_order_curve(12, seed=7)
    assert (E1.p, E1.a, E1.b, E1.order, P1) == (E2.p, E2.a, E2.b, E2.order, P2)


def test_sqrt_mod_both_residue_classes():
    for p in (10007, 10009, 65537):  # p = 3 mod 4 and p = 1 mod 4
        for n in range(1, 200):
            r = sqrt_mod(n, p)
            if r is not None:
                assert r * r % p == n


def test_s3_vanishes_on_sums_and_roots_recover_them(curve14):
    E, _ = curve14
    rng = random.Random(1)
    for _ in range(200):
        A, B = E.random_point(rng), E.random_point(rng)
        C = E.add(A, B)
        if C is None:
            continue
        assert s3(E, A[0], B[0], C[0]) == 0
        assert C[0] in s3_roots(E, A[0], B[0])


def test_s3_nonzero_on_random_triples(curve14):
    E, _ = curve14
    rng = random.Random(2)
    hits = sum(s3(E, rng.randrange(E.p), rng.randrange(E.p), rng.randrange(E.p)) == 0
               for _ in range(500))
    assert hits < 10


@pytest.mark.parametrize("kind", ["small_x", "subgroup", "random"])
def test_factor_base_points_on_curve_one_per_pair(curve14, kind):
    E, _ = curve14
    fb = {"small_x": FactorBase.small_x, "random": FactorBase.random,
          "subgroup": FactorBase.subgroup}[kind](E, 30)
    assert len(fb) > 0
    xs = [P[0] for P in fb.points]
    assert len(set(xs)) == len(xs)
    assert all(E.is_on_curve(P) for P in fb.points)
    if kind == "subgroup":
        d, g = fb.params["d"], fb.params["coset"]
        assert (E.p - 1) % d == 0
        assert all(pow(x, d, E.p) == pow(g, d, E.p) for x in xs)


@pytest.mark.parametrize("m", [2, 3])
def test_decomposition_is_verified_sum(curve14, m):
    E, _ = curve14
    fb = FactorBase.small_x(E, 40)
    rng = random.Random(m)
    found = 0
    for _ in range(60):
        R = E.random_point(rng)
        rel = decompose(E, fb, R, m)
        if rel is None:
            continue
        found += 1
        S = None
        for i, s in rel:
            S = E.add(S, fb.points[i] if s > 0 else E.neg(fb.points[i]))
        assert S == R and len(rel) == m
    assert found > 0


def test_elimination_recovers_known_k():
    N, k = 101, 37
    rng = random.Random(0)
    logs = [rng.randrange(N) for _ in range(5)]
    la = EliminationState(N)
    got = None
    while got is None:
        i, j = rng.sample(range(5), 2)
        b = rng.randrange(1, N)
        a = (logs[i] + logs[j] - b * k) % N
        got = la.add_row({i: 1, j: 1}, -b, a)
    assert got == k


@pytest.mark.parametrize("m,fb", [(2, "small_x"), (2, "subgroup"), (2, "random"),
                                  (3, "small_x")])
def test_index_calculus_solves_and_verifies(curve14, m, fb):
    E, P = curve14
    k = 4242 % E.order
    Q = E.mul(k, P)
    res = solve_index_calculus(E, P, Q, m=m, fb_kind=fb, seed=1)
    assert res.verified and res.k == k
    assert res.relations >= 1 and res.s3_solves > 0


def test_rho_solves(curve14):
    E, P = curve14
    Q = E.mul(1234, P)
    rr = pollard_rho(E, P, Q, seed=1)
    assert rr.verified and rr.k == 1234 % E.order


def test_cli_sweep_smoke(capsys):
    assert main(["sweep", "--bits", "10", "12", "--curves", "1", "--json"]) == 0
    assert '"fits"' in capsys.readouterr().out
