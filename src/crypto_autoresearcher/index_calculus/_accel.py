"""Optional numpy scan for the last two decomposition variables.

For a target R and factor-base element F_i with x_i != x(R), the two roots of
S_3(x_i, X, x(R)) are exactly x(R - F_i) and x(R + F_i).  This module computes
both for every i at once -- one batched inversion of x_i - x(R) (a product
tree, about three modular multiplications per element) and a few vector
multiplications -- and marks the indices where a root lies in the factor base.

It only *locates* work: decompose.py still runs its scalar step at every
marked index and charges every skipped index exactly what the scalar step
would have (one S_3 solve, two membership tests, no group operations), so
relations and operation counts are identical with and without numpy.  All
arithmetic is on uint64 with p < 2^32, so every product fits.
"""

from __future__ import annotations

try:
    import numpy as np
except ImportError:  # pragma: no cover - exercised only without numpy
    np = None

MAX_P = 1 << 32  # (p - 1)^2 must fit in uint64


def available() -> bool:
    return np is not None


def usable(p: int) -> bool:
    return np is not None and p < MAX_P


class FBArrays:
    """Factor-base coordinates as arrays, with a sorted index for lookups."""

    def __init__(self, fb) -> None:
        if not usable(fb.p):
            raise RuntimeError("vectorised scan needs numpy and p < 2^32")
        self.n = len(fb.points)
        self.p = np.uint64(fb.p)
        self.X = np.array([P[0] for P in fb.points], dtype=np.uint64)
        self.Y = np.array([P[1] for P in fb.points], dtype=np.uint64)
        self.order = np.argsort(self.X, kind="stable").astype(np.int64)
        self.sorted_x = self.X[self.order]

    def lookup(self, vals):
        """Factor-base index of each value, or -1."""
        pos = np.searchsorted(self.sorted_x, vals)
        pos = np.minimum(pos, self.n - 1)
        found = self.sorted_x[pos] == vals
        return np.where(found, self.order[pos], -1)


def batch_inverse(v, p):
    """Elementwise inverses mod p of a non-zero uint64 vector (product tree)."""
    levels = []
    cur = v
    while cur.shape[0] > 1:
        if cur.shape[0] & 1:
            cur = np.concatenate([cur, np.ones(1, dtype=np.uint64)])
        levels.append(cur)
        cur = (cur[0::2] * cur[1::2]) % p
    inv = np.array([pow(int(cur[0]), -1, int(p))], dtype=np.uint64)
    for lvl in reversed(levels):
        inv = inv[: lvl.shape[0] // 2]
        out = np.empty(lvl.shape[0], dtype=np.uint64)
        out[0::2] = (inv * lvl[1::2]) % p
        out[1::2] = (inv * lvl[0::2]) % p
        inv = out
    return inv[: v.shape[0]]


def m2_candidates(arr: FBArrays, xR: int, yR: int, lo: int):
    """Indices i >= lo that the scalar m = 2 step must visit, ascending.

    Those are the i where x(R - F_i) or x(R + F_i) is the x-coordinate of a
    factor-base element F_j with j >= i, plus the (at most one) i with
    x_i = x(R), whose S_3 is degenerate and is left to the scalar code.
    """
    return m2_candidates_multi(arr, [(xR, yR, lo)])[0]


def m2_candidates_multi(arr: FBArrays, targets: list[tuple[int, int, int]]):
    """``m2_candidates`` for several (x(R), y(R), lo) targets in one 2-D pass."""
    n = arr.n
    if not targets:
        return []
    lo_min = min(t[2] for t in targets)
    if lo_min >= n:
        return [np.empty(0, dtype=np.int64) for _ in targets]
    p = arr.p
    X, Y = arr.X[None, lo_min:], arr.Y[None, lo_min:]
    xr = np.array([t[0] for t in targets], dtype=np.uint64)[:, None]
    yr = np.array([t[1] for t in targets], dtype=np.uint64)[:, None]
    los = np.array([t[2] for t in targets], dtype=np.int64)[:, None]
    dx = (X + (p - xr)) % p
    zero = dx == 0
    dx[zero] = 1
    inv = batch_inverse(dx.ravel(), p).reshape(dx.shape)
    s = (X + xr) % p
    lam = ((p - Y) + (p - yr)) % p * inv % p          # slope of R + (-F_i)
    x_minus = (lam * lam % p + (p - s)) % p
    lam = (Y + (p - yr)) % p * inv % p                # slope of R + F_i
    x_plus = (lam * lam % p + (p - s)) % p
    idx = np.arange(lo_min, n, dtype=np.int64)[None, :]
    hit = (arr.lookup(x_minus) >= idx) | (arr.lookup(x_plus) >= idx)
    mask = (idx >= los) & ((hit & ~zero) | zero)
    return [idx[0, mask[k]] for k in range(len(targets))]


def subtract_many(arr: FBArrays, xR: int, yR: int, idx, signs):
    """x, y of R - s_k F_{i_k} for each k, and a mask of the entries with
    x_{i_k} = x(R) (R -/+ F is O or a doubling there; the caller handles them).
    """
    p = arr.p
    X, Y = arr.X[idx], arr.Y[idx]
    xr, yr = np.uint64(xR), np.uint64(yR)
    Yn = np.where(signs > 0, (p - Y) % p, Y)          # y of -s F
    dx = (X + (p - xr)) % p
    zero = dx == 0
    dx[zero] = 1
    inv = batch_inverse(dx, p)
    lam = (Yn + (p - yr)) % p * inv % p
    x3 = (lam * lam % p + (p - (X + xr) % p)) % p
    y3 = (lam * ((xr + (p - x3)) % p) % p + (p - yr)) % p
    return x3, y3, zero
