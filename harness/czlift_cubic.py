"""Arithmetic in K = Q(theta), theta^3 = 2, O_K = Z[theta], for IDEA-20261009-105291.

Elements are integer triples (c0, c1, c2) = c0 + c1 theta + c2 theta^2.
Rational points of E/Q over K are searched as x = alpha / d^2, Y = gamma / d^3
with alpha, gamma in Z[theta]; the square test Y^2 = g(x) is decided by the
three complex embeddings (one real, one conjugate pair): the candidate
coordinates of gamma are solved from the numeric square roots and verified
EXACTLY in Z[theta]. Reduction mod a split prime p (p = 1 mod 3 with 2 a
cube) sends theta to a cube root of 2 in F_p.
"""
from __future__ import annotations

import cmath
import math

THETA = 2 ** (1 / 3)
OMEGA = complex(-0.5, math.sqrt(3) / 2)
EMB = (complex(THETA), THETA * OMEGA, THETA * OMEGA * OMEGA)


def mul(a, b):
    a0, a1, a2 = a; b0, b1, b2 = b
    # theta^3 = 2, theta^4 = 2 theta
    return (a0 * b0 + 2 * (a1 * b2 + a2 * b1), a0 * b1 + a1 * b0 + 2 * a2 * b2, a0 * b2 + a1 * b1 + a2 * b0)


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def scale(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def embed(a, i):
    t = EMB[i]
    return a[0] + a[1] * t + a[2] * t * t


def g_value(alpha, d, b2, b4, b6):
    """gamma^2 target: d^6 g(alpha/d^2) = 4 alpha^3 + b2 alpha^2 d^2 + 2 b4 alpha d^4 + b6 d^6 in Z[theta]."""
    a2 = mul(alpha, alpha); a3 = mul(a2, alpha)
    return add(add(scale(a3, 4), scale(a2, b2 * d * d)), add(scale(alpha, 2 * b4 * d ** 4), (b6 * d ** 6, 0, 0)))


def exact_sqrt(G):
    """gamma in Z[theta] with gamma^2 = G, or None."""
    g0 = embed(G, 0)
    if g0.real < -1e-9:
        return None
    r0 = math.sqrt(max(g0.real, 0.0))
    r1 = cmath.sqrt(embed(G, 1))
    # solve c0 + c1 t_i + c2 t_i^2 = r_i for i = 0, 1, 2 with r_2 = conj(r_1); use real/imag parts of embedding 1
    # Basis values: t0 = THETA, t1 = THETA*OMEGA (complex); equations: real: c0 + c1 t0 + c2 t0^2 = +-r0
    #   complex: c0 + c1 t1 + c2 t1^2 = +-r1 -> two real equations
    t0 = THETA; t1 = EMB[1]
    for s0 in (1, -1):
        for s1 in (1, -1):
            # 3x3 real system
            Mx = [[1.0, t0, t0 * t0], [1.0, t1.real, (t1 * t1).real], [0.0, t1.imag, (t1 * t1).imag]]
            rhs = [s0 * r0, (s1 * r1).real, (s1 * r1).imag]
            sol = _solve3(Mx, rhs)
            if sol is None:
                continue
            cand = tuple(int(round(v)) for v in sol)
            if mul(cand, cand) == tuple(G):
                return cand
    return None


def _solve3(M, b):
    import copy
    A = [row[:] + [bv] for row, bv in zip(M, b)]
    n = 3
    for i in range(n):
        piv = max(range(i, n), key=lambda r: abs(A[r][i]))
        if abs(A[piv][i]) < 1e-12:
            return None
        A[i], A[piv] = A[piv], A[i]
        for r in range(n):
            if r != i:
                f = A[r][i] / A[i][i]
                for c in range(i, n + 1):
                    A[r][c] -= f * A[i][c]
    return [A[i][n] / A[i][i] for i in range(n)]


def search_points(ainvs, H: int, dmax: int):
    """All (alpha, d, gamma) with x = alpha/d^2, |coords of alpha| <= H, 1 <= d <= dmax, gamma^2 = d^6 g(x)."""
    a1, a2, a3, a4, a6 = ainvs
    b2 = a1 * a1 + 4 * a2; b4 = 2 * a4 + a1 * a3; b6 = a3 * a3 + 4 * a6
    pts = []
    for d in range(1, dmax + 1):
        for c0 in range(-H, H + 1):
            for c1 in range(-H, H + 1):
                for c2 in range(-H, H + 1):
                    if math.gcd(math.gcd(abs(c0), abs(c1)), math.gcd(abs(c2), d)) != 1:
                        continue
                    alpha = (c0, c1, c2)
                    G = g_value(alpha, d, b2, b4, b6)
                    if embed(G, 0).real < -1e-6:
                        continue
                    gamma = exact_sqrt(G)
                    if gamma is None:
                        continue
                    pts.append((alpha, d, gamma))
                    if gamma != (0, 0, 0):
                        pts.append((alpha, d, (-gamma[0], -gamma[1], -gamma[2])))
    return pts


def height(pt) -> int:
    alpha, d, _ = pt
    return max(max(abs(c) for c in alpha), d * d)


def cube_roots_of_2(p: int):
    return [r for r in range(p) if pow(r, 3, p) == 2 % p]


def reduce_point(ainvs, pt, p: int, root: int):
    a1, a2, a3, a4, a6 = ainvs
    alpha, d, gamma = pt
    if d % p == 0:
        return "O"
    di = pow(d % p, -1, p)
    x = (alpha[0] + alpha[1] * root + alpha[2] * root * root) * di * di % p
    Y = (gamma[0] + gamma[1] * root + gamma[2] * root * root) * di ** 3 % p
    y = (Y - a1 * x - a3) * pow(2, -1, p) % p
    return (x, y)
