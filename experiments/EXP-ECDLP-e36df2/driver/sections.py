"""Three contrast sections for EXP-ECDLP-e36df2 Stage 2/3, per
specification.yaml inputs.instrument items (1)-(2):

  s_x    -- Teichmuller-lift x, Hensel-lift y. Reuses
            frozen_ref.teichmuller_section UNMODIFIED (item: "the existing
            instrument.teichmuller_section, reused unmodified").
  s_y    -- Teichmuller-lift y, Hensel-lift x from the cubic. NEW,
            independently coded (item (1)): lifts the y-coordinate to its
            Teichmuller representative, then Hensel-Newton-lifts an x root
            of x^3 + A x + (B - y_t^2) = 0 starting from the known mod-p
            root x0_true, doubling precision each step exactly like
            frozen_ref.hensel_lift_sqrt's own Newton iteration (same
            pattern, applied to a different polynomial).
  s_rand -- seeded pseudorandom-digit null object (item (2)): a valid
            on-curve point with no relationship to the true global lift
            beyond agreeing mod p, built by picking a pseudorandom x' with
            the correct residue mod p and Hensel-lifting y from it.

All three return (x, y) mod p^K, matching frozen_ref.teichmuller_section's
own return convention, so digit_of_section (below) can treat them
uniformly via the SAME defect-digit computation frozen_ref.split_point's
machinery uses (teichmuller_defect_digit-style pattern, per
specification.yaml Stage 2), just rewired onto fastseries's cached-series
evaluator for tractable cost at this ladder's depth.
"""
from __future__ import annotations

import hashlib

from frozen_ref import (
    teichmuller_section, teichmuller_lift_scalar, hensel_lift_sqrt,
    padd, pneg, is_identity, to_tw, valuation_modp, _exponent,
)
from fastseries import fast_eval_reduced


def s_x_section(a: int, b: int, p: int, K: int, x0_true: int, y0_true: int):
    """Reuse of frozen_ref.teichmuller_section, unmodified."""
    return teichmuller_section(a, b, p, K, x0_true, y0_true)


def _hensel_lift_cubic_root(x0: int, y_t_squared_mod, a: int, b: int,
                             p: int, K: int) -> int:
    """Newton-lift a root of f(x) = x^3 + a x + (b - y_t_squared) mod p^K,
    starting from x0 (a root mod p, i.e. x0^3 + a x0 + b == y0_true^2 mod p
    -- true since x0_true, y0_true is the real point mod p and y_t_squared
    == y0_true^2 mod p by Teichmuller-lift construction). f'(x0) = 3 x0^2 + a
    must be a unit mod p (checked); doubles precision each Newton step,
    exactly the pattern frozen_ref.hensel_lift_sqrt uses for its own
    (different) polynomial y^2 - rhs."""
    N = p ** K
    x = x0 % p
    fpx0 = (3 * x * x + a) % p
    if fpx0 == 0:
        raise ValueError("_hensel_lift_cubic_root: f'(x0) == 0 mod p "
                          "(3x0^2+a not a unit); cannot Hensel-lift")
    prec = 1
    cur_mod = p
    while prec < K:
        prec = min(2 * prec, K)
        cur_mod = p ** prec
        rhs = y_t_squared_mod % cur_mod
        fx = (x * x * x + a * x - (rhs - b)) % cur_mod
        fpx = (3 * x * x + a) % cur_mod
        fpx_inv = pow(fpx, -1, cur_mod)
        x = (x - fx * fpx_inv) % cur_mod
    return x % N


def s_y_section(a: int, b: int, p: int, K: int, x0_true: int, y0_true: int):
    """s_y(R) = (x, omega(y0)), the y-Teichmuller / x-Hensel mirror of
    s_x_section. omega(y0) is the Teichmuller lift of R's y-coordinate;
    x is the Hensel-Newton-lifted root of the cubic at that fixed y,
    branch fixed by x0_true mod p."""
    N = p ** K
    y0 = y0_true % p
    if y0 == 0:
        raise ValueError("s_y_section: y0 == 0 mod p has no (p-1)-th root "
                          "of unity Teichmuller lift")
    y_t = teichmuller_lift_scalar(y0, p, K)
    y_t_sq = (y_t * y_t) % N
    x = _hensel_lift_cubic_root(x0_true, y_t_sq, a, b, p, K)
    return (x % N, y_t % N)


def _prng_digit_mod(seed: int, curve_idx: int, p: int, m: int, modulus: int) -> int:
    """Deterministic pseudorandom integer in [0, modulus), seeded from
    (seed, curve_idx, p, m). SHA-256-based counter construction (no
    dependence on Python's random module's internal state layout, so this
    is stable across Python versions -- important since this value is part
    of a frozen, reproducible protocol)."""
    out = 0
    bits_needed = modulus.bit_length() + 64
    counter = 0
    acc_bits = 0
    while acc_bits < bits_needed:
        h = hashlib.sha256(
            f"s_rand:{seed}:{curve_idx}:{p}:{m}:{counter}".encode()
        ).digest()
        out = (out << 256) | int.from_bytes(h, "big")
        acc_bits += 256
        counter += 1
    return out % modulus


def s_rand_section(a: int, b: int, p: int, K: int, x0_true: int, y0_true: int,
                    seed: int, curve_idx: int, m: int):
    """Seeded pseudorandom-digit null-object section (specification.yaml
    inputs.instrument item (2)): x' = x0 + p * PRNG(seed, curve_idx, p, m)
    mod p^(K-1), y Hensel-lifted from x' with the branch fixed by y0_true
    mod p. x0_true is the true value only mod p (the top digit is genuine,
    every higher digit is pseudorandom noise uncorrelated with the true
    global lift, which is exactly the null-object property this control
    needs)."""
    N = p ** K
    x0 = x0_true % p
    if K <= 1:
        xprime = x0 % N
    else:
        upper_modulus = p ** (K - 1)
        r = _prng_digit_mod(seed, curve_idx, p, m, upper_modulus)
        xprime = (x0 + p * r) % N
    rhs_mod = (xprime * xprime * xprime + a * xprime + b) % N
    y = hensel_lift_sqrt(y0_true % p, rhs_mod, p, K)
    return (xprime % N, y % N)


def digit_of_section_minus_torsion(section_pt, p: int, t_mS_proj, A: int,
                                    N_big: int, reduced_log) -> int | None:
    """d = digit of section_pt - t_mS_proj, mirroring
    stage23.teichmuller_defect_digit's construction exactly (same
    subtraction, same (t,w)-chart + log-series read), but evaluating the
    formal log via fastseries's cached-coefficient Horner loop instead of
    re-reducing instrument.eval_series_mod's Fraction coefficients on every
    call. `t_mS_proj` = [m mod n] t(S) is computed ONCE by the caller and
    shared across all three sections' digit reads for the same m (avoiding
    three redundant pmul calls per m). Returns None where
    teichmuller_defect_digit itself would return 0 for the "diff is
    identity" case (an exact coincidence at that valuation), matching its
    convention."""
    x, y = section_pt
    diff = padd((x % N_big, y % N_big, 1), pneg(t_mS_proj, N_big), A, N_big)
    if is_identity(diff):
        return 0
    t2, w2, N2 = to_tw(diff, N_big, p)
    K2 = _exponent(N2, p)
    ell = fast_eval_reduced(reduced_log, t2, N2)
    v2 = valuation_modp(ell, p, K2)
    if v2 >= K2:
        return 0
    return ((ell % (p ** K2)) // (p ** v2)) % p
