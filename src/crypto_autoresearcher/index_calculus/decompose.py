"""Point decomposition R = s_1 F_{i_1} + ... + s_m F_{i_m} over a factor base.

The search fixes the first m - 2 factor-base elements (with sign) and solves
the last two with S_3: for R' = R - (fixed part) and each candidate x1 = x(F_i),
the roots X of S_3(x1, X, x(R')) are exactly the x-coordinates of points P_2
with +/- F_i +/- P_2 = +/- R'; a root is useful only if it is in the factor base.
Indices are kept non-decreasing, so each unordered decomposition is visited
once.  Every returned decomposition is verified by point addition.

Cost per attempt is about |F|^{m-1} S_3 root solves: this is the exhaustive
(Groebner-free) decomposition, the honest baseline every smarter solver must
beat.
"""

from __future__ import annotations

from dataclasses import dataclass

from .curve import Curve, Point
from .factor_base import FactorBase
from .semaev import s3_roots

Relation = list[tuple[int, int]]  # (factor-base index, sign +/-1)


@dataclass
class DecompStats:
    attempts: int = 0
    successes: int = 0
    s3_solves: int = 0
    membership_tests: int = 0


def decompose(E: Curve, fb: FactorBase, R: Point, m: int,
              stats: DecompStats | None = None) -> Relation | None:
    """One decomposition of R into m signed factor-base points, or None."""
    stats = stats if stats is not None else DecompStats()
    stats.attempts += 1
    rel = _decompose(E, fb, R, m, 0, stats)
    if rel is None:
        return None
    # Certificate: recompute the sum by point arithmetic.
    S: Point = None
    for i, s in rel:
        S = E.add(S, fb.points[i] if s > 0 else E.neg(fb.points[i]))
    if S != R:
        raise AssertionError("decomposition failed verification")
    stats.successes += 1
    return rel


def _decompose(E: Curve, fb: FactorBase, R: Point, m: int, lo: int,
               stats: DecompStats) -> Relation | None:
    if R is None:
        return None
    if m == 1:
        stats.membership_tests += 1
        i = fb.lookup(R[0])
        if i is None or i < lo:
            return None
        return [(i, 1 if R == fb.points[i] else -1)]
    if m == 2:
        xR = R[0]
        for i in range(lo, len(fb)):
            F = fb.points[i]
            stats.s3_solves += 1
            for x2 in s3_roots(E, F[0], xR):
                stats.membership_tests += 1
                j = fb.lookup(x2)
                if j is None or j < i:
                    continue
                for s in (1, -1):
                    T = E.sub(R, F if s > 0 else E.neg(F))
                    if T is not None and T[0] == x2:
                        return [(i, s), (j, 1 if T == fb.points[j] else -1)]
        return None
    for i in range(lo, len(fb)):
        F = fb.points[i]
        for s in (1, -1):
            Rp = E.sub(R, F if s > 0 else E.neg(F))
            sub = _decompose(E, fb, Rp, m - 1, i, stats)
            if sub is not None:
                return [(i, s)] + sub
    return None
