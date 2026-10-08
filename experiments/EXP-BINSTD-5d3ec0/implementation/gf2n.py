"""Binary-field arithmetic for EXP-BINSTD-5d3ec0 (n=19 toy + generic helpers).

Lifted from experiments/EXP-CERTBIN-e94b27/impl/gf2n.py under write_scope;
parameterised for arbitrary odd n. Schoolbook path used for independent
certificate re-verification.
"""
from __future__ import annotations

import numpy as np

# n=19 Koblitz toy cell (spec inputs.cells.BIN-TOY-n19-koblitz)
N19 = 19
MOD19 = (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1  # t^19+t^5+t^2+t+1


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
    ok = ok and cur == x
    return ok, details


class Field:
    def __init__(self, n: int, mod: int):
        self.n = n
        self.mod = mod
        self.q = 1 << n

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

    def trace(self, a: int) -> int:
        s = 0
        x = a
        for _ in range(self.n):
            s ^= x
            x = self.mul(x, x)
        assert s in (0, 1)
        return s

    def half_trace(self, a: int) -> int:
        assert self.n % 2 == 1
        s = 0
        x = a
        for _ in range((self.n - 1) // 2 + 1):
            s ^= x
            x = self.sqr(self.sqr(x))
        return s

    def sqrt(self, a: int) -> int:
        x = a
        for _ in range(self.n - 1):
            x = self.mul(x, x)
        return x

    def frobenius(self, a: int, j: int = 1) -> int:
        """a^{2^j}."""
        for _ in range(j % self.n):
            a = self.sqr(a)
        return a


class TableField(Field):
    def __init__(self, n: int = N19, mod: int = MOD19):
        super().__init__(n, mod)
        q1 = self.q - 1
        exp = [0] * (2 * q1)
        log = [0] * self.q
        x = 1
        for i in range(q1):
            exp[i] = x
            log[x] = i
            x = pmod(x << 1, mod)
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
        self.tr_mask = 0
        for j in range(n):
            if Field.trace(self, 1 << j):
                self.tr_mask |= 1 << j
        self.ht_basis = [Field.half_trace(self, 1 << j) for j in range(n)]
        self.sqrt_basis = [Field.sqrt(self, 1 << j) for j in range(n)]
        self.np_ht_basis = np.array(self.ht_basis, dtype=np.int64)
        self.np_sqrt_basis = np.array(self.sqrt_basis, dtype=np.int64)

    def mul(self, a: int, b: int) -> int:
        if a == 0 or b == 0:
            return 0
        return self.exp[self.log[a] + self.log[b]]

    def sqr(self, a: int) -> int:
        return self.mul(a, a)

    def inv(self, a: int) -> int:
        if a == 0:
            raise ZeroDivisionError
        return self.exp[(self.q1 - self.log[a]) % self.q1]

    def div(self, a: int, b: int) -> int:
        if b == 0:
            raise ZeroDivisionError
        if a == 0:
            return 0
        return self.exp[(self.log[a] - self.log[b]) % self.q1]

    def trace(self, a: int) -> int:
        return bin(a & self.tr_mask).count("1") & 1

    def half_trace(self, a: int) -> int:
        s = 0
        j = 0
        while a:
            if a & 1:
                s ^= self.ht_basis[j]
            a >>= 1
            j += 1
        return s

    def sqrt(self, a: int) -> int:
        s = 0
        j = 0
        while a:
            if a & 1:
                s ^= self.sqrt_basis[j]
            a >>= 1
            j += 1
        return s

    def vmul(self, a, b):
        a = np.asarray(a, dtype=np.int64)
        b = np.asarray(b, dtype=np.int64)
        z = (a == 0) | (b == 0)
        r = self.np_exp[(self.np_log[a] + self.np_log[b]) % self.q1]
        return np.where(z, 0, r)

    def vdiv(self, a, b):
        a = np.asarray(a, dtype=np.int64)
        b = np.asarray(b, dtype=np.int64)
        assert not np.any(b == 0)
        r = self.np_exp[(self.np_log[a] - self.np_log[b]) % self.q1]
        return np.where(a == 0, 0, r)

    def vtrace(self, a):
        return (np.bitwise_count(np.asarray(a, dtype=np.int64) & self.tr_mask) & 1).astype(np.int64)
