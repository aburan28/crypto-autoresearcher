"""
divpoly_ext.py -- GENUINELY NEW driver code (per the handoff: reused/isogeny.py's
kernel-finding only supports ell in {2,3,5,7} via reused/divpoly.py's hardcoded
psi_2..psi_7; the vertical conductor primes q in {17,19,23,29,31} require division
polynomials of much higher index that reused/divpoly.py does not compute).

Implements the FULL standard division-polynomial recursion (both odd- and
even-index cases; reused/divpoly.py's own docstring explains why EXP-ECTD-001 only
needed the odd-index half) up to any requested n, building on reused/divpoly.py's
DP class and F_p[x] arithmetic (pmul/psub/pdivmod) UNCHANGED -- only the recursion
driving those primitives is new.

Recursion (standard, e.g. Silverman AEC III.3.7 / Washington ch.3), for m>=2:
  psi_{2m+1} = psi_{m+2} psi_m^3 - psi_{m-1} psi_{m+1}^3
  2y * psi_{2m} = psi_m * (psi_{m+2} psi_{m-1}^2 - psi_{m-2} psi_{m+1}^2)

The even case is implemented via EXACT polynomial division (divpoly.pdivmod) of the
RHS (which the DP parity algebra below shows always collapses to a pure x-polynomial
equal to 2*E(x)*g_{2m}(x), E=curve poly) by 2*E(x); the division is verified exact
(zero remainder) on every call, not merely trusted.

Validated in selftest_divpoly_ext.py by (a) recomputing psi_5 and psi_7 via THIS
general recursion and checking byte-identical agreement, on several random curves,
with reused/divpoly.py's independently-already-validated psi_5/psi_7, and (b)
checking the standard degree formulas (deg psi_n = (n^2-1)/2 for odd n, deg
(psi_n/y) = (n^2-4)/2 for even n) hold for every n up to 31.
"""
from .reused import divpoly as dp


def build_division_polys(a, b, p, n_max):
    """Return dict n -> divpoly.DP for n in [1, n_max], for E: y^2=x^3+ax+b over F_p."""
    a %= p
    b %= p
    curve_poly = dp._trim([b, a, 0, 1], p)
    two_e = dp.pmul([2 % p], curve_poly, p)

    psis = {}
    psis[1] = dp.DP(0, [1])
    psis[2] = dp.DP(1, [2 % p])
    psis[3] = dp.DP(0, dp._trim([(-a * a) % p, (12 * b) % p, (6 * a) % p, 0, 3], p))
    h4 = [(-8 * b * b - a ** 3) % p, (-4 * a * b) % p, (-5 * a * a) % p,
          (20 * b) % p, (5 * a) % p, 0, 1]
    psis[4] = dp.DP(1, dp._trim([(4 * c) % p for c in h4], p))

    def sq(P):
        return dp.dp_mul(P, P, curve_poly, p)

    n = 5
    while n <= n_max:
        if n % 2 == 1:
            m = (n - 1) // 2
            # psi_{2m+1} = psi_{m+2} psi_m^3 - psi_{m-1} psi_{m+1}^3
            psi_m_cubed = dp.dp_mul(sq(psis[m]), psis[m], curve_poly, p)
            psi_mp1_cubed = dp.dp_mul(sq(psis[m + 1]), psis[m + 1], curve_poly, p)
            term1 = dp.dp_mul(psis[m + 2], psi_m_cubed, curve_poly, p)
            term2 = dp.dp_mul(psis[m - 1], psi_mp1_cubed, curve_poly, p)
            psis[n] = dp.dp_sub(term1, term2, p)
        else:
            m = n // 2
            # 2y*psi_{2m} = psi_m*(psi_{m+2} psi_{m-1}^2 - psi_{m-2} psi_{m+1}^2)
            t1 = dp.dp_mul(psis[m + 2], sq(psis[m - 1]), curve_poly, p)
            t2 = dp.dp_mul(psis[m - 2], sq(psis[m + 1]), curve_poly, p)
            bracket = dp.dp_sub(t1, t2, p)
            rhs = dp.dp_mul(psis[m], bracket, curve_poly, p)
            assert rhs.parity == 0, "even-index RHS must collapse to a pure x-polynomial"
            q_poly, r_poly = dp.pdivmod(rhs.coeffs, two_e, p)
            assert r_poly == [0], f"exact division expected building psi_{n}"
            psis[n] = dp.DP(1, q_poly)
        n += 1
    return psis, curve_poly


def torsion_poly_general(ell, a, b, p):
    """Pure-x polynomial whose roots are exactly the x-coordinates of the
    ell-torsion points (ell prime, any size -- not limited to {2,3,5,7})."""
    if ell == 2:
        return dp._trim([b % p, a % p, 0, 1], p)
    psis, _ = build_division_polys(a, b, p, ell)
    P = psis[ell]
    assert P.parity == 0, f"odd-index psi_{ell} must be a pure x-polynomial"
    return P.coeffs
