"""
Constant-fitting module for EXP-RELN-141a86, per the frozen
`constant_fitting` clause of specification.yaml:

  "On integer- or rational-valued targets (means, totals, degrees, exact
  probabilities) constants are reconstructed as exact rationals with
  denominator <= 64 by continued fractions from the least-squares value;
  on real-valued targets (Delta, E_m and R_k measured on a specific base)
  constants are least-squares fitted and are additionally refitted per
  rung subset for the constants-absorb-N check. At most two free
  constants per expression."

This stage (0a) does not fit anything to measured data -- no data is read
here. This module is written and unit-tested now (self-test at the bottom)
so that Stage 1 can call it directly on real fit tables without further
design.
"""

from __future__ import annotations

from fractions import Fraction
from typing import List, Optional, Sequence, Tuple

MAX_DENOMINATOR = 64
MAX_FREE_CONSTANTS = 2


def continued_fraction_reconstruct(value: float, max_denominator: int = MAX_DENOMINATOR) -> Fraction:
    """
    Exact-rational reconstruction of `value` by continued fractions,
    bounded to denominator <= max_denominator. This is Python's own
    convergents algorithm via Fraction.limit_denominator, which is the
    standard continued-fraction best-rational-approximation method.
    """
    return Fraction(value).limit_denominator(max_denominator)


def reconstruct_integer_or_rational_constant(
    least_squares_value: float,
    max_denominator: int = MAX_DENOMINATOR,
    residual_tolerance: float = 1e-9,
) -> Tuple[Fraction, float]:
    """
    Reconstructs an exact rational constant from a least-squares value for
    integer- or rational-valued targets. Returns (fraction, residual) where
    residual = least_squares_value - float(fraction). Does not silently
    accept a bad reconstruction: the caller must check the residual against
    the target's expected exactness (zero residual on integer-exact data).
    """
    frac = continued_fraction_reconstruct(least_squares_value, max_denominator)
    residual = least_squares_value - float(frac)
    return frac, residual


def least_squares_fit_constant(
    xs: Sequence[float], ys: Sequence[float], model
) -> Tuple[float, float]:
    """
    Fits a single free real constant c in model(x, c) = y by 1-D least
    squares (grid + refinement, dependency-free -- no numpy/scipy
    requirement in this run environment). Returns (c_hat, sum_sq_residual).

    `model` is a callable model(x, c) -> predicted y, linear in no
    particular sense; for the linear-in-c case (model(x, c) = c * f(x))
    this reduces to the closed-form least-squares solution automatically
    detected below for numerical stability.
    """
    n = len(xs)
    if n == 0:
        raise ValueError("least_squares_fit_constant: empty data")
    if len(ys) != n:
        raise ValueError("least_squares_fit_constant: xs/ys length mismatch")

    # Detect the common linear-in-c case: model(x, c) == c * model(x, 1)
    # (assume linearity if model(x, 2) == 2 * model(x, 1) for all sample x)
    try:
        linear = all(
            abs(model(x, 2.0) - 2.0 * model(x, 1.0)) < 1e-9 for x in xs
        )
    except Exception:
        linear = False

    if linear:
        f_vals = [model(x, 1.0) for x in xs]
        num = sum(f * y for f, y in zip(f_vals, ys))
        den = sum(f * f for f in f_vals)
        if den == 0:
            raise ValueError("least_squares_fit_constant: degenerate model (all-zero basis)")
        c_hat = num / den
        resid = sum((model(x, c_hat) - y) ** 2 for x, y in zip(xs, ys))
        return c_hat, resid

    # General case: coarse-to-fine grid search (deterministic, seeded only
    # by the fixed grid, no randomness).
    def sse(c):
        return sum((model(x, c) - y) ** 2 for x, y in zip(xs, ys))

    lo, hi = -1e6, 1e6
    best_c, best_sse = 0.0, sse(0.0)
    for _ in range(60):
        span = hi - lo
        step = span / 200.0
        c = lo
        while c <= hi:
            v = sse(c)
            if v < best_sse:
                best_sse, best_c = v, c
            c += step
        lo, hi = best_c - step, best_c + step
    return best_c, best_sse


def refit_per_rung_subset(
    rung_xs: Sequence[Sequence[float]],
    rung_ys: Sequence[Sequence[float]],
    model,
) -> List[Tuple[float, float]]:
    """
    Constants-absorb-N check support: refits the free constant separately
    on each rung's (xs, ys) subset (N frozen per rung), returning
    [(c_hat, residual_sse), ...] per rung so the caller can compare the
    constant's drift across rungs against its own least-squares
    uncertainty, per the frozen `constants_absorb_N_check` control.
    """
    return [least_squares_fit_constant(xs, ys, model) for xs, ys in zip(rung_xs, rung_ys)]


if __name__ == "__main__":
    # Self-test 1: exact-rational reconstruction of a binomial-mean style
    # constant with no measured data (pure numerics).
    exact_value = 1.0 / 3.0  # e.g. the m=3 leading coefficient of a mean law
    frac, resid = reconstruct_integer_or_rational_constant(exact_value)
    assert frac == Fraction(1, 3), (frac, resid)
    assert abs(resid) < 1e-9, resid

    # Self-test 2: exact reconstruction of an integer constant.
    frac2, resid2 = reconstruct_integer_or_rational_constant(3.0)
    assert frac2 == Fraction(3, 1)
    assert abs(resid2) < 1e-12

    # Self-test 3: least-squares fit of a linear-in-c model on synthetic
    # (non-measured) data: y = c * x, true c = 2.5.
    xs = [1.0, 2.0, 3.0, 4.0, 5.0]
    true_c = 2.5
    ys = [true_c * x for x in xs]
    c_hat, resid_sse = least_squares_fit_constant(xs, ys, lambda x, c: c * x)
    assert abs(c_hat - true_c) < 1e-6, c_hat
    assert resid_sse < 1e-9, resid_sse

    print("constant_fit.py self-test: OK")
