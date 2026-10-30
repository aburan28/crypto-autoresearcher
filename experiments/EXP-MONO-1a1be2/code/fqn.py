"""F_q[t]/(g) arithmetic for EXP-MONO-1a1be2 (TASK-20261029-a97206).

q is an odd prime, g is the lexicographically least monic irreducible polynomial of degree n
over F_q, coefficients read from the constant term upward, each in 0..q-1 (the specification's
scope.field rule). Elements are tuples of n ints in [0, q), constant term first. n = 1 gives
F_q itself with g = t (the least monic degree-1 polynomial), element (c0,).

Also here: a quadratic extension F_{Q^2} = F_Q[s]/(s^2 - d) used for the group-law cross-check,
and univariate polynomial helpers over either field (gcd, powmod, squarefreeness, distinct-degree
factorisation, roots) used by semaev.py and curves.py.

Pure Python, no third-party dependency. Written from the definitions; nothing is imported from
src/ (read-only reuse is documented in README.md).
"""
from __future__ import annotations

import itertools
import random


# ----------------------------------------------------------------------------- helpers over F_q
def _is_prime(p: int) -> bool:
    if p < 2:
        return False
    if p % 2 == 0:
        return p == 2
    i = 3
    while i * i <= p:
        if p % i == 0:
            return False
        i += 2
    return True


def next_prime_above(k: int) -> int:
    """Least prime strictly greater than k."""
    p = k + 1
    while not _is_prime(p):
        p += 1
    return p


def _prime_factors(n: int) -> list[int]:
    out, d = [], 2
    while d * d <= n:
        if n % d == 0:
            out.append(d)
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        out.append(n)
    return out


# --- polynomials over F_q as lists, constant term first (used only to find g)
def _ptrim(a: list[int]) -> list[int]:
    while a and a[-1] == 0:
        a.pop()
    return a


def _pmulmod(a: list[int], b: list[int], g: list[int], q: int) -> list[int]:
    """a*b mod g, g monic (list of n+1 coefficients, last is 1)."""
    n = len(g) - 1
    prod = [0] * (len(a) + len(b) - 1) if a and b else []
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                prod[i + j] = (prod[i + j] + ai * bj) % q
    for k in range(len(prod) - 1, n - 1, -1):
        c = prod[k]
        if c:
            for j in range(n + 1):
                prod[k - n + j] = (prod[k - n + j] - c * g[j]) % q
    return _ptrim(prod[:n])


def _ppowmod(base: list[int], e: int, g: list[int], q: int) -> list[int]:
    result = [1]
    b = _pmulmod(base, [1], g, q) if len(g) > 2 else _ptrim([base[0] % q] if base else [])
    while e:
        if e & 1:
            result = _pmulmod(result, b, g, q)
        e >>= 1
        if e:
            b = _pmulmod(b, b, g, q)
    return result


def _pgcd(a: list[int], b: list[int], q: int) -> list[int]:
    a, b = _ptrim(list(a)), _ptrim(list(b))
    while b:
        inv = pow(b[-1], -1, q)
        # a mod b
        while len(a) >= len(b) and a:
            c = a[-1] * inv % q
            sh = len(a) - len(b)
            for j in range(len(b)):
                a[sh + j] = (a[sh + j] - c * b[j]) % q
            _ptrim(a)
        a, b = b, a
    if a:
        inv = pow(a[-1], -1, q)
        a = [x * inv % q for x in a]
    return a


def _psub(a: list[int], b: list[int], q: int) -> list[int]:
    n = max(len(a), len(b))
    out = [((a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)) % q for i in range(n)]
    return _ptrim(out)


def is_irreducible_monic(coeffs: tuple[int, ...], q: int) -> bool:
    """Rabin test for the monic polynomial t^n + sum coeffs[i] t^i over F_q (q prime)."""
    n = len(coeffs)
    if n == 1:
        return True
    g = list(coeffs) + [1]
    if coeffs[0] == 0:
        return False
    x = [0, 1]
    xq_n = _ppowmod(x, q ** n, g, q)
    if xq_n != x:
        return False
    for p in _prime_factors(n):
        h = _ppowmod(x, q ** (n // p), g, q)
        d = _pgcd(g, _psub(h, x, q), q)
        if len(d) != 1:
            return False
    return True


def least_irreducible(q: int, n: int) -> tuple[int, ...]:
    """Lexicographically least monic irreducible of degree n over F_q, as (c0..c_{n-1})."""
    if n == 1:
        return (0,)
    for coeffs in itertools.product(range(q), repeat=n):
        if is_irreducible_monic(coeffs, q):
            return tuple(coeffs)
    raise RuntimeError("no irreducible polynomial found")  # pragma: no cover


# ----------------------------------------------------------------------------- the field
class FQ:
    """F_Q = F_q[t]/(g), Q = q^n."""

    def __init__(self, q: int, n: int, g: tuple[int, ...] | None = None):
        if not _is_prime(q) or q < 3:
            raise ValueError("q must be an odd prime")
        self.q, self.n = q, n
        self.Q = q ** n
        self.g = tuple(g) if g is not None else least_irreducible(q, n)
        if len(self.g) != n:
            raise ValueError("g must have n coefficients (monic, leading 1 implicit)")
        self.zero = (0,) * n
        self.one = (1,) + (0,) * (n - 1)
        self._neg_g = tuple((-c) % q for c in self.g)
        # Frobenius images of the basis t^j under z -> z^q: (t^q)^j
        t = self.zero if n == 1 else ((0, 1) + (0,) * (n - 2))
        tq = self.zero if n == 1 else self.pow(t, q)
        self._frob_cols = [self.one]
        for _ in range(1, n):
            self._frob_cols.append(self.mul(self._frob_cols[-1], tq))
        self._inv_cache: dict = {}
        self._sqrt_setup = None

    # --- identity / encoding
    def __repr__(self):
        return f"FQ(q={self.q}, n={self.n}, g={self.g})"

    def from_int(self, k: int):
        return ((k % self.q),) + (0,) * (self.n - 1)

    def from_code(self, code: int):
        q = self.q
        out = []
        for _ in range(self.n):
            out.append(code % q)
            code //= q
        return tuple(out)

    def to_code(self, e) -> int:
        r = 0
        for c in reversed(e):
            r = r * self.q + c
        return r

    def is_zero(self, a) -> bool:
        return not any(a)

    def is_scalar(self, a) -> bool:
        return not any(a[1:])

    # --- ring operations
    def add(self, a, b):
        q = self.q
        return tuple((x + y) % q for x, y in zip(a, b))

    def sub(self, a, b):
        q = self.q
        return tuple((x - y) % q for x, y in zip(a, b))

    def neg(self, a):
        q = self.q
        return tuple((-x) % q for x in a)

    def smul(self, a, s: int):
        q = self.q
        return tuple((x * s) % q for x in a)

    def mul(self, a, b):
        n, q = self.n, self.q
        if n == 1:
            return ((a[0] * b[0]) % q,)
        prod = [0] * (2 * n - 1)
        for i, ai in enumerate(a):
            if ai:
                for j, bj in enumerate(b):
                    prod[i + j] += ai * bj
        for k in range(2 * n - 2, n - 1, -1):
            c = prod[k] % q
            if c:
                base = k - n
                for j in range(n):
                    prod[base + j] += c * self._neg_g[j]
        return tuple(x % q for x in prod[:n])

    def sqr(self, a):
        return self.mul(a, a)

    def pow(self, a, e: int):
        if e < 0:
            return self.pow(self.inv(a), -e)
        result, base = self.one, a
        while e:
            if e & 1:
                result = self.mul(result, base)
            e >>= 1
            if e:
                base = self.mul(base, base)
        return result

    def frobenius(self, a):
        """a^q via the precomputed table (linear over F_q)."""
        out = self.zero
        for c, col in zip(a, self._frob_cols):
            if c:
                out = self.add(out, self.smul(col, c))
        return out

    def norm(self, a):
        """Norm to F_q as a field element (constant): prod_{i<n} a^(q^i)."""
        acc, cur = a, a
        for _ in range(1, self.n):
            cur = self.frobenius(cur)
            acc = self.mul(acc, cur)
        return acc

    def inv(self, a):
        if self.is_zero(a):
            raise ZeroDivisionError("inverse of zero in F_Q")
        hit = self._inv_cache.get(a)
        if hit is not None:
            return hit
        if self.n == 1:
            r = (pow(a[0], -1, self.q),)
        else:
            conj, cur = self.one, a
            for _ in range(1, self.n):
                cur = self.frobenius(cur)
                conj = self.mul(conj, cur)
            nm = self.mul(a, conj)
            assert self.is_scalar(nm)
            r = self.smul(conj, pow(nm[0], -1, self.q))
        if len(self._inv_cache) < 200000:
            self._inv_cache[a] = r
        return r

    def inv_fermat(self, a):
        """Reference inverse a^(Q-2); used only by tests."""
        return self.pow(a, self.Q - 2)

    def div(self, a, b):
        return self.mul(a, self.inv(b))

    # --- quadratic character and square roots
    def chi(self, a) -> int:
        """Quadratic character: 0 for 0, +1 for a nonzero square, -1 otherwise."""
        if self.is_zero(a):
            return 0
        r = self.pow(a, (self.Q - 1) // 2)
        return 1 if r == self.one else -1

    def is_square(self, a) -> bool:
        return self.chi(a) >= 0

    def _tonelli_setup(self):
        if self._sqrt_setup is None:
            Q1 = self.Q - 1
            s, r = 0, Q1
            while r % 2 == 0:
                r //= 2
                s += 1
            # least nonsquare by code order
            z = None
            for code in range(1, self.Q):
                cand = self.from_code(code)
                if self.chi(cand) == -1:
                    z = cand
                    break
            self._sqrt_setup = (s, r, z)
        return self._sqrt_setup

    def nonsquare(self):
        """The least nonsquare element by code order (deterministic)."""
        return self._tonelli_setup()[2]

    def sqrt(self, a):
        """A square root of a (Tonelli-Shanks), or None if a is a nonsquare. sqrt(0) = 0.
        Of the two roots the one with the smaller code is returned (deterministic)."""
        if self.is_zero(a):
            return self.zero
        if self.chi(a) != 1:
            return None
        s, r, z = self._tonelli_setup()
        c = self.pow(z, r)
        t = self.pow(a, r)
        R = self.pow(a, (r + 1) // 2)
        m = s
        while t != self.one:
            i, tt = 0, t
            while tt != self.one:
                tt = self.mul(tt, tt)
                i += 1
            b = c
            for _ in range(m - i - 1):
                b = self.mul(b, b)
            R = self.mul(R, b)
            c = self.mul(b, b)
            t = self.mul(t, c)
            m = i
        other = self.neg(R)
        return R if self.to_code(R) <= self.to_code(other) else other

    # --- iteration
    def elements(self):
        for code in range(self.Q):
            yield self.from_code(code)

    def random_element(self, rng):
        """One element from numpy Generator rng: n integers in [0, q), constant term first."""
        return tuple(int(v) for v in rng.integers(0, self.q, size=self.n))

    # field interface used by the generic group law
    def embed(self, a):
        return a


class FQ2:
    """F_{Q^2} = F_Q[s]/(s^2 - d), d the least nonsquare of F_Q. Elements are pairs (u, v) = u + v s."""

    def __init__(self, base: FQ):
        self.base = base
        self.d = base.nonsquare()
        self.zero = (base.zero, base.zero)
        self.one = (base.one, base.zero)

    def __repr__(self):
        return f"FQ2({self.base}, d={self.d})"

    def embed(self, a):
        return (a, self.base.zero)

    def from_int(self, k):
        return (self.base.from_int(k), self.base.zero)

    def is_zero(self, a):
        return self.base.is_zero(a[0]) and self.base.is_zero(a[1])

    def add(self, a, b):
        F = self.base
        return (F.add(a[0], b[0]), F.add(a[1], b[1]))

    def sub(self, a, b):
        F = self.base
        return (F.sub(a[0], b[0]), F.sub(a[1], b[1]))

    def neg(self, a):
        F = self.base
        return (F.neg(a[0]), F.neg(a[1]))

    def mul(self, a, b):
        F = self.base
        uu = F.mul(a[0], b[0])
        vv = F.mul(a[1], b[1])
        uv = F.add(F.mul(a[0], b[1]), F.mul(a[1], b[0]))
        return (F.add(uu, F.mul(self.d, vv)), uv)

    def inv(self, a):
        F = self.base
        nm = F.sub(F.mul(a[0], a[0]), F.mul(self.d, F.mul(a[1], a[1])))
        ni = F.inv(nm)
        return (F.mul(a[0], ni), F.neg(F.mul(a[1], ni)))

    def lift_y(self, y2):
        """A square root in F_{Q^2} of y2 in F_Q: in F_Q if y2 is a square, else s*sqrt(y2/d)."""
        F = self.base
        r = F.sqrt(y2)
        if r is not None:
            return (r, F.zero)
        r = F.sqrt(F.div(y2, self.d))
        assert r is not None
        return (F.zero, r)


# ----------------------------------------------------------------------------- polynomials over F
# A polynomial is a list of field elements, constant term first, no trailing zeros (zero poly = []).
def ptrim(F, a):
    while a and F.is_zero(a[-1]):
        a.pop()
    return a


def pconst(F, c):
    return [c] if not F.is_zero(c) else []


def padd(F, a, b):
    n = max(len(a), len(b))
    out = [F.add(a[i] if i < len(a) else F.zero, b[i] if i < len(b) else F.zero) for i in range(n)]
    return ptrim(F, out)


def psub(F, a, b):
    n = max(len(a), len(b))
    out = [F.sub(a[i] if i < len(a) else F.zero, b[i] if i < len(b) else F.zero) for i in range(n)]
    return ptrim(F, out)


def pmul(F, a, b):
    if not a or not b:
        return []
    out = [F.zero] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if F.is_zero(ai):
            continue
        for j, bj in enumerate(b):
            out[i + j] = F.add(out[i + j], F.mul(ai, bj))
    return ptrim(F, out)


def pscale(F, a, c):
    return ptrim(F, [F.mul(x, c) for x in a])


def pmonic(F, a):
    if not a:
        return []
    return pscale(F, a, F.inv(a[-1]))


def pdivmod(F, a, b):
    """(quotient, remainder) of a by nonzero b."""
    a = list(a)
    ptrim(F, a)
    b = ptrim(F, list(b))
    if not b:
        raise ZeroDivisionError("polynomial division by zero")
    inv = F.inv(b[-1])
    quo = [F.zero] * max(len(a) - len(b) + 1, 0)
    while len(a) >= len(b) and a:
        c = F.mul(a[-1], inv)
        sh = len(a) - len(b)
        quo[sh] = c
        for j in range(len(b)):
            a[sh + j] = F.sub(a[sh + j], F.mul(c, b[j]))
        ptrim(F, a)
    return ptrim(F, quo), a


def pmod(F, a, b):
    return pdivmod(F, a, b)[1]


def pgcd(F, a, b):
    a, b = ptrim(F, list(a)), ptrim(F, list(b))
    while b:
        a, b = b, pmod(F, a, b)
    return pmonic(F, a)


def pderiv(F, a):
    return ptrim(F, [F.smul(a[i], i) for i in range(1, len(a))])


def peval(F, a, x):
    r = F.zero
    for c in reversed(a):
        r = F.add(F.mul(r, x), c)
    return r


def ppowmod(F, base, e, mod):
    result = [F.one]
    b = pmod(F, base, mod)
    while e:
        if e & 1:
            result = pmod(F, pmul(F, result, b), mod)
        e >>= 1
        if e:
            b = pmod(F, pmul(F, b, b), mod)
    return result


def is_squarefree(F, f):
    """f nonzero of degree >= 1 over a field of characteristic > degree: gcd(f, f') = 1."""
    f = ptrim(F, list(f))
    if len(f) < 2:
        return bool(f)
    d = pderiv(F, f)
    if not d:
        return False
    return len(pgcd(F, f, d)) == 1


def ddf(F, f):
    """Distinct-degree factorisation of a squarefree polynomial f.
    Returns [(d, product of the irreducible factors of degree d)] in increasing d (monic parts)."""
    f = pmonic(F, ptrim(F, list(f)))
    out = []
    x = [F.zero, F.one]
    h = x
    d = 0
    while len(f) - 1 >= 2 * (d + 1):
        d += 1
        h = ppowmod(F, h, F.Q, f)               # x^(Q^d) mod f
        g = pgcd(F, psub(F, h, x), f)
        if len(g) > 1:
            out.append((d, g))
            f, _ = pdivmod(F, f, g)
            h = pmod(F, h, f)
    if len(f) > 1:
        out.append((len(f) - 1, f))
    return out


def splits_completely_ddf(F, f):
    """True iff the squarefree f has only degree-1 irreducible factors, via ddf."""
    fac = ddf(F, f)
    return all(d == 1 for d, _ in fac)


def splits_completely_xq(F, f):
    """Independent test: squarefree f splits completely over F_Q iff x^Q = x mod f."""
    f = pmonic(F, ptrim(F, list(f)))
    x = [F.zero, F.one]
    return ppowmod(F, x, F.Q, f) == pmod(F, x, f)


_rng = random.Random(20261029)


def roots(F, f):
    """All roots in F_Q of f (distinct, sorted by code). Uses gcd with x^Q - x and Cantor-Zassenhaus
    splitting with a fixed-seed PRNG (the root set does not depend on the randomness)."""
    f = ptrim(F, list(f))
    if len(f) < 2:
        return []
    x = [F.zero, F.one]
    xq = ppowmod(F, x, F.Q, f)
    g = pgcd(F, psub(F, xq, x), f)           # product of distinct linear factors
    out = []

    def split(h):
        if len(h) == 2:
            out.append(F.neg(h[0]))     # monic linear: t + c0 -> root -c0
            return
        if len(h) == 1:
            return
        while True:
            delta = F.from_code(_rng.randrange(F.Q))
            lin = [delta, F.one]
            e = ppowmod(F, lin, (F.Q - 1) // 2, h)
            w = pgcd(F, psub(F, e, [F.one]), h)
            if 1 < len(w) < len(h):
                split(w)
                split(pdivmod(F, h, w)[0])
                return

    if len(g) > 1:
        split(pmonic(F, g))
    return sorted(set(out), key=F.to_code)


def interpolation_basis(F, pts):
    """Monomial coefficients of the Lagrange basis polynomials for the distinct points pts."""
    basis = []
    for k, yk in enumerate(pts):
        num = [F.one]
        den = F.one
        for j, yj in enumerate(pts):
            if j != k:
                num = pmul(F, num, [F.neg(yj), F.one])
                den = F.mul(den, F.sub(yk, yj))
        basis.append(pscale(F, num, F.inv(den)))
    return basis
