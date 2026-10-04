"""
Degree-3 rational isogenies via Velu's formula, kernel {O, T, -T} with T of
order 3. Added after discovering (empirically: 60/60 sampled prime-order
census curves had zero rational 2-torsion; then proven) that isogeny2.py's
step prime ell_0=2 is STRUCTURALLY VACUOUS for every curve this experiment
samples: this experiment's own curve_sampling_rule requires prime N, and a
rational point of order 2 would need 2 | N (Lagrange), impossible for an
odd prime N. This generalizes: a rational point of order ell always needs
ell | N. Degree-3 (and every odd prime degree) sidesteps this because the
kernel {O,T,-T} does not require T itself to be F_p-rational -- only its
x-coordinate needs to be Frobenius-fixed (a root of the 3-division
polynomial in F_p); Frobenius is free to swap T <-> -T, which still leaves
the 2-element kernel set stable, hence the isogeny is still rational. This
is not a statement about points of E(F_p) at all (T need never be an
F_p-point of E), so Lagrange on N does not apply to it.

DERIVATION (not taken from memory; three earlier attempts at this closed
form were each wrong in a different way -- an ad hoc y0-substitution loop
that silently dropped terms, then a sign error in the (x0-x)^3 vs (x-x0)^3
denominator, then a double-counted leading "+x"/"+y" term left over from a
misreading of what sympy's together()/fraction() had already absorbed;
each was caught by numeric testing against two INDEPENDENT oracles built
from this driver's own verified point_add -- one over F_p with a genuinely
rational 3-torsion point, one over a hand-rolled F_p^2 for the (much more
common) case where the kernel's y-coordinate is not itself F_p-rational --
before being trusted; see tests/isogeny3_final.py for the final derivation
and both cross-checks, both passing exactly): Velu's definition
    X(P) = x(P) + sum_{Q in ker\\{O}} [x(P+Q) - x(Q)]
    Y(P) = y(P) + sum_{Q in ker\\{O}} [y(P+Q) - y(Q)]
was expanded symbolically using this driver's own affine addition law
(ecc.py), for Q = T=(x0,y0) and Q = -T=(x0,-y0); y0 was then eliminated via
proper polynomial division against the ideal generator y0^2-(x0^3+a*x0+b)
(every y0-dependence provably cancels between the T and -T contributions),
and P's own curve relation y^2=x^3+a*x+b was used, also via polynomial
division, to fully reduce the result. sympy's together()/fraction() had
already absorbed the leading x(P)/y(P) term into the combined numerator, so
the closed forms below are the COMPLETE X(P), Y(P) -- not an additive
correction to add to x/y.
"""
from __future__ import annotations
from sympy import symbols, GF, Poly
from .ecc import OpCounter


def psi_3_roots(a: int, b: int, p: int):
    """Roots of the 3-division polynomial psi_3(x) = 3x^4 + 6a x^2 + 12b x
    - a^2 (mod p): x-coordinates of (not necessarily F_p-rational, only
    Frobenius-fixed-x-coordinate) order-3 points."""
    x = symbols("x")
    poly = Poly(3 * x**4 + 6 * a * x**2 + 12 * b * x - a**2, x, domain=GF(p))
    rts = []
    for factor, mult in poly.factor_list()[1]:
        if factor.degree() == 1:
            r = (-factor.nth(0)) % p
            rts.append(int(r))
    return rts


def _raw_push_point_3(P, a: int, p: int, x0: int, ctr: OpCounter = None):
    """COMPLETE closed forms (not an additive correction to x/y -- see
    module docstring):
      X(P) = [x^3 - 2*x0*x^2 + 7*x0^2*x + 2*a*x + 2*a*x0 + 4*b - 2*x0^3] / (x0-x)^2
      Y(P) = y*[-x^3 + 3*x0*x^2 + 3*x0^2*x + 3*x0^3 + 2*a*x + 6*a*x0 + 8*b] / (x0-x)^3
    Both verified numerically against two independent oracles (F_p and
    F_p^2 kernel cases) in tests/isogeny3_final.py. NOTE: the numerators
    were derived using the ORIGIN curve's b via y^2=x^3+a*x+b, so b is
    recovered from P itself rather than taken as a parameter. Returns None
    (point at infinity) if P shares the kernel pair's x-coordinate x0.
    """
    if ctr is None:
        ctr = OpCounter()
    if P is None:
        return None
    x, y = P
    b = (y * y - x**3 - a * x) % p  # recovered from P itself; avoids a separate b parameter
    if x == x0:
        return None
    n = p
    d0x = (x0 - x) % n  # NOTE: (x0-x), not (x-x0) -- the cubed denominator is sign-sensitive
    inv_d0x = pow(d0x, -1, n)
    ctr.field_invs += 1
    inv_d0x2 = (inv_d0x * inv_d0x) % n
    inv_d0x3 = (inv_d0x2 * inv_d0x) % n

    x_num = (x**3 - 2 * x0 * x**2 + 7 * x0**2 * x + 2 * a * x + 2 * a * x0 + 4 * b - 2 * x0**3) % n
    y_num_factor = (-x**3 + 3 * x0 * x**2 + 3 * x0**2 * x + 3 * x0**3 + 2 * a * x + 6 * a * x0 + 8 * b) % n

    x_img = (x_num * inv_d0x2) % n
    y_img = (y * y_num_factor * inv_d0x3) % n
    ctr.field_mults += 10
    return (x_img, y_img)


def isogenous_curve_3(a: int, b: int, p: int, x0: int, probe1=None, probe2=None):
    """Codomain curve coefficients (A', B'), derived ROBUSTLY at runtime
    rather than from a closed-form guess: evaluate the (independently
    re-derived and verified) _raw_push_point_3 map at two known curve
    points and solve the resulting 2x2 linear system
      Y_i^2 = X_i^3 + A'*X_i + B'   (i=1,2)
    for A', B' mod p. This sidesteps needing a separately-verified
    closed-form (a-5t, b-7w)-style formula for A',B' (an earlier attempt at
    that closed form was wrong and caught exactly by this module's
    brute-force tests; deriving A',B' from the map's own output removes
    that whole class of error). Requires two points whose x-coordinate is
    not x0; random_point is used if probes are not supplied.
    """
    from .ecc import random_point
    import random as _random
    rng = _random.Random(repr((a, b, p, x0, "isogeny3-ab-probe")))
    fixed = [pt for pt in (probe1, probe2) if pt is not None]
    for attempt in range(50):
        pts = list(fixed)
        while len(pts) < 2:
            cand = random_point(a, b, p, rng)
            if cand[0] != x0 and cand not in pts:
                pts.append(cand)
        (x1, y1), (x2, y2) = pts
        X1, Y1 = _raw_push_point_3((x1, y1), a, p, x0)
        X2, Y2 = _raw_push_point_3((x2, y2), a, p, x0)
        dX = (X1 - X2) % p
        if dX == 0:
            fixed = []  # discard and retry with fresh random probes
            continue
        rhs1 = (Y1 * Y1 - X1**3) % p
        rhs2 = (Y2 * Y2 - X2**3) % p
        A_prime = ((rhs1 - rhs2) * pow(dX, -1, p)) % p
        B_prime = (rhs1 - A_prime * X1) % p
        return A_prime, B_prime
    raise RuntimeError(f"isogenous_curve_3: could not find two probes with distinct images after 50 attempts (p={p}, x0={x0})")


def push_point_3(P, a: int, p: int, x0: int, ctr: OpCounter = None):
    return _raw_push_point_3(P, a, p, x0, ctr)
