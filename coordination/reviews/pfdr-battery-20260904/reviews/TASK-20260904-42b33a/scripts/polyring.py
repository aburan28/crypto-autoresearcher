"""READING 1 executed literally, in the honest polynomial ring R = F_p[a_0..a_{n-1}].

Used at s = 2 (all 12 instances) and s = 3 (one instance) to check empirically the
equivalence proved in the report between the polynomial-ring closure with the field
equations adjoined and the squarefree-quotient closure of hky.py.

F = { S~ } u { a_i^2 - a_i }, S~ the multilinear representative (degree 4).
V_{F,D} = smallest subspace of R_{<=D} containing F n R_{<=D}, closed under
v -> h v for monomials h with deg(h) + deg(v) <= D (exact in a domain).
"""

import itertools
import numpy as np

from hky import LinSpace, popcount


def monomials(n, D):
    """all exponent tuples of total degree <= D, ordered by DESCENDING degree."""
    out = []
    for d in range(D + 1):
        for c in itertools.combinations_with_replacement(range(n), d):
            e = [0] * n
            for i in c:
                e[i] += 1
            out.append(tuple(e))
    out.sort(key=lambda e: (-sum(e), e))
    return out


class PolyRing:
    def __init__(self, n, p, D):
        self.n, self.p, self.D = n, p, D
        self.mons = monomials(n, D)
        self.pos = {m: i for i, m in enumerate(self.mons)}
        self.degs = np.array([sum(m) for m in self.mons])
        self.N = len(self.mons)

    def vec(self, poly):
        v = np.zeros(self.N)
        for m, c in poly.items():
            c %= self.p
            if c:
                v[self.pos[m]] = c
        return v

    def mul_mon(self, v, h):
        """h an exponent tuple; assumes deg(h) + deg(v) <= D."""
        out = np.zeros(self.N)
        nz = np.nonzero(v)[0]
        for j in nz:
            m = self.mons[j]
            t = tuple(m[i] + h[i] for i in range(self.n))
            out[self.pos[t]] += v[j]
        return np.mod(out, self.p)


def closure_poly(pr, gens, D, log=None):
    """gens: list of dicts {exponent tuple: coeff}. Returns (LinSpace, rounds, productive)."""
    p, n = pr.p, pr.n
    W = LinSpace(pr.N, p)
    rows = []
    for g in gens:
        dg = max(sum(m) for m in g)
        if dg > D:
            continue
        gv = pr.vec(g)
        for h in monomials(n, D - dg):
            rows.append(pr.mul_mon(gv, h))
    if not rows:
        return W, 0, 0
    W.add_rows(np.array(rows))
    rounds, productive = 0, 0
    while True:
        rows = []
        for i in range(W.dim):
            e = int(pr.degs[int(W.piv[i])])
            if e > D - 1:
                continue
            for h in monomials(n, D - e):
                if sum(h) == 0:
                    continue
                rows.append(pr.mul_mon(W.R[i], h))
        rounds += 1
        if not rows:
            break
        grew = W.add_rows(np.array(rows))
        if log:
            log(f"      [poly] D={D} round {rounds}: rows={len(rows)} dim={W.dim} grew={grew}")
        if not grew:
            break
        productive += 1
    return W, rounds, productive


def dim_leq_poly(W, pr, e):
    if W.dim == 0:
        return 0
    return int(np.sum(pr.degs[W.piv] <= e))


def field_eqs(n):
    out = []
    for i in range(n):
        e2 = [0] * n
        e2[i] = 2
        e1 = [0] * n
        e1[i] = 1
        out.append({tuple(e2): 1, tuple(e1): -1})
    return out


def mask_to_exp(m, n):
    return tuple(1 if (m >> i) & 1 else 0 for i in range(n))
