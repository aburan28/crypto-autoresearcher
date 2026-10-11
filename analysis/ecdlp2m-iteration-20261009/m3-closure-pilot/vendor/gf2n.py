"""F_{2^n} = F_2[t]/(f), element <-> n-bit integer (bit j = coefficient of t^j).

Scalar ops use schoolbook carry-less multiplication; bulk ops use exp/log
tables built from the generator t (2^n - 1 is a Mersenne prime for n = 17 and
n = 19, so every element other than 0, 1 generates the multiplicative group;
checked in C-SELF (i)).
"""
from __future__ import annotations

import numpy as np


def clmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


def poly_mod(a, f):
    df = f.bit_length() - 1
    while a.bit_length() - 1 >= df:
        a ^= f << (a.bit_length() - 1 - df)
    return a


def poly_gcd(a, b):
    while b:
        a, b = b, poly_mod(a, b)
    return a


def poly_mulmod(a, b, f):
    return poly_mod(clmul(a, b), f)


class Field:
    def __init__(self, n, modulus):
        self.n = n
        self.f = modulus
        self.size = 1 << n
        self.order = self.size - 1
        # exp/log tables from generator t
        exp = np.zeros(self.order + 1, dtype=np.int64)
        x = 1
        e = [0] * self.order
        for i in range(self.order):
            e[i] = x
            x <<= 1
            if x >> n:
                x ^= modulus
        exp[: self.order] = e
        exp[self.order] = e[0]
        assert x == 1, "t does not have order 2^n - 1"
        lg = np.zeros(self.size, dtype=np.int64)
        lg[exp[: self.order]] = np.arange(self.order, dtype=np.int64)
        self.exp_np = exp
        self.log_np = lg
        self.exp = exp.tolist()
        self.log = lg.tolist()
        # trace mask: bit j = Tr(t^j)
        self.tau = [self._trace_slow(1 << j) for j in range(n)]
        self.trmask = sum(1 << j for j in range(n) if self.tau[j])
        # half-trace images of the basis (n odd)
        assert n % 2 == 1
        self.ht_basis = [self._halftrace_slow(1 << j) for j in range(n)]

    # ---- scalar -------------------------------------------------------------
    def mul(self, a, b):
        if a == 0 or b == 0:
            return 0
        s = self.log[a] + self.log[b]
        if s >= self.order:
            s -= self.order
        return self.exp[s]

    def mul_slow(self, a, b):
        return poly_mulmod(a, b, self.f)

    def sqr(self, a):
        return self.mul(a, a)

    def inv(self, a):
        if a == 0:
            raise ZeroDivisionError
        return self.exp[(self.order - self.log[a]) % self.order]

    def div(self, a, b):
        return self.mul(a, self.inv(b))

    def pow(self, a, e):
        if a == 0:
            return 0 if e else 1
        return self.exp[(self.log[a] * e) % self.order]

    def trace(self, a):
        return bin(a & self.trmask).count("1") & 1

    def halftrace(self, a):
        r = 0
        j = 0
        while a:
            if a & 1:
                r ^= self.ht_basis[j]
            a >>= 1
            j += 1
        return r

    def sqrt(self, a):
        # a^(2^(n-1))
        r = a
        for _ in range(self.n - 1):
            r = self.mul_slow(r, r)
        return r

    def _trace_slow(self, a):
        r, x = 0, a
        for _ in range(self.n):
            r ^= x
            x = poly_mulmod(x, x, self.f)
        assert r in (0, 1)
        return r

    def _halftrace_slow(self, a):
        r, x = 0, a
        for _ in range((self.n - 1) // 2 + 1):
            r ^= x
            x = poly_mulmod(x, x, self.f)
            x = poly_mulmod(x, x, self.f)
        return r

    # ---- vectorized (numpy int64 arrays) -------------------------------------
    def vmul(self, a, b):
        a = np.asarray(a, dtype=np.int64)
        b = np.asarray(b, dtype=np.int64)
        s = self.log_np[a] + self.log_np[b]
        s = np.where(s >= self.order, s - self.order, s)
        return np.where((a == 0) | (b == 0), 0, self.exp_np[s])

    def vinv(self, a):
        a = np.asarray(a, dtype=np.int64)
        return np.where(a == 0, 0, self.exp_np[(self.order - self.log_np[a]) % self.order])

    def vtrace(self, a):
        x = np.asarray(a, dtype=np.int64) & self.trmask
        p = np.zeros(x.shape, dtype=np.int64)
        for j in range(self.n):
            p ^= (x >> j) & 1
        return p

    def vhalftrace(self, a):
        a = np.asarray(a, dtype=np.int64)
        r = np.zeros(a.shape, dtype=np.int64)
        for j in range(self.n):
            r ^= np.where((a >> j) & 1, self.ht_basis[j], 0)
        return r


def is_irreducible(n, f):
    """gcd(t^{2^i} - t, f) = 1 for i = 1..floor(n/2) and t^{2^n} = t mod f."""
    x = 2
    checks = []
    ok = True
    for i in range(1, n + 1):
        x = poly_mulmod(x, x, f)
        if i <= n // 2:
            g = poly_gcd(f, x ^ 2)
            checks.append({"i": i, "gcd": g})
            ok &= g == 1
    ok &= x == 2
    return ok, checks, x == 2


_FIELDS = {}


def field(n, modulus):
    key = (n, modulus)
    if key not in _FIELDS:
        _FIELDS[key] = Field(n, modulus)
    return _FIELDS[key]
