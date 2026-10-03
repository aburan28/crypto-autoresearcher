"""Binary-field arithmetic for EXP-CERTBIN-4e92d7.

Elements of F_2[t]/(f) are Python ints; bit j is the coefficient of t^j.

Two independent multiplication paths are provided on purpose:
  * ``Field.mul_school``  - carry-less schoolbook multiply + polynomial reduction;
  * ``TableField.mul``    - exp/log tables (used on hot paths).
The self-test cross-checks them, and certificate-style re-verification
(C-WIT) uses the schoolbook path only.
"""
import numpy as np

N = 17
MODULUS = (1 << 17) | (1 << 3) | 1  # t^17 + t^3 + 1


def clmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


def pmod(a, m):
    dm = m.bit_length() - 1
    while a and a.bit_length() - 1 >= dm:
        a ^= m << (a.bit_length() - 1 - dm)
    return a


def pgcd(a, b):
    while b:
        a, b = b, pmod(a, b)
    return a


def is_irreducible(mod):
    """Rabin-style test used in the self-test (spec: gcd(t^{2^i}-t, f) = 1 for
    i = 1..floor(n/2) and t^{2^n} = t mod f). Returns (ok, details)."""
    n = mod.bit_length() - 1
    details = {"n": n, "gcd_checks": []}
    x = 2  # t
    cur = x
    ok = True
    for i in range(1, n + 1):
        cur = pmod(clmul(cur, cur), mod)  # t^{2^i}
        if i <= n // 2:
            g = pgcd(mod, cur ^ x)
            details["gcd_checks"].append({"i": i, "gcd": g})
            if g != 1:
                ok = False
    details["t_pow_2n_equals_t"] = (cur == x)
    ok = ok and cur == x
    return ok, details


class Field:
    """Generic (slow, schoolbook) F_{2^n}."""

    def __init__(self, n, mod):
        self.n = n
        self.mod = mod
        self.q = 1 << n

    def mul_school(self, a, b):
        return pmod(clmul(a, b), self.mod)

    mul = mul_school

    def sqr(self, a):
        return self.mul(a, a)

    def pow(self, a, e):
        r = 1
        while e:
            if e & 1:
                r = self.mul(r, a)
            a = self.mul(a, a)
            e >>= 1
        return r

    def inv(self, a):
        if a == 0:
            raise ZeroDivisionError
        return self.pow(a, self.q - 2)

    def trace(self, a):
        s = 0
        x = a
        for _ in range(self.n):
            s ^= x
            x = self.mul(x, x)
        assert s in (0, 1)
        return s

    def half_trace(self, a):
        # H(c) = sum_{i=0}^{(n-1)/2} c^{2^{2i}}; for n odd, H(c)^2 + H(c) = c + Tr(c)
        assert self.n % 2 == 1
        s = 0
        x = a
        for _ in range((self.n - 1) // 2 + 1):
            s ^= x
            x = self.sqr(self.sqr(x))
        return s

    def sqrt(self, a):
        x = a
        for _ in range(self.n - 1):
            x = self.mul(x, x)
        return x


class TableField(Field):
    """F_{2^n} with exp/log tables (the multiplicative group must be cyclic with
    generator t; checked at construction)."""

    def __init__(self, n=N, mod=MODULUS):
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
        # linear maps (F_2-linear): trace mask, half-trace basis images, sqrt basis images
        self.tr_mask = 0
        for j in range(n):
            if Field.trace(self, 1 << j):
                self.tr_mask |= 1 << j
        self.ht_basis = [Field.half_trace(self, 1 << j) for j in range(n)]
        self.sqrt_basis = [Field.sqrt(self, 1 << j) for j in range(n)]
        self.np_ht_basis = np.array(self.ht_basis, dtype=np.int64)
        self.np_sqrt_basis = np.array(self.sqrt_basis, dtype=np.int64)

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

    def trace(self, a):
        return bin(a & self.tr_mask).count("1") & 1

    def half_trace(self, a):
        s = 0
        j = 0
        while a:
            if a & 1:
                s ^= self.ht_basis[j]
            a >>= 1
            j += 1
        return s

    def sqrt(self, a):
        s = 0
        j = 0
        while a:
            if a & 1:
                s ^= self.sqrt_basis[j]
            a >>= 1
            j += 1
        return s

    # ---- vectorised helpers (numpy int64 arrays) ----
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

    def _vlin(self, a, basis):
        a = np.asarray(a, dtype=np.int64)
        s = np.zeros_like(a)
        for j in range(self.n):
            s ^= np.where((a >> j) & 1 == 1, basis[j], 0)
        return s

    def vhalf_trace(self, a):
        return self._vlin(a, self.np_ht_basis)

    def vsqrt(self, a):
        return self._vlin(a, self.np_sqrt_basis)
