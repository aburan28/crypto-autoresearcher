"""Numpy-free F_2^n arithmetic and char-2 Weierstrass curves.

Measurement code for EXP-BINSTD-38f216 Stages 0-2. Field elements are ints
whose bits are coefficients of a polynomial basis, bit 0 the constant term.
"""

from __future__ import annotations

import math
from functools import lru_cache


def _poly_mul(a: int, b: int) -> int:
    out = 0
    while b:
        if b & 1:
            out ^= a
        b >>= 1
        a <<= 1
    return out


def _poly_divmod(a: int, b: int) -> tuple[int, int]:
    if b == 0:
        raise ZeroDivisionError("polynomial division by zero")
    deg_b = b.bit_length() - 1
    quot = 0
    while a.bit_length() - 1 >= deg_b and a:
        shift = (a.bit_length() - 1) - deg_b
        quot ^= 1 << shift
        a ^= b << shift
    return quot, a


def _poly_gcd(a: int, b: int) -> int:
    while b:
        a, b = b, _poly_divmod(a, b)[1]
    return a


def _poly_mod_mul(a: int, b: int, mod: int) -> int:
    return _poly_divmod(_poly_mul(a, b), mod)[1]


def _poly_mod_pow(base: int, exp: int, mod: int) -> int:
    out = 1
    while exp:
        if exp & 1:
            out = _poly_mod_mul(out, base, mod)
        base = _poly_mod_mul(base, base, mod)
        exp >>= 1
    return out


def is_irreducible(mod: int, n: int) -> bool:
    """Rabin test: x^{2^n} == x (mod mod) and gcd(x^{2^{n/p}} - x, mod) == 1."""
    if mod.bit_length() - 1 != n or n < 1:
        return False
    x_pow = 2  # the polynomial x
    for _ in range(n):
        x_pow = _poly_mod_mul(x_pow, x_pow, mod)
    if x_pow != 2:
        return False
    primes = []
    m = n
    p = 2
    while p * p <= m:
        if m % p == 0:
            primes.append(p)
            while m % p == 0:
                m //= p
        p += 1 if p == 2 else 2
    if m > 1:
        primes.append(m)
    for p in primes:
        xp = 2
        for _ in range(n // p):
            xp = _poly_mod_mul(xp, xp, mod)
        if _poly_gcd(xp ^ 2, mod) != 1:
            return False
    return True


def lowest_irreducible(n: int) -> int:
    """Least odd integer of degree n that is irreducible over F_2 (const term 1)."""
    if n == 17:
        return (1 << 17) | (1 << 3) | 1  # t^17 + t^3 + 1, frozen by the contract
    start = (1 << n) | 1
    end = (1 << (n + 1)) | 1
    for mod in range(start, end, 2):
        if is_irreducible(mod, n):
            return mod
    raise RuntimeError(f"no irreducible of degree {n}")


def _factorize(n: int) -> list[int]:
    factors = []
    p = 2
    while p * p <= n:
        if n % p == 0:
            factors.append(p)
            while n % p == 0:
                n //= p
        p += 1 if p == 2 else 2
    if n > 1:
        factors.append(n)
    return factors


class Field:
    def __init__(self, n: int, modulus: int | None = None):
        self.n = n
        self.q = 1 << n
        self.modulus = lowest_irreducible(n) if modulus is None else modulus
        if self.modulus.bit_length() - 1 != n:
            raise ValueError("modulus degree does not match n")
        self._exp: list[int] = []
        self._log = [0] * self.q
        self._build_log_table()
        self._trace_mask = self._build_trace_mask()
        self._quad_sol = self._build_quad_solutions()

    def _build_log_table(self) -> None:
        q = self.q
        order = q - 1
        primes = _factorize(order)
        gen = None
        for g in range(2, q):
            ok = True
            for p in primes:
                if self._pow_raw(g, order // p) == 1:
                    ok = False
                    break
            if ok:
                gen = g
                break
        if gen is None:
            raise RuntimeError(f"no primitive element in F_2^{self.n}")
        self.generator = gen
        exp = [1] * order
        self._log[0] = -1
        self._log[1] = 0
        x = 1
        for i in range(1, order):
            x = _poly_mod_mul(x, gen, self.modulus)
            exp[i] = x
            self._log[x] = i
        self._exp = exp

    def _pow_raw(self, base: int, exp: int) -> int:
        return _poly_mod_pow(base, exp, self.modulus)

    def _build_trace_mask(self) -> int:
        mask = 0
        for i in range(self.n):
            if self.trace_define(1 << i) == 1:
                mask |= 1 << i
        return mask

    def trace_define(self, x: int) -> int:
        if x == 0:
            return 0
        acc = 0
        y = x
        for _ in range(self.n):
            acc ^= y
            y = self.square(y) if self._exp else _poly_mod_mul(y, y, self.modulus)
        return acc & 1

    def _build_quad_solutions(self) -> dict[int, int]:
        """One root of z^2 + z = rhs, keyed by rhs, built by enumerating z."""
        sol: dict[int, int] = {}
        q = self.q
        for z in range(q):
            rhs = self.square(z) ^ z
            if rhs not in sol:
                sol[rhs] = z
        return sol

    def add(self, a: int, b: int) -> int:
        return a ^ b

    def square(self, a: int) -> int:
        if a == 0:
            return 0
        return self._exp[(2 * self._log[a]) % (self.q - 1)]

    def mul(self, a: int, b: int) -> int:
        if a == 0 or b == 0:
            return 0
        return self._exp[(self._log[a] + self._log[b]) % (self.q - 1)]

    def inv(self, a: int) -> int:
        if a == 0:
            raise ZeroDivisionError("field inversion of 0")
        return self._exp[(-(self._log[a])) % (self.q - 1)]

    def pow(self, a: int, exp: int) -> int:
        if exp == 0:
            return 1
        if a == 0:
            return 0
        return self._exp[(self._log[a] * exp) % (self.q - 1)]

    def sqrt(self, a: int) -> int:
        return self.pow(a, 1 << (self.n - 1))

    def fourth_root(self, a: int) -> int:
        """Unique solution of y^4 = a. x |-> x^4 is bijective in char 2."""
        return self.pow(a, 1 << (self.n - 2))

    def trace(self, a: int) -> int:
        # parity of bits set in a & trace_mask
        return ((a & self._trace_mask).bit_count()) & 1

    def frobenius(self, a: int, k: int = 1) -> int:
        if a == 0:
            return 0
        shift = (1 << k) % (self.q - 1) if k else 1
        # 2^k mod (q-1). For k < n, 2^k < q-1 when n > 1 and k < n, except k=n.
        e = self._log[a] * ((1 << k) % (self.q - 1))
        return self._exp[e % (self.q - 1)]

    def in_subfield(self, a: int, d: int) -> bool:
        return self.frobenius(a, d) == a

    def subfield_elements(self, d: int) -> list[int]:
        if self.n % d != 0:
            raise ValueError("d must divide n")
        # Generator of F_{2^d}^*: g^{(q-1)/(2^d-1)} has order 2^d-1.
        if d == 0:
            return [0]
        step = (self.q - 1) // ((1 << d) - 1)
        elems = [0, 1]
        if (1 << d) == 2:
            return elems
        g = self._exp[step]
        x = g
        while x != 1:
            elems.append(x)
            x = self.mul(x, g)
        return elems

    def divisors(self) -> list[int]:
        out = []
        for d in range(1, self.n + 1):
            if self.n % d == 0:
                out.append(d)
        return out

    def poly_str(self, a: int) -> str:
        if a == 0:
            return "0"
        terms = []
        for i in range(a.bit_length()):
            if (a >> i) & 1:
                if i == 0:
                    terms.append("1")
                elif i == 1:
                    terms.append("t")
                else:
                    terms.append(f"t^{i}")
        return " + ".join(reversed(terms))

    def modulus_str(self) -> str:
        return self.poly_str(self.modulus)


def rank_rows(rows: list[int]) -> int:
    pivots: dict[int, int] = {}
    for v in rows:
        x = v
        for p in sorted(pivots, reverse=True):
            if (x >> p) & 1:
                x ^= pivots[p]
        if x == 0:
            continue
        p = x.bit_length() - 1
        for q, row in list(pivots.items()):
            if (row >> p) & 1:
                pivots[q] = row ^ x
        pivots[p] = x
    return len(pivots)


def rref_basis(vectors: list[int]) -> tuple[int, ...]:
    pivots: dict[int, int] = {}
    for v in vectors:
        x = v
        for p in sorted(pivots, reverse=True):
            if (x >> p) & 1:
                x ^= pivots[p]
        if x == 0:
            continue
        p = x.bit_length() - 1
        for q, row in list(pivots.items()):
            if (row >> p) & 1:
                pivots[q] = row ^ x
        pivots[p] = x
    return tuple(pivots[p] for p in sorted(pivots))


def span_elements(basis: tuple[int, ...] | list[int]) -> list[int]:
    elems = [0]
    for b in basis:
        elems.extend([e ^ b for e in elems])
    return elems


def gaussian_binomial(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    num = 1
    den = 1
    for i in range(k):
        num *= (1 << n) - (1 << i)
        den *= (1 << k) - (1 << i)
    return num // den


def iter_rref_bases(dim: int, k: int):
    """Unique RREF bases of k-dimensional subspaces of an dim-bit F_2-space."""
    if k == 0:
        yield tuple()
        return
    if k > dim or k < 0:
        return
    # combinations of pivot columns without itertools in the hot path
    pivots = list(range(k))

    def emit(pivots: list[int]):
        pset = set(pivots)
        free: list[tuple[int, int]] = []
        for i, p in enumerate(pivots):
            for j in range(p + 1, dim):
                if j not in pset:
                    free.append((i, j))
        nfree = len(free)
        rows0 = [1 << pivots[i] for i in range(k)]
        for mask in range(1 << nfree):
            rows = rows0[:]
            bits = mask
            for i, j in free:
                if bits & 1:
                    rows[i] |= 1 << j
                bits >>= 1
            yield tuple(rows)

    while True:
        yield from emit(pivots)
        # next combination
        i = k - 1
        while i >= 0 and pivots[i] == dim - k + i:
            i -= 1
        if i < 0:
            break
        pivots[i] += 1
        for j in range(i + 1, k):
            pivots[j] = pivots[j - 1] + 1


def complete_basis(n: int, beta: int) -> list[int]:
    basis = [beta]
    for i in range(n):
        v = 1 << i
        if rank_rows(basis + [v]) == len(basis) + 1:
            basis.append(v)
        if len(basis) == n:
            break
    if len(basis) != n:
        raise RuntimeError("failed to complete a basis")
    return basis


def lift_quotient_basis(quotient_rows: tuple[int, ...], full_basis: list[int]) -> tuple[int, ...]:
    basis = [full_basis[0]]
    nq = len(full_basis) - 1
    for qrow in quotient_rows:
        v = 0
        for j in range(nq):
            if (qrow >> j) & 1:
                v ^= full_basis[j + 1]
        basis.append(v)
    return tuple(basis)


class Curve:
    """y^2 + x y = x^3 + a x^2 + b over Field."""

    def __init__(self, field: Field, a: int, b: int):
        if b == 0:
            raise ValueError("b = 0 is excluded by the contract")
        self.field = field
        self.a = a
        self.b = b
        self.sqrt_b = field.sqrt(b)
        self.fourth_b = field.fourth_root(b)
        self._order: int | None = None
        self._order_method2: int | None = None

    def iota(self, x: int) -> int:
        if x == 0:
            raise ValueError("iota is defined on F^*")
        return self.field.mul(self.sqrt_b, self.field.inv(x))

    def u_coord(self, x: int) -> int:
        if x == 0:
            raise ValueError("u undefined at 0")
        return x ^ self.iota(x)

    def rhs_trace(self, x: int) -> int:
        """Tr(x + a + b/x^2) for x != 0. Point existence criterion."""
        f = self.field
        return f.trace(x ^ self.a ^ f.mul(self.b, f.inv(f.square(x))))

    def points_at_x(self, x: int) -> list[tuple[int, int]]:
        f = self.field
        if x == 0:
            return [(0, self.sqrt_b)]
        rhs = x ^ self.a ^ f.mul(self.b, f.inv(f.square(x)))
        z = f._quad_sol.get(rhs)
        if z is None:
            return []
        y1 = f.mul(x, z)
        y2 = f.mul(x, z ^ 1)
        return [(x, y1), (x, y2)]

    def on_curve(self, pt: tuple[int, int] | None) -> bool:
        if pt is None:
            return True
        x, y = pt
        f = self.field
        left = f.square(y) ^ f.mul(x, y)
        right = f.mul(f.square(x), x) ^ f.mul(self.a, f.square(x)) ^ self.b
        return left == right

    def negate(self, pt: tuple[int, int] | None) -> tuple[int, int] | None:
        if pt is None:
            return None
        x, y = pt
        return (x, x ^ y)

    def add(self, p: tuple[int, int] | None, q: tuple[int, int] | None) -> tuple[int, int] | None:
        if p is None:
            return q
        if q is None:
            return p
        f = self.field
        x1, y1 = p
        x2, y2 = q
        if x1 == x2:
            if y1 != y2:
                return None
            if x1 == 0:
                return None  # 2-torsion
            lam = x1 ^ f.mul(y1, f.inv(x1))
            x3 = f.square(lam) ^ lam ^ self.a
            y3 = f.square(x1) ^ f.mul(lam ^ 1, x3)
            return (x3, y3)
        lam = f.mul(y1 ^ y2, f.inv(x1 ^ x2))
        x3 = f.square(lam) ^ lam ^ x1 ^ x2 ^ self.a
        y3 = f.mul(lam, x1 ^ x3) ^ x3 ^ y1
        return (x3, y3)

    def mul_scalar(self, k: int, pt: tuple[int, int] | None) -> tuple[int, int] | None:
        if pt is None or k == 0:
            return None
        if k < 0:
            raise ValueError("negative scalar")
        result = None
        addend = pt
        while k:
            if k & 1:
                result = self.add(result, addend)
            addend = self.add(addend, addend)
            k >>= 1
        return result

    def count_points(self) -> tuple[int, int]:
        """Return (#E, #E via the z^2+z image). Includes the point at infinity."""
        f = self.field
        n_aff_trace = 0
        n_aff_image = 0
        for x in range(f.q):
            if x == 0:
                n_aff_trace += 1
                n_aff_image += 1
                continue
            rhs = x ^ self.a ^ f.mul(self.b, f.inv(f.square(x)))
            if f.trace(rhs) == 0:
                n_aff_trace += 2
            if rhs in f._quad_sol:
                n_aff_image += 2
        self._order = n_aff_trace + 1
        self._order_method2 = n_aff_image + 1
        return self._order, self._order_method2

    def order(self) -> int:
        if self._order is None:
            self.count_points()
        assert self._order is not None
        return self._order


def rho_group_ops(r: int, k: float) -> float:
    """Modeled van Oorschot–Wiener / Pollard rho closed form sqrt(pi r / (4k))."""
    return math.sqrt(math.pi * r / (4.0 * k))
