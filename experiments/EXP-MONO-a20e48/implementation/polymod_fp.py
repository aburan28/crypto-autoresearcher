"""Generic univariate polynomial arithmetic mod p (plain F_p coefficients),
coefficient lists low-degree-first. Self-contained port of the SAME generic
routines used by the sibling EXP-MONO-4c7479's `polymod.py` (plain scalar
polynomial-ring plumbing, not an ad hoc tower class), duplicated here rather
than imported so this contract's write scope stays self-contained. Used
ONLY for (a) Rabin's irreducibility test on m_k(x) candidates and (b) as a
building block inside `fieldext.py`'s Frobenius/exponentiation routines
where a plain-F_p polynomial ring is genuinely what is needed (the m_k(x)
search itself is over F_p[x], not over F_{p^k}).
"""
from __future__ import annotations


def trim(poly, p):
    poly = [c % p for c in poly]
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly


def deg(poly):
    poly = [c for c in poly]
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    if len(poly) == 1 and poly[0] == 0:
        return -1
    return len(poly) - 1


def add(a, b, p):
    n = max(len(a), len(b))
    out = [0] * n
    for i in range(len(a)):
        out[i] = (out[i] + a[i]) % p
    for i in range(len(b)):
        out[i] = (out[i] + b[i]) % p
    return trim(out, p)


def sub(a, b, p):
    return add(a, [(-c) % p for c in b], p)


def mul(a, b, p):
    if deg(a) < 0 or deg(b) < 0:
        return [0]
    out = [0] * (len(a) + len(b) - 1)
    for i, ca in enumerate(a):
        if ca == 0:
            continue
        for j, cb in enumerate(b):
            out[i + j] = (out[i + j] + ca * cb) % p
    return trim(out, p)


def divmod_poly(a, b, p):
    a = trim(list(a), p)
    b = trim(list(b), p)
    db = deg(b)
    if db < 0:
        raise ZeroDivisionError("division by zero polynomial")
    inv_lead = pow(b[db], -1, p)
    rem = list(a)
    da = deg(rem)
    qlen = max(da - db + 1, 0)
    q = [0] * qlen
    while True:
        da = deg(rem)
        if da < db:
            break
        coeff = (rem[da] * inv_lead) % p
        shift = da - db
        q[shift] = coeff
        for i, cb in enumerate(b):
            rem[shift + i] = (rem[shift + i] - coeff * cb) % p
        rem = trim(rem, p)
        if deg(rem) < 0:
            break
    return (trim(q, p) if q else [0]), trim(rem, p)


def gcd(a, b, p):
    a = trim(list(a), p)
    b = trim(list(b), p)
    while deg(b) >= 0:
        _, r = divmod_poly(a, b, p)
        a, b = b, r
    if deg(a) < 0:
        return [0]
    inv_lead = pow(a[deg(a)], -1, p)
    return trim([c * inv_lead % p for c in a], p)


def mulmod(a, b, mod_poly, p):
    return divmod_poly(mul(a, b, p), mod_poly, p)[1]


def powmod_x(n, mod_poly, p):
    """Compute x^n mod mod_poly, via repeated squaring."""
    result = [1]
    base = divmod_poly(trim([0, 1], p), mod_poly, p)[1]
    while n > 0:
        if n & 1:
            result = mulmod(result, base, mod_poly, p)
        base = mulmod(base, base, mod_poly, p)
        n >>= 1
    return result
