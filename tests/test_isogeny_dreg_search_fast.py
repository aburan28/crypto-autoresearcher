"""Tests for the flint-backed fast engine, tools/isogeny_dreg_search_fast.py.

Every check is against the pure-Python reference engine or a brute-force
computation: kernel polynomials must be identical, the sieve class number
must equal the brute reduced-form count, the class mass must equal the
Hurwitz-Kronecker number, and an end-to-end search must enumerate the same
set of j-invariants as the reference.  Skipped when python-flint is absent.
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

pytest.importorskip("flint")

from tools import isogeny_dreg_search as S  # noqa: E402
from tools import isogeny_dreg_search_fast as F  # noqa: E402

P = 1009


def test_kernel_polynomials_match_reference_engine():
    rng = random.Random(1)
    compared = 0
    for (a, b) in [(3, 7), (11, 5), (100, 200), (1, 1), (0, 7), (5, 0), (42, 99)]:
        if S.is_singular(a, b, P):
            continue
        t = S.trace_exact(a, b, P)
        for ell in (2, 3, 5, 7, 11, 13):
            assert F.kernel_polynomials_fast(a, b, P, ell, t, rng) == S.rational_subgroups(a, b, P, ell, rng)
            compared += 1
    assert compared >= 30


def test_count_roots_fast_matches_brute_force():
    rng = random.Random(2)
    for _ in range(30):
        f = S._trim([rng.randrange(P) for _ in range(rng.randrange(2, 10))])
        if len(f) < 2:
            continue
        brute = sum(1 for x in range(P) if S.peval(f, x, P) == 0)
        assert F.count_roots_fast(f, P) == brute


def test_class_number_sieve_matches_brute_count():
    for D in (-3, -4, -7, -8, -15, -20, -23, -4823, -8911, -364235, -382515,
              -1000004, -3442635, -16000003, -20000011):
        if D % 4 not in (0, 1):
            continue
        assert F.class_number_sieve(D) == S.class_number_weighted(D), D


def test_class_mass_matches_hurwitz_class_number():
    for (p, t) in [(7127, -96), (35933, -34), (143729, 459), (863851, 113), (1009, 58)]:
        mass = F.class_mass(p, t)[0]
        assert mass == S.hurwitz_class_number(4 * p - t * t)


def test_fast_search_enumerates_same_class_as_reference():
    ref = S.search(P, 3, 7, seed=1, k=4, samples=16, nulls=2)
    fast = F.search_fast(P, 3, 7, seed=1, k=4, samples=16, nulls=2, workers=2, verbose=False)
    assert fast["exhaustive"] and ref["exhaustive"]
    assert {m["j"] for m in fast["members"]} == {m["j"] for m in ref["members"]}
    assert fast["summary"]["F2_dff"]["min"] == ref["summary"]["F2_dff"]["min"]
    assert fast["summary"]["F1_support"]["max"] == 13
    assert fast["class"]["order_checks_passed"] > 0


def test_fast_search_positive_control_flags_j_zero():
    rep = F.search_fast(P, 0, 7, seed=2, k=4, samples=16, nulls=2, workers=2,
                        with_f2=False, verbose=False)
    assert rep["exhaustive"]
    assert any("F1 support" in f for s in rep["survivors"] for f in s["flags"])
