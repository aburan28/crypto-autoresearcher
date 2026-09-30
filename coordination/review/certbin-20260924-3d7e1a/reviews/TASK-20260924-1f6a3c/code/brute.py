"""Brute-force W_D fixpoint for small Boolean systems (card BR-2 self-test).

Independent of closure.py / gf2lin.py: its own monomial indexing (sorted by
(degree, mask)), its own products, and NO bases: every iterate W^(i) is held as
the explicit SET OF ALL ITS ELEMENTS, and W^(i+1) adds v_j * g for EVERY element
g of W^(i) with deg g <= D-1 (not a basis), for every j. Feasible only while the
iterates have at most `cap` elements.
"""
import itertools


class Brute:
    def __init__(self, nv, D):
        self.nv, self.D = nv, D
        mons = []
        for d in range(D + 1):
            for c in itertools.combinations(range(nv), d):
                m = 0
                for i in c:
                    m |= 1 << i
                mons.append(m)
        mons.sort(key=lambda m: (bin(m).count("1"), m))
        self.mons = mons
        self.idx = {m: i for i, m in enumerate(mons)}
        self.lowmask = 0
        for i, m in enumerate(mons):
            if bin(m).count("1") <= D - 1:
                self.lowmask |= 1 << i

    def vec(self, masks):
        v = 0
        for m in masks:
            v ^= 1 << self.idx[m]
        return v

    def prod(self, g, j):
        r = 0
        i = 0
        while g:
            if g & 1:
                r ^= 1 << self.idx[self.mons[i] | (1 << j)]
            g >>= 1
            i += 1
        return r

    def rows(self, eqs):
        out = []
        for d in range(self.D - 1):
            for c in itertools.combinations(range(self.nv), d):
                mu = 0
                for i in c:
                    mu |= 1 << i
                for eq in eqs:
                    acc = set()
                    for m in eq:
                        acc ^= {m | mu}
                    out.append(self.vec(acc))
        return out

    @staticmethod
    def _span_add(S, p):
        if p in S:
            return S
        return S | {e ^ p for e in S}

    def closure(self, eqs, cap=1 << 16):
        S = {0}
        for r in self.rows(eqs):
            S = self._span_add(S, r)
            if len(S) > cap:
                return {"completed": False, "dims_prefix": [],
                        "first_one_iteration_prefix": None}
        dims = [len(S).bit_length() - 1]
        first_one = 0 if (1 in S) else None   # constant 1 has index 0 -> vector 1
        it = 0
        while True:
            lows = [g for g in S if g & ~self.lowmask == 0]
            T = S
            for g in lows:
                for j in range(self.nv):
                    T = self._span_add(T, self.prod(g, j))
                    if len(T) > cap:
                        return {"completed": False, "dims_prefix": dims,
                                "first_one_iteration_prefix": first_one}
            S = T
            it += 1
            dims.append(len(S).bit_length() - 1)
            if first_one is None and 1 in S:
                first_one = it
            if dims[-1] == dims[-2]:
                return {"completed": True, "dims": dims, "fixpoint_index": it - 1,
                        "first_one_iteration": first_one, "elements": S}
