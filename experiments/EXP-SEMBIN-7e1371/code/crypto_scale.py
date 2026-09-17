#!/usr/bin/env python3
"""crypto_scale.py -- what the measured window does and does not reach, in
arithmetic rather than in prose.

Two things are computed, both from Semaev ePrint 2015/310's OWN formulas
(frozen text at inputs/SEMAEV-2015-310/, transcribed tables at
inputs/SEMAEV-2015-310/tables.yaml).  NEITHER IS A MEASUREMENT and neither is
an extrapolation of one: they are the sizes and costs the paper's parameters
imply, printed next to the largest cell this run actually reached.

1. CERTIFIABILITY.  The degree-4 Macaulay block at the FIPS targets has
   sum_{d<=4} C(N,d) columns for N = n(m-2) + km, k = ceil(n/m).  Printed
   against the largest N this host reached, this is the exact factor by which
   direct measurement at n = 409, 571 is out of reach -- not "expensive",
   out of reach.

2. THE TWO READINGS OF TABLE 3's STAGE 1.  Section 4.5.2 derives the cost of
   solving one system (5) by F4 as [n(m-1)]^{4 omega} -- N = n(m-1) is the
   variable count of the system that is actually solved.  It then says a
   block-structured Groebner algorithm with block size n "is applicable" and
   "reduces the complexity of finding the relation to n^{4 omega}", and Table 3
   is computed with n^{12}, i.e. with the block-structured variant at omega = 3.
   That algorithm is never implemented or measured in the paper, and Tables 1-2
   are standard MAGMA F4.  So Table 3's stage 1 rests on a SECOND unmeasured
   assumption on top of Assumption 1, already recorded at
   knowledge/literature/KN-LIT-fa346d.md ("The block-structured solver ...
   without it the paper claims only two curves").  This script prints both
   columns and locates each one's crossover with Pollard rho.

Assumption 1 is what the run measures; this file prices what it would buy.
Neither column is evidence for or against it.
"""
from __future__ import annotations

import json
import math

OMEGAS = (2.376, 2.807, 3.0)
FIPS_BINARY = (163, 233, 283, 409, 571)
TABLE3_ROWS = ((100, 6), (150, 7), (200, 8), (250, 9), (300, 10), (310, 10),
               (350, 10), (400, 11), (409, 11), (450, 11), (500, 12), (571, 12))


def deg4_columns(N: int) -> int:
    return sum(math.comb(N, d) for d in range(5))


def variables(n: int, m: int, t: int | None = None, k: int | None = None) -> int:
    t = m if t is None else t
    k = math.ceil(n / m) if k is None else k
    return n * (t - 2) + k * t


def log2(x: float) -> float:
    return math.log2(x) if x > 0 else float("-inf")


def stage1_log2(n: int, m: int, omega: float, variant: str) -> float:
    """log2 of eq. (15): m! * 2^{n/m} * (cost of one F4 solve).

    variant 'paper_table3': the block-structured reading, n^{4 omega}.
    variant 'standard_f4' : the derived reading for F4 itself, [n(m-1)]^{4 omega}.
    variant 'monomials'   : (number of degree-<=4 monomials in the system's own
                            N variables)^omega, i.e. the same 4-omega power with
                            the binomial count instead of its leading term.
    """
    base = math.log2(math.factorial(m)) + n / m
    if variant == "paper_table3":
        return base + 4 * omega * log2(n)
    if variant == "standard_f4":
        return base + 4 * omega * log2(n * (m - 1))
    if variant == "monomials":
        return base + omega * log2(deg4_columns(variables(n, m)))
    raise ValueError(variant)


def best_m(n: int, omega: float, variant: str, m_max: int = 24) -> tuple[int, float]:
    best = None
    for m in range(2, m_max + 1):
        k = math.ceil(n / m)
        total = max(stage1_log2(n, m, omega, variant), 2 * n / m)  # stage 2 = 2^{2n/m}
        if best is None or total < best[1]:
            best = (m, total)
    return best


def crossover(omega: float, variant: str, n_max: int = 2000) -> int | None:
    """smallest n at which the m-optimised total falls below Pollard rho 2^{n/2}."""
    for n in range(50, n_max + 1):
        if best_m(n, omega, variant)[1] < n / 2:
            return n
    return None


def report() -> dict:
    out: dict = {"what_this_is": "arithmetic on the paper's own formulas; not a measurement",
                 "source": "inputs/SEMAEV-2015-310/ (frozen), tables.yaml table_3",
                 "omega_values": list(OMEGAS)}
    sizes = []
    for n in FIPS_BINARY:
        m = next((mm for (nn, mm) in TABLE3_ROWS if nn == n), None)
        if m is None:
            m = best_m(n, 3.0, "paper_table3")[0]
        k = math.ceil(n / m)
        N = variables(n, m)
        C = deg4_columns(N)
        sizes.append({"n": n, "m": m, "t": m, "k": k, "N_variables": N,
                      "degree4_columns": C, "log2_degree4_columns": round(log2(C), 2),
                      "dense_square_bits_log2": round(2 * log2(C), 2),
                      "note": "columns of the degree-4 Macaulay block of eq. (5) at t = m"})
    out["certifiability_at_fips_parameters"] = sizes
    rows = []
    for (n, m) in TABLE3_ROWS:
        row = {"n": n, "m": m, "k": math.ceil(n / m), "N_variables": variables(n, m),
               "pollard_rho_log2": n / 2,
               "stage2_log2": 2 * n / m}
        for variant in ("paper_table3", "standard_f4", "monomials"):
            for omega in OMEGAS:
                row[f"stage1_log2[{variant},omega={omega}]"] = round(stage1_log2(n, m, omega, variant), 2)
        rows.append(row)
    out["table3_rederived"] = rows
    out["crossover_with_pollard_rho"] = {
        f"{variant},omega={omega}": crossover(omega, variant)
        for variant in ("paper_table3", "standard_f4", "monomials") for omega in OMEGAS}
    out["crossover_note"] = (
        "smallest n whose m-optimised stage-1+stage-2 cost falls below 2^{n/2}; "
        "the paper states n > 310 for its own column, and tables.yaml derived_checks "
        "recovers n = 302 from the same formula. Time only: stage 2 must also store "
        "Theta(2^k) relations (KN-OPEN-86e7e1), which none of these columns charges.")
    return out


if __name__ == "__main__":
    print(json.dumps(report(), indent=1))
