"""Binary finite-field arithmetic for EXP-BINSTD-f14cbb.

Elements of F_2[t]/(f) are Python ints; bit j is the coefficient of t^j.
Self-contained (does not import EXP-CERTBIN gf2n); schoolbook only.
"""
from __future__ import annotations

from typing import List, Optional, Tuple


def clmul(a: int, b: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


def pmod(a: int, m: int) -> int:
    dm = m.bit_length() - 1
    while a and a.bit_length() - 1 >= dm:
        a ^= m << (a.bit_length() - 1 - dm)
    return a


def pgcd(a: int, b: int) -> int:
    while b:
        a, b = b, pmod(a, b)
    return a


def is_irreducible(mod: int) -> bool:
    """Rabin-style irreducibility test over F_2."""
    n = mod.bit_length() - 1
    x = 2  # t
    cur = x
    for i in range(1, n + 1):
        cur = pmod(clmul(cur, cur), mod)  # t^{2^i}
        if i <= n // 2:
            if pgcd(mod, cur ^ x) != 1:
                return False
    return cur == x


def find_irreducible(n: int, start: int = 0) -> int:
    """Find a monic irreducible of degree n over F_2.

    Tries odd polynomials (constant term 1) starting from an optional seed.
    """
    # monic of degree n: bit n set; require constant term 1 for no root at 0
    base = (1 << n) | 1
    limit = 1 << n
    # lower bits 1..n-1 free; bit 0 fixed to 1
    idx = start
    while idx < limit:
        cand = base | (idx << 1)
        # ensure degree exactly n
        if is_irreducible(cand):
            return cand
        idx += 1
    raise RuntimeError(f"no irreducible of degree {n} found")


# Irreducibles verified by is_irreducible() at construction time
KNOWN_IRREDUCIBLES = {
    8: (1 << 8) | (1 << 4) | (1 << 3) | (1 << 1) | 1,  # t^8+t^4+t^3+t+1
    17: (1 << 17) | (1 << 3) | 1,  # t^17+t^3+1 (same as EXP-CERTBIN)
    130: (1 << 130) | (1 << 3) | 1,  # t^130+t^3+1
    131: (1 << 131) | (1 << 7) | (1 << 6) | (1 << 5) | (1 << 4) | (1 << 1) | 1,
    # t^131+t^7+t^6+t^5+t^4+t+1 = 0x8000000000000000000000000000000f3
}


class GF2n:
    """Schoolbook F_{2^n}."""

    def __init__(self, n: int, mod: Optional[int] = None):
        self.n = n
        self.mod = mod if mod is not None else (
            KNOWN_IRREDUCIBLES[n] if n in KNOWN_IRREDUCIBLES else find_irreducible(n)
        )
        if self.mod.bit_length() - 1 != n:
            raise ValueError("modulus degree mismatch")
        if not is_irreducible(self.mod):
            raise ValueError(f"modulus not irreducible: {self.mod:#x}")
        self.q = 1 << n

    def add(self, a: int, b: int) -> int:
        return a ^ b

    def mul(self, a: int, b: int) -> int:
        return pmod(clmul(a & (self.q - 1), b & (self.q - 1)), self.mod)

    def sqr(self, a: int) -> int:
        return self.mul(a, a)

    def pow(self, a: int, e: int) -> int:
        r = 1
        a &= self.q - 1
        while e:
            if e & 1:
                r = self.mul(r, a)
            a = self.mul(a, a)
            e >>= 1
        return r

    def inv(self, a: int) -> int:
        if a == 0:
            raise ZeroDivisionError
        return self.pow(a, self.q - 2)

    def frobenius(self, a: int, times: int = 1) -> int:
        """Apply x |-> x^{2^{times}}."""
        times %= self.n
        for _ in range(times):
            a = self.sqr(a)
        return a

    def trace_to_f2(self, a: int) -> int:
        s = 0
        x = a
        for _ in range(self.n):
            s ^= x
            x = self.sqr(x)
        return s & 1

    def find_element_of_order(self, order: int) -> int:
        """Find an element of exact multiplicative order `order` (order | q-1)."""
        q1 = self.q - 1
        if q1 % order != 0:
            raise ValueError(f"order {order} does not divide {q1}")
        # Factor order for exactness checks
        fac = _prime_factors(order)
        # Try x = t, t+1, ... as candidates (poly basis)
        for cand in range(1, min(self.q, 100000)):
            if self.pow(cand, q1 // order) == 1:
                continue
            # cand^{(q-1)/order} has order dividing order; check exact
            g = self.pow(cand, q1 // order)
            if g == 1:
                continue
            ok = True
            for p in fac:
                if self.pow(g, order // p) == 1:
                    ok = False
                    break
            if ok:
                return g
        # Random-ish search via LCG through field
        x = 3
        for _ in range(self.q):
            x = self.mul(x, 5) ^ 1
            if x == 0:
                continue
            g = self.pow(x, q1 // order)
            if g == 1:
                continue
            ok = True
            for p in fac:
                if self.pow(g, order // p) == 1:
                    ok = False
                    break
            if ok:
                return g
        raise RuntimeError(f"no element of order {order} in F_2^{self.n}")


def _prime_factors(n: int) -> List[int]:
    fac = []
    p = 2
    while p * p <= n:
        if n % p == 0:
            fac.append(p)
            while n % p == 0:
                n //= p
        p += 1 if p == 2 else 2
    if n > 1:
        fac.append(n)
    return fac


def f2_rank(rows: List[int], width: int) -> int:
    """Gaussian elimination rank over F_2; rows are bit-packed ints."""
    mats = list(rows)
    rank = 0
    for col in range(width):
        pivot = None
        for i in range(rank, len(mats)):
            if (mats[i] >> col) & 1:
                pivot = i
                break
        if pivot is None:
            continue
        mats[rank], mats[pivot] = mats[pivot], mats[rank]
        for i in range(len(mats)):
            if i != rank and ((mats[i] >> col) & 1):
                mats[i] ^= mats[rank]
        rank += 1
    return rank


def subspace_frobenius_stable(basis: List[int], field: GF2n) -> bool:
    """True iff F_2-span of `basis` is closed under x |-> x^2."""
    if not basis:
        return True
    # Row-reduce basis
    width = field.n
    mats = [b for b in basis if b]
    # Build matrix and check each sq(b) is in span
    # Use bit packing: gather independent rows
    rows = list(mats)
    # RREF-ish for membership tests
    A = list(rows)
    r = 0
    pivot_col = {}
    for col in range(width):
        piv = None
        for i in range(r, len(A)):
            if (A[i] >> col) & 1:
                piv = i
                break
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        for i in range(len(A)):
            if i != r and ((A[i] >> col) & 1):
                A[i] ^= A[r]
        pivot_col[col] = r
        r += 1

    def in_span(v: int) -> bool:
        x = v
        for col, prow in pivot_col.items():
            if (x >> col) & 1:
                x ^= A[prow]
        return x == 0

    for b in mats:
        if not in_span(field.sqr(b)):
            return False
    return True


def apply_linearized(poly_bits: List[int], x: int, field: GF2n) -> int:
    """Apply sum_i a_i * x^{2^i} with a_i in F_2 (poly_bits[i] in {0,1})."""
    acc = 0
    cur = x
    for a in poly_bits:
        if a:
            acc ^= cur
        cur = field.sqr(cur)
    return acc


def minpoly_of_element(t: int, field: GF2n) -> List[int]:
    """Minimal polynomial of t over F_2 as list of coefficients [a0..ad] (a_d=1).

    Uses linear dependence of 1, t, t^2, ..., t^d in F_2-vector space.
    """
    # Powers t^0 .. t^n as vectors; find first dependence
    n = field.n
    powers = [1]
    cur = 1
    for _ in range(n):
        cur = field.mul(cur, t)
        powers.append(cur)
    # Find smallest d such that 1,t,...,t^d are dependent
    for d in range(1, n + 1):
        # Matrix with columns = powers[0..d] (each n bits) — use rows as powers
        rows = powers[: d + 1]
        # Build (d+1) x n and check rank < d+1
        if f2_rank(rows, n) < d + 1:
            # Solve sum a_i t^i = 0 with a_d = 1
            # Gaussian on transpose: find kernel of [powers[0]|...|powers[d]]
            # Represent each power as row; find nonzero kernel vector
            m = d + 1
            # Augment: rows are bit-vectors of length n; we need ker of n x m matrix
            # whose columns are the powers. Equivalently left-ker of rows.
            # Build m columns as ints of width n; find F2-deps among the m vectors.
            vecs = list(rows)
            # Row reduce recording column ops via identity
            ident = [1 << i for i in range(m)]
            r = 0
            for col in range(n):
                piv = None
                for i in range(r, m):
                    if (vecs[i] >> col) & 1:
                        piv = i
                        break
                if piv is None:
                    continue
                vecs[r], vecs[piv] = vecs[piv], vecs[r]
                ident[r], ident[piv] = ident[piv], ident[r]
                for i in range(m):
                    if i != r and ((vecs[i] >> col) & 1):
                        vecs[i] ^= vecs[r]
                        ident[i] ^= ident[r]
                r += 1
                if r == m:
                    break
            # Any zero row in vecs gives a kernel vector in ident
            for i in range(m):
                if vecs[i] == 0 and ident[i] != 0:
                    coeffs = [(ident[i] >> j) & 1 for j in range(m)]
                    # Prefer monic: if leading zero, skip
                    if coeffs[-1] == 1:
                        return coeffs
                    # Scale is free over F2 — flip if needed by finding another
            for i in range(m):
                if vecs[i] == 0 and ident[i] != 0:
                    coeffs = [(ident[i] >> j) & 1 for j in range(m)]
                    # Make monic by noting over F2 only one nonzero scale
                    # Find highest 1
                    for j in range(m - 1, -1, -1):
                        if coeffs[j]:
                            return coeffs[: j + 1]
            raise RuntimeError("dependence found but no kernel vector")
    raise RuntimeError("no minimal polynomial found")


def ker_of_linearized(poly_coeffs: List[int], field: GF2n) -> Tuple[int, List[int]]:
    """Kernel dimension and an F_2-basis of {x : sum a_i x^{2^i} = 0}."""
    n = field.n
    # Matrix of the F_2-linear map; columns = images of basis e_j = 1<<j
    images = [apply_linearized(poly_coeffs, 1 << j, field) for j in range(n)]
    # Ker of map with columns images: find x with sum x_j images[j] = 0
    # Row-reduce the n x n matrix whose column j is images[j]
    # Represent rows: bit i of row-vector pack
    # Build matrix M[row][col] = bit row of images[col]
    rows = [0] * n  # rows[r] bit c set if M[r][c]=1
    for c in range(n):
        v = images[c]
        for r in range(n):
            if (v >> r) & 1:
                rows[r] |= 1 << c
    # RREF
    ident = [1 << i for i in range(n)]  # track column space? better track row ops on identity for ker
    # Standard: augment with identity on the right for finding nullspace via RREF on transpose
    # Nullspace of columns: solve M x = 0. M has columns=images.
    # Put M as list of column-ints (width n), RREF on rows of bit-matrix.
    A = list(rows)
    rnk = 0
    pivot_for_col = [-1] * n
    for col in range(n):
        piv = None
        for i in range(rnk, n):
            if (A[i] >> col) & 1:
                piv = i
                break
        if piv is None:
            continue
        A[rnk], A[piv] = A[piv], A[rnk]
        for i in range(n):
            if i != rnk and ((A[i] >> col) & 1):
                A[i] ^= A[rnk]
        pivot_for_col[col] = rnk
        rnk += 1
    # Free columns -> basis vectors
    basis = []
    for free in range(n):
        if pivot_for_col[free] != -1:
            continue
        vec = 1 << free
        for col in range(n):
            prow = pivot_for_col[col]
            if prow != -1 and ((A[prow] >> free) & 1):
                vec ^= 1 << col
        basis.append(vec)
    return len(basis), basis
