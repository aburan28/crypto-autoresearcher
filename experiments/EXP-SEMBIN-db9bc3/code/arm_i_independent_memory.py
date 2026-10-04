"""ARM I -- independent (blind) re-implementation of the memory term.

EXP-SEMBIN-db9bc3, ARM I.  THIS FILE WAS WRITTEN FIRST, BEFORE ANY OTHER FILE IN
THIS DIRECTORY, and specifically before the ARM N cost model existed.  That
ordering is the blindness evidence: at the time these lines were written there
was no ARM N implementation and no ARM N output to read, so `blind_from` --
"the ARM N implementation" and "any ARM N output" -- is satisfied by
construction rather than by assertion.  It imports nothing from this directory.

THE STATEMENT I AM WORKING FROM, and the only thing I am working from
(experiments/EXP-SEMBIN-db9bc3/specification.yaml, ARM I `what`, and
ledger/handoffs/TASK-20260913-495fcc.yaml constraint 6):

    "the memory column alone -- C(N+4,4) at N = n(m-1) with m = n/C_0"

Parameters available to me: n (the extension degree) and C_0 (the coset
dimension k that Nagao's Section 7 fixes).  Nothing else.

WHAT THE STATEMENT DETERMINES, AND WHAT IT DOES NOT.  Recorded here before any
number is produced, because the ARM I failure mode this arm exists to catch is
precisely a parameter block that reads unambiguous and is not
(TASK-20260913-ec11c4: a block that gave a relation ROW WIDTH where it said
VARIABLE COUNT).

Determined:
  * the combinatorial object: C(N+4,4), i.e. the number of monomials of degree
    at most 4 in N variables -- the standard count, since the number of
    monomials of degree <= d in N variables is C(N+d, d).
  * N is a VARIABLE COUNT and equals n(m-1).  The statement says so in words.
  * the second index is the literal integer 4.  It is NOT written as d_F, so I
    charge 4 and do not substitute a degree parameter.  A caller wanting d = 5
    must ask for it explicitly; see `monomial_count` below.
  * the unit of the answer is "one field element per monomial", i.e. the count
    itself.  The statement gives a count and no width, no square and no bytes.

NOT determined -- and each of these is reported rather than silently resolved:
  A1. the rounding of m = n / C_0.  C_0 does not divide n at 22 of the 40
      (n, C_0) cells of this contract's declared grid, and the statement gives
      no rule.  I compute ALL THREE readings (floor, ceil, exact rational) and
      report the spread they induce in bits.  I do not pick one.
  A2. whether m is clamped below.  n(m-1) is 0 at m = 1 and negative at m = 0,
      and C(N+4,4) is then not a count of anything.  m >= 2 is the smallest
      value at which Nagao's chained system has an equation at all, so a
      reading that produces m < 2 is reported as out_of_domain rather than
      evaluated.
  A3. whether the answer is a memory in bits, words, or field elements.  I
      return the COUNT and label it; a caller multiplying by a word size is
      making a modelling choice this statement does not contain.

Exact arithmetic: the binomial is computed as an exact Python integer and only
then converted to log2, by an integer-exact routine, because C(N+4,4) at
n = 571, C_0 = 2 has 65 bits and at larger N overflows float in intermediate
products if computed naively.
"""

from __future__ import annotations

import math
from fractions import Fraction

D_STATED = 4  # the literal 4 of "C(N+4,4)"


def log2_exact_int(value: int) -> float:
    """log2 of an exact positive integer, without overflowing float.

    Shift the integer down to 53 significant bits, take log2 of that, and add
    the shift back.  Exact-integer input, ~1e-16 relative error output.
    """
    if value <= 0:
        raise ValueError(f"log2 of non-positive integer {value}")
    bits = value.bit_length()
    if bits <= 53:
        return math.log2(value)
    shift = bits - 53
    return float(shift) + math.log2(value >> shift)


def monomial_count(n_vars: int, degree: int = D_STATED) -> int:
    """C(N + d, d): monomials of degree <= d in N variables.  Exact integer.

    Computed as a running product rather than by a factorial ratio so that the
    intermediate values stay small; the division is exact at every step because
    the partial product of i consecutive integers is divisible by i!.
    """
    if n_vars < 0:
        raise ValueError(f"variable count must be >= 0 (got {n_vars})")
    if degree < 0:
        raise ValueError(f"degree must be >= 0 (got {degree})")
    total = 1
    for i in range(1, degree + 1):
        total = total * (n_vars + i) // i
    return total


def m_readings(n: int, c0: int) -> dict:
    """The three readings of the undetermined 'm = n / C_0'.  Ambiguity A1."""
    if c0 <= 0:
        raise ValueError(f"C_0 must be >= 1 (got {c0})")
    exact = Fraction(n, c0)
    return {
        "floor": n // c0,
        "ceil": -((-n) // c0),
        "exact_rational_rounded_half_up": int(exact + Fraction(1, 2)),
        "exact_rational": exact,
    }


def variable_count(n: int, m: int) -> int:
    """N = n(m-1).  The statement's own words: a VARIABLE COUNT."""
    return n * (m - 1)


def memory_term(n: int, c0: int, m_reading: str = "ceil",
                degree: int = D_STATED) -> dict:
    """The ARM I memory column at one (n, C_0) cell under one reading of m.

    Returns the exact count, its log2, and every intermediate quantity, so a
    disagreement with any other implementation localises to a named number
    rather than to 'the memory column'.
    """
    readings = m_readings(n, c0)
    if m_reading not in ("floor", "ceil", "exact_rational_rounded_half_up"):
        raise ValueError(f"unknown m reading {m_reading!r}")
    m = readings[m_reading]
    if m < 2:  # ambiguity A2
        return {
            "n": n, "C_0": c0, "m_reading": m_reading, "m": m,
            "status": "out_of_domain",
            "reason": ("m < 2: n(m-1) is not a positive variable count and "
                       "Nagao's chained system has no equation at m < 2"),
            "N": None, "count": None, "log2_count": None,
        }
    n_vars = variable_count(n, m)
    count = monomial_count(n_vars, degree)
    return {
        "n": n, "C_0": c0, "m_reading": m_reading, "m": m,
        "status": "evaluated",
        "N": n_vars,
        "degree_charged": degree,
        "count": count,
        "log2_count": log2_exact_int(count),
        "unit": "monomials, i.e. field elements at one element per monomial",
    }


def cell_with_ambiguity_spread(n: int, c0: int, degree: int = D_STATED) -> dict:
    """All three readings at one cell, plus the spread they induce, in bits."""
    per_reading = {r: memory_term(n, c0, r, degree)
                   for r in ("floor", "ceil", "exact_rational_rounded_half_up")}
    evaluated = [v["log2_count"] for v in per_reading.values()
                 if v["status"] == "evaluated"]
    divides = (n % c0 == 0)
    return {
        "n": n, "C_0": c0,
        "C_0_divides_n": divides,
        "per_reading": per_reading,
        "log2_spread_bits_across_m_readings": (
            max(evaluated) - min(evaluated) if len(evaluated) > 1 else 0.0),
        "readings_evaluated": len(evaluated),
    }


def surface(ns, c0s, degree: int = D_STATED) -> list:
    """The whole declared p = 2 memory grid, every reading, no selection."""
    return [cell_with_ambiguity_spread(n, c0, degree) for n in ns for c0 in c0s]


def self_check() -> dict:
    """Hand-checked values, computed away from any machine.

    1. C(N+4,4) at N = 2 is C(6,4) = 15.  By hand: 6*5*4*3/24 = 360/24 = 15.
    2. C(N+4,4) at N = 4 is C(8,4) = 70.  By hand: 8*7*6*5/24 = 1680/24 = 70.
    3. n = 6, C_0 = 3 -> m = 2 exactly, N = 6*(2-1) = 6, C(10,4) = 210.
       By hand: 10*9*8*7/24 = 5040/24 = 210.
    4. n = 10, C_0 = 4: floor(10/4) = 2 -> N = 10; ceil = 3 -> N = 20.
       C(14,4) = 1001 (14*13*12*11/24 = 24024/24 = 1001) and
       C(24,4) = 10626 (24*23*22*21/24 = 255024/24 = 10626).
       So the A1 ambiguity is worth log2(10626/1001) = 3.408 bits at that cell.
    5. C(N+5,5) at N = 5 is C(10,5) = 252.  By hand: 10*9*8*7*6/120 = 252.
    6. log2_exact_int on 2^200 must return exactly 200.0 (float-overflow path).
    """
    checks = []
    checks.append(("C(6,4)=15", monomial_count(2, 4), 15))
    checks.append(("C(8,4)=70", monomial_count(4, 4), 70))
    checks.append(("n=6,C0=3 -> C(10,4)=210",
                   memory_term(6, 3, "ceil")["count"], 210))
    checks.append(("n=10,C0=4,floor -> C(14,4)=1001",
                   memory_term(10, 4, "floor")["count"], 1001))
    checks.append(("n=10,C0=4,ceil -> C(24,4)=10626",
                   memory_term(10, 4, "ceil")["count"], 10626))
    checks.append(("C(10,5)=252", monomial_count(5, 5), 252))
    checks.append(("log2_exact_int(2^200)=200", log2_exact_int(2 ** 200), 200.0))
    spread = cell_with_ambiguity_spread(10, 4)["log2_spread_bits_across_m_readings"]
    checks.append(("n=10,C0=4 A1 spread = log2(10626/1001)",
                   round(spread, 9), round(math.log2(10626 / 1001), 9)))
    return {
        "checks": [{"name": name, "got": got, "want": want, "pass": got == want}
                   for name, got, want in checks],
        "all_pass": all(got == want for _, got, want in checks),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(self_check(), indent=2))
