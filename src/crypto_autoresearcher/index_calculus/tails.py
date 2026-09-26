"""Precomputed tails for meet-in-the-middle decomposition.

Exhaustive decomposition (decompose.py) fixes m - 2 signed factor-base points,
solves S_3 for the next, and asks whether the one left over is in the base: a
point of the base is a "tail" of one element.  This module stores longer
tails.  A table of arity h holds every signed sum of h factor-base points,
keyed by its x-coordinate, so a search that has fixed m - h - 1 points and
solved S_3 for the next one finishes with a lookup.  Per target that is
|F|^(m-h) S_3 solves instead of |F|^(m-1); the table itself is built once per
factor base and reused for every target of a solve.

What is stored
--------------
A tail is an *ordering* ((i_1, s_1), ..., (i_h, s_h)) with i_1 <= ... <= i_h,
exactly the order in which the exhaustive search would visit it, and every
suffix of it has a non-zero sum.  That is the search's own reachability rule:
it abandons a branch whose remainder is the point at infinity.  So a search
over the table visits precisely the decompositions exhaustive search visits,
no more (a tail ending in F - F never matches) and no fewer.

A tail and its negation have the same x-coordinate, so only one of each pair
is stored, the one with s_1 = +1, together with one bit telling which of the
two y-coordinates its sum has.  A lookup orients the tail to the point asked
about.  The table holds about (2|F|)^h / (2 h!) tails: |F|^2 at h = 2.

How it is built, and what that costs
------------------------------------
Level k is level k - 1 with one element prepended: for a stored tail T with
sum S and first index b, and each a <= b, the sums F_a + S and F_a - S give
the tails (a, +1) + T and (a, +1) + (-T).  Both come from one shared
inversion of x(S) - x(F_a), which is exactly the pair of x-coordinates one
S_3 solve yields (plus the y-coordinates, for two more multiplications).  So
each (a, T) is charged as one S_3 solve, the unit the search is counted in,
and the total is reported as ``s3_solves``.  A pair whose sum is the point at
infinity is charged and dropped.

With numpy and p < 2^32 the prepend step runs as a vector over T for each a;
the tails, codes and charges are identical to the pure-Python build.
"""

from __future__ import annotations

import time

from . import _accel
from .curve import Curve
from .factor_base import FactorBase

Tail = list[tuple[int, int]]


def default_table_arity(m: int) -> int:
    """The arity that balances table size against per-target work.

    With |F| near its default a solve tries about |F| targets, so it costs
    about |F|^h to build the table plus |F| * |F|^(m-h) to search: balanced at
    h = (m + 1) / 2.  At m = 2 that is h = 1, the exhaustive search itself.
    """
    return max(1, min(m - 1, (m + 1) // 2))


class TailTable:
    """Signed sums of ``arity`` factor-base points, keyed by x-coordinate.

    Each tail is packed into one integer: digit t (base B = 2|F|) is
    2 i_t + [s_t < 0], and the lowest bit says whether the sum's y-coordinate
    is above p / 2.  Arity 1 is the factor base itself and builds nothing.
    """

    def __init__(self, E: Curve, fb: FactorBase, arity: int,
                 accelerate: bool | None = None) -> None:
        if arity < 1:
            raise ValueError("table arity must be >= 1")
        self.fb = fb
        self.arity = arity
        self.p = E.p
        self.base = 2 * len(fb)
        self.s3_solves = 0
        self.entries = len(fb) if arity == 1 else 0
        self._map: dict[int, int | list[int]] = {}
        self._index = None
        t0 = time.perf_counter()
        if arity > 1 and len(fb):
            accel = _accel.usable(E.p) if accelerate is None else accelerate
            fits = self.base ** arity < 1 << 61  # packed codes stay int64
            if accel and fits:
                self._build_numpy(E)
            else:
                self._build_python(E)
            if accel:
                self.arrays()  # the scan's index, so its build is timed with the table
        self.seconds = time.perf_counter() - t0

    # -- lookups -------------------------------------------------------------
    def codes(self, x: int, lo: int) -> list[int]:
        """Packed tails whose sum has x-coordinate x and first index >= lo."""
        c = self._map.get(x)
        if c is None:
            return []
        cs = (c,) if type(c) is int else c
        return [code for code in cs if self._first(code) >= lo]

    def orient(self, code: int, y: int) -> Tail:
        """The tail packed in ``code``, negated if needed to sum to (x, y)."""
        v, flip = code >> 1, (code & 1) != (y > self.p // 2)
        out = []
        for _ in range(self.arity):
            v, d = divmod(v, self.base)
            s = -1 if d & 1 else 1
            out.append((d >> 1, -s if flip else s))
        return out

    def arrays(self):
        """numpy lookup for the vectorised scan: x -> largest first index."""
        if self._index is None:
            import numpy as np

            xs = np.fromiter(self._map.keys(), dtype=np.uint64, count=len(self._map))
            firsts = np.fromiter(
                (self._first(c) if type(c) is int else max(map(self._first, c))
                 for c in self._map.values()), dtype=np.int64, count=len(self._map))
            order = np.argsort(xs, kind="stable")
            self._index = _accel.KeyIndex(xs[order], firsts[order])
        return self._index

    def describe(self) -> dict:
        return {"arity": self.arity, "entries": self.entries,
                "s3_solves": self.s3_solves, "seconds": self.seconds}

    def _first(self, code: int) -> int:
        return ((code >> 1) % self.base) >> 1

    # -- building ------------------------------------------------------------
    def _insert(self, x: int, code: int) -> None:
        old = self._map.get(x)
        if old is None:
            self._map[x] = code
        elif type(old) is int:
            self._map[x] = [old, code]
        else:
            old.append(code)
        self.entries += 1

    def _build_python(self, E: Curve) -> None:
        B, pts = self.base, self.fb.points
        # (x, y, digits, digits of the negation, first index), by first index
        level = [(P[0], P[1], 2 * i, 2 * i + 1, i) for i, P in enumerate(pts)]
        for _ in range(2, self.arity + 1):
            start = _starts([e[4] for e in level], len(pts))
            nxt = []
            for a, (xa, ya) in enumerate(pts):
                for xs, ys, v, nv, _ in level[start[a]:]:
                    self.s3_solves += 1
                    plus, minus = _plus_minus(E, xa, ya, xs, ys)
                    if plus is not None:
                        nxt.append((plus[0], plus[1], 2 * a + B * v, 2 * a + 1 + B * nv, a))
                    if minus is not None:
                        nxt.append((minus[0], minus[1], 2 * a + B * nv, 2 * a + 1 + B * v, a))
            level = nxt
        for x, y, v, _, _ in level:
            self._insert(x, (v << 1) | (y > self.p // 2))
        self._sort_collisions()

    def _build_numpy(self, E: Curve) -> None:
        import numpy as np

        p, B, pts = E.p, self.base, self.fb.points
        P64 = np.uint64(p)
        FX = np.array([P[0] for P in pts], dtype=np.uint64)
        FY = np.array([P[1] for P in pts], dtype=np.uint64)
        idx = np.arange(len(pts), dtype=np.int64)
        X, Y, V, NV, FIRST = FX, FY, 2 * idx, 2 * idx + 1, idx
        for _ in range(2, self.arity + 1):
            start = _starts(FIRST.tolist(), len(pts))
            parts = []
            for a in range(len(pts)):
                s = start[a]
                xs, ys, v, nv = X[s:], Y[s:], V[s:], NV[s:]
                if not len(xs):
                    continue
                self.s3_solves += len(xs)
                xa, ya = FX[a], FY[a]
                dx = (xs + (P64 - xa)) % P64
                zero = dx == 0
                dx[zero] = 1
                inv = _accel.batch_inverse(dx, P64)
                s_sum = (xa + xs) % P64
                # F_a + S
                lam = (ys + (P64 - ya)) % P64 * inv % P64
                x1 = (lam * lam % P64 + (P64 - s_sum)) % P64
                y1 = (lam * ((xa + (P64 - x1)) % P64) % P64 + (P64 - ya)) % P64
                # F_a - S = F_a + (x_S, -y_S)
                lam = ((P64 - ys) % P64 + (P64 - ya)) % P64 * inv % P64
                x2 = (lam * lam % P64 + (P64 - s_sum)) % P64
                y2 = (lam * ((xa + (P64 - x2)) % P64) % P64 + (P64 - ya)) % P64
                ok1, ok2 = ~zero, ~zero
                for k in np.flatnonzero(zero).tolist():
                    plus, minus = _plus_minus(E, int(xa), int(ya), int(xs[k]), int(ys[k]))
                    if plus is not None:
                        x1[k], y1[k], ok1[k] = plus[0], plus[1], True
                    if minus is not None:
                        x2[k], y2[k], ok2[k] = minus[0], minus[1], True
                parts.append((x1[ok1], y1[ok1], 2 * a + B * v[ok1],
                              2 * a + 1 + B * nv[ok1], np.full(int(ok1.sum()), a)))
                parts.append((x2[ok2], y2[ok2], 2 * a + B * nv[ok2],
                              2 * a + 1 + B * v[ok2], np.full(int(ok2.sum()), a)))
            X, Y, V, NV, FIRST = (np.concatenate([q[j] for q in parts]) for j in range(5))
        half = np.uint64(p // 2)
        codes = (V << 1) | (Y > half).astype(np.int64)
        for x, c in zip(X.tolist(), codes.tolist()):
            self._insert(x, c)
        self._sort_collisions()

    def _sort_collisions(self) -> None:
        for c in self._map.values():
            if type(c) is not int:
                c.sort()


def _starts(firsts: list[int], n: int) -> list[int]:
    """start[a]: position of the first entry with first index >= a (sorted input)."""
    start, j = [0] * (n + 1), 0
    for a in range(n + 1):
        while j < len(firsts) and firsts[j] < a:
            j += 1
        start[a] = j
    return start


def _plus_minus(E: Curve, xa: int, ya: int, xs: int, ys: int):
    """(F + S, F - S) for F = (xa, ya), S = (xs, ys), None for the point at infinity."""
    p = E.p
    if xs == xa:
        # S = +/-F: one of the two is infinity, the other the doubling of +/-F
        lam = (3 * xa * xa + E.a) * pow(2 * ya, -1, p) % p
        x3 = (lam * lam - 2 * xa) % p
        D = (x3, (lam * (xa - x3) - ya) % p)  # 2F
        return (D, None) if ys == ya else (None, D)
    inv = pow(xs - xa, -1, p)
    out = []
    for y in (ys, -ys):
        lam = (y - ya) * inv % p
        x3 = (lam * lam - xa - xs) % p
        out.append((x3, (lam * (xa - x3) - ya) % p))
    return out[0], out[1]
