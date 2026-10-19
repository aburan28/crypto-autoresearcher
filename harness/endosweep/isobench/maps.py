"""Explicit Jacobian-coordinate formulas for a rational isogeny route E -> E' -> E.

A separable odd-degree (or degree-2) isogeny with kernel polynomial psi (monic,
degree s) is x' = N(x)/psi(x)^2, y' = y M(x)/psi(x)^3 with deg N = 2s+1 and
deg M = 3s.  In Jacobian coordinates (x = X/Z^2, y = Y/Z^3) the homogenised
step is X' = N_h(X, Z^2), Y' = Y M_h(X, Z^2), Z' = Z psi_h(X, Z^2), the form
chainsweep's ``optimised`` count prices.  N and M are recovered here by
interpolation from ``explicit.KernelIsogeny`` (whose x-image depends on x
only) and checked against it on random points.
"""
from __future__ import annotations

import random

from .. import explicit as EX
from ..toyverify import Curve


def _interp(xs: list[int], ys: list[int], p: int) -> list[int]:
    """Lagrange interpolation over F_p; coefficients low-first."""
    n = len(xs)
    coef = [0] * n
    for i in range(n):
        num, den = [1], 1
        for j in range(n):
            if i == j:
                continue
            num = EX.pmul(num, [(-xs[j]) % p, 1], p)
            den = den * (xs[i] - xs[j]) % p
        c = ys[i] * pow(den, -1, p) % p
        for k, v in enumerate(num):
            coef[k] = (coef[k] + c * v) % p
    return coef


def _peval(f: list[int], x: int, p: int) -> int:
    acc = 0
    for c in reversed(f):
        acc = (acc * x + c) % p
    return acc


def step_polys(phi: "EX.KernelIsogeny", seed: int = 7) -> dict:
    """{'N','M','psi'} low-first for one KernelIsogeny step, verified on points."""
    E, p, h = phi.E, phi.E.p, list(phi.h)
    s = len(h) - 1
    rng = random.Random(seed)
    xs, nx, my = [], [], []
    while len(xs) < 3 * s + 2:
        x = rng.randrange(p)
        if _peval(h, x, p) == 0 or x in xs:
            continue
        X1, Y1 = phi((x, 1))                     # y = 1: X1 = phi_x(x), Y1 = M(x)/psi(x)^3
        ps = _peval(h, x, p)
        xs.append(x)
        nx.append(X1 * ps * ps % p)
        my.append(Y1 * pow(ps, 3, p) % p)
    N = _interp(xs[:2 * s + 2], nx[:2 * s + 2], p)[:2 * s + 2]
    M = _interp(xs[:3 * s + 1], my[:3 * s + 1], p)[:3 * s + 1]
    while len(N) > 1 and N[-1] == 0:
        N.pop()
    for _ in range(4):                            # check on fresh affine points
        P = E.point(rng.randrange(1 << 30))
        Q = phi(P)
        if Q is None:
            continue
        ps = _peval(h, P[0], p)
        assert Q[0] == _peval(N, P[0], p) * pow(ps * ps, -1, p) % p, "x-map"
        assert Q[1] == P[1] * _peval(M, P[0], p) * pow(ps, -3, p) % p, "y-map"
    return {"N": N, "M": M, "psi": h, "ell": phi.ell}


def jacobian_step(pol: dict, P, p: int):
    """Reference evaluation of one homogenised step on a Jacobian point (Python, for checking C)."""
    X, Y, Z = P
    Z2 = Z * Z % p

    def hom(f, d):
        acc = 0
        for k in range(d, -1, -1):
            c = f[k] if k < len(f) else 0
            acc = (acc * X + c * pow(Z2, d - k, p)) % p
        return acc
    s = len(pol["psi"]) - 1
    return (hom(pol["N"], 2 * s + 1), Y * hom(pol["M"], 3 * s) % p, Z * hom(pol["psi"], s) % p)


def to_affine(P, p):
    X, Y, Z = P
    zi = pow(Z, -1, p)
    return (X * zi * zi % p, Y * zi * zi * zi % p)


