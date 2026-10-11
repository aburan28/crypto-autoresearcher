"""Schoolbook F_{2^n} arithmetic for EXP-BINSTD-9d1b8e Stage 2.

Adapted from experiments/EXP-CERTBIN-e94b27/impl/gf2n.py (schoolbook path
only). Adds Artin–Schreier solve for even and odd n (CERTBIN half_trace is
odd-n only).
"""
from __future__ import annotations


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
    n = mod.bit_length() - 1
    x = 2
    cur = x
    for i in range(1, n + 1):
        cur = pmod(clmul(cur, cur), mod)
        if i <= n // 2:
            if pgcd(mod, cur ^ x) != 1:
                return False
    return cur == x


def find_irreducible(n: int, start: int | None = None) -> int:
    """Return a monic irreducible of degree n (bit n set, constant term 1)."""
    if start is None:
        start = (1 << n) | 1
    cand = start if (start & 1) else start + 1
    limit = 1 << (n + 1)
    while cand < limit:
        if cand.bit_length() - 1 == n and (cand & 1) and is_irreducible(cand):
            return cand
        cand += 2
    raise RuntimeError(f"no irreducible found for n={n}")


class Field:
    """Generic schoolbook F_{2^n}."""

    def __init__(self, n: int, mod: int):
        assert mod.bit_length() - 1 == n
        self.n = n
        self.mod = mod
        self.q = 1 << n

    def mul(self, a: int, b: int) -> int:
        return pmod(clmul(a, b), self.mod)

    mul_school = mul

    def sqr(self, a: int) -> int:
        return self.mul(a, a)

    def pow(self, a: int, e: int) -> int:
        r = 1
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

    def div(self, a: int, b: int) -> int:
        return self.mul(a, self.inv(b))

    def trace(self, a: int) -> int:
        s = 0
        x = a
        for _ in range(self.n):
            s ^= x
            x = self.mul(x, x)
        assert s in (0, 1)
        return s

    def sqrt(self, a: int) -> int:
        x = a
        for _ in range(self.n - 1):
            x = self.mul(x, x)
        return x

    def frobenius(self, a: int, m: int = 1) -> int:
        """a |-> a^{2^m}."""
        x = a
        for _ in range(m):
            x = self.sqr(x)
        return x

    def solve_artin_schreier(self, c: int) -> int | None:
        """Return one z with z^2 + z = c, or None if no solution.

        Builds the F2-linear map L(z)=z^2+z and solves via Gaussian elimination.
        """
        if self.trace(c) != 0:
            return None
        n = self.n
        # Augmented matrix: n rows, n+1 cols (last = rhs). Row i is bit i of
        # (column_0 ... column_{n-1} | c).
        # column j = L(1<<j) as bits.
        rows = [0] * n
        for j in range(n):
            lj = self.sqr(1 << j) ^ (1 << j)
            for i in range(n):
                if (lj >> i) & 1:
                    rows[i] |= 1 << j
        for i in range(n):
            if (c >> i) & 1:
                rows[i] |= 1 << n  # rhs bit

        # GE
        piv_col = [-1] * n
        r = 0
        for col in range(n):
            piv = None
            for i in range(r, n):
                if (rows[i] >> col) & 1:
                    piv = i
                    break
            if piv is None:
                continue
            rows[r], rows[piv] = rows[piv], rows[r]
            for i in range(n):
                if i != r and ((rows[i] >> col) & 1):
                    rows[i] ^= rows[r]
            piv_col[r] = col
            r += 1
            if r == n:
                break
        for i in range(r, n):
            if (rows[i] >> n) & 1:
                return None
        z = 0
        for i in range(r):
            col = piv_col[i]
            if (rows[i] >> n) & 1:
                z |= 1 << col
        assert (self.sqr(z) ^ z) == c
        return z
