"""Fast kernel for the recombination search.

Multiplication by a monomial is F_2-LINEAR in the Boolean ring, so
m*(f_i + f_j) = m*f_i + m*f_j.  Precompute the row of m*f_j once per
(generator, monomial); a recombined generator's row is an XOR of those.
Degree of a product = degree of its top set column, since columns are
sorted by degree.  No set arithmetic per matrix.
"""
import sys
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from ffd_semaev import popcount

class Kernel:
    def __init__(self, eqs, N):
        self.N = N; self.l = len(eqs)
        self.monos = sorted(range(1 << N), key=lambda m: (popcount(m), m))
        self.idx = {m: i for i, m in enumerate(self.monos)}
        self.degs = [popcount(m) for m in self.monos]
        self.rowtab = []
        for f in eqs:
            row = []
            for m in self.monos:
                r = 0
                for mm in f:
                    r |= 1 << self.idx[mm | m]
                row.append(r)
            self.rowtab.append(row)
        self.nm = len(self.monos)
        self.order = {}
        for D in range(0, N + 1):
            self.order[D] = [i for i, d in enumerate(self.degs) if d == D] + \
                            [i for i, d in enumerate(self.degs) if d < D]

    def gen_rows(self, S):
        tabs = [self.rowtab[j] for j in range(self.l) if (S >> j) & 1]
        if not tabs:
            return []
        if len(tabs) == 1:
            return list(tabs[0])
        out = []
        for mi in range(self.nm):
            r = 0
            for t in tabs:
                r ^= t[mi]
            out.append(r)
        return out

    def _rk_low(self, rows, D):
        degs = self.degs
        piv = []
        for r in rows:
            cur = r
            for p, pr in piv:
                if (cur >> p) & 1:
                    cur ^= pr
            if cur:
                for col in self.order[D]:
                    if (cur >> col) & 1:
                        piv.append((col, cur)); break
        return len(piv), sum(1 for col, _ in piv if degs[col] < D)

    def collect(self, M, D, cache):
        rows = []
        for S in M:
            g = cache.get(S)
            if g is None:
                g = cache[S] = self.gen_rows(S)
            for r in g:
                if r and self.degs[r.bit_length() - 1] <= D:
                    rows.append(r)
        return rows

    def new_falls(self, M, D, cache):
        rows = self.collect(M, D, cache)
        if not rows:
            return 0
        _, low = self._rk_low(rows, D)
        prev = 0
        if D > 1:
            rp = self.collect(M, D - 1, cache)
            if rp:
                prev, _ = self._rk_low(rp, D - 1)
        return low - prev

    def ffd(self, M, cache, Dmax=None):
        for D in range(1, (Dmax or self.N) + 1):
            if self.new_falls(M, D, cache) > 0:
                return D
        return None

    def zero_gen(self, M, cache):
        for S in M:
            g = cache.get(S)
            if g is None:
                g = cache[S] = self.gen_rows(S)
            if not any(g):
                return True
        return False
