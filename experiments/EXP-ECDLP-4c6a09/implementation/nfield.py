"""Number-field toolkit for the SNFS-G lifting contracts. Pure Python 3 stdlib.

K = Q[t]/(g) for a monic irreducible g in Z[t] of degree d (d = 1 gives Q).
Elements are tuples of d Fractions (coefficients on 1, t, ..., t^(d-1)).

Provides: exact ring arithmetic, discriminant (resultant), roots of g modulo a
prime (Cantor-Zassenhaus), complete-splitting test, embeddings into F_p at the
roots, a Legendre-symbol square test through several completely split
auxiliary primes, an exact square root in K (Hensel lift at one split prime,
Vandermonde recovery, rational reconstruction, exact verification), an
irreducibility test (distinct-degree factorisation modulo primes), Gaussian-
period defining polynomials for the subfields of Q(zeta_c), and a seeded search
for random fields of given degree in which a given prime splits completely.
Byte-identical copies live in every SNFS-G implementation directory.
"""
from __future__ import annotations

import math
import random
from fractions import Fraction

# ----------------------------------------------------------------------------
# integer polynomials modulo a prime (lists, low to high)
# ----------------------------------------------------------------------------


def _trim(a):
    while a and a[-1] == 0:
        a.pop()
    return a


def pmod_mul(a, b, m, q):
    """a * b mod (m, q); m monic over Z/q, lists low->high."""
    if not a or not b:
        return []
    res = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai == 0:
            continue
        for j, bj in enumerate(b):
            res[i + j] = (res[i + j] + ai * bj) % q
    return pmod_rem(res, m, q)


def pmod_rem(a, m, q):
    a = [x % q for x in a]
    dm = len(m) - 1
    for i in range(len(a) - 1, dm - 1, -1):
        c = a[i]
        if c:
            for j in range(dm + 1):
                a[i - dm + j] = (a[i - dm + j] - c * m[j]) % q
    return _trim(a[:dm])


def pmod_pow(a, e, m, q):
    r = [1]
    a = pmod_rem(a, m, q)
    while e:
        if e & 1:
            r = pmod_mul(r, a, m, q)
        a = pmod_mul(a, a, m, q)
        e >>= 1
    return r


def pmod_gcd(a, b, q):
    a, b = _trim([x % q for x in a]), _trim([x % q for x in b])
    while b:
        a, b = b, _pdivmod(a, b, q)[1]
    if a:
        inv = pow(a[-1], -1, q)
        a = [x * inv % q for x in a]
    return a


def _pdivmod(a, b, q):
    a = _trim([x % q for x in a])
    b = _trim([x % q for x in b])
    if not b:
        raise ZeroDivisionError
    inv = pow(b[-1], -1, q)
    quo = [0] * max(0, len(a) - len(b) + 1)
    r = a[:]
    while len(r) >= len(b) and r:
        c = r[-1] * inv % q
        k = len(r) - len(b)
        quo[k] = c
        for j in range(len(b)):
            r[k + j] = (r[k + j] - c * b[j]) % q
        _trim(r)
    return quo, r


def poly_roots_mod(g, q, rng=None):
    """All distinct roots of g in F_q (Cantor-Zassenhaus on the linear part)."""
    rng = rng or random.Random(12345)
    g = [x % q for x in g]
    inv = pow(g[-1], -1, q)
    g = [x * inv % q for x in g]
    xq = pmod_pow([0, 1], q, g, q)
    h = pmod_gcd(_trim([(xq[i] if i < len(xq) else 0) - (1 if i == 1 else 0) for i in range(max(len(xq), 2))]), g, q)
    roots = []

    def split(h):
        deg = len(h) - 1
        if deg <= 0:
            return
        if deg == 1:
            roots.append((-h[0] * pow(h[1], -1, q)) % q)
            return
        if q == 2:
            for r in (0, 1):
                if sum(c * r ** i for i, c in enumerate(h)) % 2 == 0:
                    roots.append(r)
            return
        while True:
            a = [rng.randrange(q), 1]
            t = pmod_pow(a, (q - 1) // 2, h, q)
            t = _trim([(t[i] if i < len(t) else 0) - (1 if i == 0 else 0) for i in range(max(len(t), 1))])
            d1 = pmod_gcd(t, h, q)
            if 0 < len(d1) - 1 < deg:
                split(d1)
                split(_pdivmod(h, d1, q)[0])
                return

    split(h)
    return sorted(set(roots))


def ddf_pattern(g, q):
    """Degrees of the distinct-degree factorisation of squarefree g mod q (list of (degree, count))."""
    g = [x % q for x in g]
    inv = pow(g[-1], -1, q)
    f = [x * inv % q for x in g]
    if len(pmod_gcd(f, _trim([(i * c) % q for i, c in enumerate(f)][1:]), q)) > 1:
        return None  # not squarefree mod q
    out = []
    h = [0, 1]
    i = 1
    while len(f) - 1 >= 2 * i:
        h = pmod_pow(h, q, f, q)
        diff = _trim([(h[j] if j < len(h) else 0) - (1 if j == 1 else 0) for j in range(max(len(h), 2))])
        gi = pmod_gcd(diff, f, q)
        if len(gi) > 1:
            out.append((i, (len(gi) - 1) // i))
            f = _pdivmod(f, gi, q)[0]
            h = pmod_rem(h, f, q)
        i += 1
    if len(f) > 1:
        out.append((len(f) - 1, 1))
    return out


def _psub_const(a, c, q):
    """a - c (polynomials low->high) mod q."""
    a = list(a) + ([0] if not a else [])
    a[0] = (a[0] - c) % q
    return _trim(a)


def factor_mod(g, q, rng=None):
    """Monic irreducible factors of squarefree g mod q (q odd prime), as (factor, degree) pairs,
    by distinct-degree factorisation then equal-degree Cantor-Zassenhaus. None if not squarefree."""
    rng = rng or random.Random(777)
    g = [x % q for x in g]
    inv = pow(g[-1], -1, q)
    f = [x * inv % q for x in g]
    if len(pmod_gcd(f, _trim([(i * c) % q for i, c in enumerate(f)][1:]), q)) > 1:
        return None
    pieces = []  # (polynomial, degree of its irreducible factors)
    h = [0, 1]
    i = 1
    while len(f) - 1 >= 2 * i:
        h = pmod_pow(h, q, f, q)
        diff = _trim([(h[j] if j < len(h) else 0) - (1 if j == 1 else 0) for j in range(max(len(h), 2))])
        gi = pmod_gcd(diff, f, q)
        if len(gi) > 1:
            pieces.append((gi, i))
            f = _pdivmod(f, gi, q)[0]
            h = pmod_rem(h, f, q)
        i += 1
    if len(f) > 1:
        pieces.append((f, len(f) - 1))
    out = []

    def edf(h, e):
        deg = len(h) - 1
        if deg == e:
            out.append((h, e))
            return
        while True:
            a = [rng.randrange(q) for _ in range(deg)]
            if not _trim(a[:]):
                continue
            t = pmod_pow(a, (q ** e - 1) // 2, h, q)
            d1 = pmod_gcd(_psub_const(t, 1, q), h, q)
            if 0 < len(d1) - 1 < deg:
                edf(d1, e)
                edf(_pdivmod(h, d1, q)[0], e)
                return

    for piece, e in pieces:
        edf(piece, e)
    out.sort(key=lambda fe: (fe[1], fe[0]))
    return out


def _ff_inverse(a, h, e, q):
    """Inverse in F_q[t]/(h), h irreducible of degree e: a^(q^e - 2)."""
    return pmod_pow(a, q ** e - 2, h, q)


def _ff_sqrt(a, h, e, q, rng):
    """Square root of a in F_q[t]/(h) (h irreducible of degree e, q odd) by Tonelli-Shanks in the
    cyclic group of order q^e - 1; None if a is a non-residue. a != 0."""
    N = q ** e - 1
    one = [1]
    if pmod_pow(a, N // 2, h, q) != one:
        return None
    Q, s = N, 0
    while Q % 2 == 0:
        Q //= 2
        s += 1
    if s == 1:
        return pmod_pow(a, (Q + 1) // 2, h, q)
    while True:  # a non-residue z
        z = [rng.randrange(q) for _ in range(e)]
        if _trim(z[:]) and pmod_pow(z, N // 2, h, q) != one:
            break
    m = s
    c = pmod_pow(z, Q, h, q)
    t = pmod_pow(a, Q, h, q)
    r = pmod_pow(a, (Q + 1) // 2, h, q)
    while t != one:
        i, tt = 0, t
        while tt != one:
            tt = pmod_mul(tt, tt, h, q)
            i += 1
        b = pmod_pow(c, 1 << (m - i - 1), h, q)
        m = i
        c = pmod_mul(b, b, h, q)
        t = pmod_mul(t, c, h, q)
        r = pmod_mul(r, b, h, q)
    return r


def _padd(a, b, m):
    return _trim([((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)) % m for i in range(max(len(a), len(b)))])


def _psub(a, b, m):
    return _trim([((a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)) % m for i in range(max(len(a), len(b)))])


def _poly_crt(parts, factors, g, q):
    """y mod (q, g) with y = parts[j] mod factors[j]: sum_j parts[j] * M_j * (M_j^-1 mod h_j)."""
    y = []
    for (h, e), part in zip(factors, parts):
        M = _pdivmod(g, h, q)[0]
        Minv = _ff_inverse(pmod_rem(M, h, q), h, e, q)
        y = _padd(y, pmod_mul(pmod_mul(part, Minv, h, q), M, g, q), q)
    return y


def _is_prime_small(n):
    return n > 1 and all(n % k for k in range(2, int(n ** 0.5) + 1))


_IRRED_PRIMES = tuple(q for q in range(3, 400) if _is_prime_small(q)) + (
    1000003, 1000033, 1000037, 1000039, 1000081, 1000099, 1000117, 1000121, 1000133, 1000151,
    1000159, 1000171, 1000183, 1000187, 1000193, 1000199, 1000211, 1000213, 1000231, 1000249)


def is_irreducible_over_Q(g, primes=None):
    """True if g is irreducible modulo some prime in the list (sufficient); None if undecided."""
    d = len(g) - 1
    for q in (primes or _IRRED_PRIMES):
        pat = ddf_pattern(g, q)
        if pat is None:
            continue
        if pat == [(d, 1)]:
            return True
    return None


# ----------------------------------------------------------------------------
# the field K = Q[t]/(g)
# ----------------------------------------------------------------------------


class NumberField:
    def __init__(self, g):
        assert g[-1] == 1, "g must be monic"
        self.g = [int(c) for c in g]
        self.d = len(g) - 1
        self._root_cache = {}

    # --- exact arithmetic -------------------------------------------------
    def elt(self, coeffs):
        c = [Fraction(x) for x in coeffs] + [Fraction(0)] * (self.d - len(coeffs))
        return tuple(c[: self.d])

    def from_rational(self, r):
        return self.elt([Fraction(r)])

    def add(self, a, b):
        return tuple(x + y for x, y in zip(a, b))

    def sub(self, a, b):
        return tuple(x - y for x, y in zip(a, b))

    def neg(self, a):
        return tuple(-x for x in a)

    def mul(self, a, b):
        d = self.d
        if d == 1:
            return (a[0] * b[0],)
        res = [Fraction(0)] * (2 * d - 1)
        for i, ai in enumerate(a):
            if ai == 0:
                continue
            for j, bj in enumerate(b):
                if bj:
                    res[i + j] += ai * bj
        for i in range(2 * d - 2, d - 1, -1):
            c = res[i]
            if c:
                for j in range(d + 1):
                    res[i - d + j] -= c * self.g[j]
        return tuple(res[:d])

    def scalar(self, a, r):
        r = Fraction(r)
        return tuple(x * r for x in a)

    def is_zero(self, a):
        return all(x == 0 for x in a)

    def is_rational(self, a):
        return all(x == 0 for x in a[1:])

    def inv(self, a):
        """Inverse by solving the d x d linear system M_a y = 1 over Q."""
        d = self.d
        cols = []
        basis = self.elt([1])
        for i in range(d):
            ei = tuple(Fraction(1 if j == i else 0) for j in range(d))
            cols.append(self.mul(a, ei))
        M = [[cols[j][i] for j in range(d)] + [basis[i]] for i in range(d)]
        for c in range(d):
            piv = next((r for r in range(c, d) if M[r][c] != 0), None)
            if piv is None:
                raise ZeroDivisionError("not invertible")
            M[c], M[piv] = M[piv], M[c]
            pv = M[c][c]
            M[c] = [x / pv for x in M[c]]
            for r in range(d):
                if r != c and M[r][c] != 0:
                    f = M[r][c]
                    M[r] = [x - f * y for x, y in zip(M[r], M[c])]
        return tuple(M[i][d] for i in range(d))

    def div(self, a, b):
        return self.mul(a, self.inv(b))

    def height(self, a):
        """Naive logarithmic height proxy: log of max |numerator| and denominators lcm."""
        den = 1
        for x in a:
            den = den * x.denominator // math.gcd(den, x.denominator)
        num = max((abs(int(x * den)) for x in a), default=0)
        return math.log(max(num, den, 1))

    # --- discriminant ------------------------------------------------------
    def discriminant(self):
        g = self.g
        d = self.d
        if d == 1:
            return 1
        dg = [i * g[i] for i in range(1, d + 1)]
        n = 2 * d - 1
        M = [[Fraction(0)] * n for _ in range(n)]
        for r in range(d - 1):
            for j in range(d + 1):
                M[r][r + j] = Fraction(g[d - j])
        for r in range(d):
            for j in range(d):
                M[d - 1 + r][r + j] = Fraction(dg[d - 1 - j])
        det = Fraction(1)
        for c in range(n):
            piv = next((r for r in range(c, n) if M[r][c] != 0), None)
            if piv is None:
                return 0
            if piv != c:
                M[c], M[piv] = M[piv], M[c]
                det = -det
            det *= M[c][c]
            pv = M[c][c]
            for r in range(c + 1, n):
                if M[r][c] != 0:
                    f = M[r][c] / pv
                    M[r] = [x - f * y for x, y in zip(M[r], M[c])]
        res = det  # resultant(g, g') for monic g
        sign = -1 if (d * (d - 1) // 2) % 2 else 1
        return int(sign * res)

    def root_discriminant(self):
        return abs(self.discriminant()) ** (1.0 / self.d)

    # --- primes and embeddings --------------------------------------------
    def roots_mod(self, q):
        if q not in self._root_cache:
            self._root_cache[q] = poly_roots_mod(self.g, q) if self.d > 1 else [(-self.g[0]) % q]
        return self._root_cache[q]

    def splits_completely(self, q):
        return len(self.roots_mod(q)) == self.d and (self.discriminant() % q != 0)

    def embed(self, a, q, root):
        """Image of a in F_q under t -> root (denominators must be prime to q)."""
        num = 0
        pw = 1
        for x in a:
            if x:
                num = (num + x.numerator * pow(x.denominator, -1, q) * pw) % q
            pw = pw * root % q
        return num

    def embed_all(self, a, q):
        return [self.embed(a, q, r) for r in self.roots_mod(q)]

    def split_primes(self, count, start=10 ** 6, avoid=()):
        """The first `count` primes >= start (not in avoid) in which K splits completely."""
        out = []
        q = start | 1
        while len(out) < count:
            if q not in avoid and _is_prime(q) and self.splits_completely(q):
                out.append(q)
            q += 2
        return out

    def degree_one_primes(self, count, start=10 ** 6, avoid=(), max_scan=200000):
        """The first `count` primes q >= start (q not dividing disc, not in avoid) at which g has at
        least one root mod q, i.e. K has a degree-one prime above q. For a Galois K these are the
        completely split primes; for a generic K they exist with positive density at every degree."""
        out = []
        q = start | 1
        disc = self.discriminant()
        scanned = 0
        while len(out) < count and scanned < max_scan:
            scanned += 1
            if q not in avoid and _is_prime(q) and disc % q != 0 and self.roots_mod(q):
                out.append(q)
            q += 2
        return out

    def lift_primes(self, count=3, start=10 ** 6 + 7, candidates=40):
        """Primes q (not dividing disc) modulo which g has the fewest irreducible factors, among the
        first `candidates` primes >= start; cached. Used by sqrt for Hensel lifting."""
        key = ("lift", count, start, candidates)
        if key not in self._root_cache:
            disc = self.discriminant()
            found = []
            q = start | 1
            while len(found) < candidates:
                if _is_prime(q) and disc % q != 0:
                    fac = factor_mod(self.g, q) if self.d > 1 else [([(-self.g[0]) % q, 1], 1)]
                    if fac is not None:
                        found.append((len(fac), q, fac))
                q += 2
            found.sort(key=lambda t: (t[0], t[1]))
            self._root_cache[key] = [(q, fac) for _, q, fac in found[:count]]
        return self._root_cache[key]

    # --- squares and square roots ----------------------------------------
    def embeds_are_squares(self, a, q):
        for v in self.embed_all(a, q):
            if v == 0:
                return None
            if pow(v, (q - 1) // 2, q) != 1:
                return False
        return True

    def sqrt(self, a, aux_primes=(), max_doublings=7):
        """Exact square root of a in K, or None (a not a square). Method: at a lift prime q with
        g = h_1 ... h_m mod q, take square roots in each finite field F_q[t]/(h_j) (Tonelli-Shanks;
        a non-residue anywhere proves a is not a square), combine by CRT for each of the 2^(m-1)
        sign patterns, Hensel-lift y and (2y)^-1 in (Z/q^k)[t]/(g) with k doubling, rationally
        reconstruct the coefficients and verify y^2 = a exactly. aux_primes: optional degree-one
        primes used first as a cheap residue filter."""
        if self.is_zero(a):
            return a
        for q in aux_primes:
            if self.embeds_are_squares(a, q) is False:
                return None
        den = 1
        for x in a:
            den = den * x.denominator // math.gcd(den, x.denominator)
        a_int = [int(x * den) for x in a]
        rng = random.Random(str(("nfield-sqrt", tuple(self.g), tuple(a_int), den)))
        g = self.g
        for q, factors in self.lift_primes():
            if den % q == 0:
                continue
            a_q = _trim([x * pow(den, -1, q) % q for x in a_int])
            parts = []
            for h, e in factors:
                r = pmod_rem(a_q, h, q) if a_q else []
                if not r:
                    parts = None  # a vanishes mod h: Hensel would be singular; try another prime
                    break
                sr = _ff_sqrt(r, h, e, q, rng)
                if sr is None:
                    return None
                parts.append(sr)
            if parts is None:
                continue
            m = len(parts)
            for pattern in range(1 << (m - 1)):
                signed = [parts[0]] + [(parts[j] if (pattern >> (j - 1)) & 1 == 0 else [(-c) % q for c in parts[j]])
                                      for j in range(1, m)]
                y = _poly_crt(signed, factors, g, q) if m > 1 else signed[0]
                inv_parts = [_ff_inverse(pmod_rem([2 * c % q for c in y], h, q), h, e, q) for h, e in factors]
                z = _poly_crt(inv_parts, factors, g, q) if m > 1 else inv_parts[0]
                k = 1
                for _ in range(max_doublings):
                    k *= 2
                    qk = q ** k
                    a_k = [x * pow(den, -1, qk) % qk for x in a_int]
                    # y <- y - (y^2 - a) z ; z <- z (2 - 2 y z)   (mod q^k)
                    y = _psub(y, pmod_mul(_psub(pmod_mul(y, y, g, qk), a_k, qk), z, g, qk), qk)
                    z = pmod_mul(z, _psub([2], pmod_mul([2 * c for c in y], z, g, qk), qk), g, qk)
                    cand = []
                    for i in range(self.d):
                        r = _rational_reconstruct(y[i] if i < len(y) else 0, qk)
                        if r is None:
                            break
                        cand.append(r)
                    else:
                        cand = tuple(cand)
                        if self.mul(cand, cand) == tuple(a):
                            return cand
            return None  # every sign pattern failed to reconstruct within precision: not a square
        return None


def _is_prime(n):
    if n < 2:
        return False
    for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % q == 0:
            return n == q
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def _sqrt_mod_prime(n, p):
    n %= p
    if n == 0:
        return 0
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p)
    while t != 1:
        i, tt = 0, t
        while tt != 1:
            tt = tt * tt % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, b * b % p, t * b * b % p, r * b % p
    return r


def _vandermonde_solve(xs, ys, m):
    """Solve sum_j c_j x_i^j = y_i (mod m) for c; Gaussian elimination mod m (m a prime power)."""
    n = len(xs)
    A = [[pow(x, j, m) for j in range(n)] + [y % m] for x, y in zip(xs, ys)]
    for c in range(n):
        piv = next((r for r in range(c, n) if math.gcd(A[r][c], m) == 1), None)
        if piv is None:
            return None
        A[c], A[piv] = A[piv], A[c]
        inv = pow(A[c][c], -1, m)
        A[c] = [x * inv % m for x in A[c]]
        for r in range(n):
            if r != c and A[r][c]:
                f = A[r][c]
                A[r] = [(x - f * y) % m for x, y in zip(A[r], A[c])]
    return [A[i][n] for i in range(n)]


def _rational_reconstruct(a, m):
    """Rational r = n/d with |n|, d <= sqrt(m/2) and r = a mod m, or None."""
    a %= m
    bound = math.isqrt(m // 2)
    r0, r1 = m, a
    s0, s1 = 0, 1
    while r1 > bound:
        qq = r0 // r1
        r0, r1 = r1, r0 - qq * r1
        s0, s1 = s1, s0 - qq * s1
    if s1 == 0 or abs(s1) > bound:
        return None
    if s1 < 0:
        r1, s1 = -r1, -s1
    if math.gcd(r1, s1) != 1:
        return None
    return Fraction(r1, s1)


# ----------------------------------------------------------------------------
# subfields of Q(zeta_c) by Gaussian periods, and random split fields
# ----------------------------------------------------------------------------


def _cyclo_mul(a, b, c):
    """Multiply in Z[x]/(Phi_c), c prime, using x^c = 1 then reducing by 1 + x + ... + x^(c-1)."""
    res = [0] * c
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                if bj:
                    res[(i + j) % c] += ai * bj
    # normal form: subtract res[c-1] * (1 + x + ... + x^(c-1))
    t = res[c - 1]
    return [v - t for v in res[: c - 1]] + [0] * 0


def gaussian_period_polynomial(c, d):
    """Monic defining polynomial of the degree-d subfield of Q(zeta_c), c prime, d | c - 1."""
    assert (c - 1) % d == 0
    # primitive root mod c
    def order(a):
        k, v = 1, a % c
        while v != 1:
            v = v * a % c
            k += 1
        return k
    gen = next(a for a in range(2, c) if order(a) == c - 1)
    f = (c - 1) // d
    # H = <gen^d>, cosets gen^j H for j in 0..d-1
    periods = []
    for j in range(d):
        vec = [0] * (c - 1)
        for i in range(f):
            e = pow(gen, j + d * i, c)
            if e == c - 1:
                # x^(c-1) = -(1 + x + ... + x^(c-2))
                for k in range(c - 1):
                    vec[k] -= 1
            else:
                vec[e] += 1
        periods.append(vec + [0])  # length c for _cyclo_mul
    # expand prod (X - eta_j) with coefficients in Z[zeta]
    poly = [[1] + [0] * (c - 1)]  # list of coefficient vectors (length c), low -> high in X
    for eta in periods:
        neg_eta = [-v for v in eta]
        new = [[0] * c for _ in range(len(poly) + 1)]
        for i, coef in enumerate(poly):
            # coef * X^(i+1)
            for k in range(c):
                new[i + 1][k] += coef[k]
            prod = _cyclo_mul(coef, neg_eta, c)
            for k in range(c - 1):
                new[i][k] += prod[k]
        poly = new
    out = []
    for coef in poly:
        assert all(v == 0 for v in coef[1:c - 1]), "period polynomial coefficient not rational"
        out.append(coef[0])
    assert out[-1] == 1
    return out


def random_split_field(d, p, seed, coeff_bound=3, tries=20000, target_rootdisc=None):
    """Seeded search for monic irreducible g of degree d, coefficients in [-B, B], with p splitting
    completely; returns the candidate whose root discriminant is closest to target (if given)."""
    rng = random.Random(f"nfield:split:{d}:{p}:{seed}")
    best = None
    found = 0
    for _ in range(tries):
        g = [rng.randint(-coeff_bound, coeff_bound) for _ in range(d)] + [1]
        if g[0] == 0:
            continue
        K = NumberField(g)
        if K.discriminant() == 0 or not K.splits_completely(p):
            continue
        if is_irreducible_over_Q(g) is not True:
            continue
        found += 1
        rd = K.root_discriminant()
        key = abs(math.log(rd) - math.log(target_rootdisc)) if target_rootdisc else 0.0
        if best is None or key < best[0]:
            best = (key, g, rd)
        if target_rootdisc is None or found >= 40:
            break
    return None if best is None else {"g": best[1], "root_discriminant": best[2]}
