"""Generic univariate polynomial arithmetic OVER AN ARBITRARY FIELD OBJECT
`F` (here always an `fieldext.FpK` instance -- F_{p^k} itself, treated as
the coefficient field of the polynomial ring F_{p^k}[Y]). This generalises
the sibling contract's plain-F_p `polymod.py` from scalar mod-p coefficients
to F_{p^k} coefficients, exactly the generalisation
`battery.N3.classification_method` / `N5.classification_method` require.

`F` must expose: zero(), one(), add(x,y), sub(x,y), mul(x,y), eq(x,y),
is_zero(x), pow(x,n), inv(x), lex_key(x). `fieldext.FpK` provides all of
these.

Polynomials are lists of field elements, ascending degree (ELEMENT 0 is
the constant term), never empty (a zero polynomial is `[F.zero()]`).
"""
from __future__ import annotations


def trim(poly, F):
    poly = list(poly)
    while len(poly) > 1 and F.is_zero(poly[-1]):
        poly.pop()
    return poly


def deg(poly, F):
    poly = trim(poly, F)
    if len(poly) == 1 and F.is_zero(poly[0]):
        return -1
    return len(poly) - 1


def add(a, b, F):
    n = max(len(a), len(b))
    out = [F.zero()] * n
    for i in range(len(a)):
        out[i] = F.add(out[i], a[i])
    for i in range(len(b)):
        out[i] = F.add(out[i], b[i])
    return trim(out, F)


def sub(a, b, F):
    return add(a, [F.neg(c) if hasattr(F, "neg") else F.sub(F.zero(), c) for c in b], F)


def mul(a, b, F):
    da, db = deg(a, F), deg(b, F)
    if da < 0 or db < 0:
        return [F.zero()]
    out = [F.zero()] * (len(a) + len(b) - 1)
    for i, ca in enumerate(a):
        if F.is_zero(ca):
            continue
        for j, cb in enumerate(b):
            out[i + j] = F.add(out[i + j], F.mul(ca, cb))
    return trim(out, F)


def divmod_poly(a, b, F):
    a = trim(list(a), F)
    b = trim(list(b), F)
    db = deg(b, F)
    if db < 0:
        raise ZeroDivisionError("division by zero polynomial")
    inv_lead = F.inv(b[db])
    rem = list(a)
    da = deg(rem, F)
    qlen = max(da - db + 1, 0)
    q = [F.zero()] * qlen
    while True:
        da = deg(rem, F)
        if da < db:
            break
        coeff = F.mul(rem[da], inv_lead)
        shift = da - db
        q[shift] = coeff
        for i, cb in enumerate(b):
            rem[shift + i] = F.sub(rem[shift + i], F.mul(coeff, cb))
        rem = trim(rem, F)
        if deg(rem, F) < 0:
            break
    return (trim(q, F) if q else [F.zero()]), trim(rem, F)


def gcd(a, b, F):
    a = trim(list(a), F)
    b = trim(list(b), F)
    while deg(b, F) >= 0:
        _, r = divmod_poly(a, b, F)
        a, b = b, r
    if deg(a, F) < 0:
        return [F.zero()]
    inv_lead = F.inv(a[deg(a, F)])
    return trim([F.mul(c, inv_lead) for c in a], F)


def mulmod(a, b, mod_poly, F):
    return divmod_poly(mul(a, b, F), mod_poly, F)[1]


def powmod_x(n: int, mod_poly, F):
    """x^n mod mod_poly, x = the ring variable Y (poly [0,1])."""
    result = [F.one()]
    base = divmod_poly([F.zero(), F.one()], mod_poly, F)[1]
    while n > 0:
        if n & 1:
            result = mulmod(result, base, mod_poly, F)
        base = mulmod(base, base, mod_poly, F)
        n >>= 1
    return result


def powmod_poly(base, n: int, mod_poly, F):
    result = [F.one()]
    b = divmod_poly(base, mod_poly, F)[1]
    while n > 0:
        if n & 1:
            result = mulmod(result, b, mod_poly, F)
        b = mulmod(b, b, mod_poly, F)
        n >>= 1
    return result


def derivative(poly, F):
    poly = trim(list(poly), F)
    if len(poly) <= 1:
        return [F.zero()]
    out = []
    for i, c in enumerate(poly):
        if i == 0:
            continue
        # i * c, integer multiple via repeated addition (i is small: <=5)
        acc = F.zero()
        for _ in range(i % F.p if hasattr(F, "p") else i):
            acc = F.add(acc, c)
        out.append(acc)
    return trim(out, F)


def is_squarefree(poly, F):
    d = derivative(poly, F)
    if deg(d, F) < 0:
        return deg(poly, F) <= 0
    g = gcd(poly, d, F)
    return deg(g, F) <= 0


def distinct_degree_shape(poly, F, q: int):
    """Distinct-degree factorization shape of a squarefree poly over the
    field F (of size q), generalising polymod.py's routine to F != F_p."""
    poly = trim(list(poly), F)
    n = deg(poly, F)
    if n <= 0:
        return []
    inv_lead = F.inv(poly[n])
    remaining = trim([F.mul(c, inv_lead) for c in poly], F)
    factors = []
    d = 1
    while deg(remaining, F) > 0 and d <= deg(remaining, F):
        xpd = powmod_x(q ** d, remaining, F)
        diff = sub(xpd, [F.zero(), F.one()], F)
        g = gcd(remaining, diff, F)
        if deg(g, F) > 0:
            factors.append((d, deg(g, F) // d))
            remaining = divmod_poly(remaining, g, F)[0]
            remaining = trim(remaining, F)
        d += 1
    if deg(remaining, F) > 0:
        factors.append((deg(remaining, F), 1))
    return sorted(factors)


def eval_poly(poly, x, F):
    result = F.zero()
    for c in reversed(poly):
        result = F.add(F.mul(result, x), c)
    return result


def full_split_roots(poly, F, q: int, rng):
    """Find ALL roots of a poly known to split completely into DISTINCT
    linear factors over the field F (size q, q odd). Cantor-Zassenhaus
    equal-degree-1 splitting via random shifts, seeded by `rng`
    (a callable producing a deterministic sequence of field elements, for
    reproducibility -- see `seed.py`). Returns a list of roots (field
    elements)."""
    def split(h):
        d = deg(h, F)
        if d <= 0:
            return []
        if d == 1:
            # h = c1*Y + c0 -> root = -c0/c1
            c0, c1 = h[0], h[1]
            return [F.mul(F.neg(c0) if hasattr(F, "neg") else F.sub(F.zero(), c0), F.inv(c1))]
        while True:
            r = next(rng)
            shifted = [F.sub(F.zero(), r), F.one()]  # (Y - r)
            t = powmod_poly(shifted, (q - 1) // 2, h, F)
            t = sub(t, [F.one()], F)
            g = gcd(h, t, F)
            gd = deg(g, F)
            if 0 < gd < d:
                h2 = divmod_poly(h, g, F)[0]
                return split(g) + split(h2)
    return split(poly)
