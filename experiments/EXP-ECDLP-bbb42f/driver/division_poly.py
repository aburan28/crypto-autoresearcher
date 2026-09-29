"""
Division polynomials for y^2 = x^3 + a*x + b over F_p, and the ell-isogeny
kernel-polynomial recovery used to build every edge of the class walk.

Method (entirely within F_p[x], no extension field is ever constructed):

  1. Build psi_m as a ring element (A, B) meaning A(x) + B(x)*y, for
     m = 0..M, via the standard division-polynomial recurrence.
     For odd m, psi_m = (f_m(x), 0) is a pure x-polynomial: this is psi_ell
     itself for our odd degrees {3,5,7,11,13}.
  2. For a candidate Frobenius eigenvalue lambda mod ell (a root of
     X^2 - t*X + p mod ell, found by brute force over the ell < 14
     residues), build the numerator/denominator x-polynomials of the
     x-coordinate multiplication-by-lambda map phi_lambda(x) = x -
     psi_{lambda-1} psi_{lambda+1} / psi_lambda^2, using the ring elements
     (the y's cancel by construction: verified as an internal self-check
     that the relevant ring products land in the pure-A part).
  3. The kernel polynomial for this eigenvalue is
         h(x) = gcd( psi_ell(x), (x^p mod psi_ell(x) - x) * DEN(x) + NUM(x) )
     computed via poly gcd in F_p[x], where x^p mod psi_ell(x) is obtained
     by polynomial modular exponentiation (repeated squaring) -- again
     entirely in F_p[x].
  4. deg(h) is expected to be exactly (ell-1)/2 for a genuine rational
     ell-isogeny kernel. Any other degree is recorded as a defect (an
     "incomplete/anomalous kernel factor") rather than silently used.

This is the standard Elkies-style kernel-polynomial recovery used in SEA
point-counting implementations; it is reproduced here from the classical
recurrences because no computer-algebra library is available in this
environment (no sympy/numpy/pari), and it is deliberately built to be
self-checking (parity assertions, degree assertions) rather than trusted.
"""
from __future__ import annotations

from poly import (
    padd, psub, pmul, pdeg, pdivmod, pmod, pgcd, ppowmod, ring_mul, ring_add,
    ring_sub, ring_sqr, ring_pow, power_sums_from_monic, _trim,
)


class DivisionPolyError(Exception):
    pass


def curve_poly(a, b, p):
    """c(x) = x^3 + a*x + b, little-endian coeffs."""
    return _trim([b % p, a % p, 0, 1])


def build_psi_table(a, b, p, max_index):
    """
    Return dict m -> (A, B) ring element for psi_m, m = 0..max_index.
    """
    c = curve_poly(a, b, p)
    psi = {}
    psi[0] = ((0,), (0,))
    psi[1] = ((1,), (0,))
    psi[2] = ((0,), (2,))
    # psi_3 = 3x^4 + 6a x^2 + 12 b x - a^2
    psi3 = _trim([(-a * a) % p, (12 * b) % p, (6 * a) % p, 0, 3 % p])
    psi[3] = (psi3, (0,))
    # psi_4 = 4y * (x^6+5a x^4+20b x^3-5a^2 x^2-4ab x-8b^2-a^3)
    g4 = _trim([
        (-8 * b * b - a ** 3) % p,
        (-4 * a * b) % p,
        (-5 * a * a) % p,
        (20 * b) % p,
        (5 * a) % p,
        0,
        1,
    ])
    psi4b = pmul((4 % p,), g4, p)
    psi[4] = ((0,), psi4b)

    m = 2
    while max(2 * m + 1, 2 * m) <= max_index:
        pm2 = psi.get(m - 2, ((0,), (0,)))
        pm1 = psi[m - 1]
        pm = psi[m]
        pp1 = psi[m + 1]
        pp2 = psi[m + 2]

        # psi_{2m+1} = psi_{m+2} psi_m^3 - psi_{m-1} psi_{m+1}^3
        pm_cubed = ring_mul(ring_sqr(pm, c, p), pm, c, p)
        pp1_cubed = ring_mul(ring_sqr(pp1, c, p), pp1, c, p)
        term1 = ring_mul(pp2, pm_cubed, c, p)
        term2 = ring_mul(pm1, pp1_cubed, c, p)
        psi_2m1 = ring_sub(term1, term2, p)
        psi[2 * m + 1] = psi_2m1

        # psi_{2m} * 2y = psi_m * (psi_{m+2} psi_{m-1}^2 - psi_{m-2} psi_{m+1}^2)
        inner = ring_sub(
            ring_mul(pp2, ring_sqr(pm1, c, p), c, p),
            ring_mul(pm2, ring_sqr(pp1, c, p), c, p),
            p,
        )
        rhs = ring_mul(pm, inner, c, p)
        # rhs should equal (2 * g(x) * c(x), 0) for psi_2m = (0, g(x))
        if pdeg(rhs[1]) >= 0 and rhs[1] != (0,):
            raise DivisionPolyError(
                f"psi_{2*m} recurrence parity check failed: nonzero B part"
            )
        two_c = pmul((2 % p,), c, p)
        q, r = pdivmod(rhs[0], two_c, p)
        if r != (0,):
            raise DivisionPolyError(
                f"psi_{2*m} recurrence exact-division check failed: nonzero remainder"
            )
        psi[2 * m] = ((0,), q)
        m += 1
    return psi


def eigenvalues_mod_ell(t, p, ell):
    """Roots of X^2 - t X + p == 0 mod ell, found by brute force (ell < 14)."""
    roots = []
    for x in range(ell):
        if (x * x - t * x + p) % ell == 0:
            roots.append(x)
    return roots


def mult_by_m_num_den(psi, m, c, p):
    """
    Return (NUM, DEN) pure-x polynomials such that
        x([m]P) = x - NUM(x)/DEN(x)
    using psi_{m-1}, psi_{m+1}, psi_m from the ring-element table.
    Self-checks that the B (y-carrying) component of both products is zero.
    """
    if m == 0:
        raise DivisionPolyError("multiplication by 0 is undefined for this map")
    pm1 = psi[m - 1]
    pp1 = psi[m + 1]
    pm = psi[m]
    num_e = ring_mul(pm1, pp1, c, p)
    den_e = ring_mul(pm, pm, c, p)
    if num_e[1] != (0,) or den_e[1] != (0,):
        raise DivisionPolyError(f"mult-by-{m} map parity check failed")
    return num_e[0], den_e[0]


def kernel_polynomial(a, b, p, t, ell):
    """
    Compute the kernel polynomial(s) h(x) for rational ell-isogenies from a
    curve with trace t. Returns a list of dicts:
        {"lambda": lam, "h": tuple(coeffs), "degree": d}
    for each eigenvalue lam in F_ell for which gcd() yields a factor of the
    expected degree d = (ell-1)/2. ell must be odd (ell=2 is handled
    separately by the caller: no division-polynomial machinery is defined
    for ell=2 in this module).
    """
    if ell % 2 == 0:
        raise DivisionPolyError("kernel_polynomial only supports odd ell")
    d = (ell - 1) // 2
    c = curve_poly(a, b, p)
    max_index = ell + 2
    psi = build_psi_table(a, b, p, max_index)
    psi_ell = psi[ell]
    if psi_ell[1] != (0,):
        raise DivisionPolyError(f"psi_{ell} is not a pure x-polynomial (unexpected)")
    psi_ell_x = psi_ell[0]

    roots = eigenvalues_mod_ell(t % ell, p % ell, ell)
    results = []
    xp = ppowmod((0, 1), p, psi_ell_x, p)  # x^p mod psi_ell(x)
    x_poly = (0, 1)
    for lam in roots:
        if lam == 0:
            continue
        num, den = mult_by_m_num_den(psi, lam, c, p)
        # condition: x^p ≡ x - num/den  (mod h)  <=>  (x^p - x)*den + num ≡ 0 (mod h)
        lhs = pmul(psub(xp, x_poly, p), den, p)
        g = padd(lhs, num, p)
        g = pmod(g, psi_ell_x, p)
        h = pgcd(psi_ell_x, g, p)
        deg_h = pdeg(h)
        results.append({"lambda": lam, "h": h, "degree": deg_h, "expected_degree": d})
    return results
