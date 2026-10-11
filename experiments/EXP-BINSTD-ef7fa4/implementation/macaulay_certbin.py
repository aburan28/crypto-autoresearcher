"""Weil descent of S_3 and the fixed-shape Macaulay matrix M_D.

Conventions (spec object block):
  * Boolean variables v_0 > v_1 > ... > v_17 (NV = 18); x_1 = sum_{j<9} v_j t^j,
    x_2 = sum_{j<9} v_{9+j} t^j.
  * A multilinear monomial is a sorted tuple of variable indices.
  * "mu order" (used for Macaulay row multipliers and for the 172 columns of the
    17 x 172 coefficient matrix E): degree ascending, then the ascending sorted
    index tuple, lexicographically.
  * Macaulay COLUMN order: descending degrevlex with v_0 > ... > v_17, i.e.
    degree descending, then (within a degree) the integer mask sum_{i in m} 2^i
    ascending (a > b iff at the largest index where they differ, a lacks it).
    The constant monomial is last.
  * Macaulay ROW index = (index of mu in mu order) * 17 + k.
"""
from itertools import combinations

import numpy as np

NV = 18
L = 9
NEQ = 17


def mu_order(dmax, nv=NV):
    out = []
    for d in range(dmax + 1):
        out.extend(combinations(range(nv), d))
    return out


def mono_mask(m):
    s = 0
    for i in m:
        s |= 1 << i
    return s


def column_order(D, nv=NV):
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


EQ_MONS = mu_order(2)          # 172 monomials, the columns of E
EQ_INDEX = {m: i for i, m in enumerate(EQ_MONS)}
assert len(EQ_MONS) == 172


# ---------------------------------------------------------------------------
# Descent: generic multilinear expansion over F_{2^17}
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


def s3_multilinear(F, B, xR):
    """S_3(x_1, x_2, x_R) expanded as a multilinear polynomial in v with
    F_{2^17} coefficients: dict monomial -> field element."""
    X1 = {(j,): 1 << j for j in range(L)}
    X2 = {(L + j,): 1 << j for j in range(L)}
    s12 = _pmul(F, X1, X2)
    e1 = _padd(s12, _pscal(F, X1, xR), _pscal(F, X2, xR))
    S = _padd(_psq(F, e1), _pscal(F, s12, xR), {(): B})
    return S


def descended_E(F, B, xR):
    """17 x 172 uint8 coefficient matrix E(r): row k = coefficient of t^k."""
    S = s3_multilinear(F, B, xR)
    E = np.zeros((NEQ, len(EQ_MONS)), dtype=np.uint8)
    for m, c in S.items():
        if c == 0:
            continue
        j = EQ_INDEX[m]
        for k in range(NEQ):
            if (c >> k) & 1:
                E[k, j] = 1
    return E


def affine_basis(F, B):
    """(E^0, [E^j for j = 0..16]) with E^0 = E(x_R = 0), E^j = E(t^j) - E^0."""
    E0 = descended_E(F, B, 0)
    Ej = [descended_E(F, B, 1 << j) ^ E0 for j in range(NEQ)]
    return E0, Ej


def affine_combine(E0, Ej, r):
    E = E0.copy()
    for j in range(NEQ):
        if (r >> j) & 1:
            E ^= Ej[j]
    return E


def eval_equations_scalar(E, u):
    """Evaluate the 17 Boolean equations at assignment u (bit i = v_i), scalar
    Python code (independent of the bit-sliced oracle B)."""
    vals = []
    for k in range(NEQ):
        acc = 0
        for j in np.flatnonzero(E[k]):
            m = EQ_MONS[j]
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
    def __init__(self, D):
        self.D = D
        self.mus = mu_order(D - 2)
        self.cols = column_order(D)
        self.colidx = {m: i for i, m in enumerate(self.cols)}
        self.R = len(self.mus) * NEQ
        self.C = len(self.cols)
        self.W = (self.C + 63) // 64
        # T[mu_i, j] = column of mu_i * EQ_MONS[j] (multilinear)
        T = np.zeros((len(self.mus), len(EQ_MONS)), dtype=np.int64)
        for a, mu in enumerate(self.mus):
            smu = set(mu)
            for j, m in enumerate(EQ_MONS):
                T[a, j] = self.colidx[tuple(sorted(smu | set(m)))]
        self.T = T
        self.mu_rows = np.arange(len(self.mus), dtype=np.int64) * NEQ
        self.col_masks = np.array([mono_mask(m) for m in self.cols], dtype=np.int64)
        self.col_deg = np.array([len(m) for m in self.cols], dtype=np.int64)
        self.const_col = self.C - 1
        assert self.cols[-1] == ()

    def row_order(self):
        return [{"row": a * NEQ + k, "mu": list(mu), "k": k}
                for a, mu in enumerate(self.mus) for k in range(NEQ)]

    def build_dense(self, E):
        M = np.zeros((self.R, self.C), dtype=np.uint8)
        for k in range(NEQ):
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
