"""
Degree-2 rational isogenies via Velu's formula (Velu 1971), kernel {O, T}
with T = (x0, 0) a rational 2-torsion point (root of x^3+ax+b mod p).
This is the single fixed step prime ell_0 = 2 used by this experiment's
isogeny graph (see specification.yaml inputs.isogeny_step_primes and
inputs.isogeny_degree_budget). Correctness is verified empirically in
tests/test_isogeny2.py against brute-force small-field group homomorphism
checks, not assumed from memory alone.
"""
from __future__ import annotations
from sympy import roots, symbols, GF, Poly
from .ecc import OpCounter


def two_torsion_roots(a: int, b: int, p: int):
    """Roots of x^3 + a*x + b mod p, i.e. x-coordinates of rational
    2-torsion points. Uses exact polynomial factorization over GF(p)."""
    x = symbols("x")
    poly = Poly(x**3 + a * x + b, x, domain=GF(p))
    rts = []
    for factor, mult in poly.factor_list()[1]:
        if factor.degree() == 1:
            # factor = x - r  (monic over GF(p))
            r = (-factor.nth(0)) % p
            rts.append(int(r))
    return rts


def isogenous_curve_2(a: int, b: int, p: int, x0: int):
    t = (3 * x0 * x0 + a) % p
    a_prime = (a - 5 * t) % p
    b_prime = (b - 7 * x0 * t) % p
    return a_prime, b_prime, t


def push_point_2(P, a: int, p: int, x0: int, t: int, ctr: OpCounter = None):
    """Map P through the degree-2 isogeny with kernel {O,(x0,0)} to the
    codomain curve. Returns None (point at infinity) if P is O or in the
    kernel."""
    if ctr is None:
        ctr = OpCounter()
    if P is None:
        return None
    x, y = P
    if x == x0:
        return None  # P is the kernel point (x0, 0); maps to O
    dx = (x - x0) % p
    inv_dx = pow(dx, -1, p)
    ctr.field_invs += 1
    x_img = (x + t * inv_dx) % p
    y_img = (y * (1 - t * inv_dx * inv_dx)) % p
    ctr.field_mults += 3
    return (x_img, y_img)
