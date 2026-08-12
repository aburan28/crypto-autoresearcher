"""
divpoly.py -- division polynomials psi_n(x) for E: y^2=x^3+ax+b over F_p, computed
via the standard recursion, restricted to the odd indices we actually need
(psi_1, psi_2, psi_3, psi_4, psi_5, psi_7), represented as plain F_p[x] coefficient
lists (index = power of x).

Convention: psi_n for odd n is a polynomial purely in x (no y). psi_n for even n
equals y times a polynomial in x. Internally we track a pair (parity, coeffs) with
parity=0 meaning "pure poly in x" and parity=1 meaning "y * poly in x"; whenever two
parity-1 factors are multiplied together, y^2 is substituted by the curve equation
x^3+a*x+b, collapsing back to parity 0. We only ever need the ODD-index recursion
  psi_{2m+1} = psi_{m+2} * psi_m^3 - psi_{m-1} * psi_{m+1}^3
which (as verified below) only ever combines same-parity terms, so no polynomial
division step is required (avoiding the messier even-index recursion entirely).

Base cases (standard, e.g. Silverman AEC III.5.8 / Washington ch.3):
  psi_1 = 1
  psi_2 = 2y
  psi_3 = 3x^4 + 6a x^2 + 12b x - a^2
  psi_4 = 4y (x^6 + 5a x^4 + 20b x^3 - 5a^2 x^2 - 4ab x - 8b^2 - a^3)
"""


def _trim(poly, p):
    poly = [c % p for c in poly]
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly


def padd(f, g, p):
    n = max(len(f), len(g))
    out = [0] * n
    for i, c in enumerate(f):
        out[i] = (out[i] + c) % p
    for i, c in enumerate(g):
        out[i] = (out[i] + c) % p
    return _trim(out, p)


def psub(f, g, p):
    n = max(len(f), len(g))
    out = [0] * n
    for i, c in enumerate(f):
        out[i] = (out[i] + c) % p
    for i, c in enumerate(g):
        out[i] = (out[i] - c) % p
    return _trim(out, p)


def pmul(f, g, p):
    out = [0] * (len(f) + len(g) - 1)
    for i, cf in enumerate(f):
        if cf == 0:
            continue
        for j, cg in enumerate(g):
            if cg == 0:
                continue
            out[i + j] = (out[i + j] + cf * cg) % p
    return _trim(out, p)


def peval(poly, x, p):
    r = 0
    for c in reversed(poly):
        r = (r * x + c) % p
    return r


def pdivmod(f, g, p):
    """Polynomial division f = q*g + r over F_p, g monic-normalized internally."""
    f = _trim(list(f), p)
    g = _trim(list(g), p)
    if g == [0]:
        raise ZeroDivisionError
    lead_inv = pow(g[-1], p - 2, p)
    q = [0] * max(1, len(f) - len(g) + 1)
    r = list(f)
    while len(r) >= len(g) and r != [0]:
        r = _trim(r, p)
        if len(r) < len(g):
            break
        coef = (r[-1] * lead_inv) % p
        shift = len(r) - len(g)
        q[shift] = (q[shift] + coef) % p
        sub = [0] * shift + [(coef * c) % p for c in g]
        r = psub(r, sub, p)
        r = _trim(r, p)
        if r == [0]:
            break
    return _trim(q, p), _trim(r, p)


def pgcd(f, g, p):
    f = _trim(list(f), p)
    g = _trim(list(g), p)
    while g != [0]:
        _, r = pdivmod(f, g, p)
        f, g = g, r
    # normalize monic
    if f != [0]:
        inv = pow(f[-1], p - 2, p)
        f = _trim([(c * inv) % p for c in f], p)
    return f


def pmod_pow(base, exp, mod, p):
    """base^exp mod `mod` (all polys over F_p). Repeated squaring."""
    result = [1]
    b = pdivmod(base, mod, p)[1]
    e = exp
    while e > 0:
        if e & 1:
            result = pdivmod(pmul(result, b, p), mod, p)[1]
        b = pdivmod(pmul(b, b, p), mod, p)[1]
        e >>= 1
    return result


class DP:
    """A division-polynomial value: parity in {0,1}, coeffs = poly in x."""
    __slots__ = ("parity", "coeffs")

    def __init__(self, parity, coeffs):
        self.parity = parity
        self.coeffs = coeffs


def dp_mul(A, B, curve_poly, p):
    poly = pmul(A.coeffs, B.coeffs, p)
    s = A.parity + B.parity
    if s == 2:
        poly = pmul(poly, curve_poly, p)
        parity = 0
    else:
        parity = s
    return DP(parity, poly)


def dp_sub(A, B, p):
    assert A.parity == B.parity, "division-polynomial subtraction requires equal parity"
    return DP(A.parity, psub(A.coeffs, B.coeffs, p))


def dp_cube(A, curve_poly, p):
    A2 = dp_mul(A, A, curve_poly, p)
    return dp_mul(A2, A, curve_poly, p)


def division_polys(a, b, p):
    """Return dict n -> DP for n in {1,2,3,4,5,7}, plus the raw curve x-poly (for n=2
    torsion: roots of x^3+ax+b give 2-torsion x-coordinates directly)."""
    a %= p
    b %= p
    curve_poly = _trim([b, a, 0, 1], p)  # b + a x + x^3

    psi1 = DP(0, [1])
    psi2 = DP(1, [2 % p])
    psi3 = DP(0, _trim([(-a * a) % p, (12 * b) % p, (6 * a) % p, 0, 3], p))
    h4 = [(-8 * b * b - a ** 3) % p, (-4 * a * b) % p, (-5 * a * a) % p,
          (20 * b) % p, (5 * a) % p, 0, 1]
    psi4 = DP(1, _trim([(4 * c) % p for c in h4], p))

    # psi5 = psi4*psi2^3 - psi1*psi3^3  (m=2)
    term1 = dp_mul(psi4, dp_cube(psi2, curve_poly, p), curve_poly, p)
    term2 = dp_mul(psi1, dp_cube(psi3, curve_poly, p), curve_poly, p)
    psi5 = dp_sub(term1, term2, p)

    # psi7 = psi5*psi3^3 - psi2*psi4^3  (m=3)
    term1b = dp_mul(psi5, dp_cube(psi3, curve_poly, p), curve_poly, p)
    term2b = dp_mul(psi2, dp_cube(psi4, curve_poly, p), curve_poly, p)
    psi7 = dp_sub(term1b, term2b, p)

    assert psi5.parity == 0 and psi7.parity == 0, "odd-index division polys must be pure in x"
    return {1: psi1, 2: psi2, 3: psi3, 4: psi4, 5: psi5, 7: psi7, "curve_poly": curve_poly}


def torsion_poly(ell, a, b, p):
    """Return the pure-x polynomial whose roots (in F_p-bar) are exactly the
    x-coordinates of the ell-torsion points (excluding O). For ell=2 this is the
    curve's own cubic x^3+ax+b (its roots ARE F_p-rational 2-torsion x-coords whenever
    they exist, since y=0 there). For odd ell in {3,5,7} this is psi_ell(x)."""
    if ell == 2:
        return _trim([b % p, a % p, 0, 1], p)
    dps = division_polys(a, b, p)
    if ell not in dps:
        raise ValueError(f"unsupported ell={ell}")
    return dps[ell].coeffs
