"""Second, structurally different W_D implementation for small systems (self-test only).

Differences from closure.py: dense numpy 0/1 matrices; its own monomial order
(degree ascending, then combinations order); W^(i) cap B_{<=D-1} is obtained as
{ x * Wb : x * Wb[:, top] = 0 } via the LEFT KERNEL of the degree-D block (no
leading-monomial argument); ranks by plain Gauss-Jordan on dense arrays.
"""
import itertools

import numpy as np


def _rref(M):
    M = M.copy() % 2
    r = 0
    rows, cols = M.shape
    piv = []
    for c in range(cols):
        if r >= rows:
            break
        nz = np.nonzero(M[r:, c])[0]
        if nz.size == 0:
            continue
        p = r + nz[0]
        if p != r:
            M[[r, p]] = M[[p, r]]
        others = np.nonzero(M[:, c])[0]
        others = others[others != r]
        M[others] ^= M[r]
        piv.append(c)
        r += 1
    return M[:r], piv


def _left_kernel(H):
    """Basis (rows) of {x : x H = 0} over F_2."""
    r = H.shape[0]
    aug = np.concatenate([H % 2, np.eye(r, dtype=np.uint8)], axis=1)
    # eliminate on the H columns only; the rows left with a zero H-part carry,
    # in their identity part, a basis of the left kernel
    h = H.shape[1]
    M = aug.copy()
    rr = 0
    for c in range(h):
        nz = np.nonzero(M[rr:, c])[0]
        if nz.size == 0:
            continue
        p = rr + nz[0]
        if p != rr:
            M[[rr, p]] = M[[p, rr]]
        others = np.nonzero(M[:, c])[0]
        others = others[others != rr]
        M[others] ^= M[rr]
        rr += 1
        if rr >= r:
            break
    K = M[rr:, h:]
    return K


class Dense:
    def __init__(self, nv, D):
        self.nv, self.D = nv, D
        mons = []
        for d in range(D + 1):
            for c in itertools.combinations(range(nv), d):
                m = 0
                for i in c:
                    m |= 1 << i
                mons.append(m)
        self.mons = mons
        self.idx = {m: i for i, m in enumerate(mons)}
        self.top = np.array([i for i, m in enumerate(mons) if bin(m).count("1") == D], dtype=np.int64)
        self.C = len(mons)

    def rows(self, eqs):
        out = []
        for d in range(self.D - 1):
            for c in itertools.combinations(range(self.nv), d):
                mu = 0
                for i in c:
                    mu |= 1 << i
                for eq in eqs:
                    v = np.zeros(self.C, dtype=np.uint8)
                    for m in eq:
                        v[self.idx[m | mu]] ^= 1
                    out.append(v)
        return np.array(out, dtype=np.uint8).reshape(len(out), self.C)

    def prod(self, g, j):
        r = np.zeros(self.C, dtype=np.uint8)
        for i in np.nonzero(g)[0]:
            r[self.idx[self.mons[i] | (1 << j)]] ^= 1
        return r

    def closure(self, eqs, max_iter=64):
        Wb, _ = _rref(self.rows(eqs))
        dims = [Wb.shape[0]]
        one = np.zeros(self.C, dtype=np.uint8)
        one[self.idx[0]] = 1

        def has_one(Wb):
            R2, _ = _rref(np.vstack([Wb, one[None, :]]))
            return R2.shape[0] == Wb.shape[0]

        first_one = 0 if has_one(Wb) else None
        it = 0
        while True:
            K = _left_kernel(Wb[:, self.top]) if self.top.size else np.eye(Wb.shape[0], dtype=np.uint8)
            low = (K.astype(np.int64) @ Wb.astype(np.int64)) % 2 if K.shape[0] else np.zeros((0, self.C), np.int64)
            low = low.astype(np.uint8)
            prods = [self.prod(g, j) for g in low for j in range(self.nv)]
            if prods:
                Wb, _ = _rref(np.vstack([Wb] + [p[None, :] for p in prods]))
            it += 1
            dims.append(Wb.shape[0])
            if first_one is None and has_one(Wb):
                first_one = it
            if dims[-1] == dims[-2]:
                return {"dims": dims, "fixpoint_index": it - 1, "first_one_iteration": first_one}
            if it >= max_iter:
                raise RuntimeError("no fixpoint")
