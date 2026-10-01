#!/usr/bin/env python3
"""Counting machinery for EXP-SEMBIN-354a75: decompositions, never solves.

THE OBJECT. For a target point R and a factor base {(x, y) in E : x in V}, a
decomposition of R is a multiset of t points summing to -R. Semaev's eq. (11)
models the number of such multisets as a symmetric random map V^t -> F_q, so it
is a statement about CLASSES OF x-TUPLES, and the quantity it predicts is the
fraction of R with none. This module produces that count exactly, by adding
points, at three granularities that are deliberately kept apart:

  usable_point_multiset  t-multisets of F_q-RATIONAL factor-base points summing
                         to -R. These are the relations the algorithm can
                         actually use.
  single_eq4_x_multiset  x-multisets {x_1..x_t} from V for which SOME choice of
                         y_i in F_{q^2} sums to -R -- equivalently
                         S_{t+1}(x_1..x_t, R_X) = 0, obtained by counting and
                         never by constructing the polynomial. This is the
                         class count eq. (11) models.
  chained_eq5_x_multiset x-multisets admitting a full chain of eq. (5): an
                         ordering whose every intermediate partial sum is
                         affine with x-coordinate in F_q, which is what having
                         u_1..u_{t-2} in F_q means.

chained <= single always, and Lemma 2 says they agree when the lower-t systems
are unsatisfiable. Measuring the gap is the point, so the two are never merged.

NO SAMPLING INSIDE A CELL. Every count here is a complete enumeration. The
histogram path walks all C(L+t-1, t) multisets; the per-R path walks all
(t-1)-multisets and resolves the last point by lookup, which is also complete.
The two are computed independently and compared, so a defect in either shows up
as a disagreement rather than as a yield.

CHANGE LOG, RUN-SEMBIN-1b9afe. This module was inherited in the working tree
(untracked, authored 2026-09-13T15:39Z) and four changes were made before any
count was taken. All four are recorded in the run manifest.

  1. `chain_satisfiable` treated a partial sum as affine whenever the two sides
     were not both empty, which misses A = T2 with twist part T2: their sum is
     T2 + T2 = infinity, so the chain has no u_i there. The condition is now
     stated as "A + psi(B) = infinity iff both parts are empty, or both equal
     the 2-torsion point".
  2. `chain_satisfiable` searched all t! orderings. A partial sum depends on the
     SET of positions consumed, not their order, so the search is reachability
     in the subset lattice: 2^t states instead of t!, and 720 -> 64 at t = 6,
     which is what makes the t = 6 cell affordable. The permutation version is
     retained as `chain_satisfiable_permutations` and the two are checked
     against each other in selftest_yield_core.py.
  3. Counts are now reported at BOTH granularities. eq. (11)'s class count is
     over x-multisets, while HEUR-003 states a mean of 2^{tk-n} which is the
     ORDERED count |V|^t/q; the two differ by the orbit size and a ratio
     reported at the wrong one is off by up to t!. Both are emitted per R.
  4. Targets may now lie on the twist (`side="T"`). eq. (11) models a random
     z in F_q, while the algorithm's R_X is the x-coordinate of an F_q-rational
     point, which is only about half of F_q. The two populations are measured
     separately rather than conflated.
  5. A dead first definition of `twist_parts`, shadowed by the later
     `torsion_parts` wrapper of the same name and keyed differently in the
     cache, was removed. It was never reachable; deleting it changes no count.
  6. Per-R output now carries `s_counts` (solutions by how many y_i fall
     outside F_q) and `tau_counts_for_s_positive` (whether their sum H is
     infinity or the 2-torsion point). Lemma 2 part 1 is a statement about
     exactly those two distributions, and reporting only a total would have
     made it unmeasurable.
  7. `lemma2_side_condition` was added: the lemma's hypothesis is that the
     LOWER-i systems are unsatisfiable, and the contract makes that the
     denominator of the chained-versus-single comparison.
"""
from __future__ import annotations

import itertools
from math import comb, factorial

import numpy as np

from fastfield import INF_KEY, FastCurve, FastField, twist_a

U32 = np.uint32
U64 = np.uint64


# --------------------------------------------------------------------------
# Subspaces
# --------------------------------------------------------------------------
def span_of(basis: list[int]) -> list[int]:
    out = [0]
    for bvec in basis:
        out += [v ^ bvec for v in out]
    return sorted(out)


def build_subspace(field: FastField, k: int, variant: str,
                   rng: np.random.Generator) -> tuple[list[int], list[int]]:
    """V as an F_2-subspace of F_{2^n} of dimension exactly k, with its basis.

    low_degree_polynomial is Semaev's default V = {polynomials of degree < k},
    which in this encoding is the integers below 2^k. random_k_dimensional is
    the starred variant of Table 1: a random basis, rejected and redrawn until
    its rank over F_2 is exactly k.
    """
    if variant == "low_degree_polynomial":
        basis = [1 << i for i in range(k)]
    elif variant == "random_k_dimensional":
        while True:
            basis = [int(v) for v in rng.integers(1, field.q, size=k)]
            if _rank_f2(basis, field.n) == k:
                break
    else:
        raise ValueError(f"unknown subspace variant {variant}")
    V = span_of(basis)
    validate_subspace(V, k)
    return V, basis


def _rank_f2(vectors: list[int], n: int) -> int:
    rows, rank = list(vectors), 0
    for bit in reversed(range(n)):
        pivot = next((i for i, r in enumerate(rows) if r >> bit & 1), None)
        if pivot is None:
            continue
        p = rows.pop(pivot)
        rows = [r ^ p if r >> bit & 1 else r for r in rows]
        rank += 1
    return rank


def validate_subspace(V, k: int) -> None:
    """Reject anything that is not an F_2-subspace. An invalid_input control.

    V must contain 0, be closed under addition, and have exactly 2^k elements.
    A factor base that is merely a SET makes the Weil-descent formulation of
    eq. (5) false, so this is a correctness gate and not a convenience check.
    """
    s = set(V)
    if len(s) != len(V):
        raise ValueError("V has repeated elements")
    if len(V) != 1 << k:
        raise ValueError(f"V has {len(V)} elements, expected 2^{k}")
    if 0 not in s:
        raise ValueError("V does not contain 0, so it is not a subspace")
    for a in V:
        for b in V:
            if a ^ b not in s:
                raise ValueError(f"V is not closed under F_2-addition: "
                                 f"{a} ^ {b} = {a ^ b} is outside V")


def validate_target(R) -> None:
    """Reject the point at infinity as a target. An invalid_input control.

    Semaev's step 2 handles R = infinity by solving bz + a = 0 mod r, which is
    not a decomposition at all; counting it would put a spurious success into
    every cell.
    """
    if R is None:
        raise ValueError("R is the point at infinity: not a decomposition "
                         "target; handled by the linear relation in step 2")
    x, y = R
    if not isinstance(x, int) or not isinstance(y, int):
        raise ValueError("R must be an affine point (x, y)")


# --------------------------------------------------------------------------
# Scalar group law over the log tables (used for the chain condition)
# --------------------------------------------------------------------------
class ScalarCurve:
    """Group law on single points, fast enough for the per-solution chain walk.

    Same formulas as `fastfield.FastCurve`, on Python ints. Infinity is None.
    """

    def __init__(self, field: FastField, a: int, b: int) -> None:
        self.f = field
        self.a = a
        self.b = b
        self.antilog = field.antilog
        self.logt = field.logt
        self.order = field.order

    def mul(self, u: int, v: int) -> int:
        if u == 0 or v == 0:
            return 0
        s = int(self.logt[u]) + int(self.logt[v])
        if s >= self.order:
            s -= self.order
        return int(self.antilog[s])

    def inv(self, u: int) -> int:
        l = int(self.logt[u])
        return int(self.antilog[0 if l == 0 else self.order - l])

    def add(self, p, q):
        if p is None:
            return q
        if q is None:
            return p
        x1, y1 = p
        x2, y2 = q
        if x1 == x2:
            if (y1 ^ y2) == x1:
                return None
            lam = x1 ^ self.mul(y1, self.inv(x1))
            x3 = self.mul(lam, lam) ^ lam ^ self.a
            y3 = self.mul(x1, x1) ^ self.mul(lam ^ 1, x3)
            return (x3, y3)
        lam = self.mul(y1 ^ y2, self.inv(x1 ^ x2))
        x3 = self.mul(lam, lam) ^ lam ^ x1 ^ x2 ^ self.a
        y3 = self.mul(lam, x1 ^ x3) ^ x3 ^ y1
        return (x3, y3)

    def neg(self, p):
        return None if p is None else (p[0], p[0] ^ p[1])


# --------------------------------------------------------------------------
# Exhaustive multiset enumeration
# --------------------------------------------------------------------------
def _expand(last: np.ndarray, L: int):
    """Ragged extension of multiset prefixes: every next index >= last."""
    counts = L - last
    total = int(counts.sum())
    parent = np.repeat(np.arange(last.size, dtype=np.int64), counts)
    starts = np.zeros(last.size, dtype=np.int64)
    np.cumsum(counts[:-1], out=starts[1:])
    offs = np.arange(total, dtype=np.int64) - np.repeat(starts, counts)
    return parent, last[parent] + offs


def multiset_tuples(L: int, m: int) -> np.ndarray:
    """Every index tuple i_1 <= ... <= i_m over range(L); shape (C(L+m-1,m), m)."""
    if m == 0:
        return np.zeros((1, 0), dtype=np.int64)
    tup = np.arange(L, dtype=np.int64).reshape(L, 1)
    for _ in range(m - 1):
        parent, new = _expand(tup[:, -1], L)
        tup = np.concatenate([tup[parent], new.reshape(-1, 1)], axis=1)
    assert tup.shape[0] == comb(L + m - 1, m)
    return tup


def sums_of_tuples(curve: FastCurve, X, Y, tup: np.ndarray):
    """Group sum of each index tuple, as (sx, sy, sinf) arrays."""
    if tup.shape[1] == 0:
        z = np.zeros(tup.shape[0], dtype=U32)
        return z, z.copy(), np.ones(tup.shape[0], dtype=bool)
    sx = X[tup[:, 0]].copy()
    sy = Y[tup[:, 0]].copy()
    si = np.zeros(tup.shape[0], dtype=bool)
    for col in range(1, tup.shape[1]):
        idx = tup[:, col]
        sx, sy, si = curve.add(sx, sy, si, X[idx], Y[idx],
                               np.zeros(idx.shape, dtype=bool))
    return sx, sy, si


def count_multiset_sums(curve: FastCurve, X, Y, t: int, target_keys: np.ndarray,
                        perm: np.ndarray | None = None,
                        state_cap: int = 4_000_000) -> tuple[np.ndarray, int]:
    """Per-target counts of t-multisets of the point list summing to the target.

    ONE enumeration per cell, then a lookup per target -- never one enumeration
    per target. Chunked on the first index so peak memory stays bounded
    regardless of |V|^t; the chunking changes nothing about what is visited,
    and `perm` (which reorders the point list) is the exhaustiveness control's
    second, independent ordering.
    """
    if perm is not None:
        X, Y = X[perm], Y[perm]
    L = int(X.size)
    counts = np.zeros(target_keys.size, dtype=np.int64)
    uniq, inverse = np.unique(target_keys, return_inverse=True)
    total_states = 0
    expected = comb(L + t - 1, t)
    per_first = max(1, comb(L + t - 2, t - 1)) if t > 1 else 1
    block = max(1, min(L, state_cap // max(1, per_first)))
    for lo in range(0, L, block):
        hi = min(lo + block, L)
        idx = np.arange(lo, hi, dtype=np.int64)
        sx, sy = X[idx].copy(), Y[idx].copy()
        si = np.zeros(idx.size, dtype=bool)
        last = idx
        for _ in range(t - 1):
            parent, new = _expand(last, L)
            sx, sy, si = curve.add(sx[parent], sy[parent], si[parent],
                                   X[new], Y[new], np.zeros(new.shape, dtype=bool))
            last = new
        total_states += int(sx.size)
        keys = curve.key(sx, sy, si)
        pos = np.searchsorted(uniq, keys)
        np.clip(pos, 0, uniq.size - 1, out=pos)
        hit = uniq[pos] == keys
        if hit.any():
            found = np.bincount(pos[hit], minlength=uniq.size)
            counts += found[inverse]
    assert total_states == expected, (total_states, expected)
    return counts, total_states


# --------------------------------------------------------------------------
# Per-R exhaustive extraction
# --------------------------------------------------------------------------
class PointList:
    """A factor-base point list with a sorted key index for exact lookup."""

    def __init__(self, curve: FastCurve, X, Y):
        self.curve = curve
        self.X = np.asarray(X, dtype=U32)
        self.Y = np.asarray(Y, dtype=U32)
        self.n = int(self.X.size)
        self.keys = curve.key(self.X, self.Y, np.zeros(self.n, dtype=bool))
        self._order = np.argsort(self.keys)
        self._sorted = self.keys[self._order]
        self._cache: dict[int, tuple] = {}

    def lookup(self, keys: np.ndarray):
        """Index of each key in the point list, or -1."""
        if self.n == 0:
            return np.full(keys.shape, -1, dtype=np.int64)
        pos = np.searchsorted(self._sorted, keys)
        np.clip(pos, 0, self.n - 1, out=pos)
        idx = self._order[pos]
        return np.where(self._sorted[pos] == keys, idx, -1)

    def prefix(self, m: int):
        """Cached (tuples, sums) for all m-multisets; independent of R."""
        if m not in self._cache:
            tup = multiset_tuples(self.n, m)
            self._cache[m] = (tup,) + sums_of_tuples(self.curve, self.X, self.Y, tup)
        return self._cache[m]

    def solutions(self, s: int, target) -> np.ndarray:
        """Every index tuple of size s whose points sum to `target`.

        `target` is (x, y) or None for infinity. Complete: it walks all
        (s-1)-multisets and closes each with the unique point that would
        finish it, keeping only closures that preserve the index ordering, so
        each multiset is produced exactly once.
        """
        if s == 0:
            return (np.zeros((1, 0), dtype=np.int64) if target is None
                    else np.zeros((0, 0), dtype=np.int64))
        tup, sx, sy, si = self.prefix(s - 1)
        # needed = target - partial
        nx, ny, ni = self.curve.negate(sx, sy, si)
        if target is None:
            tx, ty, ti = nx, ny, ni
        else:
            tgx = np.full(nx.shape, target[0], dtype=U32)
            tgy = np.full(nx.shape, target[1], dtype=U32)
            tz = np.zeros(nx.shape, dtype=bool)
            tx, ty, ti = self.curve.add(tgx, tgy, tz, nx, ny, ni)
        keys = self.curve.key(tx, ty, ti)
        idx = self.lookup(keys)
        ok = idx >= 0
        if s > 1:
            ok &= idx >= tup[:, -1]
        if not ok.any():
            return np.zeros((0, s), dtype=np.int64)
        return np.concatenate([tup[ok], idx[ok].reshape(-1, 1)], axis=1)


class CellContext:
    """Everything a cell needs: curve, twist, factor base, target machinery."""

    def __init__(self, n: int, a: int, b: int, V: list[int]) -> None:
        self.field = FastField.get(n)
        self.n, self.a, self.b, self.V = n, a, b, V
        self.curve = FastCurve(self.field, a, b)
        self.twist = FastCurve(self.field, twist_a(self.field, a), b)
        self.scalar_e = ScalarCurve(self.field, a, b)
        self.scalar_t = ScalarCurve(self.field, twist_a(self.field, a), b)
        self.t2 = self.curve.t2                       # (0, sqrt(b)), shared
        exs, eys, txs, tys = [], [], [], []
        for x in V:
            if x == 0:
                exs.append(0)
                eys.append(self.t2[1])
                continue
            roots = self.curve.ys_for_x_scalar(x)
            if roots:
                for y in roots:
                    exs.append(x)
                    eys.append(y)
            else:
                for y in self.twist.ys_for_x_scalar(x):
                    txs.append(x)
                    tys.append(y)
        self.e_pts = PointList(self.curve, np.array(exs, dtype=U32),
                               np.array(eys, dtype=U32))
        self.t_pts = PointList(self.twist, np.array(txs, dtype=U32),
                               np.array(tys, dtype=U32))
        assert bool(np.all(self.curve.on_curve(self.e_pts.X, self.e_pts.Y)))
        assert bool(np.all(self.twist.on_curve(self.t_pts.X, self.t_pts.Y)))
        self.n_rational_x = len(set(int(v) for v in self.e_pts.X))
        self.n_irrational_x = len(set(int(v) for v in self.t_pts.X))
        self._twist_cache: dict[int, list] = {}

    # -- the chain condition ----------------------------------------------
    def _point_of(self, item):
        kind, idx = item
        if kind == "E":
            return (int(self.e_pts.X[idx]), int(self.e_pts.Y[idx]))
        return (int(self.t_pts.X[idx]), int(self.t_pts.Y[idx]))

    def _partial_ok(self, A, B, size: int, t: int) -> bool:
        """Is a partial sum A + psi(B) a legal value of a chain variable u_i?

        u_i ranges over F_q and is the x-coordinate of the partial sum, so the
        partial sum must be AFFINE and its x-coordinate must lie in F_q.
        Writing phi for the non-trivial automorphism of F_{q^2}/F_q,
        phi(A + psi(B)) = A - psi(B), and a point has its x in F_q exactly when
        phi of it is itself or its negative, which gives 2 psi(B) = O or
        2 A = O -- i.e. A or B is infinity or the 2-torsion point. The sum is
        infinity exactly when both parts are empty or both are T2, since T2 is
        the one point the curve and its twist share.
        """
        if size <= 1 or size >= t:
            return True                       # no u_i is attached to these
        at_infinity = ((A is None and B is None)
                       or (A == self.t2 and B == self.t2))
        if at_infinity:
            return False
        return ((A is None or A == self.t2)
                or (B is None or B == self.t2))

    def chain_satisfiable(self, items: list[tuple[str, int]], t: int) -> bool:
        """Does some ordering give a full eq. (5) chain with u_1..u_{t-2} in F_q?

        Reachability in the subset lattice: a partial sum depends only on WHICH
        points have been consumed, so the t! orderings collapse to 2^t states.
        Equivalent to `chain_satisfiable_permutations` and checked against it.
        """
        if t <= 2:
            return True                       # no auxiliary variables at all
        full = (1 << t) - 1
        sums: list = [None] * (1 << t)
        sums[0] = (None, None)
        for S in range(1, 1 << t):
            low = S & -S
            i = low.bit_length() - 1
            A, B = sums[S ^ low]
            kind, _idx = items[i]
            if kind == "E":
                A = self.scalar_e.add(A, self._point_of(items[i]))
            else:
                B = self.scalar_t.add(B, self._point_of(items[i]))
            sums[S] = (A, B)
        reach = [False] * (1 << t)
        reach[0] = True
        for S in range(1, 1 << t):
            size = S.bit_count()
            A, B = sums[S]
            if not self._partial_ok(A, B, size, t):
                continue
            rest = S
            while rest:
                low = rest & -rest
                rest ^= low
                if reach[S ^ low]:
                    reach[S] = True
                    break
        return reach[full]

    def chain_satisfiable_permutations(self, items, t: int) -> bool:
        """The inherited t!-ordering version, retained as a cross-check only."""
        if t <= 2:
            return True
        for order in itertools.permutations(range(t)):
            A, B = None, None
            ok = True
            for pos, i in enumerate(order):
                kind, _idx = items[i]
                if kind == "E":
                    A = self.scalar_e.add(A, self._point_of(items[i]))
                else:
                    B = self.scalar_t.add(B, self._point_of(items[i]))
                if not self._partial_ok(A, B, pos + 1, t):
                    ok = False
                    break
            if ok:
                return True
        return False

    # -- the full per-R solution set --------------------------------------
    def torsion_parts(self, pts: "PointList", t: int, tag: str) -> dict:
        """For each j, the j-multisets of `pts` summing to O or to T2.

        Lemma 2 part 1 in arithmetic form, stated for whichever side is the
        MINORITY side of the decomposition: that side's partial sum has to
        re-enter the other curve, and the only two points both curves share
        are infinity and the 2-torsion point.
        """
        key = (tag, t)
        if key not in self._twist_cache:
            out = {}
            for j in range(0, t + 1):
                rows = []
                for tau_name, tau in (("O", None), ("T2", self.t2)):
                    if j == 0 and tau is not None:
                        continue
                    for row in pts.solutions(j, tau):
                        rows.append((tau_name, tuple(int(v) for v in row)))
                out[j] = rows
            self._twist_cache[key] = out
        return self._twist_cache[key]

    def twist_parts(self, t: int) -> dict:
        return self.torsion_parts(self.t_pts, t, "T")

    def solve_for_target(self, R: tuple[int, int], t: int,
                         side: str = "E") -> dict:
        """Complete solution set for one target at size t, Lemma-2 split.

        `side` says which curve the target sits on. side="E" is the contract's
        R in E(F_q), the target the algorithm actually decomposes. side="T" is
        a z in F_q with Tr(z + a + b/z^2) = 1, which carries no F_q-rational
        point at all but is still a legal argument of S_{t+1} and is half of
        the population eq. (11)'s "random z in F_q" model averages over.

        A decomposition splits as (E-part) + psi(twist-part); whichever side
        the target is NOT on must sum to O or T2, so that side is enumerated
        by `torsion_parts` and crossed with the target side.
        """
        validate_target(R)
        if side == "E":
            side_pts, other_pts = self.e_pts, self.t_pts
            side_scalar, other_tag = self.scalar_e, "T"
            side_kind, other_kind = "E", "T"
        elif side == "T":
            side_pts, other_pts = self.t_pts, self.e_pts
            side_scalar, other_tag = self.scalar_t, "E"
            side_kind, other_kind = "T", "E"
        else:
            raise ValueError(f"unknown target side {side}")
        minus_r = side_scalar.neg(R)
        results = []
        for j, rows in self.torsion_parts(other_pts, t, other_tag).items():
            if j > t or not rows:
                continue
            for tau_name in ("O", "T2"):
                other_rows = [tw for name, tw in rows if name == tau_name]
                if not other_rows:
                    continue
                # The TARGET side is resolved FIRST. At j = t there can be
                # thousands of pairs summing to O or T2, and looping over them
                # before discovering the target side is empty would cost more
                # than the whole enumeration it is meant to complete.
                side_target = (minus_r if tau_name == "O"
                               else side_scalar.add(minus_r, self.t2))
                side_sols = side_pts.solutions(t - j, side_target)
                if side_sols.shape[0] == 0:
                    continue
                for srow in side_sols:
                    base = [(side_kind, int(v)) for v in srow]
                    for other in other_rows:
                        results.append((base + [(other_kind, int(v))
                                                for v in other], tau_name))
        return self._summarise(results, t)

    def _xs_of(self, items) -> tuple:
        return tuple(sorted(
            (int(self.e_pts.X[i]) if kind == "E" else int(self.t_pts.X[i]))
            for kind, i in items))

    def _summarise(self, results: list, t: int) -> dict:
        """Every reported quantity for one target, with the Lemma-2 split kept.

        `s_counts` and `tau_counts` are the Lemma-2 part 1 instrument. The
        lemma says the sum H of the points with y outside F_q has order
        EXACTLY 2, so s = 0 or s >= 2 and H is the 2-torsion point rather than
        infinity. `s_counts[1]` must therefore be empty, and under the side
        condition `tau_counts["O"]` must be empty for s > 0; both are recorded
        per R rather than asserted, because the whole point of the cell is to
        measure how often the side condition fails.
        """
        x_multisets, chained_x = set(), set()
        with_rational, with_outside = set(), set()
        usable_pm = outside_pm = 0
        max_s = 0
        s_counts: dict[int, int] = {}
        tau_counts = {"O": 0, "T2": 0}
        for items, tau_name in results:
            xs = self._xs_of(items)
            x_multisets.add(xs)
            s = sum(1 for kind, _i in items if kind == "T")
            s_counts[s] = s_counts.get(s, 0) + 1
            if s == 0:
                usable_pm += 1
                with_rational.add(xs)
            else:
                outside_pm += 1
                with_outside.add(xs)
                max_s = max(max_s, s)
                tau_counts[tau_name] += 1
            if xs not in chained_x and self.chain_satisfiable(items, t):
                chained_x.add(xs)
        return {
            "point_multiset_total": len(results),
            "usable_point_multiset": usable_pm,
            "outside_fq_point_multiset": outside_pm,
            "max_y_outside_fq": max_s,
            "s_counts": {str(s): c for s, c in sorted(s_counts.items())},
            "tau_counts_for_s_positive": dict(tau_counts),
            "single_x_multiset": len(x_multisets),
            "chained_x_multiset": len(chained_x),
            "single_x_ordered": sum(ordered_orbit(xs, t) for xs in x_multisets),
            "chained_x_ordered": sum(ordered_orbit(xs, t) for xs in chained_x),
            "x_multiset_outside_only": len(with_outside - with_rational),
            "x_multiset_both_kinds": len(with_outside & with_rational),
        }

    # -- Lemma 2's side condition -----------------------------------------
    def lemma2_side_condition(self, R: tuple[int, int], t: int,
                              side: str = "E") -> dict:
        """Are the LOWER-i systems S_{i+1}(x_1..x_i, R_X) = 0 unsatisfiable?

        Lemma 2 assumes exactly this for 2 <= i < t, and both its conclusions
        -- that the chain (9) exists, and that H has order exactly 2 -- are
        conditional on it. It is therefore the denominator of the
        chained-versus-single comparison: an R where it fails is an R where
        the lemma predicts nothing, and averaging those in would hide the
        thing the comparison is for.

        Returns the per-i single-presentation counts, so a reader can see
        WHICH lower system was satisfiable rather than only that one was.
        """
        per_i = {}
        for i in range(2, t):
            per_i[str(i)] = int(self.solve_for_target(R, i, side=side)
                                ["single_x_multiset"])
        return {
            "lower_i_single_counts": per_i,
            "holds": all(v == 0 for v in per_i.values()),
            "vacuous": t <= 2,
        }


def ordered_orbit(xs: tuple, t: int) -> int:
    """Distinct orderings of an x-multiset: t! / prod(multiplicity!).

    The bridge between the two count granularities. eq. (11) counts classes;
    2^{tk-n} counts ordered tuples; a class of full orbit size contributes t!
    ordered tuples and a degenerate one contributes fewer, which is exactly
    the discrepancy between |V|^t/t! and C(|V|+t-1, t).
    """
    out = factorial(t)
    run = 1
    for i in range(1, len(xs)):
        if xs[i] == xs[i - 1]:
            run += 1
            out //= run
        else:
            run = 1
    return out
