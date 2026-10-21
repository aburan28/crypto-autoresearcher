import sys, time, random, itertools
from itertools import combinations
sys.path.insert(0, '.')
import proto


def monomials_upto(nv, D):
    out = [0]
    for d in range(1, D + 1):
        for c in combinations(range(nv), d):
            m = 0
            for j in c:
                m |= 1 << j
            out.append(m)
    return out


def deg(mask):
    return mask.bit_count()


class Mac:
    def __init__(self, nv, D):
        self.nv, self.D = nv, D
        mons = monomials_upto(nv, D)
        self.idx = {m: i for i, m in enumerate(mons)}
        self.ncol = len(mons)
        self.bydeg = [[m for m in mons if deg(m) == d] for d in range(D + 1)]
        self.mon_upto = [[m for m in mons if deg(m) <= d] for d in range(D + 1)]

    def rows_of(self, gen, mult_deg):
        """rows m*gen for all multipliers deg<=mult_deg; each as int bitset over columns"""
        idx = self.idx
        out = []
        for m in self.mon_upto[mult_deg]:
            v = 0
            for g in gen:
                v ^= 1 << idx[g | m]
            out.append(v)
        return out


def rref(rows):
    piv = {}
    for r in rows:
        while r:
            hb = r.bit_length() - 1
            p = piv.get(hb)
            if p is None:
                piv[hb] = r
                break
            r ^= p
    pm = 0
    for b in piv:
        pm |= 1 << b
    for hb in sorted(piv):  # ascending: lower pivot rows are already fully reduced
        r = piv[hb]
        t = (r ^ (1 << hb)) & pm
        while t:
            lb = t & -t
            r ^= piv[lb.bit_length() - 1]
            t ^= lb
        piv[hb] = r
    return piv


def make_nf(piv):
    pm = 0
    for b in piv:
        pm |= 1 << b

    def nf(v):
        t = v & pm
        while t:
            lb = t & -t
            v ^= piv[lb.bit_length() - 1]
            t ^= lb
        return v
    return nf
