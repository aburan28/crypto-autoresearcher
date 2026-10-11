"""Dual-route F_{2^n} arithmetic for EXP-BINSTD-88a926.

Elements are Python ints; bit j is the coefficient of t^j.

Route A: Field.mul_school (carry-less schoolbook + polynomial reduction).
Route B: TableField.mul (exp/log tables). Certificate re-verify uses schoolbook only.
No Magma/Sage/AUXIN/Bedrock. No numpy.
"""
from __future__ import annotations

MODULI = {
    17: (1 << 17) | (1 << 3) | 1,  # t^17+t^3+1
    23: (1 << 23) | (1 << 5) | 1,  # t^23+t^5+1
    31: (1 << 31) | (1 << 3) | 1,  # t^31+t^3+1
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


def is_irreducible(mod: int) -> tuple[bool, dict]:
    n = mod.bit_length() - 1
    details: dict = {"n": n, "gcd_checks": []}
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
    """Schoolbook F_{2^n} (Route A / certificate path)."""

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


class TableField(Field):
    """Exp/log tables (Route B). Re-verify never uses this class."""

    def __init__(self, n: int, mod: int):
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
        self.tr_mask = 0
        for j in range(n):
            if Field.trace(self, 1 << j):
                self.tr_mask |= 1 << j
        self.ht_basis = [Field.half_trace(self, 1 << j) for j in range(n)]
        self.sqrt_basis = [Field.sqrt(self, 1 << j) for j in range(n)]

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
