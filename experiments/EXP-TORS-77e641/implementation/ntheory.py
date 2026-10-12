"""Division polynomials and factor counts for EXP-TORS-77e641.

The odd-index recurrence is the one in
experiments/EXP-ECTD-001/driver/divpoly.py, which this design session
read on 2026-10-06. Polynomials are coefficient lists, index = power.
This module does not choose a reading row.
"""

from __future__ import annotations


def trim(poly, p):
    poly = [c % p for c in poly]
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly


def deg(poly):
    if not poly:
        return -1
    i = len(poly) - 1
    while i > 0 and poly[i] == 0:
        i -= 1
    if i == 0 and poly[0] == 0:
        return -1
    return i


def padd(f, g, p):
    n = max(len(f), len(g))
    out = [0] * n
    for i, c in enumerate(f):
        out[i] = (out[i] + c) % p
    for i, c in enumerate(g):
        out[i] = (out[i] + c) % p
    return trim(out, p)


def psub(f, g, p):
    n = max(len(f), len(g))
    out = [0] * n
    for i, c in enumerate(f):
        out[i] = (out[i] + c) % p
    for i, c in enumerate(g):
        out[i] = (out[i] - c) % p
    return trim(out, p)


def pmul(f, g, p):
    if deg(f) < 0 or deg(g) < 0:
        return [0]
    out = [0] * (len(f) + len(g) - 1)
    for i, cf in enumerate(f):
        if cf % p == 0:
            continue
        for j, cg in enumerate(g):
            if cg % p == 0:
                continue
            out[i + j] = (out[i + j] + cf * cg) % p
    return trim(out, p)


def monic(f, p):
    f = trim(f, p)
    if deg(f) < 0:
        raise ValueError("monic of zero")
    inv = pow(f[-1], p - 2, p)
    return trim([(c * inv) % p for c in f], p)


def pdivmod(f, g, p):
    f = trim(list(f), p)
    g = trim(list(g), p)
    if g == [0]:
        raise ZeroDivisionError("polynomial division by zero")
    lead_inv = pow(g[-1], p - 2, p)
    q = [0] * max(1, len(f) - len(g) + 1)
    r = list(f)
    while len(r) >= len(g) and r != [0]:
        r = trim(r, p)
        if len(r) < len(g) or r == [0]:
            break
        coef = (r[-1] * lead_inv) % p
        shift = len(r) - len(g)
        if shift >= len(q):
            q.extend([0] * (shift + 1 - len(q)))
        q[shift] = (q[shift] + coef) % p
        sub = [0] * shift + [(coef * c) % p for c in g]
        r = trim(psub(r, sub, p), p)
        if r == [0]:
            break
    return trim(q, p), trim(r, p)


def exact_quo(f, g, p):
    q, r = pdivmod(f, g, p)
    if r != [0]:
        raise ValueError("exact division failed")
    return q


def pgcd(f, g, p):
    f = trim(list(f), p)
    g = trim(list(g), p)
    while g != [0]:
        _, r = pdivmod(f, g, p)
        f, g = g, r
    if f != [0]:
        f = monic(f, p)
    return f


def pmod_pow(base, exp, mod, p):
    result = [1]
    b = pdivmod(base, mod, p)[1]
    e = exp
    while e > 0:
        if e & 1:
            result = pdivmod(pmul(result, b, p), mod, p)[1]
        b = pdivmod(pmul(b, b, p), mod, p)[1]
        e >>= 1
    return result


def derivative(f, p):
    if len(f) <= 1:
        return [0]
    out = [((i * f[i]) % p) for i in range(1, len(f))]
    return trim(out, p) if out else [0]


def pth_root_poly(f, p):
    f = trim(f, p)
    out = []
    for i, c in enumerate(f):
        if i % p == 0:
            out.append(c % p)
        elif c % p != 0:
            raise ValueError("not a p-th power")
    return trim(out, p)


class DP:
    __slots__ = ("parity", "coeffs")

    def __init__(self, parity, coeffs):
        self.parity = parity
        self.coeffs = coeffs


def dp_mul(a, b, curve_poly, p):
    poly = pmul(a.coeffs, b.coeffs, p)
    s = a.parity + b.parity
    if s == 2:
        poly = pmul(poly, curve_poly, p)
        parity = 0
    elif s > 2:
        raise ValueError("parity overflow")
    else:
        parity = s
    return DP(parity, poly)


def dp_sub(a, b, p):
    if a.parity != b.parity:
        raise ValueError("parity mismatch")
    return DP(a.parity, psub(a.coeffs, b.coeffs, p))


def dp_cube(a, curve_poly, p):
    a2 = dp_mul(a, a, curve_poly, p)
    return dp_mul(a2, a, curve_poly, p)


def psi7(a, b, p):
    """Return the pure-x coefficient list of psi_7, not yet made monic."""
    a %= p
    b %= p
    curve_poly = trim([b, a, 0, 1], p)
    psi1 = DP(0, [1])
    psi2 = DP(1, [2 % p])
    psi3 = DP(0, trim([(-a * a) % p, (12 * b) % p, (6 * a) % p, 0, 3 % p], p))
    h4 = [
        (-8 * b * b - a ** 3) % p,
        (-4 * a * b) % p,
        (-5 * a * a) % p,
        (20 * b) % p,
        (5 * a) % p,
        0,
        1,
    ]
    psi4 = DP(1, trim([(4 * c) % p for c in h4], p))
    term1 = dp_mul(psi4, dp_cube(psi2, curve_poly, p), curve_poly, p)
    term2 = dp_mul(psi1, dp_cube(psi3, curve_poly, p), curve_poly, p)
    psi5 = dp_sub(term1, term2, p)
    term1b = dp_mul(psi5, dp_cube(psi3, curve_poly, p), curve_poly, p)
    term2b = dp_mul(psi2, dp_cube(psi4, curve_poly, p), curve_poly, p)
    psi7_dp = dp_sub(term1b, term2b, p)
    if psi5.parity != 0 or psi7_dp.parity != 0:
        raise ValueError("odd division polynomial acquired a y factor")
    return trim(psi7_dp.coeffs, p)


def monic_psi7(a, b, p):
    raw = psi7(a, b, p)
    return monic(raw, p), deg(raw), (raw[-1] % p if raw else 0)


def square_free_factorization(f, p):
    """Return pairs (square-free monic g, multiplicity) with f = product g**m."""
    f = monic(f, p)
    result = []
    df = derivative(f, p)
    if df == [0]:
        root = pth_root_poly(f, p)
        for g, m in square_free_factorization(root, p):
            result.append((g, m * p))
        return result
    c = pgcd(f, df, p)
    w = monic(exact_quo(f, c, p), p)
    i = 1
    guard = deg(f) + 3
    while deg(w) > 0:
        if i > guard:
            raise RuntimeError("square-free factorization did not finish")
        y = pgcd(w, c, p)
        z = exact_quo(w, y, p)
        if deg(z) > 0:
            result.append((monic(z, p), i))
        i += 1
        w = y if deg(y) > 0 else [0]
        if deg(y) < 0 or y == [0] or y == [1]:
            w = [0]
        c = exact_quo(c, y, p) if deg(y) > 0 else c
        if c == [0]:
            break
        if deg(c) == 0:
            c = [1]
    if deg(c) > 0:
        root = pth_root_poly(monic(c, p), p)
        for g, m in square_free_factorization(root, p):
            result.append((g, m * p))
    return result


def distinct_degree_factors(f, p):
    """Square-free f -> pairs (product of degree-d irreducibles, d)."""
    f = monic(f, p)
    if deg(f) <= 0:
        return []
    if deg(f) == 1:
        return [(f, 1)]
    x = [0, 1]
    h = [0, 1]
    d = 0
    out = []
    while deg(f) > 0:
        d += 1
        if d > deg(f):
            break
        h = pmod_pow(h, p, f, p)
        g = pgcd(psub(h, x, p), f, p)
        if deg(g) > 0:
            g = monic(g, p)
            out.append((g, d))
            f = monic(exact_quo(f, g, p), p)
            if deg(f) > 0:
                h = pdivmod(h, f, p)[1]
            else:
                break
    if deg(f) > 0:
        out.append((monic(f, p), deg(f)))
    return out


def equal_degree_factors(f, d, p):
    f = monic(f, p)
    n = deg(f)
    if n < 0:
        return []
    if n == 0:
        return []
    if n == d:
        return [f]
    if n % d != 0:
        raise ValueError(f"degree {n} is not a multiple of {d}")
    exp = (pow(p, d) - 1) // 2
    separators = []
    for c in range(p):
        separators.append([c, 1])
    for c in range(p):
        separators.append([1, c, 1])
    for sep in separators:
        if deg(sep) <= 0:
            continue
        powered = pmod_pow(sep, exp, f, p)
        g = pgcd(psub(powered, [1], p), f, p)
        if 0 < deg(g) < n:
            g = monic(g, p)
            quot = monic(exact_quo(f, g, p), p)
            return equal_degree_factors(g, d, p) + equal_degree_factors(quot, d, p)
    raise RuntimeError("equal-degree split found no separator")


def irreducible_factors(f, p):
    """List of (monic irreducible, multiplicity)."""
    found = []
    for g, mult in square_free_factorization(f, p):
        for block, d in distinct_degree_factors(g, p):
            for q in equal_degree_factors(block, d, p):
                found.append((monic(q, p), mult))
    return found


def factor_count_with_multiplicity(f, p):
    """Sum of multiplicities of the monic irreducible factors."""
    return sum(mult for _, mult in irreducible_factors(monic(f, p), p))


def discriminant(a, b, p):
    return (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p


def smallest_nonsquare(p):
    squares = {pow(i, 2, p) for i in range(p)}
    for c in range(p):
        if c not in squares:
            return c
    raise RuntimeError("no nonsquare")


def is_square(c, p):
    if c % p == 0:
        return True
    return pow(c % p, (p - 1) // 2, p) == 1


def point_count(a, b, p):
    total = 1
    for x in range(p):
        rhs = (pow(x, 3, p) + (a * x) + b) % p
        if rhs == 0:
            total += 1
        elif pow(rhs, (p - 1) // 2, p) == 1:
            total += 2
    return total


def trace(a, b, p):
    return p + 1 - point_count(a, b, p)


def twist_coeffs(a, b, c, p):
    c %= p
    return (a * pow(c, 2, p)) % p, (b * pow(c, 3, p)) % p
