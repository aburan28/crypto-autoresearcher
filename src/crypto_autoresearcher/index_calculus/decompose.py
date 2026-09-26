"""Point decomposition R = s_1 F_{i_1} + ... + s_m F_{i_m} over a factor base.

The search fixes the first m - 2 factor-base elements (with sign) and solves
the last two with S_3: for R' = R - (fixed part) and each candidate x1 = x(F_i),
the roots X of S_3(x1, X, x(R')) are exactly the x-coordinates of points P_2
with +/- F_i +/- P_2 = +/- R'; a root is useful only if it is in the factor base.
Indices are kept non-decreasing, so each unordered decomposition is visited
once.  Every returned decomposition is verified by point addition.

Cost per attempt is about |F|^{m-1} S_3 root solves: this is the exhaustive
(Groebner-free) decomposition, the honest baseline every smarter solver must
beat.  With numpy installed and p < 2^32 the last level is located by a
vectorised scan (``_accel``); the relations found and every counter are the
same as the pure-Python path, only faster.

Meet in the middle
------------------
Given a ``TailTable`` of arity h (tails.py: every signed sum of h base points,
keyed by x), the search fixes only m - h - 1 points, solves S_3 for the next
one and looks the root up in the table instead of in the base: |F|^(m-h) S_3
solves per attempt instead of |F|^(m-1), for a table built once per factor
base.  The exhaustive search is the case h = 1, and it is still the code that
runs when no table is given.

The table holds exactly the tails the exhaustive search can reach, so
``decompose_all`` returns the same set with or without it.  ``decompose``
returns the same relation too: at the first index where the table search
finds anything it collects every hit and keeps the one the exhaustive search
would have reached first (``_search_order``), so an index-calculus run makes
the same relations, attempts and logarithm with either engine and differs
only in what they cost.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import _accel
from .curve import Curve, Point
from .factor_base import FactorBase
from .semaev import s3_roots
from .tails import TailTable, default_table_arity

__all__ = ["DecompStats", "Relation", "TailTable", "canonical", "decompose",
           "decompose_all", "default_table_arity", "use_acceleration", "verify"]

Relation = list[tuple[int, int]]  # (factor-base index, sign +/-1)

ACCEL_MIN_SPAN = 48  # below this many indices the scalar loop is faster


@dataclass
class DecompStats:
    attempts: int = 0
    successes: int = 0
    s3_solves: int = 0
    membership_tests: int = 0


def use_acceleration(fb: FactorBase, accelerate: bool | None) -> bool:
    """Resolve the ``accelerate`` switch: None means "when available"."""
    if accelerate is None:
        return _accel.usable(fb.p)
    if accelerate and not _accel.usable(fb.p):
        raise RuntimeError("acceleration needs numpy and p < 2^32")
    return accelerate


def verify(E: Curve, fb: FactorBase, rel: Relation, R: Point) -> None:
    S: Point = None
    for i, s in rel:
        S = E.add(S, fb.points[i] if s > 0 else E.neg(fb.points[i]))
    if S != R:
        raise AssertionError("decomposition failed verification")


def canonical(rel: Relation) -> tuple[tuple[int, int], ...]:
    return tuple(sorted(rel))


def _table(fb: FactorBase, m: int, table: TailTable | None) -> TailTable | None:
    """The table to search with, or None for the exhaustive search."""
    if table is None or table.arity == 1:
        return None
    if table.fb is not fb:
        raise ValueError("the table was built for a different factor base")
    if table.arity >= m:
        raise ValueError(f"table arity {table.arity} needs m > {table.arity}, got m = {m}")
    return table


def decompose(E: Curve, fb: FactorBase, R: Point, m: int,
              stats: DecompStats | None = None,
              accelerate: bool | None = None,
              table: TailTable | None = None) -> Relation | None:
    """One decomposition of R into m signed factor-base points, or None."""
    stats = stats if stats is not None else DecompStats()
    tab = _table(fb, m, table)
    stats.attempts += 1
    found = _decompose(E, fb, R, m, 0, stats, False, use_acceleration(fb, accelerate), tab)
    if not found:
        return None
    rel = found[0]
    verify(E, fb, rel, R)
    stats.successes += 1
    return rel


def decompose_all(E: Curve, fb: FactorBase, R: Point, m: int,
                  stats: DecompStats | None = None,
                  accelerate: bool | None = None,
                  table: TailTable | None = None) -> list[tuple[tuple[int, int], ...]]:
    """Every decomposition the search can reach, canonicalised and verified.

    A decomposition that needs a cancelling pair F - F (possible only when R
    is a sum of fewer than m base points) is reached only in the orders
    whose partial remainders all avoid the point at infinity; the S_3 search
    and the table search reach the same ones.
    """
    stats = stats if stats is not None else DecompStats()
    tab = _table(fb, m, table)
    stats.attempts += 1
    found = _decompose(E, fb, R, m, 0, stats, True, use_acceleration(fb, accelerate), tab)
    out = sorted({canonical(r) for r in found})
    for rel in out:
        verify(E, fb, list(rel), R)
    if out:
        stats.successes += 1
    return out


def _m2_at(E: Curve, fb: FactorBase, R: Point, i: int, stats: DecompStats,
           all_: bool) -> list[Relation]:
    """The m = 2 step at one index: R = s F_i + t F_j with j >= i."""
    F = fb.points[i]
    stats.s3_solves += 1
    out: list[Relation] = []
    for x2 in s3_roots(E, F[0], R[0]):
        stats.membership_tests += 1
        j = fb.lookup(x2)
        if j is None or j < i:
            continue
        for s in (1, -1):
            T = E.sub(R, F if s > 0 else E.neg(F))
            if T is not None and T[0] == x2:
                out.append([(i, s), (j, 1 if T == fb.points[j] else -1)])
                break
        if out and not all_:
            return out
    return out


def _tail_at(E: Curve, fb: FactorBase, R: Point, i: int, stats: DecompStats,
             all_: bool, tab: TailTable) -> list[Relation]:
    """The last S_3 step at one index against a table: R = s F_i + (a tail).

    Charged like ``_m2_at``: one S_3 solve, one lookup per root, and the group
    operations that fix the sign of F_i only at a root the table knows.
    """
    F = fb.points[i]
    stats.s3_solves += 1
    out: list[Relation] = []
    for x2 in s3_roots(E, F[0], R[0]):
        stats.membership_tests += 1
        codes = tab.codes(x2, i)
        if not codes:
            continue
        for s in (1, -1):
            T = E.sub(R, F if s > 0 else E.neg(F))
            if T is not None and T[0] == x2:
                out.extend([(i, s)] + tab.orient(c, T[1]) for c in codes)
                break
    if all_ or len(out) < 2:
        return out
    return [min(out, key=lambda rel: _search_order(fb, rel))]


def _search_order(fb: FactorBase, rel: Relation) -> tuple:
    """Where the exhaustive search meets the end ``rel`` of a relation.

    It loops over (index, sign), + before -, at every level but the last,
    and over (index, root x) at the last, so its first find among relations
    sharing a prefix is the least of these keys.
    """
    head = tuple((i, s < 0) for i, s in rel[:-2])
    return head + ((rel[-2][0], fb.points[rel[-1][0]][0]),)


def _level2(E: Curve, fb: FactorBase, R: Point, lo: int, stats: DecompStats,
            all_: bool, accel: bool, tab: TailTable | None = None) -> list[Relation]:
    """The last S_3 step over i = lo, lo + 1, ... (the m = 2 level when tab is None)."""
    n = len(fb)
    out: list[Relation] = []
    if not accel or n - lo < ACCEL_MIN_SPAN:
        for i in range(lo, n):
            if tab is None:
                found = _m2_at(E, fb, R, i, stats, all_)
            else:
                found = _tail_at(E, fb, R, i, stats, all_, tab)
            if found:
                out.extend(found)
                if not all_:
                    return out
        return out
    cands = _accel.m2_candidates(fb.arrays(), R[0], R[1], lo,
                                 None if tab is None else tab.arrays())
    return _walk_candidates(E, fb, R, lo, cands, stats, all_, tab)


def _walk_candidates(E: Curve, fb: FactorBase, R: Point, lo: int, cands,
                     stats: DecompStats, all_: bool,
                     tab: TailTable | None = None) -> list[Relation]:
    """Run the scalar m = 2 step at the scan's marked indices only.

    Every index the scan does not mark has x_i != x(R) and no root in the
    base at j >= i: the scalar step would solve S_3 once, test both roots and
    move on, so it is charged exactly that.
    """
    n = len(fb)
    out: list[Relation] = []
    pos = lo
    for c in cands.tolist():
        stats.s3_solves += c - pos
        stats.membership_tests += 2 * (c - pos)
        pos = c + 1
        if tab is None:
            found = _m2_at(E, fb, R, c, stats, all_)
        else:
            found = _tail_at(E, fb, R, c, stats, all_, tab)
        if found:
            out.extend(found)
            if not all_:
                return out
    stats.s3_solves += n - pos
    stats.membership_tests += 2 * (n - pos)
    return out


LEVEL3_BLOCK = 64  # (i, sign) pairs scanned together at m = 3


def _level3(E: Curve, fb: FactorBase, R: Point, lo: int, stats: DecompStats,
            all_: bool, tab: TailTable | None = None) -> list[Relation]:
    """m = 3 (m = h + 2 with a table) with blocks of (i, s) pairs scanned in one 2-D pass.

    The scalar loop visits (i, +1), (i, -1) for i = lo, lo+1, ... and runs the
    m = 2 level on R - s F_i from index i.  Here the R - s F_i of a block are
    computed together and scanned together, then walked in the same order,
    charging each visited pair the one group operation of its E.sub and the
    m = 2 level exactly what ``_walk_candidates`` charges; pairs after an early
    return are never charged, as the scalar loop never reaches them.
    """
    import numpy as np

    n, arr = len(fb), fb.arrays()
    out: list[Relation] = []
    pairs = [(i, s) for i in range(lo, n) for s in (1, -1)]
    for start in range(0, len(pairs), LEVEL3_BLOCK):
        chunk = pairs[start:start + LEVEL3_BLOCK]
        idx = np.array([i for i, _ in chunk], dtype=np.int64)
        sg = np.array([s for _, s in chunk], dtype=np.int64)
        xs, ys, degenerate = _accel.subtract_many(arr, R[0], R[1], idx, sg)
        rps: list[Point] = []
        for k, (i, s) in enumerate(chunk):
            if degenerate[k]:  # x_i = x(R): R - s F_i is O or 2R
                F = fb.points[i]
                before = E.ops.group_ops
                rps.append(E.sub(R, F if s > 0 else E.neg(F)))
                E.ops.group_ops = before
            else:
                rps.append((int(xs[k]), int(ys[k])))
        live = [k for k, Rp in enumerate(rps) if Rp is not None]
        cands = _accel.m2_candidates_multi(
            arr, [(rps[k][0], rps[k][1], chunk[k][0]) for k in live],
            None if tab is None else tab.arrays())
        cand_of = dict(zip(live, cands))
        for k, (i, s) in enumerate(chunk):
            E.ops.group_ops += 1  # the scalar path's E.sub(R, s F_i)
            Rp = rps[k]
            if Rp is None:
                continue
            for sub in _walk_candidates(E, fb, Rp, i, cand_of[k], stats, all_, tab):
                out.append([(i, s)] + sub)
                if not all_:
                    return out
    return out


def _decompose(E: Curve, fb: FactorBase, R: Point, m: int, lo: int,
               stats: DecompStats, all_: bool, accel: bool,
               tab: TailTable | None = None) -> list[Relation]:
    if R is None:
        return []
    h = 1 if tab is None else tab.arity
    if m == 1:
        stats.membership_tests += 1
        i = fb.lookup(R[0])
        if i is None or i < lo:
            return []
        return [[(i, 1 if R == fb.points[i] else -1)]]
    if m == h + 1:
        return _level2(E, fb, R, lo, stats, all_, accel, tab)
    if m == h + 2 and accel and len(fb) - lo >= ACCEL_MIN_SPAN:
        return _level3(E, fb, R, lo, stats, all_, tab)
    out: list[Relation] = []
    for i in range(lo, len(fb)):
        F = fb.points[i]
        for s in (1, -1):
            Rp = E.sub(R, F if s > 0 else E.neg(F))
            for sub in _decompose(E, fb, Rp, m - 1, i, stats, all_, accel, tab):
                out.append([(i, s)] + sub)
                if not all_:
                    return out
    return out
