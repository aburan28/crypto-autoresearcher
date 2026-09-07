"""Toy prime-order short-Weierstrass curve arithmetic and r-adding walk for
the Stage 3 curve arm of EXP-ECDLP-612fb1.

y^2 = x^3 + a x + b over F_p, p about 2^24, p = 3 mod 4 (so square roots
are rhs^((p+1)/4)).  Two implementations of the group law live here: a
scalar Python-int one (used by the SOLVER for precomputation restarts and
target generation) and a vectorised NumPy int64 one (used by the WALK and
the exact basin enumeration; products stay below 2^50).  The independent
certificate verifier is in verify_certificate.py and shares NO code with
this module.

Points are affine (x, y) with the point at infinity represented by
(x = -1, y = -1) in the vectorised code and by None in the scalar code.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np

from instrument import mix64, Params


# ---------------------------------------------------------------------------
# scalar arithmetic (solver side)
# ---------------------------------------------------------------------------

@dataclass
class Curve:
    p: int
    a: int
    b: int
    N: int                       # group order (prime)
    G: Tuple[int, int]           # generator P

    def on_curve(self, Q) -> bool:
        if Q is None:
            return True
        x, y = Q
        return (y * y - (x * x * x + self.a * x + self.b)) % self.p == 0

    def add(self, P1, P2):
        p = self.p
        if P1 is None:
            return P2
        if P2 is None:
            return P1
        x1, y1 = P1
        x2, y2 = P2
        if x1 == x2:
            if (y1 + y2) % p == 0:
                return None
            lam = (3 * x1 * x1 + self.a) * pow(2 * y1, -1, p) % p
        else:
            lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
        x3 = (lam * lam - x1 - x2) % p
        y3 = (lam * (x1 - x3) - y1) % p
        return (x3, y3)

    def mul(self, k: int, Q):
        """Left-to-right double-and-add (solver side)."""
        k %= self.N
        R = None
        for bit in bin(k)[2:]:
            R = self.add(R, R)
            if bit == "1":
                R = self.add(R, Q)
        return R


def is_probable_prime(n: int) -> bool:
    """Deterministic Miller-Rabin for n < 3,215,031,751 (bases 2, 3, 5, 7)."""
    if n < 2:
        return False
    for q in (2, 3, 5, 7):
        if n % q == 0:
            return n == q
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a_ in (2, 3, 5, 7):
        x = pow(a_, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


# ---------------------------------------------------------------------------
# vectorised arithmetic (walk side)
# ---------------------------------------------------------------------------

def modpow_vec(base: np.ndarray, e: int, p: int) -> np.ndarray:
    result = np.ones_like(base)
    b = base % p
    while e:
        if e & 1:
            result = result * b % p
        b = b * b % p
        e >>= 1
    return result


def inv_vec(x: np.ndarray, p: int) -> np.ndarray:
    return modpow_vec(x, p - 2, p)


def add_vec(x1, y1, x2, y2, a: int, p: int):
    """Vectorised affine addition; infinity encoded as x = -1."""
    inf1 = x1 < 0
    inf2 = x2 < 0
    same_x = (x1 == x2) & ~inf1 & ~inf2
    dbl = same_x & (y1 == y2) & (y1 != 0)
    neg = same_x & ~dbl
    gen = ~inf1 & ~inf2 & ~same_x
    x3 = np.full_like(x1, -1)
    y3 = np.full_like(y1, -1)
    # general case
    if gen.any():
        dx = (x2[gen] - x1[gen]) % p
        lam = (y2[gen] - y1[gen]) % p * inv_vec(dx, p) % p
        xx = (lam * lam - x1[gen] - x2[gen]) % p
        yy = (lam * (x1[gen] - xx) % p - y1[gen]) % p
        x3[gen] = xx
        y3[gen] = yy
    if dbl.any():
        num = (3 * x1[dbl] % p * x1[dbl] + a) % p
        lam = num * inv_vec(2 * y1[dbl] % p, p) % p
        xx = (lam * lam - 2 * x1[dbl]) % p
        yy = (lam * (x1[dbl] - xx) % p - y1[dbl]) % p
        x3[dbl] = xx
        y3[dbl] = yy
    # P + O = P
    x3[inf2 & ~inf1] = x1[inf2 & ~inf1]
    y3[inf2 & ~inf1] = y1[inf2 & ~inf1]
    x3[inf1 & ~inf2] = x2[inf1 & ~inf2]
    y3[inf1 & ~inf2] = y2[inf1 & ~inf2]
    # neg and inf1&inf2 stay at infinity
    return x3, y3


def count_points(p: int, a: int, b: int) -> int:
    """#E(F_p) = 1 + sum_x (1 + legendre(x^3 + a x + b)) by Euler's criterion,
    vectorised over all x (p about 2^24)."""
    total = 1
    chunk = 1 << 22
    for lo in range(0, p, chunk):
        x = np.arange(lo, min(p, lo + chunk), dtype=np.int64)
        rhs = (x * x % p * x + a * x + b) % p
        leg = modpow_vec(rhs, (p - 1) // 2, p)
        total += int(np.sum(rhs == 0)) + 2 * int(np.sum(leg == 1))
    return total


# ---------------------------------------------------------------------------
# the r-adding walk (r = 32), point enumeration and exact basins
# ---------------------------------------------------------------------------

class CurveWalk:
    """f(X) = X + M_{j(X)}, j(X) = hash(x(X)) mod 32, M_j = [m_j] P with seeded
    known m_j independent of every target; DP predicate on hash(x(X))."""

    R_ADD = 32

    def __init__(self, E: Curve, P: Params):
        self.E = E
        self.P = P
        rng = np.random.default_rng([P.seed, 7])        # multiplier stream from the walk-key seed
        self.m = [int(v) for v in rng.integers(1, E.N, size=self.R_ADD, dtype=np.int64)]
        pts = [E.mul(mj, E.G) for mj in self.m]
        self.Mx = np.asarray([q[0] for q in pts], dtype=np.int64)
        self.My = np.asarray([q[1] for q in pts], dtype=np.int64)
        self.m_arr = np.asarray(self.m, dtype=np.int64)
        self.K_j = P.K ^ 0xA5A5A5A5A5A5A5A5

    def j_of(self, x: np.ndarray) -> np.ndarray:
        return (mix64(x.astype(np.uint64) ^ np.uint64(self.K_j)) % np.uint64(self.R_ADD)).astype(np.int64)

    def is_dp(self, x: np.ndarray) -> np.ndarray:
        return self.P.is_dp(x.astype(np.uint64))

    def key(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Canonical integer identity of an affine point: 2 x + [y > p/2]."""
        return 2 * x + (y > self.E.p // 2).astype(np.int64)

    def step(self, x, y):
        j = self.j_of(x)
        nx, ny = add_vec(x, y, self.Mx[j], self.My[j], self.E.a, self.E.p)
        return nx, ny, self.m_arr[j]

    def walk(self, x0: np.ndarray, y0: np.ndarray, s0: np.ndarray):
        """Walk every start to its first DP or the cap.  Returns
        (term_key, length, scalar) with term_key = -1 for a capped walk or a
        walk that reached the point at infinity (charged at the cap, no DP);
        scalar = s0 + accumulated m_j (mod N) at the terminal point."""
        n = len(x0)
        x = x0.astype(np.int64).copy()
        y = y0.astype(np.int64).copy()
        s = s0.astype(np.int64).copy() % self.E.N
        term = np.full(n, -1, dtype=np.int64)
        length = np.zeros(n, dtype=np.int64)
        inf_hits = 0
        active = np.arange(n)
        dp = self.is_dp(x[active])
        term[active[dp]] = self.key(x[active[dp]], y[active[dp]])
        active = active[~dp]
        steps = 0
        while active.size and steps < self.P.cap:
            nx, ny, dm = self.step(x[active], y[active])
            x[active] = nx
            y[active] = ny
            s[active] = (s[active] + dm) % self.E.N
            steps += 1
            inf = nx < 0
            if inf.any():
                inf_hits += int(inf.sum())
                active = active[~inf]
                nx, ny = nx[~inf], ny[~inf]
            dp = self.is_dp(nx)
            hit = active[dp]
            term[hit] = self.key(nx[dp], ny[dp])
            length[hit] = steps
            active = active[~dp]
        length[term < 0] = self.P.cap
        return term, length, s, inf_hits


def enumerate_points(E: Curve):
    """All affine points sorted by key = 2x + [y > p/2]; returns (keys, x, y)."""
    p = E.p
    xs, ys = [], []
    chunk = 1 << 22
    for lo in range(0, p, chunk):
        x = np.arange(lo, min(p, lo + chunk), dtype=np.int64)
        rhs = (x * x % p * x + E.a * x + E.b) % p
        leg = modpow_vec(rhs, (p - 1) // 2, p)
        sq = leg == 1
        y = modpow_vec(rhs[sq], (p + 1) // 4, p)
        xs.append(x[sq]); ys.append(y)
        xs.append(x[sq]); ys.append((p - y) % p)
        z = rhs == 0
        xs.append(x[z]); ys.append(np.zeros(int(z.sum()), dtype=np.int64))
    x = np.concatenate(xs)
    y = np.concatenate(ys)
    keys = 2 * x + (y > p // 2).astype(np.int64)
    order = np.argsort(keys, kind="stable")
    return keys[order], x[order], y[order]


def exact_basins_curve(E: Curve, walk: CurveWalk):
    """Exact basins of every DP over all N - 1 affine points by pointer
    jumping (the point at infinity is an absorbing non-DP sink)."""
    from instrument import Basins
    keys, x, y = enumerate_points(E)
    n = len(keys)
    assert n == E.N - 1, (n, E.N)
    sink = n                                  # virtual node for the point at infinity
    nx, ny, _ = walk.step(x, y)
    nk = walk.key(nx, ny)
    nxt = np.searchsorted(keys, nk).astype(np.int64)
    nxt = np.minimum(nxt, n - 1)
    bad = keys[nxt] != nk
    nxt[bad | (nx < 0)] = sink
    nxt = np.append(nxt, sink).astype(np.int32)
    dp = np.append(walk.is_dp(x), False)
    dps_idx = np.flatnonzero(dp)
    nxt[dp] = dps_idx.astype(np.int32)
    dist = (~dp).astype(np.int32)
    del nx, ny, nk
    n_bits = int(math.ceil(math.log2(n + 1)))
    for _ in range(n_bits):
        dist = dist + dist[nxt]
        nxt = nxt[nxt]
    sat = np.int32(1 << n_bits)
    reach = (dist < sat) & (nxt != sink)
    reach[sink] = False
    ok = reach & (dist <= walk.P.cap)
    ok[sink] = False
    cycle_mass = int((~reach[:n]).sum())
    capped_mass = int((reach[:n] & ~ok[:n]).sum())
    dps_keys = keys[dps_idx]
    idx = np.searchsorted(dps_idx, nxt[ok])
    size = np.bincount(idx, minlength=len(dps_idx)).astype(np.int64)
    B = Basins(dps=dps_keys, size=size, first_dp=nxt[:n], dist=dist[:n],
               cycle_mass=cycle_mass, capped_mass=capped_mass, N=E.N, cap=walk.P.cap)
    B.keys = keys
    B.dps_idx = dps_idx
    return B
