"""Boolean ring B = F_2[v_0..v_17]/(v_i^2 + v_i), monomial orders, the descended
S_3 system and the Macaulay matrices M_D, written from:
  EXP-CERTBIN-4e92d7 object.{unknowns, summation_polynomial, descended_system,
                             macaulay_matrix}
  EXP-CERTBIN-e94b27 object.{ring, macaulay_M_D}

Representation.
  * A multilinear monomial is an 18-bit mask (bit i <-> v_i).
  * A vector of B_{<=D} is a Python int whose bit b is the coefficient of the
    monomial with GLOBAL BIT INDEX b. The global bit index is the position of the
    monomial in ASCENDING degrevlex order over all multilinear monomials, so the
    constant 1 is bit 0 and the highest monomial is the top bit. Hence, for every
    D, "column c of M_D" (descending degrevlex, constant LAST) is bit C_D - 1 - c,
    the leading monomial of a vector is its highest set bit, and a vector lies in
    B_{<=d} iff it is < 2^{N(d)} with N(d) = #monomials of degree <= d.
"""
import itertools
from functools import cmp_to_key

import gf2n as F

NV = 18          # variables v_0..v_17
NEQ = 17         # equations f_0..f_16
L = 9            # dim V
FULL = (1 << NV) - 1


def popcount(x):
    return bin(x).count("1")


def mask_to_list(m):
    return [i for i in range(NV) if (m >> i) & 1]


def list_to_mask(lst):
    m = 0
    for i in lst:
        m |= 1 << i
    return m


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------
def degrevlex_greater(a, b):
    """Literal rule of EXP-CERTBIN-4e92d7 object.macaulay_matrix:
    a > b iff deg a > deg b; or deg a = deg b and, at the largest variable
    index i where a and b differ, a does NOT contain v_i."""
    da, db = popcount(a), popcount(b)
    if da != db:
        return da > db
    d = a ^ b
    if d == 0:
        return False
    i = d.bit_length() - 1
    return not ((a >> i) & 1)


def _cmp_desc(a, b):
    if a == b:
        return 0
    return -1 if degrevlex_greater(a, b) else 1


def monomials_upto(D, nv=NV):
    """All multilinear monomial masks of degree <= D."""
    out = []
    for d in range(D + 1):
        for c in itertools.combinations(range(nv), d):
            out.append(list_to_mask(c))
    return out


def row_mu_order(Dm2, nv=NV):
    """mu ordered by (deg ascending, then ascending sorted index tuple, lexicographically)."""
    out = []
    for d in range(Dm2 + 1):
        for c in itertools.combinations(range(nv), d):  # lexicographic ascending tuples
            out.append(list_to_mask(c))
    return out


def column_order(D, nv=NV):
    """Columns of M_D: every monomial of degree <= D in DESCENDING degrevlex, constant LAST."""
    mons = monomials_upto(D, nv)
    return sorted(mons, key=cmp_to_key(_cmp_desc))


def N_upto(d, nv=NV):
    from math import comb
    return sum(comb(nv, e) for e in range(d + 1))


class MonomialIndex:
    """Global bit index = position in ASCENDING degrevlex order (up to degree Dmax)."""

    def __init__(self, Dmax, nv=NV):
        self.Dmax = Dmax
        self.nv = nv
        cols = column_order(Dmax, nv)      # descending
        asc = list(reversed(cols))         # ascending: constant first
        self.mono = asc                    # bit -> mask
        self.bit = {m: b for b, m in enumerate(asc)}
        self.N = [N_upto(d, nv) for d in range(Dmax + 1)]
        # sanity: degree-graded, contiguous blocks
        for b, m in enumerate(asc):
            dg = popcount(m)
            lo = self.N[dg - 1] if dg > 0 else 0
            assert lo <= b < self.N[dg], "order is not degree-graded"
        self.deg_of_bit = [popcount(m) for m in asc]

    def vec_from_masks(self, masks):
        v = 0
        for m in masks:
            v ^= 1 << self.bit[m]
        return v

    def masks_from_vec(self, v):
        out = []
        while v:
            b = v.bit_length() - 1
            out.append(self.mono[b])
            v ^= 1 << b
        return out

    def degree(self, v):
        if v == 0:
            return -1
        return self.deg_of_bit[v.bit_length() - 1]


# ---------------------------------------------------------------------------
# Polynomials over F_{2^17} in the Boolean ring: dict mask -> field element
# ---------------------------------------------------------------------------
def pmul(P, Q):
    R = {}
    for m1, c1 in P.items():
        for m2, c2 in Q.items():
            m = m1 | m2              # multilinear reduction: v^2 = v
            c = F.mul(c1, c2)
            R[m] = R.get(m, 0) ^ c
    return {m: c for m, c in R.items() if c}


def padd(*Ps):
    R = {}
    for P in Ps:
        for m, c in P.items():
            R[m] = R.get(m, 0) ^ c
    return {m: c for m, c in R.items() if c}


def descended_equations(xR, B):
    """Expand S_3(x_1, x_2, x_R) over F_{2^17} in v_0..v_17 with v^2 = v; equation k
    is the coefficient of t^k. Returns a list of 17 sets of monomial masks."""
    X1 = {1 << j: 1 << j for j in range(L)}            # sum_{j<9} v_j t^j
    X2 = {1 << (L + j): 1 << j for j in range(L)}      # sum_{j<9} v_{9+j} t^j
    X3 = {0: xR} if xR else {}
    Bc = {0: B} if B else {}
    U = padd(pmul(X1, X2), pmul(X1, X3), pmul(X2, X3))
    S = padd(pmul(U, U), pmul(pmul(X1, X2), X3), Bc)
    eqs = [set() for _ in range(NEQ)]
    for m, c in S.items():
        for k in range(NEQ):
            if (c >> k) & 1:
                eqs[k].add(m)
    return eqs


def explicit_equations(eq_lists):
    eqs = []
    for eq in eq_lists:
        s = set()
        for mon in eq:
            assert list(mon) == sorted(set(mon)), "monomial not an ascending index list"
            m = list_to_mask(mon)
            assert m not in s, "duplicate monomial in explicit equation"
            s.add(m)
        eqs.append(s)
    assert len(eqs) == NEQ
    return eqs


def eval_eqs(eqs, vmask):
    """Evaluate each equation at the Boolean point vmask (monomial m -> 1 iff m subset of vmask)."""
    out = 0
    for k, eq in enumerate(eqs):
        bit = 0
        for m in eq:
            if m & vmask == m:
                bit ^= 1
        out |= bit << k
    return out


# ---------------------------------------------------------------------------
# Macaulay matrices
# ---------------------------------------------------------------------------
class Macaulay:
    def __init__(self, D, MI, neq=NEQ):
        assert D <= MI.Dmax
        self.D = D
        self.MI = MI
        self.neq = neq
        self.mus = row_mu_order(D - 2, MI.nv)
        self.R = len(self.mus) * neq
        self.C = MI.N[D]

    def rows(self, eqs):
        """Row index = mu_index * neq + k; row = multilinear reduction of mu * f_k."""
        assert len(eqs) == self.neq
        bit = self.MI.bit
        out = []
        for mu in self.mus:
            for k in range(self.neq):
                v = 0
                for m in eqs[k]:
                    v ^= 1 << bit[m | mu]
                out.append(v)
        return out

    def row_key(self, r):
        return mask_to_list(self.mus[r // self.neq]), r % self.neq
