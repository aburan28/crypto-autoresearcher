"""The S_3 descent at (n, l), the affine decomposition, union support, the
ell kernel and the rc_b substitution (object.descended_system,
affine_decomposition, union_support, ell_and_rc_b).

The descent is computed DIRECTLY by generic sparse multilinear polynomial
arithmetic over F_{2^n} (dict: monomial mask -> field element); the affine
decomposition E^0 + sum r_j E^j is computed separately and compared (C-AFF19).
"""
from __future__ import annotations

import numpy as np

from common import eq_monomials


class Descent:
    def __init__(self, F, l, Bc):
        self.F, self.n, self.l, self.Bc = F, F.n, l, Bc
        self.nv = 2 * l
        self.neq = F.n
        self.mons = eq_monomials(self.nv)
        self.masks = [sum(1 << i for i in m) for m in self.mons]
        self.col = {mk: c for c, mk in enumerate(self.masks)}
        self.ncol = len(self.mons)
        self._E0 = None
        self._Ej = None

    # ---- generic polynomial arithmetic --------------------------------------
    def padd(self, p, q):
        r = dict(p)
        for m, c in q.items():
            r[m] = r.get(m, 0) ^ c
        return {m: c for m, c in r.items() if c}

    def pmul(self, p, q):
        F = self.F
        r = {}
        for m1, c1 in p.items():
            for m2, c2 in q.items():
                m = m1 | m2
                r[m] = r.get(m, 0) ^ F.mul(c1, c2)
        return {m: c for m, c in r.items() if c}

    def psqr(self, p):
        # (sum c_m m)^2 = sum c_m^2 m (char 2, m^2 = m in B)
        return {m: self.F.mul(c, c) for m, c in p.items() if c}

    def pconst(self, c):
        return {0: c} if c else {}

    def x1(self):
        return {1 << i: 1 << i for i in range(self.l)}

    def x2(self):
        return {1 << (self.l + j): 1 << j for j in range(self.l)}

    def s3_poly(self, xR):
        x1, x2, x3 = self.x1(), self.x2(), self.pconst(xR)
        s = self.padd(self.padd(self.pmul(x1, x2), self.pmul(x1, x3)), self.pmul(x2, x3))
        return self.padd(self.padd(self.psqr(s), self.pmul(self.pmul(x1, x2), x3)), self.pconst(self.Bc))

    def E_direct(self, xR):
        p = self.s3_poly(xR)
        E = np.zeros((self.neq, self.ncol), dtype=np.uint8)
        for m, c in p.items():
            col = self.col[m]  # KeyError would mean degree > 2
            for k in range(self.neq):
                if (c >> k) & 1:
                    E[k, col] = 1
        return E

    # ---- affine decomposition ---------------------------------------------------
    def affine_parts(self):
        if self._E0 is None:
            E0 = self.E_direct(0)
            Ej = [self.E_direct(1 << j) ^ E0 for j in range(self.n)]
            self._E0, self._Ej = E0, Ej
        return self._E0, self._Ej

    def E_affine(self, xR):
        E0, Ej = self.affine_parts()
        E = E0.copy()
        for j in range(self.n):
            if (xR >> j) & 1:
                E ^= Ej[j]
        return E

    def union_support(self):
        E0, Ej = self.affine_parts()
        U = E0.astype(bool).copy()
        for e in Ej:
            U |= e.astype(bool)
        return U

    # ---- direct evaluation of S_3 in the field (C-SELF (iv)) --------------
    def s3_eval(self, v, xR):
        F = self.F
        x1 = v & ((1 << self.l) - 1)
        x2 = (v >> self.l) & ((1 << self.l) - 1)
        s = F.mul(x1, x2) ^ F.mul(x1, xR) ^ F.mul(x2, xR)
        return F.mul(s, s) ^ F.mul(F.mul(x1, x2), xR) ^ self.Bc


def eval_system(E, masks, u):
    """Evaluate every equation of E at assignment u (bit i = v_i) -> list of bits."""
    out = []
    for k in range(E.shape[0]):
        acc = 0
        for j in np.flatnonzero(E[k]):
            m = masks[j]
            if (u & m) == m:
                acc ^= 1
        out.append(acc)
    return out


# ---------------------------------------------------------------------------
# rc_b: left kernel of the quadratic part, ell, substitution
# ---------------------------------------------------------------------------
def left_kernel(Mq):
    """Left kernel of Mq (neq x ncols over F_2): basis of {c : c Mq = 0}.
    Own Gaussian elimination on Python ints (rows = equations, augmented with
    an identity to track combinations)."""
    neq = Mq.shape[0]
    piv = []   # (value, combination, lowest set bit)
    kern = []
    for k in range(neq):
        v = 0
        for j in np.flatnonzero(Mq[k]):
            v |= 1 << int(j)
        c = 1 << k
        for pv, pc, lb in piv:
            if (v >> lb) & 1:
                v ^= pv
                c ^= pc
        if v:
            piv.append((v, c, (v & -v).bit_length() - 1))
        else:
            kern.append(c)
    return kern


def kernel_basis(Mq):
    return left_kernel(Mq)


def combine_rows(E, cvec):
    """sum_k c_k E[k] over F_2 (cvec: int bitmask over rows)."""
    r = np.zeros(E.shape[1], dtype=np.uint8)
    for k in range(E.shape[0]):
        if (cvec >> k) & 1:
            r ^= E[k]
    return r


def substitute(E, ell_row, masks, nv):
    """pi: v_{j*} := ell + v_{j*} where j* = least index in ell's linear
    support; the remaining nv-1 variables are relabelled ascending 0..nv-2;
    every f_k is reduced multilinearly.

    ell_row: length-ncol 0/1 vector (degree <= 1). Returns (eqs', jstar, affine)
    where eqs' is a list of neq lists of monomial masks over nv-1 variables and
    affine = (list of variable indices, constant) is v_{j*}'s image in the
    ORIGINAL indexing."""
    lin = [i for i in range(nv) if ell_row[1 + i]]
    const = int(ell_row[0])
    assert lin
    jstar = lin[0]
    others = lin[1:]
    # image of v_{j*}: sum_{i in others} v_i + const  (as dict mask -> 1)
    img = {}
    for i in others:
        img[1 << i] = img.get(1 << i, 0) ^ 1
    if const:
        img[0] = img.get(0, 0) ^ 1
    bj = 1 << jstar

    def relabel(m):
        out = 0
        for i in range(nv):
            if (m >> i) & 1:
                assert i != jstar
                out |= 1 << (i if i < jstar else i - 1)
        return out

    eqs = []
    for k in range(E.shape[0]):
        acc = {}
        for c in np.flatnonzero(E[k]):
            m = masks[c]
            if m & bj:
                rest = m & ~bj
                for im, par in img.items():
                    if par:
                        mm = rest | im
                        acc[mm] = acc.get(mm, 0) ^ 1
            else:
                acc[m] = acc.get(m, 0) ^ 1
        eqs.append(sorted(relabel(m) for m, p in acc.items() if p))
    return eqs, jstar, (others, const)


def extend_assignment(uprime, jstar, affine, nv):
    """u' over nv-1 relabelled variables -> u over nv variables with
    v_{j*} = sum_{i in others} v_i + const (so ell(u) = 0)."""
    u = 0
    for i in range(nv - 1):
        if (uprime >> i) & 1:
            u |= 1 << (i if i < jstar else i + 1)
    others, const = affine
    val = const
    for i in others:
        val ^= (u >> i) & 1
    if val:
        u |= 1 << jstar
    return u
