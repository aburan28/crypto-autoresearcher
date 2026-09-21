"""Curve-level formal-group construction: w(t), F(t), log(t), exp(u).

Built once per curve (a, b); does not depend on p. See
experiments/EXP-ECDLP-a26bde/derivation_note.md for the derivation and
derive_formulas.py for the symbolic checks these formulas satisfy.
"""
from __future__ import annotations

from fractions import Fraction

from padic import (
    Series, WORKING_DEGREE, series_add, series_mul, series_scale,
    series_deriv, series_integrate, series_divide_same_valuation,
    series_valuation, series_reversion, series_trim,
)


def compute_w_series(a: int, b: int, D: int = WORKING_DEGREE, iters: int = 40) -> Series:
    """w(t) solving w = t^3 + a t w^2 + b w^3, by fixed-point iteration on
    truncated polynomials with exact Fraction coefficients. w0 = t^3."""
    a_, b_ = Fraction(a), Fraction(b)
    t3 = [Fraction(0)] * (D + 1)
    if D >= 3:
        t3[3] = Fraction(1)
    w = list(t3)
    for _ in range(iters):
        w2 = series_mul(w, w, D)
        w3 = series_mul(w2, w, D)
        t_w2 = [Fraction(0)] * (D + 1)
        for i in range(D + 1):
            if i + 1 <= D:
                t_w2[i + 1] = w2[i]
        new_w = series_add(t3, series_add(series_scale(t_w2, a_, D),
                                           series_scale(w3, b_, D), D), D)
        if new_w == w:
            break
        w = new_w
    else:
        raise RuntimeError("compute_w_series: fixed-point iteration did not "
                            "converge in the allotted iterations")
    return w


def compute_F_series(w: Series, D: int = WORKING_DEGREE) -> Series:
    """F(t) = (t w'(t) - w(t)) / (2 w(t)), valuation-aware division."""
    wprime = series_deriv(w, D)
    t_wprime = [Fraction(0)] * (D + 1)
    for i in range(D):
        if i + 1 <= D:
            t_wprime[i + 1] = wprime[i]
    numerator = [t_wprime[i] - w[i] for i in range(D + 1)]
    denominator = series_scale(w, Fraction(2), D)
    F = series_divide_same_valuation(numerator, denominator, D)
    return F


def compute_log_series(F: Series, D: int = WORKING_DEGREE) -> Series:
    """log(t) = t + integral(F - 1) ... precisely: log'(t) = F(t), log(0)=0.
    Equivalent phrasing used in the task: log(t) = t + sum_{i>=1} F_i/(i+1) t^(i+1).
    series_integrate already implements int(F dt) with F[0]=1 giving the
    leading t term for free (F_0/(0+1) t^1 = t)."""
    return series_integrate(F, D)


def compute_exp_series(log_series: Series, D: int = WORKING_DEGREE) -> Series:
    """Compositional inverse of log_series (log_series[0]=0, log_series[1]=1
    required by series_reversion)."""
    return series_reversion(log_series, D)


class FormalGroup:
    """Precomputed formal-group data for one curve (a, b); independent of p."""

    def __init__(self, a: int, b: int, D: int = WORKING_DEGREE):
        self.a, self.b, self.D = a, b, D
        self.w = compute_w_series(a, b, D)
        self.F = compute_F_series(self.w, D)
        self.log = compute_log_series(self.F, D)
        self.exp = compute_exp_series(self.log, D)
        self._verify()

    def _verify(self):
        assert self.F[0] == 1, f"F(0) should be 1, got {self.F[0]}"
        assert self.log[0] == 0 and self.log[1] == 1
        # log(exp(u)) == u to working degree (compositional-inverse check)
        from padic import series_compose
        check = series_compose(self.log, self.exp, self.D)
        expected = [Fraction(0)] * (self.D + 1)
        if self.D >= 1:
            expected[1] = Fraction(1)
        assert check == expected, (
            f"log(exp(u)) != u to degree {self.D}: got {check}")
