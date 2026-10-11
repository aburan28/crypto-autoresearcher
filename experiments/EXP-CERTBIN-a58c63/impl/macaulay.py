"""Regime A: Weil descent of S_3 and the fixed-shape Macaulay matrix M_D.

Copied from EXP-CERTBIN-4e92d7/impl/macaulay.py and generalized from the
Stage-1 constants (n = 17, l = 9, NV = 18, NEQ = 17) to a parameter object
``Descent(F, l)`` (n = F.n equations, NV = 2l Boolean variables). Every
convention is unchanged (see impl-provenance.json):

  * Boolean variables v_0 > v_1 > ... > v_{2l-1}; x_1 = sum_{j<l} v_j t^j,
    x_2 = sum_{j<l} v_{l+j} t^j.
  * A multilinear monomial is a sorted tuple of variable indices.
  * "mu order" (Macaulay row multipliers and the columns of E): degree
    ascending, then the ascending sorted index tuple, lexicographically.
  * Macaulay COLUMN order: descending degrevlex with v_0 > ... > v_{NV-1},
    i.e. degree descending, then (within a degree) the integer mask
    sum_{i in m} 2^i ascending. The constant monomial is last.
  * Macaulay ROW index = (index of mu in mu order) * n + k.
"""
from itertools import combinations

import numpy as np


def mu_order(dmax, nv):
    out = []
    for d in range(dmax + 1):
        out.extend(combinations(range(nv), d))
    return out


def mono_mask(m):
    s = 0
    for i in m:
        s |= 1 << i
    return s


def column_order(D, nv):
    mons = mu_order(D, nv)
    return sorted(mons, key=lambda m: (-len(m), mono_mask(m)))


def degrevlex_greater(a, b):
    """Literal transcription of the spec's comparison (used in the self-test)."""
    if len(a) != len(b):
        return len(a) > len(b)
    sa, sb = set(a), set(b)
    diff = sa ^ sb
    if not diff:
        return False
    i = max(diff)
    return i not in sa


# ---------------------------------------------------------------------------
# Descent: generic multilinear expansion over F_{2^n}
# ---------------------------------------------------------------------------
def _pmul(F, P, Q):
    out = {}
    for m1, c1 in P.items():
        for m2, c2 in Q.items():
            m = tuple(sorted(set(m1) | set(m2)))
            out[m] = out.get(m, 0) ^ F.mul(c1, c2)
    return out


def _padd(*Ps):
    out = {}
    for P in Ps:
        for m, c in P.items():
            out[m] = out.get(m, 0) ^ c
    return out


def _pscal(F, P, c):
    return {m: F.mul(v, c) for m, v in P.items()}


def _psq(F, P):
    # char 2 + multilinear (v^2 = v): (sum c_m m)^2 = sum c_m^2 m
    out = {}
    for m, c in P.items():
        out[m] = out.get(m, 0) ^ F.mul(c, c)
    return out


class Descent:
    """The descended system of S_3(x_1, x_2, x_R) over F = F_{2^n}, V = {deg < l}."""

    def __init__(self, F, l):
        self.F = F
        self.n = F.n
        self.l = l
        self.nv = 2 * l
        self.neq = F.n
        self.eq_mons = mu_order(2, self.nv)
        self.eq_index = {m: i for i, m in enumerate(self.eq_mons)}
        assert len(self.eq_mons) == 1 + self.nv + self.nv * (self.nv - 1) // 2

    def s3_multilinear(self, B, xR):
        F, L = self.F, self.l
        X1 = {(j,): 1 << j for j in range(L)}
        X2 = {(L + j,): 1 << j for j in range(L)}
        s12 = _pmul(F, X1, X2)
        e1 = _padd(s12, _pscal(F, X1, xR), _pscal(F, X2, xR))
        return _padd(_psq(F, e1), _pscal(F, s12, xR), {(): B})

    def descended_E(self, B, xR):
        """n x |eq_mons| uint8 coefficient matrix E(r): row k = coefficient of t^k."""
        S = self.s3_multilinear(B, xR)
        E = np.zeros((self.neq, len(self.eq_mons)), dtype=np.uint8)
        for m, c in S.items():
            if c == 0:
                continue
            j = self.eq_index[m]
            for k in range(self.neq):
                if (c >> k) & 1:
                    E[k, j] = 1
        return E

    def affine_basis(self, B):
        """(E^0, [E^j for j = 0..n-1]) with E^0 = E(x_R = 0), E^j = E(t^j) - E^0."""
        E0 = self.descended_E(B, 0)
        Ej = [self.descended_E(B, 1 << j) ^ E0 for j in range(self.neq)]
        return E0, Ej

    def affine_combine(self, E0, Ej, r):
        E = E0.copy()
        for j in range(self.neq):
            if (r >> j) & 1:
                E ^= Ej[j]
        return E

    def eval_equations_scalar(self, E, u):
        """Evaluate the n Boolean equations at assignment u (bit i = v_i),
        scalar Python code (independent of the bit-sliced oracle B)."""
        vals = []
        for k in range(self.neq):
            acc = 0
            for j in np.flatnonzero(E[k]):
                m = self.eq_mons[j]
                t = 1
                for i in m:
                    if not (u >> i) & 1:
                        t = 0
                        break
                acc ^= t
            vals.append(acc)
        return vals


# ---------------------------------------------------------------------------
# Fixed-shape Macaulay matrix
# ---------------------------------------------------------------------------
class MacaulayShape:
    def __init__(self, D, desc):
        self.D = D
        self.desc = desc
        nv, neq = desc.nv, desc.neq
        self.NEQ = neq
        self.mus = mu_order(D - 2, nv)
        self.cols = column_order(D, nv)
        self.colidx = {m: i for i, m in enumerate(self.cols)}
        self.R = len(self.mus) * neq
        self.C = len(self.cols)
        self.W = (self.C + 63) // 64
        T = np.zeros((len(self.mus), len(desc.eq_mons)), dtype=np.int64)
        for a, mu in enumerate(self.mus):
            smu = set(mu)
            for j, m in enumerate(desc.eq_mons):
                T[a, j] = self.colidx[tuple(sorted(smu | set(m)))]
        self.T = T
        self.mu_rows = np.arange(len(self.mus), dtype=np.int64) * neq
        self.col_masks = np.array([mono_mask(m) for m in self.cols], dtype=np.int64)
        self.col_deg = np.array([len(m) for m in self.cols], dtype=np.int64)
        self.const_col = self.C - 1
        assert self.cols[-1] == ()

    def row_order(self):
        return [{"row": a * self.NEQ + k, "mu": list(mu), "k": k}
                for a, mu in enumerate(self.mus) for k in range(self.NEQ)]

    def build_dense(self, E):
        M = np.zeros((self.R, self.C), dtype=np.uint8)
        for k in range(self.NEQ):
            rows = self.mu_rows + k
            for j in np.flatnonzero(E[k]):
                M[rows, self.T[:, j]] ^= 1
        return M

    def pack(self, Mdense):
        R = Mdense.shape[0]
        pad = self.W * 64 - self.C
        if pad:
            Mdense = np.concatenate([Mdense, np.zeros((R, pad), dtype=np.uint8)], axis=1)
        b = np.packbits(Mdense, axis=1, bitorder="little")
        return np.ascontiguousarray(b).view(np.uint64).reshape(R, self.W).copy()

    def build(self, E, reverse=False):
        M = self.pack(self.build_dense(E))
        if reverse:
            M = M[::-1].copy()
        return M

    def unpack(self, M):
        b = M.view(np.uint8).reshape(M.shape[0], self.W * 8)
        return np.unpackbits(b, axis=1, bitorder="little")[:, :self.C]

    def eval_vector(self, u):
        """Packed evaluation vector of the column monomials at assignment u."""
        ev = ((self.col_masks & ~np.int64(u)) == 0).astype(np.uint8)[None, :]
        return self.pack(ev)[0]
