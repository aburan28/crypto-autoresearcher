"""Satisfiability oracles.

Oracle A (O(2^l) root finding; EXP-CERTBIN-4e92d7 C-ORACLE rule): for each
x_1 in V solve a X^2 + b X + c = 0 with a = x_1^2 + x_R^2, b = x_1 x_R,
c = x_1^2 x_R^2 + B and count roots X in V.

Oracle B (exhaustive 2^nv evaluation of the descended Boolean system), split
in halves: u = a + 2^l b with a = (v_0..v_{l-1}), b = (v_l..v_{2l-1}). Each
equation is G(a) + H(b) + a^T M b; H and the bilinear part are bit-packed
over b (2^l / 64 words), the a-dependence is expanded by subset doubling.
Works for any degree <= 2 system in 2l variables (any monomial class).
"""
from __future__ import annotations

import numpy as np

from common import eq_monomials


def quad_roots(F, a, b, c):
    """All roots X in F_{2^n} of a X^2 + b X + c = 0 (n odd), or None if every
    X is a root (a = b = c = 0)."""
    if a == 0 and b == 0:
        return None if c == 0 else []
    if a == 0:
        return [F.div(c, b)]
    if b == 0:
        return [F.sqrt(F.div(c, a))]
    z = F.div(F.mul(a, c), F.mul(b, b))
    if F.trace(z):
        return []
    y0 = F.halftrace(z)
    ba = F.div(b, a)
    return [F.mul(ba, y0), F.mul(ba, y0 ^ 1)]


def oracle_A(F, l, xR, Bc):
    """Number of (x_1, x_2) in V x V with S_3(x_1, x_2, x_R) = 0, and the list
    (u = x_1 + 2^l x_2)."""
    lim = 1 << l
    x1 = np.arange(lim, dtype=np.int64)
    x1s = F.vmul(x1, x1)
    xR2 = F.mul(xR, xR)
    a = x1s ^ xR2
    b = F.vmul(x1, np.full_like(x1, xR))
    c = F.vmul(x1s, np.full_like(x1, xR2)) ^ Bc
    sols = []
    for i in range(lim):
        roots = quad_roots(F, int(a[i]), int(b[i]), int(c[i]))
        if roots is None:
            roots = range(lim)
        for X in roots:
            if X < lim:
                sols.append(i | (X << l))
    sols = sorted(set(sols))
    return len(sols), sols


class Exhaustive:
    def __init__(self, l):
        self.l = l
        self.nv = 2 * l
        self.mons = eq_monomials(self.nv)
        self.ncol = len(self.mons)
        n = 1 << l
        self.nwords = max(1, n // 64)
        idx = np.arange(n, dtype=np.int64)
        bits = [((idx >> i) & 1).astype(np.uint8) for i in range(l)]
        a_cols, b_cols, bil = [], [], []
        Ta, Tb = [], []
        for c, m in enumerate(self.mons):
            if all(i < l for i in m):
                a_cols.append(c)
                t = np.ones(n, dtype=np.uint8)
                for i in m:
                    t &= bits[i]
                Ta.append(t)
            elif all(i >= l for i in m):
                b_cols.append(c)
                t = np.ones(n, dtype=np.uint8)
                for i in m:
                    t &= bits[i - l]
                Tb.append(t)
            else:
                i, j = m
                bil.append((c, i, j - l))
        self.a_cols = np.array(a_cols)
        self.b_cols = np.array(b_cols)
        self.Ta = np.array(Ta, dtype=np.int32)   # (na, 2^l)
        self.Tb = np.array(Tb, dtype=np.int32)   # (nb, 2^l)
        self.bil = bil
        self.bil_cols = np.array([c for c, _, _ in bil])
        self.bil_i = np.array([i for _, i, _ in bil])
        self.bil_j = np.array([j for _, _, j in bil])
        self.Tlin_b = np.array([bits[j] for j in range(l)], dtype=np.int32)  # (l, 2^l)

    def _pack(self, bitsarr):
        # (..., 2^l) 0/1 -> (..., nwords) uint64, bit (b & 63) of word b >> 6
        sh = bitsarr.shape
        n = sh[-1]
        flat = bitsarr.reshape(-1, n).astype(np.uint8)
        if n < 64:
            flat = np.concatenate([flat, np.zeros((flat.shape[0], 64 - n), np.uint8)], axis=1)
        p = np.packbits(flat, axis=1, bitorder="little")
        return p.view(np.uint64).reshape(sh[:-1] + (self.nwords,))

    def zero_table(self, E):
        """OR over equations of the evaluation table: (2^l a) x (nwords over b)."""
        l = self.l
        n = 1 << l
        E = np.asarray(E, dtype=np.int32)
        neq = E.shape[0]
        G = (E[:, self.a_cols] @ self.Ta) & 1               # (neq, 2^l) over a
        Hb = (E[:, self.b_cols] @ self.Tb) & 1              # (neq, 2^l) over b
        Hp = self._pack(Hb)                                  # (neq, nw)
        # bilinear: Mk[i, j] for (i in a-half, j in b-half)
        Mk = np.zeros((neq, l, l), dtype=np.int32)
        if len(self.bil):
            Mk[:, self.bil_i, self.bil_j] = E[:, self.bil_cols]
        Lt = (Mk @ self.Tlin_b) & 1                          # (neq, l, 2^l): L_i(b)
        Lp = self._pack(Lt)                                  # (neq, l, nw)
        tab = np.zeros((neq, n, self.nwords), dtype=np.uint64)
        for i in range(l):
            h = 1 << i
            tab[:, h:2 * h] = tab[:, 0:h] ^ Lp[:, i][:, None, :]
        full = np.uint64(0xFFFFFFFFFFFFFFFF) if n >= 64 else np.uint64((1 << n) - 1)
        tab ^= Hp[:, None, :]
        tab ^= np.where(G.astype(bool)[:, :, None], full, np.uint64(0))
        return np.bitwise_or.reduce(tab, axis=0)             # (2^l, nw)

    def count(self, E, want_solutions=False):
        assert self.l >= 6, "packed layout needs 2^l >= 64"
        orr = self.zero_table(E)
        n = 1 << self.l
        ones = int(np.unpackbits(orr.view(np.uint8)).sum())
        s = (1 << self.nv) - ones
        if not want_solutions:
            return s, None
        z = np.unpackbits((~orr).view(np.uint8), bitorder="little").reshape(n, self.nwords * 64)[:, :n]
        aa, bb = np.nonzero(z)
        sols = sorted(int(a) | (int(b) << self.l) for a, b in zip(aa, bb))
        assert len(sols) == s
        return s, sols
