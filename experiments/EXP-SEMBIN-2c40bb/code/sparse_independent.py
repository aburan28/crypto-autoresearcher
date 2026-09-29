#!/usr/bin/env python3
"""ARM I -- second implementation of the SEMAEV-SPARSE working set.

Written from the formula statement recorded in knowledge/literature/KN-LIT-e77232.md
(Semaev's 2015-04-20 reply in the ellipticnews thread):

    columns           (n m)^4 / 24
    nonzeros per row  n^3 / m
    total nonzero positions ~ columns x nonzeros-per-row, with the row count taken
    to be of the order of the column count (the thread's own reading),
    at n = 571, m = 12:  2^46.38 columns, 2^23.89 nonzeros per row, 2^70.3 total.

This module does NOT import memory_charged_cost.py or surface_cost.py, and it takes
a different arithmetic route on purpose: the product is formed EXACTLY as a Python
integer ratio  n^7 m^3 / 24  and only then reduced to log2, so that agreement with a
float-domain sum of logarithms is a check on two computations rather than one.
"""

from __future__ import annotations

import math
from fractions import Fraction


def columns_exact(n: int, m: int) -> Fraction:
    return Fraction((n * m) ** 4, 24)


def nonzeros_per_row_exact(n: int, m: int) -> Fraction:
    return Fraction(n ** 3, m)


def total_nonzeros_exact(n: int, m: int) -> Fraction:
    return columns_exact(n, m) * nonzeros_per_row_exact(n, m)


def _log2_fraction(x: Fraction) -> float:
    # exact-integer route: log2 of numerator and denominator separately
    return math.log2(x.numerator) - math.log2(x.denominator)


def sparse_working_set_log2_bits(n: int, m: int) -> dict:
    """log2 of the total nonzero count, one bit per nonzero (the reading used by the
    record under comparison; the column-index overhead is a separate reading)."""
    if not isinstance(n, int) or not isinstance(m, int):
        raise ValueError("n and m must be integers")
    if m < 2 or m > n:
        raise ValueError(f"require 2 <= m <= n (got n={n}, m={m})")
    cols = columns_exact(n, m)
    nz = nonzeros_per_row_exact(n, m)
    tot = total_nonzeros_exact(n, m)
    return {
        "n": n,
        "m": m,
        "columns_log2": _log2_fraction(cols),
        "nonzeros_per_row_log2": _log2_fraction(nz),
        "total_nonzeros_log2": _log2_fraction(tot),
        "exact_total_numerator": str(tot.numerator) if tot.numerator < 10 ** 40 else None,
        "exact_total_denominator": tot.denominator,
    }


def kn_lit_e77232_n571_check() -> dict:
    """Reproduce that record's own arithmetic: 2^46.38 columns, 2^23.89 nonzeros,
    2^70.3 total, at n = 571, m = 12 (printed to 2, 2 and 1 decimals)."""
    r = sparse_working_set_log2_bits(571, 12)
    printed = {"columns_log2": 46.38, "nonzeros_per_row_log2": 23.89,
               "total_nonzeros_log2": 70.3}
    decimals = {"columns_log2": 2, "nonzeros_per_row_log2": 2, "total_nonzeros_log2": 1}
    out = {"n": 571, "m": 12, "recomputed": {}, "printed_in_KN_LIT_e77232": printed,
           "agrees_at_printed_precision": {}}
    for key, val in printed.items():
        out["recomputed"][key] = r[key]
        out["agrees_at_printed_precision"][key] = (
            round(r[key], decimals[key]) == val)
    out["all_agree"] = all(out["agrees_at_printed_precision"].values())
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(kn_lit_e77232_n571_check(), indent=2))
