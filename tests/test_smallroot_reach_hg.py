"""Tests for tools/smallroot_reach_hg.py (Howgrave-Graham comparison exponent).

The committed tests/test_smallroot_reach.py calibrates only against univariate
Coppersmith (reach exactly 1/d), where the TOOL and HG conventions coincide as
t -> infinity.  These tests calibrate where they DIFFER (n >= 2): the
information ceiling and Boneh-Durfee.
"""
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import smallroot_reach as R  # noqa: E402
from tools import smallroot_reach_hg as H  # noqa: E402


def test_univariate_matches_coppersmith_and_cannot_tell_conventions_apart():
    # Kept as a guard, NOT as the discriminating check: at n = 1 the two closed
    # forms are 2n/(d(n+1)) = 1/d = 2/(d(n+1)).
    for d in (1, 2, 3, 5, 8):
        beta, _ = H.jm_reach_limit_hg(1, d, t_max=160)
        assert abs(beta - 1.0 / d) < 1e-4, (d, beta)
        assert R.jm_reach_closed_form(1, d) == H.jm_reach_closed_form_hg(1, d)


def test_hand_instance_n1_d2_t1():
    # basis {p, pX, f}: det = p^2 X^3 < p^3  =>  X < p^(1/3).
    # (TOOL convention would say p^(2/3); see DEC-20260929-821525.)
    assert H.jm_reach_full_box_hg(1, 2, 1) == Fraction(1, 3)
    assert R.jm_reach_full_box(1, 2, 1) == Fraction(2, 3)


def test_full_box_limit_matches_closed_form():
    for (n, d) in [(1, 2), (2, 2), (3, 2), (4, 2), (2, 4), (3, 8), (5, 2)]:
        _, eps = H.jm_reach_limit_hg(n, d, t_max=80)
        assert abs(eps - float(H.jm_reach_closed_form_hg(n, d))) < 1e-3, (n, d, eps)


def test_information_ceiling_one_equation_never_exceeds_eps_one():
    # A single congruence mod p cannot determine roots in a box of volume > p.
    # TOOL's 2n/(d(n+1)) breaks this for d = 1, n >= 2; HG never does.
    for n in range(1, 9):
        for d in range(1, 9):
            assert H.jm_reach_closed_form_hg(n, d) <= 1, (n, d)
            assert H.jm_reach_full_box_hg(n, d, 12) * n <= 1, (n, d)
    assert R.jm_reach_closed_form(2, 1) > 1          # documents the defect


def test_boneh_durfee_x_shifts_only_gives_delta_one_quarter():
    # f = xy + Ax + 1 (mod e), X = e^delta, Y = e^(1/2).  The JM shift set built
    # from x-shifts only is the classical Boneh-Durfee basic lattice, delta < 1/4.
    bd = [(1, 1), (1, 0), (0, 0)]
    t = 60
    below = H.success_ratio(bd, t, (Fraction(24, 100), Fraction(1, 2)), leading=(1, 1))
    above = H.success_ratio(bd, t, (Fraction(26, 100), Fraction(1, 2)), leading=(1, 1))
    assert below < 1.0 < above, (below, above)
    # the TOOL convention accepts delta far above any known bound (0.292)
    s_p, s_vec, dim = R.jm_reach_extended(bd, t, leading=(1, 1))
    lhs = Fraction(74, 100) * s_vec[0] + Fraction(1, 2) * s_vec[1]
    assert float(lhs / s_p) < 1.0


def test_nested_shift_sets_make_hg_rhs_the_sum_of_levels():
    # t*dim - s_p == sum_{k>=1}|M_k| because M_k is contained in M_{k-1}.
    sup = R.s3_support()
    t = 5
    rhs, _, dim = H.hg_rhs(sup, t)
    lead = max(sup, key=lambda a: (sum(a), a))
    levels = 0
    for k in range(1, t + 1):
        shift = tuple(k * c for c in lead)
        levels += len({tuple(s + b for s, b in zip(shift, a))
                       for a in R.minkowski_power(sup, t - k)})
    assert rhs == levels


def test_extended_hg_is_tool_over_n_in_the_limit():
    # eps_HG = eps_TOOL / n for any support.  Checked on the full box (exact
    # closed forms) and on the sparse S_3 polytope (numerically).
    for (n, d) in [(2, 2), (3, 2), (4, 4)]:
        assert (R.jm_reach_closed_form(n, d) / n) == H.jm_reach_closed_form_hg(n, d)
    e_hg, _ = H.eps_extended_symmetric_hg(R.s3_support(), t_a=8, t_b=16)
    assert abs(e_hg - H.MEASURED_REACH_HG[2]) < 0.01, e_hg
    assert abs(H.MEASURED_REACH_HG[2] * 3 - R.MEASURED_REACH[2]) < 1e-12
    assert abs(H.MEASURED_REACH_HG[3] * 4 - R.MEASURED_REACH[3]) < 1e-12


def test_sparse_s3_beats_its_full_box_under_hg_too():
    full = float(H.jm_reach_closed_form_hg(3, 2))      # 0.25
    assert H.MEASURED_REACH_HG[2] > full               # sparsity is a real gain
    assert H.MEASURED_REACH_HG[2] < 0.30               # but nowhere near 0.84
    assert R.SPARSITY_ALLOWANCE > H.MEASURED_REACH_HG[2] / 0.25
    assert R.SPARSITY_ALLOWANCE > H.MEASURED_REACH_HG[3] / 0.10


def test_no_configuration_is_alive_and_the_gap_is_at_least_one_half():
    rep = H.summarize_hg([4, 5, 6, 8, 12, 16, 24, 32])
    assert rep["any_configuration_alive"] is False
    plain = [r for r in rep["rows"] if not r.get("is_best_for_m")]
    # corrected: the gap is not 0.048.  It is >= ~1/2 everywhere in range.
    assert max(r["margin"] for r in plain) < -0.5
    by_m = {r["m"]: r for r in rep["best_per_m"]}
    assert (by_m[4]["w"], round(by_m[4]["margin"], 3)) == (2, -0.609)
    # (4,0) is close behind (4,2); record that the ordering is not robust
    r40 = next(r for r in plain if (r["m"], r["w"]) == (4, 0))
    assert abs(r40["margin"] - by_m[4]["margin"]) < 0.02


def test_margin_is_not_monotone_widening_in_m_under_hg():
    # The TOOL note claimed the margin widens monotonically in every direction.
    # Under HG the w = 0 margin shrinks toward -1/2 as m grows.
    rep = H.summarize_hg([4, 8, 16, 32])
    w0 = [r for r in rep["rows"] if r["w"] == 0 and not r.get("is_best_for_m")]
    margins = [r["margin"] for r in sorted(w0, key=lambda r: r["m"])]
    assert all(b > a for a, b in zip(margins, margins[1:])), margins
    assert margins[-1] < -0.5


def test_frozen_instrument_is_untouched():
    # EXP-PFDR-9b4f2a freezes tools/smallroot_reach.py: its published numbers
    # must still be the TOOL-convention ones.
    assert R.MEASURED_REACH[2] == 0.840814
    assert R.jm_reach_closed_form(3, 2) == Fraction(3, 4)
