#!/usr/bin/env python3
"""EXP-QSP-33b442 core arithmetic: GF(2)[X], F_{2^n}, K[Y], factorisation,
root extraction and the three counting instruments I1 / I2 / I3.

PROVENANCE.  The bit-packed GF(2)[X] primitives in the first section
(`deg`, `clmul`, `square`, `polymod`, `polymod_sparse_tail`, `gcd`,
`polydivmod`, `compose`, `iterate`, `frob_power_mod`,
`frob_power_mod_sparse`, `is_irreducible`, `is_linearized`,
`polys_of_degree`, `poly_str`, the `IRRED` table, `fmul`, `fpow2k`,
`feval_f2poly`, `feval_kpoly`) are ADAPTED, with edits, from
analysis/qsp-ecc2k130/explore/qsp_explore.py (the out-of-harness
pre-compute audit of 2026-09-17, which is CONTEXT, not evidence).  No
number, table or JSON value from that directory is read by this module or
by any script in this package.

Everything below that section -- the general F_2 factorisation
(`ddf_factor`), the K[Y] layer (`KField`, `kp_*`, `kp_roots`), the
explicit-K-root machinery (`f2_factor_roots_in_K`), the three instruments
(`i1_brute_f2`, `i1_brute_k`, `i2_gcd_f2`, `i2_gcd_k`, `i3_injection_f2`,
`i3_injection_k`), the twisted iterate `Lambda_{k+1} = Lambda_k^{(n')} o
lambda` over K, the independent certificate re-verifier (`verify_roots`)
and the Proposition-2 linearized decision procedure (`c6_linearized_N`)
-- is written for this experiment.

Convention: a polynomial over F_2 is a Python int, bit i = coefficient of
X^i.  A polynomial over K is a list of K elements, index i = coefficient
of Y^i, no trailing zeros.  A K element is a Python int, bit i =
coefficient of z^i, reduced modulo the declared field polynomial.
"""
from __future__ import annotations

import random

# ---------------------------------------------------------------------------
# F_2[X] on bit-packed ints  (adapted from qsp_explore.py)
# ---------------------------------------------------------------------------


def deg(a: int) -> int:
    return a.bit_length() - 1


def clmul(a: int, b: int) -> int:
    """Carry-less product; loops over the set bits of the sparser operand."""
    if a.bit_count() > b.bit_count():
        a, b = b, a
    r = 0
    if a and a.bit_count() > 1:
        a ^= 1 << (a.bit_length() - 1)
    while a:
        low = a & -a
        r ^= b << (low.bit_length() - 1)
        a ^= low
    return r


_SPREAD_MASKS: dict[int, list[tuple[int, int]]] = {}


def square(a: int) -> int:
    """a(X)^2 = a(X^2) over F_2: spread the bits with zeros in between."""
    if a == 0:
        return 0
    nbits = a.bit_length()
    w = 1
    while w < nbits:
        w <<= 1
    if w not in _SPREAD_MASKS:
        masks = []
        s = w
        while s >= 1:
            block = (1 << s) - 1
            m = 0
            for i in range(0, 2 * w, 2 * s):
                m |= block << i
            masks.append((s, m))
            s >>= 1
        _SPREAD_MASKS[w] = masks
    x = a
    for s, m in _SPREAD_MASKS[w]:
        if s == w:
            continue
        x = (x | (x << s)) & m
    return x


def polymod(a: int, m: int) -> int:
    dm = deg(m)
    while a and deg(a) >= dm:
        a ^= m << (deg(a) - dm)
    return a


def polymod_sparse_tail(a: int, np2: int, lam: int) -> int:
    """Reduce a modulo L = X^{np2} + lam(X), deg lam < np2, by X^{np2} -> lam."""
    mask = (1 << np2) - 1
    while a >> np2:
        high = a >> np2
        a = (a & mask) ^ clmul(high, lam)
    return a


def gcd(a: int, b: int) -> int:
    while b:
        a = polymod(a, b)
        a, b = b, a
    return a


def polydivmod(a: int, m: int) -> tuple[int, int]:
    q = 0
    dm = deg(m)
    while a and deg(a) >= dm:
        s = deg(a) - dm
        q |= 1 << s
        a ^= m << s
    return q, a


def compose(f: int, g: int) -> int:
    """f(g(X)) over F_2 by Horner."""
    r = 0
    for i in range(deg(f), -1, -1):
        r = clmul(r, g)
        if (f >> i) & 1:
            r ^= 1
    return r


def iterate(lam: int, k: int) -> int:
    """lambda^{o k}(X); iterate(lam, 0) = X."""
    r = 0b10
    for _ in range(k):
        r = compose(lam, r)
    return r


def frob_power_mod(k: int, m: int) -> int:
    """X^(2^k) mod m, dense reduction."""
    x = 0b10
    for _ in range(k):
        x = polymod(square(x), m)
    return x


def frob_power_mod_sparse(k: int, np2: int, lam: int) -> int:
    x = 0b10
    for _ in range(k):
        x = polymod_sparse_tail(square(x), np2, lam)
    return x


def is_irreducible(f: int) -> bool:
    n = deg(f)
    x = 0b10
    xp = x
    for _ in range(1, n // 2 + 1):
        xp = polymod(square(xp), f)
        if gcd(f, xp ^ x) != 1:
            return False
    return True


def is_linearized(lam: int) -> bool:
    """True iff every exponent with a nonzero coefficient is a power of 2
    (2^0 = 1 included); a constant term X^0 is NOT a power-of-two exponent,
    so affine polynomials are not linearized."""
    i = 0
    l = lam
    while l:
        if l & 1 and (i == 0 or (i & (i - 1)) != 0):
            return False
        l >>= 1
        i += 1
    return True


def is_affine(lam: int) -> bool:
    """lambda = (linearized) + constant, with a nonzero constant term."""
    return bool(lam & 1) and is_linearized(lam ^ 1)


def polys_of_degree(d: int):
    for low in range(1 << d):
        yield (1 << d) | low


def poly_str(p: int) -> str:
    if p == 0:
        return "0"
    terms = [("X^%d" % i if i > 1 else ("X" if i == 1 else "1"))
             for i in range(deg(p), -1, -1) if (p >> i) & 1]
    return " + ".join(terms)


def tpoly_str(p: int) -> str:
    if p == 0:
        return "0"
    terms = [("T^%d" % i if i > 1 else ("T" if i == 1 else "1"))
             for i in range(deg(p), -1, -1) if (p >> i) & 1]
    return " + ".join(terms)


# ---------------------------------------------------------------------------
# F_2 factorisation of a squarefree product of irreducibles (written here)
# ---------------------------------------------------------------------------


def ddf_factor(g: int, n: int, rng: random.Random) -> list[int]:
    """Factor g, known squarefree with every irreducible factor of degree
    dividing n, into its irreducible factors.  Distinct-degree split by
    gcd(g, X^{2^k} - X) followed by equal-degree Cantor-Zassenhaus with the
    absolute trace.  Returns the list of irreducible factors (with
    multiplicity 1)."""
    out: list[int] = []
    rest = g
    if deg(rest) <= 0:
        return out
    for k in range(1, n + 1):
        if n % k:
            continue
        if deg(rest) <= 0:
            break
        if deg(rest) < k:
            break
        xk = frob_power_mod(k, rest) ^ 0b10
        part = rest if xk == 0 else gcd(rest, xk)
        if deg(part) <= 0:
            continue
        rest = polydivmod(rest, part)[0]
        out.extend(_edf(part, k, rng))
    assert deg(rest) <= 0, "unfactored remainder of degree %d" % deg(rest)
    return out


def _edf(f: int, k: int, rng: random.Random) -> list[int]:
    """Split f, a product of distinct irreducibles all of degree k, into them."""
    stack = [f]
    out: list[int] = []
    while stack:
        h = stack.pop()
        if deg(h) == k:
            out.append(h)
            continue
        while True:
            u = rng.getrandbits(deg(h)) | 1
            t = u
            acc = u
            for _ in range(k - 1):
                t = polymod(square(t), h)
                acc ^= t
            dd = gcd(h, acc)
            if 0 < deg(dd) < deg(h):
                stack.append(dd)
                stack.append(polydivmod(h, dd)[0])
                break
    return out


# ---------------------------------------------------------------------------
# K = F_2[z]/(f) and K[Y]  (written here)
# ---------------------------------------------------------------------------

# Irreducible field polynomials, recorded explicitly per cell in every run.
FIELD_POLY = {
    3: (1 << 3) | 0b011,                              # z^3 + z + 1
    4: (1 << 4) | 0b0011,                             # z^4 + z + 1
    7: (1 << 7) | 0b0000011,                          # z^7 + z + 1
    11: (1 << 11) | (1 << 2) | 1,                     # z^11 + z^2 + 1
    12: (1 << 12) | (1 << 6) | (1 << 4) | (1 << 1) | 1,  # z^12+z^6+z^4+z+1
    13: (1 << 13) | (1 << 4) | (1 << 3) | (1 << 1) | 1,  # z^13+z^4+z^3+z+1
    17: (1 << 17) | (1 << 3) | 1,
    19: (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1,
    23: (1 << 23) | (1 << 5) | 1,
    29: (1 << 29) | (1 << 2) | 1,
    31: (1 << 31) | (1 << 3) | 1,
    131: (1 << 131) | (1 << 13) | (1 << 2) | (1 << 1) | 1,   # ECC2K-130 field
}


def field_poly_str(n: int) -> str:
    f = FIELD_POLY[n]
    terms = [("z^%d" % i if i > 1 else ("z" if i == 1 else "1"))
             for i in range(deg(f), -1, -1) if (f >> i) & 1]
    return " + ".join(terms)


class KField:
    """K = F_2[z]/(FIELD_POLY[n]).  Elements are ints (bit i <-> z^i)."""

    def __init__(self, n: int):
        self.n = n
        self.mod = FIELD_POLY[n]
        assert deg(self.mod) == n
        assert is_irreducible(self.mod), "declared field polynomial is reducible"
        self.poly_str = field_poly_str(n)

    # -- field ops ---------------------------------------------------------
    def mul(self, a: int, b: int) -> int:
        return polymod(clmul(a, b), self.mod)

    def sq(self, a: int) -> int:
        return polymod(square(a), self.mod)

    def pow2k(self, a: int, k: int) -> int:
        for _ in range(k):
            a = polymod(square(a), self.mod)
        return a

    def inv(self, a: int) -> int:
        assert a, "inversion of zero"
        r0, r1 = self.mod, a
        s0, s1 = 0, 1
        while r1:
            q, r = polydivmod(r0, r1)
            r0, r1 = r1, r
            s0, s1 = s1, s0 ^ clmul(q, s1)
        return polymod(s0, self.mod)

    def rand(self, rng: random.Random) -> int:
        return rng.getrandbits(self.n)

    def elements(self):
        return range(1 << self.n)

    # -- evaluation --------------------------------------------------------
    def eval_f2poly(self, lam: int, x: int) -> int:
        """lambda(x) for lambda in F_2[X], x in K."""
        r = 0
        for i in range(deg(lam), -1, -1):
            r = self.mul(r, x)
            if (lam >> i) & 1:
                r ^= 1
        return r

    def eval_kpoly(self, coeffs: list[int], x: int) -> int:
        r = 0
        for c in reversed(coeffs):
            r = self.mul(r, x) ^ c
        return r

    def to_vector(self, a: int) -> list[int]:
        return [(a >> i) & 1 for i in range(self.n)]

    def elt_str(self, a: int) -> str:
        if a == 0:
            return "0"
        return " + ".join(("z^%d" % i if i > 1 else ("z" if i == 1 else "1"))
                          for i in range(deg(a), -1, -1) if (a >> i) & 1)


# ---- K[Y] polynomials as coefficient lists (low index = low degree) -------


def kp_norm(a: list[int]) -> list[int]:
    while a and a[-1] == 0:
        a.pop()
    return a


def kp_deg(a: list[int]) -> int:
    return len(a) - 1


def kp_from_f2(p: int) -> list[int]:
    return kp_norm([(p >> i) & 1 for i in range(max(p.bit_length(), 1))])


def kp_add(a: list[int], b: list[int]) -> list[int]:
    m = max(len(a), len(b))
    return kp_norm([(a[i] if i < len(a) else 0) ^ (b[i] if i < len(b) else 0)
                    for i in range(m)])


def kp_mul(K: KField, a: list[int], b: list[int]) -> list[int]:
    if not a or not b:
        return []
    r = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if not ai:
            continue
        for j, bj in enumerate(b):
            if bj:
                r[i + j] ^= K.mul(ai, bj)
    return kp_norm(r)


def kp_divmod(K: KField, a: list[int], b: list[int]) -> tuple[list[int], list[int]]:
    a = kp_norm(a[:])
    b = kp_norm(b[:])
    db = kp_deg(b)
    assert db >= 0, "division by zero polynomial"
    binv = K.inv(b[db])
    q = [0] * max(len(a) - db, 0)
    while kp_deg(kp_norm(a)) >= db and a:
        da = kp_deg(a)
        c = K.mul(a[da], binv)
        q[da - db] ^= c
        for j in range(db + 1):
            if b[j]:
                a[da - db + j] ^= K.mul(c, b[j])
        kp_norm(a)
    return kp_norm(q), kp_norm(a)


def kp_mod(K: KField, a: list[int], b: list[int]) -> list[int]:
    return kp_divmod(K, a, b)[1]


def kp_gcd(K: KField, a: list[int], b: list[int]) -> list[int]:
    a, b = a[:], b[:]
    while b:
        a, b = b, kp_mod(K, a, b)
    return kp_monic(K, a)


def kp_monic(K: KField, a: list[int]) -> list[int]:
    if not a:
        return a
    c = K.inv(a[-1])
    return [K.mul(c, x) for x in a]


def kp_sqmod(K: KField, a: list[int], m: list[int]) -> list[int]:
    """a^2 mod m over K, char 2: (sum a_i Y^i)^2 = sum a_i^2 Y^{2i}."""
    r = [0] * (2 * len(a) - 1) if a else []
    for i, ai in enumerate(a):
        if ai:
            r[2 * i] = K.sq(ai)
    return kp_mod(K, kp_norm(r), m)


def kp_frob_pow(K: KField, k: int, m: list[int]) -> list[int]:
    """Y^{2^k} mod m."""
    x = kp_mod(K, [0, 1], m)
    for _ in range(k):
        x = kp_sqmod(K, x, m)
    return x


def kp_eval(K: KField, a: list[int], x: int) -> int:
    r = 0
    for c in reversed(a):
        r = K.mul(r, x) ^ c
    return r


def kp_compose(K: KField, f: list[int], g: list[int]) -> list[int]:
    """f(g(Y)) over K by Horner."""
    r: list[int] = []
    for c in reversed(f):
        r = kp_mul(K, r, g)
        if c:
            r = kp_add(r, [c])
    return r


def kp_twist(K: KField, f: list[int], k: int) -> list[int]:
    """f^{(k)}: every coefficient raised to the 2^k-th power."""
    return [K.pow2k(c, k) for c in f]


def kp_roots(K: KField, f: list[int], rng: random.Random) -> list[int]:
    """All distinct roots of f in K.  gcd with Y^{2^n} - Y, then repeated
    trace-based equal-degree splitting down to linear factors."""
    if not f:
        raise ValueError("zero polynomial has every element as a root")
    if kp_deg(f) == 0:
        return []
    fm = kp_monic(K, f)
    xq = kp_frob_pow(K, K.n, fm)
    g = kp_gcd(K, fm, kp_add(xq, [0, 1]))
    if kp_deg(g) <= 0:
        return []
    roots: list[int] = []
    stack = [g]
    while stack:
        h = stack.pop()
        dh = kp_deg(h)
        if dh == 1:
            roots.append(K.mul(h[0], K.inv(h[1])))
            continue
        # h splits into distinct linear factors; split with the trace map
        while True:
            c = K.rand(rng)
            if c == 0:
                continue
            t = kp_mod(K, [0, c], h)
            acc = t[:]
            for _ in range(K.n - 1):
                t = kp_sqmod(K, t, h)
                acc = kp_add(acc, t)
            d = kp_gcd(K, h, acc)
            if 0 < kp_deg(d) < dh:
                stack.append(d)
                stack.append(kp_divmod(K, h, d)[0])
                break
    roots.sort()
    return roots


def f2_roots_in_K(K: KField, p: int, rng: random.Random) -> list[int]:
    """All distinct roots in K of an F_2-coefficient polynomial p."""
    return kp_roots(K, kp_from_f2(p), rng)


# ---------------------------------------------------------------------------
# Instruments
# ---------------------------------------------------------------------------


def i1_brute_f2(K: KField, lam: int, npr: int, want_roots: bool = False):
    """I1: enumerate every x in K and test x^{2^{n'}} == lambda(x)."""
    n = K.n
    size = 1 << n
    frob = _frob_table(K, npr)
    vals = _lam_table_f2(K, lam)
    cnt = 0
    roots = []
    for x in range(size):
        if frob[x] == vals[x]:
            cnt += 1
            if want_roots:
                roots.append(x)
    return (cnt, roots) if want_roots else (cnt, None)


_FROB_CACHE: dict[tuple[int, int], list[int]] = {}
_XPOW_CACHE: dict[int, list[list[int]]] = {}


def _frob_table(K: KField, npr: int) -> list[int]:
    key = (K.n, npr)
    t = _FROB_CACHE.get(key)
    if t is None:
        t = list(range(1 << K.n))
        for _ in range(npr):
            t = [polymod(square(v), K.mod) for v in t]
        _FROB_CACHE[key] = t
    return t


def _xpow_tables(K: KField, dmax: int) -> list[list[int]]:
    cur = _XPOW_CACHE.get(K.n)
    if cur is None or len(cur) <= dmax:
        size = 1 << K.n
        tabs = [[1] * size]
        tabs.append(list(range(size)))
        while len(tabs) <= dmax:
            prev = tabs[-1]
            tabs.append([polymod(clmul(prev[x], x), K.mod) for x in range(size)])
        _XPOW_CACHE[K.n] = tabs
        cur = tabs
    return cur


def _lam_table_f2(K: KField, lam: int) -> list[int]:
    d = deg(lam)
    tabs = _xpow_tables(K, max(d, 1))
    size = 1 << K.n
    out = [0] * size
    for i in range(d + 1):
        if (lam >> i) & 1:
            ti = tabs[i]
            out = [a ^ b for a, b in zip(out, ti)]
    return out


def i1_brute_k(K: KField, coeffs: list[int], npr: int):
    """I1 for lambda with coefficients in K."""
    frob = _frob_table(K, npr)
    d = kp_deg(coeffs)
    tabs = _xpow_tables(K, max(d, 1))
    size = 1 << K.n
    out = [0] * size
    for i, c in enumerate(coeffs):
        if c == 0:
            continue
        ti = tabs[i]
        if c == 1:
            out = [a ^ b for a, b in zip(out, ti)]
        else:
            out = [a ^ polymod(clmul(c, b), K.mod) for a, b in zip(out, ti)]
    return sum(1 for x in range(size) if frob[x] == out[x])


def i2_gcd_f2(n: int, npr: int, lam: int) -> int:
    """I2: deg gcd(X^{2^n} - X, L) with L = X^{2^{n'}} + lambda in F_2[X]."""
    np2 = 1 << npr
    assert deg(lam) < np2
    L = (1 << np2) ^ lam
    h = frob_power_mod_sparse(n, np2, lam) ^ 0b10
    return deg(gcd(L, h)) if h else np2


def i2_gcd_k(K: KField, npr: int, coeffs: list[int]) -> int:
    """I2 over K[X]: deg gcd(X^{2^n} - X, X^{2^{n'}} + lambda(X))."""
    np2 = 1 << npr
    assert kp_deg(coeffs) < np2
    L = coeffs[:] + [0] * (np2 - len(coeffs)) + [1]
    kp_norm(L)
    x = kp_mod(K, [0, 1], L)
    for _ in range(K.n):
        x = kp_sqmod(K, x, L)
    h = kp_add(x, [0, 1])
    if not h:
        return np2
    return kp_deg(kp_gcd(K, L, h))


def difference_poly_f2(lam: int, n: int, npr: int) -> int:
    """D(Y) = Lambda_{q+1}(Y) + Y^{2^{n'-r}} for lambda in F_2[X].
    F_2 coefficients make every twist trivial, so Lambda_{q+1} = lam^{o(q+1)}."""
    q, r = divmod(n, npr)
    return iterate(lam, q + 1) ^ (1 << (1 << (npr - r)))


def deg_D_and_degenerate(lam: int, n: int, npr: int) -> tuple[int, bool]:
    """(deg D, D == 0) for lambda in F_2[X], WITHOUT constructing D unless it
    is necessary.

    D(Y) = Lambda_{q+1}(Y) + Y^{2^{n'-r}} is the difference of a polynomial of
    degree a = d^{q+1} and a monomial of degree b = 2^{n'-r}.  If a != b the
    leading terms cannot cancel, so D != 0 and deg D = max(a, b) exactly, and
    no construction is needed -- which matters because a = d^{q+1} reaches
    8^16 = 2^48 bits in the Stage 2 cell list and cannot be built at all.
    If a == b, the common value is at most 2^{n'}, so D is cheap to build and
    is built; that is also the ONLY case in which D can vanish (the degenerate
    case needs d^{q+1} = p^{n'-r}).  The degenerate test therefore stays
    symbolic and exact.
    """
    d = deg(lam)
    q, r = divmod(n, npr)
    a = d ** (q + 1)
    b = 1 << (npr - r)
    if a != b:
        return max(a, b), False
    D = difference_poly_f2(lam, n, npr)
    return (deg(D) if D else -1), (D == 0)


def twisted_iterates_k(K: KField, coeffs: list[int], npr: int, k: int) -> list[int]:
    """Lambda_k with Lambda_1 = lambda, Lambda_{j+1} = Lambda_j^{(n')} o lambda."""
    cur = coeffs[:]
    for _ in range(k - 1):
        cur = kp_compose(K, kp_twist(K, cur, npr), coeffs)
    return cur


def difference_poly_k(K: KField, coeffs: list[int], n: int, npr: int) -> list[int]:
    q, r = divmod(n, npr)
    lam_q1 = twisted_iterates_k(K, coeffs, npr, q + 1)
    mono = [0] * (1 << (npr - r)) + [1]
    return kp_add(lam_q1, mono)


def i3_injection_f2(K: KField, lam: int, npr: int, rng: random.Random,
                    want_roots: bool = False) -> dict:
    """I3: roots of D in K taken orbit by orbit under the 2-Frobenius, each
    orbit retained iff its representative x satisfies L(x) = 0, i.e.
    x^{2^{n'}} = lambda(x).  Returns N, slack, orbit sizes, deg D."""
    n = K.n
    q, r = divmod(n, npr)
    D = difference_poly_f2(lam, n, npr)
    if D == 0:
        return {"degenerate": True, "N": None, "deg_D": None}
    h = frob_power_mod(n, D) ^ 0b10
    g = D if h == 0 else gcd(D, h)
    n_D_roots = deg(g)
    factors = ddf_factor(g, n, rng) if n_D_roots > 0 else []
    N = 0
    slack = 0
    orbits: list[int] = []
    kept_factors: list[int] = []
    for hf in factors:
        k = deg(hf)
        # work in F_2[Y]/(hf): x = Y
        xn = 0b10
        for _ in range(npr):
            xn = polymod(square(xn), hf)
        lx = polymod(compose(lam, 0b10), hf)
        if xn == lx:
            N += k
            orbits.append(k)
            kept_factors.append(hf)
        else:
            slack += k
    out = {"degenerate": False, "N": N, "slack": slack, "orbit_sizes": sorted(orbits),
           "n_orbits": len(orbits), "deg_D": deg(D), "D_roots_in_K": n_D_roots}
    if want_roots:
        roots: list[int] = []
        for hf in kept_factors:
            rs = f2_roots_in_K(K, hf, rng)
            assert len(rs) == deg(hf), "irreducible factor has %d roots, expected %d" % (len(rs), deg(hf))
            roots.append(sorted(rs))
        out["root_orbits"] = roots
    return out


def i3_injection_k(K: KField, coeffs: list[int], npr: int, rng: random.Random) -> dict:
    """I3 over K[Y]: explicit K-roots of D, then the closing test L(x) = 0."""
    n = K.n
    D = difference_poly_k(K, coeffs, n, npr)
    if not D:
        return {"degenerate": True, "N": None, "deg_D": None}
    droots = kp_roots(K, D, rng)
    kept = []
    for x in droots:
        if K.pow2k(x, npr) == kp_eval(K, coeffs, x):
            kept.append(x)
    return {"degenerate": False, "N": len(kept), "slack": len(droots) - len(kept),
            "deg_D": kp_deg(D), "D_roots_in_K": len(droots), "roots": kept}


# ---------------------------------------------------------------------------
# Independent certificate re-verification (the run wrapper)
# ---------------------------------------------------------------------------


def verify_roots_f2(K: KField, lam: int, npr: int, roots: list[int]) -> dict:
    """Independently re-verify a claimed root list: every listed x satisfies
    x^{2^{n'}} - lambda(x) = 0 in K, and the listed roots are pairwise
    distinct.  This evaluates L directly and shares no code path with the
    injection count that produced the list."""
    ok = True
    bad = []
    for x in roots:
        lhs = K.pow2k(x, npr)
        rhs = K.eval_f2poly(lam, x)
        if lhs != rhs:
            ok = False
            bad.append(x)
    distinct = len(set(roots)) == len(roots)
    return {"all_roots_verified": ok and distinct, "n_roots": len(roots),
            "pairwise_distinct": distinct, "failing_roots": bad}


def verify_roots_k(K: KField, coeffs: list[int], npr: int, roots: list[int]) -> dict:
    ok = True
    bad = []
    for x in roots:
        if K.pow2k(x, npr) != kp_eval(K, coeffs, x):
            ok = False
            bad.append(x)
    distinct = len(set(roots)) == len(roots)
    return {"all_roots_verified": ok and distinct, "n_roots": len(roots),
            "pairwise_distinct": distinct, "failing_roots": bad}


# ---------------------------------------------------------------------------
# C6: Proposition 2 of KN-LIT-4fe9d2, the independent linearized decision
# ---------------------------------------------------------------------------


def linearized_symbol(lam: int, npr: int) -> int | None:
    """For lambda linearized over F_2, L = X^{2^{n'}} + lambda is the
    linearized polynomial with symbol f(T) = T^{n'} + sum_i c_i T^i, where
    lambda = sum_i c_i X^{2^i}.  Returns f as a bit-packed F_2[T] element."""
    if not is_linearized(lam):
        return None
    f = 1 << npr
    i = 0
    l = lam
    while l:
        if l & 1:
            e = 0 if i == 0 else i.bit_length() - 1   # i = 2^e
            f ^= 1 << e
        l >>= 1
        i += 1
    return f


def c6_linearized_N(lam: int, npr: int, n: int) -> tuple[int, int, bool]:
    """Number of K-roots of a linearized L decided independently of I1/I2/I3:
    F_{2^n} is F_2[T]/(T^n - 1) as an F_2[T]-module with T acting as the
    Frobenius, so ker f(sigma) has F_2-dimension deg gcd(f, T^n - 1) and
    N = 2^{that}.  Complete splitting (N = 2^{n'}) iff f | T^n - 1, which is
    Proposition 2 of KN-LIT-4fe9d2.  Returns (N, deg gcd, splits_completely)."""
    f = linearized_symbol(lam, npr)
    assert f is not None
    g = gcd(f, (1 << n) ^ 1)
    k = deg(g)
    return (1 << k), k, (k == npr)
