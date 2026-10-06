"""Binary-field arithmetic for EXP-BINSTD-6211a9.

Adapted from experiments/EXP-CERTBIN-e94b27/impl/gf2n.py.
Elements of F_2[t]/(f) are Python ints; bit j is the coefficient of t^j.
"""
from __future__ import annotations

import numpy as np

# Irreducible reduction polynomials used by this experiment (odd n only).
IRRED = {
    17: (1 << 17) | (1 << 3) | 1,  # t^17 + t^3 + 1 (Trimoska / CERTBIN)
    23: (1 << 23) | (1 << 5) | 1,  # t^23 + t^5 + 1
    29: (1 << 29) | (1 << 2) | 1,  # t^29 + t^2 + 1
}


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


def is_irreducible(mod: int):
    n = mod.bit_length() - 1
    details = {"n": n, "gcd_checks": []}
    x = 2
    cur = x
    ok = True
    for i in range(1, n + 1):
        cur = pmod(clmul(cur, cur), mod)
        if i <= n // 2:
            g = pgcd(mod, cur ^ x)
            details["gcd_checks"].append({"i": i, "gcd": g})
            if g != 1:
                ok = False
    details["t_pow_2n_equals_t"] = cur == x
    return ok and cur == x, details


class Field:
    """Schoolbook F_{2^n}."""

    def __init__(self, n: int, mod: int | None = None):
        self.n = n
        self.mod = IRRED[n] if mod is None else mod
        self.q = 1 << n
        ok, _ = is_irreducible(self.mod)
        if not ok:
            raise ValueError(f"modulus not irreducible for n={n}: {self.mod:#x}")

    def mul_school(self, a: int, b: int) -> int:
        return pmod(clmul(a, b), self.mod)

    mul = mul_school

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
            x = self.mul_school(x, x)
        return s & 1

    def half_trace(self, a: int) -> int:
        assert self.n % 2 == 1
        s = 0
        x = a
        for _ in range((self.n - 1) // 2 + 1):
            s ^= x
            x2 = self.mul_school(x, x)
            x = self.mul_school(x2, x2)
        return s

    def sqrt(self, a: int) -> int:
        x = a
        for _ in range(self.n - 1):
            x = self.mul_school(x, x)
        return x


class LinearMapsField(Field):
    """Schoolbook mul with precomputed F2-linear trace / half-trace / sqrt maps.

    Safe for n=29 (no 2^n tables). Preferred default for all odd n here.
    """

    def __init__(self, n: int, mod: int | None = None):
        super().__init__(n, mod)
        self.tr_mask = 0
        for j in range(n):
            if Field.trace(self, 1 << j):
                self.tr_mask |= 1 << j
        self.ht_basis = [Field.half_trace(self, 1 << j) for j in range(n)]
        self.sqrt_basis = [Field.sqrt(self, 1 << j) for j in range(n)]

    def trace(self, a):
        return bin(int(a) & self.tr_mask).count("1") & 1

    def half_trace(self, a):
        s = 0
        j = 0
        aa = int(a)
        while aa:
            if aa & 1:
                s ^= self.ht_basis[j]
            aa >>= 1
            j += 1
        return s

    def sqrt(self, a):
        s = 0
        j = 0
        aa = int(a)
        while aa:
            if aa & 1:
                s ^= self.sqrt_basis[j]
            aa >>= 1
            j += 1
        return s

    def vtrace(self, a):
        a = np.asarray(a, dtype=np.int64)
        x = a & np.int64(self.tr_mask)
        out = np.zeros(a.shape, dtype=np.int64)
        while np.any(x):
            out ^= x & 1
            x >>= 1
        return out.astype(np.uint8)


class TableField(LinearMapsField):
    """F_{2^n} with exp/log tables (generator t). Only for n <= 23."""

    def __init__(self, n: int, mod: int | None = None):
        if n > 23:
            raise ValueError("TableField refuses n>23 (memory)")
        super().__init__(n, mod)
        q1 = self.q - 1
        exp = [0] * (2 * q1)
        log = [0] * self.q
        x = 1
        for i in range(q1):
            exp[i] = x
            log[x] = i
            x = pmod(x << 1, self.mod)
        if x != 1:
            raise ValueError("t does not have order q-1")
        if len(set(exp[:q1])) != q1:
            raise ValueError("t is not a generator")
        for i in range(q1, 2 * q1):
            exp[i] = exp[i - q1]
        self.exp = exp
        self.log = log
        self.q1 = q1
        self.np_exp = np.array(exp, dtype=np.int64)
        self.np_log = np.array(log, dtype=np.int64)

    def mul(self, a, b):
        if a == 0 or b == 0:
            return 0
        return self.exp[self.log[a] + self.log[b]]

    def sqr(self, a):
        return self.mul(a, a)

    def inv(self, a):
        if a == 0:
            raise ZeroDivisionError
        return self.exp[(self.q1 - self.log[a]) % self.q1]

    def div(self, a, b):
        if b == 0:
            raise ZeroDivisionError
        if a == 0:
            return 0
        return self.exp[(self.log[a] - self.log[b]) % self.q1]

    def vmul(self, a, b):
        a = np.asarray(a, dtype=np.int64)
        b = np.asarray(b, dtype=np.int64)
        z = (a == 0) | (b == 0)
        r = self.np_exp[(self.np_log[a] + self.np_log[b]) % self.q1]
        return np.where(z, 0, r)

    def vdiv(self, a, b):
        a = np.asarray(a, dtype=np.int64)
        b = np.asarray(b, dtype=np.int64)
        if np.any(b == 0):
            raise ZeroDivisionError
        z = a == 0
        r = self.np_exp[(self.np_log[a] - self.np_log[b]) % self.q1]
        return np.where(z, 0, r)


def make_field(n: int, mod: int | None = None, prefer_tables: bool = True):
    if prefer_tables and n <= 23:
        try:
            return TableField(n, mod)
        except ValueError:
            return LinearMapsField(n, mod)
    return LinearMapsField(n, mod)
