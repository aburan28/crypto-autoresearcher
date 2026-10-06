"""S_4 Weil descent over binary curves for EXP-BINSTD-89d952.

S_3 (CERTBIN / A-free, empirically verified on both Stage-1 arms):
  S3(x,y,z) = (xy+xz+yz)^2 + xyz + B

S_4 via resultant (char 2):
  S4(x1,x2,x3,x4) = Res_t(S3(x1,x2,t), S3(x3,x4,t))

No per-instance mu-orbit / canonical-representative constraint is encoded.
"""
from __future__ import annotations

from collections import Counter

import numpy as np

from macaulay import mono_mask, mu_order, column_order


def s3_field(F, B, x1, x2, x3):
    s = F.mul(x1, x2) ^ F.mul(x1, x3) ^ F.mul(x2, x3)
    return F.mul(s, s) ^ F.mul(F.mul(x1, x2), x3) ^ B


def s3_coeffs_field(F, B, x, y):
    """S3(x,y,t) = α t² + β t + γ over F."""
    xy = F.mul(x, y)
    xp = x ^ y
    alpha = F.mul(xp, xp)
    beta = xy
    gamma = F.mul(xy, xy) ^ B
    return alpha, beta, gamma


def s4_field(F, B, x1, x2, x3, x4):
    a1, b1, c1 = s3_coeffs_field(F, B, x1, x2)
    a2, b2, c2 = s3_coeffs_field(F, B, x3, x4)
    t1 = F.mul(a1, c2) ^ F.mul(a2, c1)
    t2 = F.mul(a1, b2) ^ F.mul(a2, b1)
    t3 = F.mul(b1, c2) ^ F.mul(b2, c1)
    return F.mul(t1, t1) ^ F.mul(t2, t3)


# ---- sparse multilinear polys: dict mask -> F-coeff --------------------

def _pmul(F, P, Q):
    out = {}
    for m1, c1 in P.items():
        for m2, c2 in Q.items():
            m = m1 | m2
            out[m] = out.get(m, 0) ^ F.mul(c1, c2)
    return {m: c for m, c in out.items() if c}


def _padd(*Ps):
    out = {}
    for P in Ps:
        for m, c in P.items():
            out[m] = out.get(m, 0) ^ c
    return {m: c for m, c in out.items() if c}


def _psq(F, P):
    out = {}
    for m, c in P.items():
        out[m] = out.get(m, 0) ^ F.mul(c, c)
    return {m: c for m, c in out.items() if c}


def embed_block(basis, block, L):
    """X = sum_j v_{block*L+j} * basis[j] as sparse poly."""
    P = {}
    for j, b in enumerate(basis):
        if b:
            P[1 << (block * L + j)] = b
    return P


def s3_coeffs_poly(F, B, X, Y):
    XY = _pmul(F, X, Y)
    Xp = _padd(X, Y)
    alpha = _psq(F, Xp)
    beta = XY
    gamma = _padd(_psq(F, XY), {0: B})
    return alpha, beta, gamma


def s4_poly(F, B, X1, X2, X3, xR):
    """S4(X1,X2,X3,xR) as multilinear poly in the boolean vars of X1..X3."""
    a1, b1, c1 = s3_coeffs_poly(F, B, X1, X2)
    a2, b2, c2 = s3_coeffs_poly(F, B, X3, {0: xR})
    t1 = _padd(_pmul(F, a1, c2), _pmul(F, a2, c1))
    t2 = _padd(_pmul(F, a1, b2), _pmul(F, a2, b1))
    t3 = _padd(_pmul(F, b1, c2), _pmul(F, b2, c1))
    return _padd(_psq(F, t1), _pmul(F, t2, t3))


def descend_s4(F, B, basis, xR):
    """Weil-descend S4 to n Boolean equations (lists of monomial masks).

    Returns (eqs, meta) where eqs[k] is the list of monomial masks with
    coefficient bit k set (F_2 coefficients of t^k).
    """
    L = len(basis)
    X1, X2, X3 = embed_block(basis, 0, L), embed_block(basis, 1, L), embed_block(basis, 2, L)
    S = s4_poly(F, B, X1, X2, X3, xR)
    n = F.n
    eqs = [[] for _ in range(n)]
    degs = []
    for m, c in S.items():
        degs.append(bin(m).count("1"))
        for k in range(n):
            if (c >> k) & 1:
                eqs[k].append(int(m))
    meta = {
        "n_terms_field_poly": len(S),
        "max_boolean_degree": max(degs) if degs else 0,
        "degree_histogram": dict(sorted(Counter(degs).items())),
        "nv": 3 * L,
        "neq": n,
        "L": L,
    }
    return eqs, meta


def eqs_fit_macaulay_D(eqs, D):
    """True iff every monomial in eqs has degree <= D."""
    for f in eqs:
        for m in f:
            if bin(m).count("1") > D:
                return False
    return True


class ClosureGeneric:
    """Macaulay / W_D for equations of max degree eq_deg (not necessarily 2).

    Adapted from EXP-CERTBIN-e94b27/impl/closure.py Closure, with
    mus = mu_order(D - eq_deg). For eq_deg == D, mus = {1} only.
    """

    def __init__(self, nv, D, neq, eq_deg):
        if eq_deg > D:
            raise ValueError(f"eq_deg {eq_deg} > D {D}: equations do not fit M_D")
        self.nv, self.D, self.neq, self.eq_deg = nv, D, neq, eq_deg
        self.cols = column_order(D, nv)
        self.C = len(self.cols)
        self.W = (self.C + 63) // 64
        self.col_mask = np.array([mono_mask(m) for m in self.cols], dtype=np.int64)
        self.col_deg = np.array([len(m) for m in self.cols], dtype=np.int64)
        self.const_col = self.C - 1
        assert self.cols[-1] == ()
        self.mask2col = np.full(1 << nv, -1, dtype=np.int64)
        self.mask2col[self.col_mask] = np.arange(self.C)
        self.mus = mu_order(D - eq_deg, nv)
        self.mu_mask = np.array([mono_mask(m) for m in self.mus], dtype=np.int64)
        self.R = len(self.mus) * neq
        low = np.flatnonzero(self.col_deg <= D - 1)
        self.maps = []
        for j in range(nv):
            bj = np.int64(1 << j)
            has = (self.col_mask[low] & bj) != 0
            A = low[~has]
            tA = self.mask2col[self.col_mask[A] | bj]
            assert np.all(tA >= 0)
            self.maps.append((A, tA, low[has]))

    def pack(self, dense):
        n = dense.shape[0]
        pad = self.W * 64 - self.C
        if pad:
            dense = np.concatenate([dense, np.zeros((n, pad), dtype=np.uint8)], axis=1)
        b = np.packbits(dense, axis=1, bitorder="little")
        return np.ascontiguousarray(b).view(np.uint64).reshape(n, self.W).copy()

    def unpack(self, M):
        b = M.view(np.uint8).reshape(M.shape[0], self.W * 8)
        return np.unpackbits(b, axis=1, bitorder="little")[:, : self.C]

    def build_M(self, eqs):
        assert len(eqs) == self.neq
        dense = np.zeros((self.R, self.C), dtype=np.uint8)
        base = np.arange(len(self.mus), dtype=np.int64) * self.neq
        for k, f in enumerate(eqs):
            rows = base + k
            for m in f:
                cols = self.mask2col[self.mu_mask | np.int64(m)]
                if np.any(cols < 0):
                    raise ValueError("monomial outside M_D column space")
                dense[rows, cols] ^= 1
        return self.pack(dense)

    def products(self, rows, chunk=2048):
        n = rows.shape[0]
        out = np.zeros((self.nv * n, self.W), dtype=np.uint64)
        if n == 0:
            return out
        for s in range(0, n, chunk):
            d = self.unpack(rows[s : s + chunk])
            m = d.shape[0]
            for j in range(self.nv):
                A, tA, Bc = self.maps[j]
                o = np.zeros_like(d)
                o[:, tA] = d[:, A]
                o[:, Bc] ^= d[:, Bc]
                out[j * n + s : j * n + s + m] = self.pack(o)
        return out

    def macaulay_build_only(self, eqs):
        M = self.build_M(eqs)
        return {
            "rows": int(M.shape[0]),
            "cols": self.C,
            "words": self.W,
            "nbytes": int(M.nbytes),
        }
