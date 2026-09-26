#!/usr/bin/env python3
"""Small, literal Boolean-ring engine for the J8 constructions of
TASK-20260926-f50294 (6 to 8 variables). Own code; stdlib only.

Ring B_n = F_2[v_0..v_{n-1}]/(v_i^2 + v_i); monomial = n-bit mask; polynomial =
Python int whose bit c is the coefficient of the c-th monomial of the graded
order ORDER (degree DESCENDING, then mask ascending; constant last), so that the
highest set bit of a vector is its leading (highest-degree) monomial.

  * M_D rows: mu * f_k, |mu| <= D - 2, every k (zero rows irrelevant).
  * W_D: the literal iteration of EXP-CERTBIN-e94b27 object.mutant_closure_W_D:
    W^(0) = rowspace(M_D); W^(i+1) = W^(i) + span{v_j b : b in a basis of
    W^(i) cap B_{<=D-1}, j = 0..n-1}; stop at the first i with equal dims.
    The basis of W^(i) cap B_{<=D-1} is the set of fully reduced echelon rows
    whose leading monomial has degree <= D - 1 (graded order).
  * Elimination keeps identity TAGS (which generators were combined), so a
    membership of 1 comes with an explicit certificate.
"""
from itertools import combinations


def popcount(x):
    return bin(x).count("1")


class Ring:
    def __init__(self, n, D):
        self.n, self.D = n, D
        monos = [m for m in range(1 << n) if popcount(m) <= D]
        # graded: higher degree -> higher bit; so sort ascending by (deg, -mask)
        # and give bit index = position; leading bit = highest degree, and
        # within a degree the smallest mask is the highest bit.
        self.monos = sorted(monos, key=lambda m: (popcount(m), -m))
        self.pos = {m: i for i, m in enumerate(self.monos)}
        self.N = len(self.monos)
        self.deg_of_bit = [popcount(m) for m in self.monos]
        self.low_limit = sum(1 for m in self.monos if popcount(m) <= D - 1)  # bits < this have deg <= D-1

    def vec(self, poly_masks):
        v = 0
        for m in poly_masks:
            v ^= 1 << self.pos[m]
        return v

    def masks(self, v):
        out = []
        while v:
            b = v.bit_length() - 1
            out.append(self.monos[b])
            v ^= 1 << b
        return out

    def deg(self, v):
        return self.deg_of_bit[v.bit_length() - 1] if v else -1

    def mul_mono(self, poly_masks, mu):
        out = set()
        for m in poly_masks:
            x = m | mu
            out ^= {x}
        return out

    def mul_var_vec(self, v, j):
        out = 0
        for m in self.masks(v):
            out ^= 1 << self.pos[m | (1 << j)]
        return out


class Echelon:
    """Fully reduced echelon basis with tags (tags are Python ints over
    generator indices)."""

    def __init__(self):
        self.rows = {}  # leading bit -> (vec, tag)

    def reduce(self, v, t):
        while v:
            b = v.bit_length() - 1
            if b not in self.rows:
                return v, t
            rv, rt = self.rows[b]
            v ^= rv
            t ^= rt
        return 0, t

    def add(self, v, t):
        v, t = self.reduce(v, t)
        if not v:
            return False
        b = v.bit_length() - 1
        # full reduction of the other rows by the new one
        for lb, (rv, rt) in list(self.rows.items()):
            if (rv >> b) & 1:
                self.rows[lb] = (rv ^ v, rt ^ t)
        self.rows[b] = (v, t)
        return True

    def dim(self):
        return len(self.rows)

    def contains(self, v):
        r, _ = self.reduce(v, 0)
        return r == 0


def macaulay(R, fs, D):
    """Rows (vec, generator description) of M_D."""
    mus = [0] + [sum(1 << i for i in c) for d in range(1, D - 1) for c in combinations(range(R.n), d)]
    gens = []
    for mu in mus:
        for k, f in enumerate(fs):
            gens.append((R.vec(R.mul_mono(f, mu)), ("row", mu, k)))
    return gens


def rowspace(R, fs, D):
    gens = macaulay(R, fs, D)
    E = Echelon()
    for g, (v, _) in enumerate(gens):
        E.add(v, 1 << g)
    return E, gens


def literal_W(R, fs, D):
    """Returns dict with dims per iteration, fixpoint index, one_first_iteration,
    final echelon, generator list (for tags: rows of M_D, then (j, vec) products)."""
    E, gens = rowspace(R, fs, D)
    one = R.vec({0})
    dims = [E.dim()]
    first = 0 if E.contains(one) else None
    it = 0
    while True:
        basis = [(v, t) for lb, (v, t) in E.rows.items() if lb < R.low_limit]
        new = False
        prods = []
        for v, t in basis:
            for j in range(R.n):
                prods.append((R.mul_var_vec(v, j), t, j, v))
        for p, t, j, v in prods:
            g = len(gens)
            gens.append((p, ("prod", j, v, t)))
            if E.add(p, 1 << g):
                new = True
        it += 1
        dims.append(E.dim())
        if first is None and E.contains(one):
            first = it
        if dims[-1] == dims[-2]:
            break
    return {"dims": dims[:-1], "fixpoint_index": it - 1, "one_first_iteration": first,
            "one": first is not None, "final_dim": dims[-1], "echelon": E, "gens": gens}


def solutions(fs, n):
    sols = []
    for a in range(1 << n):
        ok = True
        for f in fs:
            s = 0
            for m in f:
                if m & a == m:
                    s ^= 1
            if s:
                ok = False
                break
        if ok:
            sols.append(a)
    return sols
