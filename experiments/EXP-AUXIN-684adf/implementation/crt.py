"""Production generalized-CRT combiner for EXP-AUXIN-684adf.

Frozen source: experiments/EXP-AUXIN-684adf/specification.yaml, section
`arithmetic_definitions.fold` and `arithmetic_definitions.candidate_set`.

Scope discipline (binding, do not relax):

  * This module's public functions receive ONLY an integer domain size `n`
    and an ordered sequence of congruences `(a, m)`. They never receive,
    import, or otherwise gain access to fixture ground truth `k`/`x`, a
    reference/oracle result, a primitive element, or a prime `r`. Those
    belong to the fixture generator, the independent verification service,
    or the toy original-target equality service (see fixtures.py /
    reference.py), never to the combiner as "advice".
  * No group operation, elliptic-curve point, or Cheon first-stage logic is
    implemented or referenced here. This is finite integer-exponent
    arithmetic only.
  * No code in this module executes anything at import time: only function
    and data definitions are declared. Nothing here is invoked by importing
    the module (no self-test on import, per the implementation handoff's
    hard constraint).
  * Zero scientific execution occurs as part of writing this file. Calling
    these functions is a later, separately authorized act (see driver.py).

Congruence convention
----------------------
Each congruence is a 2-tuple ``(a, m)`` meaning "the unknown exponent k
satisfies k = a (mod m)", where the caller-supplied `a` need not already be
in canonical form; this module performs canonical residue reduction itself
(0 <= a < m, with the residue fixed at 0 when m == 1, since m == 1 carries
no information about k). `m` is assumed to be a positive integer dividing
the ambient domain size `n`; that divisibility/range property is validated
upstream (fixtures.py's input gate) before a congruence is ever handed to
this module -- this module does not re-derive or assume knowledge of `n`'s
factorization, it only uses `n` for final candidate enumeration.
"""

from __future__ import annotations

import math
from typing import Iterable, List, NamedTuple, Optional, Sequence, Tuple


class FoldResult(NamedTuple):
    """Outcome of folding an ordered sequence of congruences.

    status: "consistent" or "inconsistent".
    k0: canonical residue representative in [0, M) when consistent, else None.
    M: combined modulus (lcm of all supplied moduli, 1 if none supplied)
       when consistent, else None.
    reject_index: 0-based index of the congruence record that first exposed
       an inconsistency, when status == "inconsistent"; else None.
    steps_folded: number of congruences successfully folded before either
       exhausting the list (consistent) or hitting the rejecting record
       (inconsistent). Diagnostic only, not a scientific measurement.
    """

    status: str
    k0: Optional[int]
    M: Optional[int]
    reject_index: Optional[int]
    steps_folded: int


def canonical_residue(a: int, m: int) -> int:
    """Reduce `a` to the canonical representative in [0, m).

    Per specification `arithmetic_definitions.residue`: canonical integer
    0 <= a < m, with a = 0 for m = 1 (the trivial modulus carries no
    information). This is exact integer arithmetic; no floating point.
    """
    if m <= 0:
        raise ValueError("modulus m must be a positive integer")
    if m == 1:
        return 0
    return a % m


def _egcd(a: int, b: int) -> Tuple[int, int, int]:
    """Extended Euclidean algorithm. Returns (g, x, y) with a*x + b*y = g."""
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    return old_r, old_s, old_t


def modular_inverse(a: int, m: int) -> int:
    """Return the inverse of `a` modulo `m`.

    Per the frozen fold, this is only ever called with h > 1 (the h == 1
    case is short-circuited by the caller and never needs an inverse, since
    dividing by a modulus of 1 is trivial and would be degenerate to invert
    against). Raises ValueError if `a` and `m` are not coprime.
    """
    if m <= 1:
        raise ValueError("modular_inverse requires m > 1")
    g, x, _ = _egcd(a % m, m)
    if g != 1:
        raise ValueError(f"{a} has no inverse modulo {m} (gcd={g})")
    return x % m


def fold_congruences(n: int, congruences: Iterable[Tuple[int, int]]) -> FoldResult:
    """Fold an ordered sequence of (a, m) congruences via generalized CRT.

    Implements exactly `arithmetic_definitions.fold`:

        Start (A, M) = (0, 1). For each (a, m):
          g = gcd(M, m)
          reject inconsistent when (a - A) mod g != 0
          otherwise h = m / g
            if h == 1: u = 0
            else: u = (((a - A) / g) * inverse(M / g mod h, h)) mod h
          M_new = M * h
          A_new = (A + M * u) mod M_new
        End with k0 = A.

    `n` is accepted for interface symmetry with the rest of the pipeline
    (candidate enumeration needs it) but this function does not need or use
    `n` to decide consistency; the fold is defined purely in terms of the
    supplied congruences. No fixture truth, prime `r`, or primitive element
    is visible to this function -- only integers `a`, `m`, and `n`.

    All integers are preserved exactly (Python's arbitrary-precision ints);
    no floating point is used anywhere in this module.
    """
    if n <= 0:
        raise ValueError("n must be a positive integer")

    A, M = 0, 1
    steps_folded = 0
    for idx, (a_raw, m) in enumerate(congruences):
        if m <= 0:
            raise ValueError(f"modulus m must be positive at index {idx}")
        a = canonical_residue(a_raw, m)

        g = math.gcd(M, m)
        if (a - A) % g != 0:
            return FoldResult(
                status="inconsistent",
                k0=None,
                M=None,
                reject_index=idx,
                steps_folded=steps_folded,
            )

        h = m // g
        if h == 1:
            u = 0
        else:
            u = (((a - A) // g) * modular_inverse((M // g) % h, h)) % h

        M_new = M * h
        A_new = (A + M * u) % M_new
        A, M = A_new, M_new
        steps_folded += 1

    return FoldResult(status="consistent", k0=A, M=M, reject_index=None, steps_folded=steps_folded)


def enumerate_candidates(n: int, k0: int, M: int) -> List[int]:
    """Enumerate the candidate exponent set E = {k0 + M*t | 0 <= t < n/M}.

    Per `arithmetic_definitions.candidate_set`, listed in ascending
    exponent order. Requires M to divide n exactly (guaranteed by the
    design derivation whenever every input modulus divides n and the fold
    above is used); this function raises ValueError rather than silently
    truncating if that invariant is violated, since a caller violating it
    would indicate an implementation error, not a scientific outcome.
    """
    if M <= 0:
        raise ValueError("M must be a positive integer")
    if n % M != 0:
        raise ValueError(f"M={M} does not divide n={n}; invariant violated")
    count = n // M
    return [k0 + M * t for t in range(count)]


def fold_and_enumerate(n: int, congruences: Sequence[Tuple[int, int]]) -> Tuple[FoldResult, Optional[List[int]]]:
    """Convenience composition: fold, then enumerate candidates if consistent.

    Returns (fold_result, candidates_or_None). This performs no I/O and
    accesses no fixture state; it is provided purely to keep the two-step
    protocol (`fold` then `enumerate`) available as a single call for the
    future guarded driver, without smuggling any additional inputs into the
    combiner's interface.
    """
    result = fold_congruences(n, congruences)
    if result.status != "consistent":
        return result, None
    candidates = enumerate_candidates(n, result.k0, result.M)
    return result, candidates
