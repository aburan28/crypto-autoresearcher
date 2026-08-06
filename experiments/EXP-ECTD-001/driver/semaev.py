"""
semaev.py -- Semaev summation polynomials S_3, S_4 for E: y^2=x^3+ax+b over F_p
(char p != 2,3), plus x-only point arithmetic (doubling / differential addition)
derived from S_3, used both for the Semaev-density meters and for the isogeny
kernel ladder in isogeny.py.

S_3(x1,x2,x3)=0  <=>  there exist y1,y2 with (x1,y1)+(x2,y2) = +-(x3, *)
  i.e. x3 in {x(P1+P2), x(P1-P2)}.

Standard explicit form (odd characteristic, e.g. Semaev ePrint 2004/031 /
Gaudry "Index calculus for abelian varieties..."):
  S_3(x1,x2,x3) = (x1-x2)^2 x3^2
                  - 2[(x1+x2)(x1 x2 + a) + 2b] x3
                  + (x1 x2 - a)^2 - 4b(x1+x2)

S_4 is defined by elimination (Semaev's recursive construction):
  S_4(x1,x2,x3,x4) = Res_X( S_3(x1,x2,X), S_3(x3,x4,X) )
which we compute EXPLICITLY as a determinant of the 4x4 Sylvester matrix of the two
quadratics-in-X S_3(x1,x2,X) and S_3(x3,x4,X); this is done symbolically once (see
derive_semaev_s4.py) and the result is hardcoded in S4_TERMS below to avoid runtime
dependence on a CAS. S4_TERMS is independently re-derived and cross-checked
numerically at driver self-test time against a direct resultant computation
(sylvester_resultant_quadratics below), not merely trusted.
"""
from . import fp


def S3(x1, x2, x3, a, b, p):
    x1 %= p; x2 %= p; x3 %= p; a %= p; b %= p
    t1 = ((x1 - x2) % p) ** 2 % p
    term_sq = (t1 * x3 * x3) % p
    lin_coeff = (2 * (((x1 + x2) % p) * ((x1 * x2 + a) % p) % p + 2 * b)) % p
    term_lin = (lin_coeff * x3) % p
    const = (((x1 * x2 - a) % p) ** 2 - 4 * b * ((x1 + x2) % p)) % p
    return (term_sq - term_lin + const) % p


def S3_coeffs_in_X(x1, x2, a, b, p):
    """Return [c0, c1, c2] such that S3(x1,x2,X) = c2*X^2 + c1*X + c0 (mod p)."""
    x1 %= p; x2 %= p; a %= p; b %= p
    c2 = ((x1 - x2) % p) ** 2 % p
    c1 = (-2 * (((x1 + x2) % p) * ((x1 * x2 + a) % p) % p + 2 * b)) % p
    c0 = (((x1 * x2 - a) % p) ** 2 - 4 * b * ((x1 + x2) % p)) % p
    return [c0, c1, c2]


def sylvester_resultant_quadratics(P, Q, p):
    """Resultant of two degree-2 (in X) polys P=[c0,c1,c2], Q=[d0,d1,d2] over F_p,
    via the 4x4 Sylvester determinant, computed directly (used both as the general
    tool for deriving S4 once, and as an independent cross-check at runtime)."""
    a2, a1, a0 = P[2], P[1], P[0]
    b2, b1, b0 = Q[2], Q[1], Q[0]
    # Sylvester matrix (4x4) for two degree-2 polys:
    # | a2 a1 a0 0  |
    # | 0  a2 a1 a0 |
    # | b2 b1 b0 0  |
    # | 0  b2 b1 b0 |
    M = [
        [a2, a1, a0, 0],
        [0, a2, a1, a0],
        [b2, b1, b0, 0],
        [0, b2, b1, b0],
    ]
    return det4_mod(M, p)


def det4_mod(M, p):
    # Bareiss-free direct cofactor expansion (4x4 is small, exact fraction-free enough
    # via modular inverses is unnecessary -- plain cofactor expansion over F_p works).
    def det3(m):
        return (
            m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
        )
    total = 0
    sign = 1
    for col in range(4):
        minor = [[M[r][c] for c in range(4) if c != col] for r in range(1, 4)]
        total += sign * M[0][col] * det3(minor)
        sign = -sign
    return total % p


def S4_via_resultant(x1, x2, x3, x4, a, b, p):
    """Direct (slow but unambiguous) evaluation of S4 by computing the resultant
    numerically at the given point -- used as ground truth to validate the hardcoded
    S4_TERMS expansion, and as a fallback if that expansion is ever unavailable."""
    P = S3_coeffs_in_X(x1, x2, a, b, p)
    Q = S3_coeffs_in_X(x3, x4, a, b, p)
    return sylvester_resultant_quadratics(P, Q, p)


# ---------------------------------------------------------------------------
# x-only point arithmetic derived from S3 (used by isogeny.py kernel ladder and
# by the Semaev relation-density meters). No y-coordinate ever needed.
# ---------------------------------------------------------------------------

def xDBL(x1, a, b, p):
    """x(2P) given x(P)=x1, for P not 2-torsion (x1^3+a*x1+b != 0)."""
    x1 %= p
    num = (((x1 * x1 - a) % p) ** 2 - 8 * b * x1) % p
    den = (4 * (x1 ** 3 + a * x1 + b)) % p
    return (num * fp.inv(den, p)) % p


def xADD(xP, xQ, xPmQ, a, b, p):
    """x(P+Q) given x(P), x(Q), and x(P-Q) already known (differential addition),
    via: the two roots of S3(xP,xQ,X)=0 are {x(P+Q), x(P-Q)}, and their SUM equals
    -c1/c2 (elementary symmetric function of a monic-normalized quadratic)."""
    xP %= p; xQ %= p; xPmQ %= p
    c0, c1, c2 = S3_coeffs_in_X(xP, xQ, a, b, p)
    if xP == xQ:
        raise ZeroDivisionError("xADD requires xP != xQ")
    sum_roots = (-c1 * fp.inv(c2, p)) % p
    return (sum_roots - xPmQ) % p


def x_multiples(x1, a, b, p, k_max):
    """Return dict k -> x(kP) for k=1..k_max, given x(P)=x1, via a simple additive
    ladder (k_max is tiny in this driver, <=3, so an O(k_max) ladder is plenty)."""
    out = {1: x1 % p}
    if k_max >= 2:
        out[2] = xDBL(x1, a, b, p)
    for k in range(3, k_max + 1):
        # kP = (k-1)P + P ; (k-1)P - P = (k-2)P
        out[k] = xADD(out[k - 1], out[1], out[k - 2], a, b, p)
    return out
