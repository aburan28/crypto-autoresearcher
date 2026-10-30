"""Numeric Semaev summation polynomials S_{n+1}(x_1..x_n, T) for EXP-MONO-1a1be2
(TASK-20261029-a97206): resultant recursion, squarefreeness, degree, distinct-degree
factorisation and the complete-split test, plus the group-law cross-check.

Curve y^2 = x^3 + a x + b over F = FQ (a, b in F). Conventions:

  S_2(x1, x2) = x1 - x2
  S_3(x1, x2, x3) = (x1-x2)^2 x3^2 - 2((x1+x2)(x1 x2 + a) + 2b) x3 + ((x1 x2 - a)^2 - 4b(x1+x2))
  S_{k+m}(x_1..x_{k+m}) = Res_X( S_{k+1}(x_1..x_k, X), S_{m+1}(x_{k+1}..x_{k+m}, X) )   (Semaev)

Defining property: S_{m+1}(x_1..x_{m+1}) = 0 iff there are points P_i with x(P_i) = x_i and
P_1 + ... + P_{m+1} = O (over the algebraic closure).

Numeric evaluation. With x_1..x_n numeric, the free variable T gives a univariate polynomial of
formal degree 2^{n-1}. The recursion used is

  S_{m}(Y, c_2..c_m) = Res_Z( S_3(Y, c_2, Z), S_{m-1}(Z, c_3..c_m) )

with S_{m-1}(Z, c_3..c_m) already a numeric polynomial P(Z) of formal degree D' = 2^{m-3}. For each
numeric Y = y0 the quadratic A(Z) = S_3(y0, c_2, Z) has leading coefficient (y0 - c_2)^2, nonzero for
y0 != c_2, and Res_Z(A, P) = a_2^{D'} * Norm(P(alpha)) = a_2^{D'} (r0^2 - alpha1 r0 r1 + alpha0 r1^2) where
r1 Z + r0 = P mod A (monic form A/a_2 = Z^2 + alpha1 Z + alpha0). The values at 2^{m-2}+1 points
y0 != c_2 are interpolated (Lagrange basis cached per point set). Formal degrees are kept, so the
result equals the Sylvester-resultant specialisation exactly (not only up to a unit).
"""
from __future__ import annotations

import itertools

import fqn
from curves import WCurve
from fqn import FQ, FQ2


def s3_quad(F: FQ, a, b, u, v):
    """Coefficients [c0, c1, c2] in z of S_3(u, v, z)."""
    uv = F.mul(u, v)
    s = F.add(u, v)
    d = F.sub(u, v)
    c2 = F.mul(d, d)
    inner = F.add(F.mul(s, F.add(uv, a)), F.smul(b, 2))
    c1 = F.neg(F.smul(inner, 2))
    t = F.sub(uv, a)
    c0 = F.sub(F.mul(t, t), F.smul(F.mul(b, s), 4))
    return [c0, c1, c2]


def s3_eval(F: FQ, a, b, x1, x2, x3):
    c0, c1, c2 = s3_quad(F, a, b, x1, x2)
    return F.add(F.add(F.mul(F.mul(c2, x3), x3), F.mul(c1, x3)), c0)


class _BasisCache:
    def __init__(self):
        self.d = {}

    def get(self, F, pts):
        key = (F.q, F.n, F.g, tuple(pts))
        hit = self.d.get(key)
        if hit is None:
            if len(self.d) > 4096:
                self.d.clear()
            hit = fqn.interpolation_basis(F, list(pts))
            self.d[key] = hit
        return hit


_BASIS = _BasisCache()


def _eval_points(F: FQ, count: int, avoid):
    """The first `count` field elements by code, skipping `avoid`."""
    if F.Q < count + 1:
        raise ValueError(f"field F_{F.Q} too small to interpolate degree {count - 1}")
    pts = []
    code = 0
    while len(pts) < count:
        e = F.from_code(code)
        code += 1
        if e != avoid:
            pts.append(e)
    return pts


def _poly_S(F: FQ, a, b, cs):
    """Formal-degree 2^{m-2} coefficient list (length 2^{m-2}+1) in the free variable Y of
    S_m(Y, c_2..c_m), cs = (c_2..c_m), m = len(cs)+1 >= 3."""
    m = len(cs) + 1
    if m == 3:
        return s3_quad(F, a, b, cs[0], cs[1])
    P = _poly_S(F, a, b, cs[1:])                 # formal degree D' = 2^{m-3}
    Dp = len(P) - 1
    c2 = cs[0]
    deg = 2 ** (m - 2)
    pts = _eval_points(F, deg + 1, c2)
    vals = []
    for y0 in pts:
        A0, A1, A2 = s3_quad(F, a, b, y0, c2)
        inv2 = F.inv(A2)
        al1, al0 = F.mul(A1, inv2), F.mul(A0, inv2)
        r1, r0 = F.zero, F.zero
        for pk in reversed(P):
            r1, r0 = F.sub(r0, F.mul(al1, r1)), F.add(F.neg(F.mul(al0, r1)), pk)
        norm = F.add(F.sub(F.mul(r0, r0), F.mul(al1, F.mul(r0, r1))), F.mul(al0, F.mul(r1, r1)))
        vals.append(F.mul(F.pow(A2, Dp), norm))
    basis = _BASIS.get(F, pts)
    out = [F.zero] * (deg + 1)
    for v, Lk in zip(vals, basis):
        if F.is_zero(v):
            continue
        for i, c in enumerate(Lk):
            out[i] = F.add(out[i], F.mul(v, c))
    return out


def semaev_poly(F: FQ, a, b, xs):
    """S_{n+1}(x_1..x_n, T) as a coefficient list in T (constant first) of formal degree 2^{n-1},
    length 2^{n-1}+1, n = len(xs) >= 2. Trailing entries may be zero (degree-deficient fibre)."""
    if len(xs) < 2:
        raise ValueError("need at least two x-coordinates")
    return _poly_S(F, a, b, tuple(xs))


def semaev_eval(F: FQ, a, b, xs, t):
    """S_{n+1}(x_1..x_n, t)."""
    return fqn.peval(F, semaev_poly(F, a, b, xs), t)


# ----------------------------------------------------------------------------- fibre analysis
def analyse_fibre(F: FQ, E, xs, detail: bool = True):
    """Everything arm B records for one x-tuple.

    Returns a dict with: degree (actual), full_degree (actual == 2^{n-1}), squarefree, chis (chi(f(x_i)) for
    each i as -1/0/+1), split_completely (None when the fibre is zero or not squarefree), and, when
    detail is True, ddf (list of (d, number of factors of degree d)), split_check_xq (independent
    x^Q = x test, same convention) and roots_Fq (the F_Q roots).

    With detail False the complete-split decision is the first stage of the distinct-degree
    factorisation (g = gcd(x^Q - x, f) has the degree of f), which is all the contract's M3/M4 need;
    the full factorisation pattern, the independent test and the roots are then skipped for speed."""
    n = len(xs)
    poly = fqn.ptrim(F, list(semaev_poly(F, E.a, E.b, xs)))
    out = {"n": n, "degree": len(poly) - 1 if poly else None, "zero_poly": not poly}
    out["full_degree"] = bool(poly) and len(poly) - 1 == 2 ** (n - 1)
    out["chis"] = [F.chi(E.f(x)) for x in xs]
    if not poly or len(poly) < 2:
        out.update(squarefree=False, ddf=None, split_completely=None, split_check_xq=None, roots_Fq=[])
        return out
    sf = fqn.is_squarefree(F, poly)
    out["squarefree"] = sf
    if not sf:
        out.update(ddf=None, split_completely=None, split_check_xq=None, roots_Fq=fqn.roots(F, poly) if detail else None)
        return out
    if detail:
        out["roots_Fq"] = fqn.roots(F, poly)
        fac = fqn.ddf(F, poly)
        out["ddf"] = [(d, len(g) - 1) for d, g in fac]
        out["split_completely"] = all(d == 1 for d, _ in fac)
        out["split_check_xq"] = fqn.splits_completely_xq(F, poly)
    else:
        f = fqn.pmonic(F, poly)
        x = [F.zero, F.one]
        h = fqn.ppowmod(F, x, F.Q, f)
        g = fqn.pgcd(F, fqn.psub(F, h, x), f)
        out.update(ddf=None, roots_Fq=None, split_check_xq=None, split_completely=(len(g) == len(f)))
    return out


# ----------------------------------------------------------------------------- group-law cross-check
def roots_via_group_law(F: FQ, E, xs, F2: FQ2 | None = None):
    """x-coordinates in F_Q of the signed sums sum_i eps_i P_i, eps_1 = +, where P_i is a lift of
    x_i over F_{Q^2}. Sums equal to O are skipped (and counted). Returns (sorted list of F_Q roots, #O sums)."""
    F2 = F2 or FQ2(F)
    E2 = WCurve(F2, F2.embed(E.a), F2.embed(E.b))
    pts = [(F2.embed(x), F2.lift_y(E.f(x))) for x in xs]
    found, n_inf = set(), 0
    for eps in itertools.product((1, -1), repeat=len(xs) - 1):
        S = pts[0]
        for e, P in zip(eps, pts[1:]):
            S = E2.add(S, P if e == 1 else E2.neg(P))
        if S is None:
            n_inf += 1
            continue
        if F.is_zero(S[0][1]):
            found.add(S[0][0])
    return sorted(found, key=F.to_code), n_inf
