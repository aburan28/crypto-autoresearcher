"""Generic univariate polynomial arithmetic mod p, coefficient lists
low-degree-first. Used by arm_b.py's distinct-degree factorization AND by
the random-quartic null control (which is REQUIRED to reuse "the SAME arm
(b) code path", per the frozen contract). Contains no notion of t1, t2,
c1, c0, e1, or e2 -- it is generic polynomial plumbing, imported by arm_b
only (never by arm_a).
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
    """Polynomial division a = q*b + r mod p. b must be non-zero."""
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
    return trim(q, p) if q else [0], trim(rem, p)


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


def is_squarefree(poly, p):
    d = derivative(poly, p)
    if deg(d) < 0:
        return deg(poly) <= 0
    g = gcd(poly, d, p)
    return deg(g) <= 0


def derivative(poly, p):
    if len(poly) <= 1:
        return [0]
    out = [(i * c) % p for i, c in enumerate(poly)][1:]
    return trim(out, p)


def distinct_degree_factorization_shape(poly, p):
    """Distinct-degree factorization of a squarefree poly over F_p.

    Returns a sorted list of (degree, multiplicity) pairs describing the
    degrees of the irreducible factors present (multiplicity = how many
    irreducible factors of that degree), e.g. a quartic with two distinct
    roots and one irreducible quadratic factor -> [(1,2),(2,1)].
    """
    poly = trim(list(poly), p)
    n = deg(poly)
    if n <= 0:
        return []
    remaining = [c for c in poly]
    inv_lead = pow(remaining[deg(remaining)], -1, p)
    remaining = trim([c * inv_lead % p for c in remaining], p)
    factors = []
    d = 1
    while deg(remaining) > 0 and d <= deg(remaining):
        xpd = powmod_x(p ** d, remaining, p)
        diff = sub(xpd, trim([0, 1], p), p)
        g = gcd(remaining, diff, p)
        if deg(g) > 0:
            factors.append((d, deg(g) // d))
            remaining = divmod_poly(remaining, g, p)[0]
            remaining = trim(remaining, p)
        d += 1
    if deg(remaining) > 0:
        factors.append((deg(remaining), 1))
    return sorted(factors)


def shape_to_partition_label(factors) -> str:
    """Map the distinct-degree factorization shape of a QUARTIC to the
    five-class partition vocabulary (1^4, 2.1.1, 2^2, 3+1, 4)."""
    degrees = []
    for d, mult in factors:
        degrees.extend([d] * mult)
    degrees.sort()
    if degrees == [1, 1, 1, 1]:
        return "1^4"
    if degrees == [1, 1, 2]:
        return "2.1.1"
    if degrees == [2, 2]:
        return "2^2"
    if degrees == [1, 3]:
        return "3+1"
    if degrees == [4]:
        return "4"
    return f"other:{degrees}"
