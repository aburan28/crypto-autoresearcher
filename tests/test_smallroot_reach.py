"""Tests for tools/smallroot_reach.py.

The load-bearing check is `test_jm_calculator_reproduces_coppersmith`: the
Jochemsz-May machinery is calibrated against a THEOREM (Coppersmith's univariate
reach is exactly 1/d), not against itself.  Everything downstream inherits that
calibration.
"""
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import smallroot_reach as R  # noqa: E402


def test_jm_calculator_reproduces_coppersmith():
    # Coppersmith: a degree-d univariate congruence mod p is solvable for roots
    # up to p^(1/d), exactly.  The JM sum must land on that for every d.
    for d in (1, 2, 3, 4, 5, 8, 16):
        beta, _ = R.jm_reach_limit(1, d, t_max=160)
        assert abs(beta - 1.0 / d) < 1e-4, (d, beta)


def test_jm_limit_matches_closed_form_full_box():
    for (n, d) in [(1, 2), (2, 2), (3, 2), (4, 2), (2, 4), (3, 8), (5, 2)]:
        _, eps = R.jm_reach_limit(n, d, t_max=80)
        assert abs(eps - float(R.jm_reach_closed_form(n, d))) < 1e-3, (n, d, eps)


def test_eps_required_reduces_to_the_proposal_inequality_at_w_zero():
    # IDEA-20260808-486ae2 states the win condition eps > m/(2(m-1)) at w = 0.
    for m in (4, 5, 6, 8, 16, 32):
        assert R.eps_required(m, 0) == Fraction(m, 2 * (m - 1))


def test_eps_required_rises_with_w_toward_one():
    for m in (6, 12, 24):
        vals = [float(R.eps_required(m, w)) for w in range(0, m - 1)]
        assert all(b > a for a, b in zip(vals, vals[1:])), vals
        assert vals[-1] < 1.0


def test_s3_support_is_the_thirteen_measured_monomials():
    sup = R.s3_support()
    assert len(sup) == 13                     # not the 27 of the full box [0,2]^3
    assert all(0 <= e <= 2 for a in sup for e in a)
    # symmetric in its three arguments, as S_3 must be
    assert {tuple(sorted(a)) for a in sup} == {tuple(sorted(a)) for a in sup}
    for a in sup:
        assert tuple(reversed(a)) in [tuple(x) for x in sup]


def test_extended_strategy_recovers_the_basic_bound_on_a_full_box():
    box = [(i, j, k) for i in range(3) for j in range(3) for k in range(3)]
    eps, _ = R.eps_extended_symmetric(box, t_max=8)
    assert abs(eps - 0.75) < 0.02, eps        # 2n/(d(n+1)) = 6/8


def test_sparse_s3_beats_the_full_box_but_stays_under_the_information_bound():
    eps, _ = R.eps_extended_symmetric(R.s3_support(), t_max=10)
    assert eps > 0.75                          # sparsity is a real gain
    assert eps < 1.0                           # never above the information bound


def test_l_equals_two_blocks_only_on_the_full_tree():
    # A kept node's value is an input to its parent block, so the w+1 blocks
    # consume m + w inputs; l = 2 forces w >= m-2.
    for m in (4, 6, 8, 12):
        for w in range(0, m - 1):
            if R.block_inputs(m, w) == 2:
                assert w >= m - 2, (m, w)


def test_no_configuration_is_alive_and_the_margin_is_worst_at_m4():
    rep = R.summarize([4, 5, 6, 8, 12, 16, 24, 32])
    assert rep["any_configuration_alive"] is False
    rows = [r for r in rep["rows"] if not r.get("is_best_for_m")]
    best = max(rows, key=lambda r: r["margin"])
    assert best["margin"] < 0
    assert (best["m"], best["w"]) == (4, 2)
    assert abs(best["margin"] - (-0.0481)) < 0.005


def test_closure_is_conservative_toward_the_attack():
    # l >= 4 blocks are credited a sparsity allowance larger than anything
    # measured at l = 2 (1.12x) or l = 3 (1.035x), and the bonus shrinks with l.
    assert R.SPARSITY_ALLOWANCE > R.MEASURED_REACH[2] / 0.75
    assert R.SPARSITY_ALLOWANCE > R.MEASURED_REACH[3] / 0.40
