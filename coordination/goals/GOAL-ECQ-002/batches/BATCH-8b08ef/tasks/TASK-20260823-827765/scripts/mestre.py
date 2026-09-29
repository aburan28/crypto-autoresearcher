#!/usr/bin/env python3
"""
Mestre's Q(T) construction, regenerated from a degree-6 polynomial q(x).

TASK-20260823-416e78 / BATCH-541940 / GOAL-ECQ-002 / H-ECQ-8b600d.

The construction is taken from the BATCH-da59ec VALIDATOR's independent
re-derivation
(BATCH-da59ec/tasks/TASK-20260823-72505a/validation_report.md and the
H-ECQ-8b600d `mechanism` field), NOT re-invented here:

    q(x) = prod_{i=1}^{6} (x - a_i)          (a monic degree-6 polynomial)
    p(x,T) = q(x-T) q(x+T)                   (degree 12 in x, monic)
    p = g^2 - r                              (g monic degree 6 in x, deg_x r <= 5)
    C : y^2 = r(x,T)                         (a quartic in x, i.e. genus 1)

and the twelve sections come for free: p(a_i +- T, T) = 0, so at
x = a_i +- T one has r = g^2 and y = g(a_i +- T, T) is a point ON C,
identically in T.  Each RATIONAL root a_i of q contributes two sections.

Everything here is exact rational arithmetic (fractions.Fraction).  Nothing in
this module uses PARI or floating point.

Null objects of the SAME SHAPE: q need not split over Q.  Taking q with k
rational roots and (6-k)/2 irreducible quadratic factors gives the SAME
degree-12 p, the SAME quartic r, the SAME surface shape and comparable
coefficient content, but only 2k rational sections -- hence low generic rank.
That is the control the campaign has owed since BATCH-f2341e.
"""
from fractions import Fraction as F

# ---------------------------------------------------------------------------
# univariate polynomials over Q in T:  list of Fractions, index = degree
# ---------------------------------------------------------------------------


def t_trim(a):
    while len(a) > 1 and a[-1] == 0:
        a = a[:-1]
    return a


def t_add(a, b):
    n = max(len(a), len(b))
    return t_trim([(a[i] if i < len(a) else F(0)) + (b[i] if i < len(b) else F(0))
                   for i in range(n)])


def t_sub(a, b):
    n = max(len(a), len(b))
    return t_trim([(a[i] if i < len(a) else F(0)) - (b[i] if i < len(b) else F(0))
                   for i in range(n)])


def t_mul(a, b):
    if a == [F(0)] or b == [F(0)]:
        return [F(0)]
    out = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x == 0:
            continue
        for j, y in enumerate(b):
            if y:
                out[i + j] += x * y
    return t_trim(out)


def t_scal(a, c):
    c = F(c)
    return t_trim([x * c for x in a])


def t_const(c):
    return [F(c)]


def t_is_zero(a):
    return all(x == 0 for x in a)


def t_deg(a):
    a = t_trim(a)
    return -1 if t_is_zero(a) else len(a) - 1


def t_eval(a, v):
    v = F(v)
    s = F(0)
    for c in reversed(a):
        s = s * v + c
    return s


T_VAR = [F(0), F(1)]          # the polynomial T

# ---------------------------------------------------------------------------
# polynomials in x whose coefficients are polynomials in T: list of T-polys
# ---------------------------------------------------------------------------


def x_trim(P):
    while len(P) > 1 and t_is_zero(P[-1]):
        P = P[:-1]
    return P


def x_add(P, Q):
    n = max(len(P), len(Q))
    return x_trim([t_add(P[i] if i < len(P) else t_const(0),
                         Q[i] if i < len(Q) else t_const(0)) for i in range(n)])


def x_sub(P, Q):
    n = max(len(P), len(Q))
    return x_trim([t_sub(P[i] if i < len(P) else t_const(0),
                         Q[i] if i < len(Q) else t_const(0)) for i in range(n)])


def x_mul(P, Q):
    out = [t_const(0)] * (len(P) + len(Q) - 1)
    for i, a in enumerate(P):
        if t_is_zero(a):
            continue
        for j, b in enumerate(Q):
            if not t_is_zero(b):
                out[i + j] = t_add(out[i + j], t_mul(a, b))
    return x_trim(out)


def x_deg(P):
    P = x_trim(P)
    return -1 if len(P) == 1 and t_is_zero(P[0]) else len(P) - 1


def x_shift(P, s):
    """P(x) -> P(x + s), s a T-polynomial.  Horner in (x + s)."""
    out = [t_const(0)]
    for c in reversed(P):
        out = x_add(x_mul(out, [s, t_const(1)]), [c])
    return x_trim(out)


def x_eval(P, xval):
    """Evaluate at x = xval (a T-polynomial); returns a T-polynomial."""
    out = t_const(0)
    for c in reversed(P):
        out = t_add(t_mul(out, xval), c)
    return t_trim(out)


# ---------------------------------------------------------------------------
# the construction
# ---------------------------------------------------------------------------

class MestreFamily:
    """Mestre's construction for a monic degree-6 q with rational coefficients.

    q_coeffs: list of 7 rationals, q = sum q_coeffs[i] x^i, q_coeffs[6] == 1.
    rational_roots: the roots of q that lie in Q (may be fewer than 6).
    """

    def __init__(self, q_coeffs, rational_roots, name, tuple_entries=None,
                 kind='mestre'):
        assert len(q_coeffs) == 7 and F(q_coeffs[6]) == 1
        self.name = name
        self.kind = kind
        self.tuple_entries = tuple_entries
        self.q = [F(c) for c in q_coeffs]
        self.rational_roots = [F(a) for a in rational_roots]
        # q as an x-polynomial with constant T-coefficients
        qx = x_trim([t_const(c) for c in self.q])
        self.p = x_mul(x_shift(qx, t_scal(T_VAR, -1)), x_shift(qx, T_VAR))
        assert x_deg(self.p) == 12
        self.g, self.r = _sqrt_split(self.p)
        self.deg_x_r = x_deg(self.r)
        # sections: x = a +- T, y = g(x, T)
        self.sections = []
        for a in self.rational_roots:
            for sgn in (1, -1):
                xv = t_add(t_const(a), t_scal(T_VAR, sgn))
                yv = x_eval(self.g, xv)
                self.sections.append((xv, yv))

    # ------------------------------------------------------------------
    def identity_checks(self):
        """Re-verify the construction identically in T.  Returns a dict."""
        out = {}
        lhs = x_sub(x_sub(x_mul(self.g, self.g), self.r), self.p)
        out['p_equals_g2_minus_r_identically'] = x_deg(lhs) == -1
        out['deg_x_r'] = self.deg_x_r
        out['deg_x_g'] = x_deg(self.g)
        # every section on y^2 = r(x,T), identically in T
        bad = []
        for i, (xv, yv) in enumerate(self.sections):
            if t_sub(t_mul(yv, yv), x_eval(self.r, xv)) != [F(0)]:
                bad.append(i)
        out['n_sections'] = len(self.sections)
        out['sections_on_curve_identically_in_T'] = (bad == [])
        out['section_failures'] = bad
        return out

    # ------------------------------------------------------------------
    def quartic_at(self, t0):
        """r(x, t0) as [e, d, c, b, a] (ascending), exact Fractions."""
        return [t_eval(c, t0) for c in self.r]

    def sections_at(self, t0):
        return [(t_eval(xv, t0), t_eval(yv, t0)) for xv, yv in self.sections]

    def r_coeff_polys(self):
        """r's x-coefficients as T-polynomials, ascending: e,d,c,b,a."""
        c = list(self.r) + [t_const(0)] * (5 - len(self.r))
        return c[:5]


def _sqrt_split(p):
    """p monic of degree 12 in x -> (g, r) with g monic degree 6 and r = g^2 - p."""
    n = x_deg(p)
    assert n % 2 == 0
    m = n // 2
    P = list(p) + [t_const(0)] * 0
    # g = x^m + g_{m-1} x^{m-1} + ...
    g = [t_const(0)] * (m + 1)
    g[m] = t_const(1)
    half = F(1, 2)
    for k in range(1, m + 1):
        # coefficient of x^(n-k) in g^2 is sum_{i+j=k} g_{m-i} g_{m-j}
        s = t_const(0)
        for i in range(1, k):
            s = t_add(s, t_mul(g[m - i], g[m - (k - i)]))
        target = P[n - k] if n - k < len(P) else t_const(0)
        g[m - k] = t_scal(t_sub(target, s), half)
    g = x_trim(g)
    r = x_sub(x_mul(g, g), p)
    return g, r


# ---------------------------------------------------------------------------
# quartic  ->  Weierstrass
# ---------------------------------------------------------------------------

def quartic_IJ(quart):
    """(I, J) of v^2 = a u^4 + b u^3 + c u^2 + d u + e; quart ascending [e,d,c,b,a].

    Jacobian:  Y^2 = X^3 - 27 I X - 27 J.
    """
    e, d, c, b, a = [F(z) for z in (list(quart) + [F(0)] * 5)[:5]]
    I = 12 * a * e - 3 * b * d + c * c
    J = 72 * a * c * e + 9 * b * c * d - 27 * a * d * d - 27 * e * b * b - 2 * c ** 3
    return I, J


def quartic_to_weierstrass(quart, u0, v0):
    """Weierstrass model of v^2 = quart(u) using the rational point (u0, v0).

    Returns (a_invariants over Q, map) where map(u, v) -> (X, Y) or None for
    the point (u0, v0) itself, which goes to the identity.

    Formulas (Connell, Handbook of Elliptic Curves, quartic-to-Weierstrass;
    every use is CHECKED by substituting the image into the Weierstrass
    equation in exact arithmetic -- nothing here is trusted unverified).
    """
    e0, d0, c0, b0, a0 = [F(z) for z in (list(quart) + [F(0)] * 5)[:5]]
    # shift u = u0 + w so the point sits at w = 0
    # A w^4 + B w^3 + C w^2 + D w + E  with E = v0^2
    A = a0
    B = b0 + 4 * a0 * u0
    C = c0 + 3 * b0 * u0 + 6 * a0 * u0 ** 2
    D = d0 + 2 * c0 * u0 + 3 * b0 * u0 ** 2 + 4 * a0 * u0 ** 3
    E = e0 + d0 * u0 + c0 * u0 ** 2 + b0 * u0 ** 3 + a0 * u0 ** 4
    q = F(v0)
    assert E == q * q, 'point not on quartic'
    a1 = D / q
    a2 = C - D * D / (4 * q * q)
    a3 = 2 * q * B
    a4 = -4 * q * q * A
    a6 = a2 * a4
    ai = [a1, a2, a3, a4, a6]

    def mp(u, v):
        w = F(u) - u0
        if w == 0:
            return None
        X = (2 * q * (F(v) + q) + D * w) / (w * w)
        Y = (4 * q * q * (F(v) + q) + 2 * q * (D * w + C * w * w)
             - D * D * w * w / (2 * q)) / (w ** 3)
        return (X, Y)

    return ai, mp


def on_weierstrass(ai, P):
    a1, a2, a3, a4, a6 = [F(z) for z in ai]
    x, y = F(P[0]), F(P[1])
    return y * y + a1 * x * y + a3 * y == x ** 3 + a2 * x * x + a4 * x + a6


def integral_model(ai, points):
    """Scale (x,y) -> (u^2 x, u^3 y) to make a_i integral.  Returns (ai_int, pts)."""
    ai = [F(z) for z in ai]
    u = 1
    for a in ai:
        u = u * a.denominator // _gcd(u, a.denominator)
    exps = (1, 2, 3, 4, 6)
    aint = [int(ai[i] * F(u) ** exps[i]) for i in range(5)]
    pts = [(F(x) * u * u, F(y) * u ** 3) for x, y in points]
    return aint, pts


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def poly_from_roots_and_quadratics(roots, quadratics):
    """Monic degree-6 q from rational roots and monic irreducible quadratics.

    quadratics: list of (s, n) meaning x^2 - s x + n.
    Returns (q_coeffs ascending, rational_roots).
    """
    q = [F(1)]

    def mulp(P, Q):
        out = [F(0)] * (len(P) + len(Q) - 1)
        for i, x in enumerate(P):
            for j, y in enumerate(Q):
                out[i + j] += x * y
        return out

    for a in roots:
        q = mulp(q, [F(-a), F(1)])
    for s, n in quadratics:
        q = mulp(q, [F(n), F(-s), F(1)])
    assert len(q) == 7
    return q, [F(a) for a in roots]
