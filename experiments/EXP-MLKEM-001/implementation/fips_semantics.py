"""FIPS 203 and pinned-estimator rounding / modulo-q semantics."""

from __future__ import annotations

from fractions import Fraction
from math import comb
from typing import Dict, Iterable, List, Tuple

Q = 3329
HALF_Q = 1664  # centered reps in [-1664, 1664]


def ctr_q(x: int, q: int = Q) -> int:
    """Centered representative in [-floor(q/2), ceil(q/2)] for odd q: [-1664, 1664]."""
    r = x % q
    if r > HALF_Q:
        r -= q
    return r


def canonical_q(x: int, q: int = Q) -> int:
    return x % q


def round_ties_up(num: int, den: int) -> int:
    """Nearest integer with ties toward +infinity (FIPS 203).

    Equivalent to floor((num + den/2) / den) for positive den, using integers:
    floor((2*num + den) / (2*den)) when den odd? For FIPS Compress:
      Compress_d(x) = floor( (2^d / q) * x + 1/2 ) mod 2^d
    i.e. floor( (2*2^d*x + q) / (2*q) ) when working with integers.
    """
    if den <= 0:
        raise ValueError("den must be positive")
    # round(num/den) with ties away toward +inf:
    # floor(num/den + 1/2) = floor((2*num + den) / (2*den))
    return (2 * num + den) // (2 * den)


def round_half_even(num: int, den: int) -> int:
    """Python3 round half-to-even on num/den using exact rationals."""
    # Use Fraction and round half-even via builtin round on float only if exact;
    # Prefer integer algorithm: round(Fraction(num, den)).
    return round(Fraction(num, den))


def compress_fips(x: int, d: int, q: int = Q) -> int:
    """Compress_d with FIPS ties-up; x canonical in [0, q-1]."""
    x = canonical_q(x, q)
    # floor(2^d * x / q + 1/2) mod 2^d
    return round_ties_up(x * (1 << d), q) % (1 << d)


def decompress_fips(y: int, d: int, q: int = Q) -> int:
    """Decompress_d with FIPS ties-up."""
    y = y % (1 << d)
    return round_ties_up(y * q, 1 << d)


def compress_python(x: int, d: int, q: int = Q) -> int:
    x = canonical_q(x, q)
    return round_half_even(x * (1 << d), q) % (1 << d)


def decompress_python(y: int, d: int, q: int = Q) -> int:
    y = y % (1 << d)
    return round_half_even(y * q, 1 << d)


def compression_error_fips(x: int, d: int, q: int = Q) -> int:
    x = canonical_q(x, q)
    y = compress_fips(x, d, q)
    z = decompress_fips(y, d, q)
    return ctr_q(z - x, q)


def cbd_weights(eta: int) -> Dict[int, int]:
    """Exact integer weights for CBD_eta; total mass 2**(2*eta)."""
    den = 1 << (2 * eta)
    return {x: comb(2 * eta, eta + x) for x in range(-eta, eta + 1)}


def cbd_law_fraction(eta: int) -> Dict[int, Fraction]:
    den = 1 << (2 * eta)
    return {x: Fraction(comb(2 * eta, eta + x), den) for x in range(-eta, eta + 1)}


def enumerate_rounding_tables(ds: Iterable[int], q: int = Q) -> dict:
    """Exhaustive Compress/Decompress comparison for each d."""
    out = {}
    for d in ds:
        mod = 1 << d
        compress_diffs = []
        decompress_diffs = []
        for x in range(q):
            cf = compress_fips(x, d, q)
            cp = compress_python(x, d, q)
            if cf != cp:
                # classify tie: (2^d * x) / q is half-integer
                twice = 2 * (1 << d) * x
                is_tie = (twice % (2 * q) == q)
                compress_diffs.append(
                    {
                        "x": x,
                        "fips": cf,
                        "python": cp,
                        "is_tie": is_tie,
                        "error_fips": compression_error_fips(x, d, q),
                        "error_python": ctr_q(decompress_python(cp, d, q) - x, q),
                    }
                )
        for y in range(mod):
            df = decompress_fips(y, d, q)
            dp = decompress_python(y, d, q)
            if df != dp:
                twice = 2 * y * q
                is_tie = (twice % (2 * mod) == mod)
                decompress_diffs.append(
                    {"y": y, "fips": df, "python": dp, "is_tie": is_tie}
                )
        out[d] = {
            "compress_mismatch_count": len(compress_diffs),
            "decompress_mismatch_count": len(decompress_diffs),
            "compress_mismatches": compress_diffs,
            "decompress_mismatches": decompress_diffs,
        }
    return out


FAMILIES = {
    "ML-KEM-512": {"eta1": 3, "eta2": 2, "du": 10, "dv": 4},
    "ML-KEM-768": {"eta1": 2, "eta2": 2, "du": 10, "dv": 4},
    "ML-KEM-1024": {"eta1": 2, "eta2": 2, "du": 11, "dv": 5},
}
