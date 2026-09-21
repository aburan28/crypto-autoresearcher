#!/usr/bin/env python3
"""rt_degree_probe.py -- RED TEAM instrument for TASK-20260904-6681da, joint R1.

Purpose: measure, independently of every record in the repository, two things.

 (P1) The total degree Delta(m) of the Semaev summation polynomial
      S_{m+1}(x_1, ..., x_m, x_R) in the m UNKNOWNS (x_R numeric), and its
      per-variable degrees, for m = 2, 3, 4, 5.
 (P2) The degree of the DIGIT-SUBSTITUTED, MULTILINEARLY REDUCED generator
      S~ = S_{m+1}(ell_1, ..., ell_m, x_R) mod (a_{k,i}^2 - a_{k,i}) at small
      (m, s), by exhibiting a nonzero coefficient of a degree-Delta squarefree
      monomial (Moebius inversion over the Boolean cube).

Method for (P1): black-box evaluation over F_p (p = 2^61 - 1) plus exact
Lagrange interpolation along a random line x_k = t u_k. Semaev polynomials are
built by the standard resultant recursion, the same route used by
EXP-PFDR-5726af Stage 0:
      S_3(x, y, z) = (x-y)^2 z^2 - 2((x+y)(xy+a) + 2b) z + (xy-a)^2 - 4b(x+y)
      S_4(x1,x2,x3,x4)   = Res_T(S_3(x1,x2,T), S_3(x3,x4,T))
      S_5(x1,...,x5)     = Res_T(S_4(x1,x2,x3,T), S_3(x4,x5,T))
      S_6(x1,...,x6)     = Res_T(S_4(x1,x2,x3,T), S_4(x4,x5,x6,T))
Every resultant is the determinant of a Sylvester matrix built at FIXED formal
degrees, so the numeric value is the specialisation of the polynomial
resultant.  Deterministic: the "random" a, b, x_R, u are drawn from a seeded
PRNG and printed.

This is a DERIVATION AID for a review report.  It is not an experiment, it
touches no curve group law, it samples no point, it produces no run record.
Standard library only.
"""
import json
import random
from itertools import combinations

P = (1 << 61) - 1  # prime


# ---------------------------------------------------------------- linear algebra
def det_mod(mat, p=P):
    """Determinant of a square matrix over F_p by Gaussian elimination."""
    a = [row[:] for row in mat]
    n = len(a)
    det = 1
    for c in range(n):
        piv = None
        for r in range(c, n):
            if a[r][c] % p:
                piv = r
                break
        if piv is None:
            return 0
        if piv != c:
            a[c], a[piv] = a[piv], a[c]
            det = (-det) % p
        det = det * a[c][c] % p
        inv = pow(a[c][c], p - 2, p)
        for r in range(c + 1, n):
            f = a[r][c] * inv % p
            if f:
                for k in range(c, n):
                    a[r][k] = (a[r][k] - f * a[c][k]) % p
    return det % p


def sylvester_res(f, g, p=P):
    """Resultant of f, g given as coefficient lists [c_d, ..., c_0] (leading
    first) at FIXED formal degrees d = len(f)-1, e = len(g)-1."""
    d, e = len(f) - 1, len(g) - 1
    n = d + e
    m = [[0] * n for _ in range(n)]
    for i in range(e):
        for j, c in enumerate(f):
            m[i][i + j] = c % p
    for i in range(d):
        for j, c in enumerate(g):
            m[e + i][i + j] = c % p
    return det_mod(m, p)


def lagrange_coeffs(xs, ys, p=P):
    """Exact coefficients (ascending) of the interpolating polynomial."""
    n = len(xs)
    coeffs = [0] * n
    for i in range(n):
        # basis polynomial prod_{j != i} (X - x_j) / (x_i - x_j)
        num = [1] + [0] * n
        deg = 0
        den = 1
        for j in range(n):
            if j == i:
                continue
            new = [0] * (n + 1)
            for k in range(deg + 1):
                new[k + 1] = (new[k + 1] + num[k]) % p
                new[k] = (new[k] - xs[j] * num[k]) % p
            num = new
            deg += 1
            den = den * (xs[i] - xs[j]) % p
        scale = ys[i] * pow(den, p - 2, p) % p
        for k in range(deg + 1):
            coeffs[k] = (coeffs[k] + scale * num[k]) % p
    return coeffs


def poly_degree(coeffs, p=P):
    d = -1
    for i, c in enumerate(coeffs):
        if c % p:
            d = i
    return d


# ---------------------------------------------------------------- Semaev
def s3_coeffs_in_T(x, y, a, b, p=P):
    """S_3(x, y, T) as [c2, c1, c0] (leading first)."""
    c2 = (x - y) ** 2 % p
    c1 = (-2 * ((x + y) * (x * y + a) + 2 * b)) % p
    c0 = ((x * y - a) ** 2 - 4 * b * (x + y)) % p
    return [c2, c1, c0]


def s3_eval(x, y, z, a, b, p=P):
    c2, c1, c0 = s3_coeffs_in_T(x, y, a, b, p)
    return (c2 * z * z + c1 * z + c0) % p


def s4_eval(x1, x2, x3, x4, a, b, p=P):
    return sylvester_res(s3_coeffs_in_T(x1, x2, a, b, p),
                         s3_coeffs_in_T(x3, x4, a, b, p), p)


def s4_coeffs_in_T(x1, x2, x3, a, b, p=P):
    """S_4(x1, x2, x3, T) as [c4, ..., c0] (leading first); formal degree 4."""
    xs = list(range(1, 6))
    ys = [s4_eval(x1, x2, x3, t, a, b, p) for t in xs]
    asc = lagrange_coeffs(xs, ys, p)          # ascending, length 5
    return list(reversed(asc))


def s5_eval(x1, x2, x3, x4, x5, a, b, p=P):
    return sylvester_res(s4_coeffs_in_T(x1, x2, x3, a, b, p),
                         s3_coeffs_in_T(x4, x5, a, b, p), p)


def s6_eval(x1, x2, x3, x4, x5, x6, a, b, p=P):
    return sylvester_res(s4_coeffs_in_T(x1, x2, x3, a, b, p),
                         s4_coeffs_in_T(x4, x5, x6, a, b, p), p)


def gen_eval(m, xs, xR, a, b, p=P):
    """S_{m+1}(x_1, ..., x_m, x_R)."""
    if m == 2:
        return s3_eval(xs[0], xs[1], xR, a, b, p)
    if m == 3:
        return s4_eval(xs[0], xs[1], xs[2], xR, a, b, p)
    if m == 4:
        return s5_eval(xs[0], xs[1], xs[2], xs[3], xR, a, b, p)
    if m == 5:
        return s6_eval(xs[0], xs[1], xs[2], xs[3], xs[4], xR, a, b, p)
    raise ValueError(m)


# ---------------------------------------------------------------- (P1)
def total_degree(m, a, b, xR, u, p=P):
    dmax = m * 2 ** (m - 1)
    xs = list(range(1, dmax + 2))
    ys = [gen_eval(m, [t * ui % p for ui in u], xR, a, b, p) for t in xs]
    return poly_degree(lagrange_coeffs(xs, ys, p), p), dmax


def per_variable_degree(m, idx, a, b, xR, base, p=P):
    dmax = 2 ** (m - 1)
    xs = list(range(1, dmax + 2))
    ys = []
    for t in xs:
        pt = list(base)
        pt[idx] = t
        ys.append(gen_eval(m, pt, xR, a, b, p))
    return poly_degree(lagrange_coeffs(xs, ys, p), p), dmax


# ---------------------------------------------------------------- (P2)
def substituted_coefficient(m, s, subset, a, b, xR, p=P):
    """Coefficient of prod_{i in subset} a_i in the multilinear (squarefree)
    reduction of S~ = S_{m+1}(ell_1, ..., ell_m, x_R), by Moebius inversion:
        c_S = sum_{T subset S} (-1)^{|S|-|T|} f(1_T),
    where f is the function on {0,1}^n induced by S~ and the digit map is
    ell_k = sum_{i < s} 2^i a_{k, i}."""
    tot = 0
    ln = len(subset)
    for r in range(ln + 1):
        for T in combinations(subset, r):
            bits = set(T)
            xs = []
            for k in range(m):
                v = 0
                for i in range(s):
                    if k * s + i in bits:
                        v += 1 << i
                xs.append(v % p)
            val = gen_eval(m, xs, xR, a, b, p)
            tot += val if (ln - r) % 2 == 0 else -val
    return tot % p


def main():
    rng = random.Random(20260904)
    a = rng.randrange(2, P)
    b = rng.randrange(2, P)
    xR = rng.randrange(2, P)
    out = {"p": P, "a": a, "b": b, "x_R": xR, "seed": 20260904, "P1": [], "P2": []}

    for m in (2, 3, 4, 5):
        u = [rng.randrange(1, P) for _ in range(m)]
        deg, dmax = total_degree(m, a, b, xR, u, P)
        base = [rng.randrange(1, P) for _ in range(m)]
        pvd = [per_variable_degree(m, i, a, b, xR, base, P)[0] for i in range(m)]
        out["P1"].append({
            "m": m,
            "generator": f"S_{m+1}(x_1..x_{m}, x_R)",
            "total_degree_in_unknowns_measured": deg,
            "m_times_2^(m-1)": dmax,
            "per_variable_degrees_measured": pvd,
            "2^(m-1)": 2 ** (m - 1),
            "direction_u": u,
        })
        print(f"m={m}: total degree {deg} (m 2^(m-1) = {dmax}); "
              f"per-variable {pvd} (2^(m-1) = {2**(m-1)})")

    # (P2) small (m, s): exhibit a nonzero degree-Delta coefficient of the
    # multilinearly reduced digit-substituted generator.
    for (m, s) in ((2, 2), (2, 3), (2, 5), (3, 4)):
        n = m * s
        delta = m * min(2 ** (m - 1), s)
        # take the "block-balanced" subset: the first min(2^{m-1}, s) digits of
        # each block
        e = min(2 ** (m - 1), s)
        subset = [k * s + i for k in range(m) for i in range(e)]
        c = substituted_coefficient(m, s, subset, a, b, xR, P)
        # also check every squarefree monomial of degree delta + 1 (only where
        # cheap) to confirm the degree is exactly delta
        higher_nonzero = None
        if n <= 10 and delta + 1 <= n:
            higher_nonzero = 0
            for S in combinations(range(n), delta + 1):
                if substituted_coefficient(m, s, list(S), a, b, xR, P):
                    higher_nonzero += 1
        out["P2"].append({
            "m": m, "s": s, "n": n,
            "predicted_deg_Stilde": delta,
            "monomial": subset,
            "coefficient_nonzero": bool(c),
            "coefficient": c,
            "count_nonzero_coefficients_at_degree_delta_plus_1": higher_nonzero,
        })
        print(f"(m={m}, s={s}): deg-{delta} coefficient nonzero: {bool(c)}; "
              f"nonzero coefficients at degree {delta+1}: {higher_nonzero}")

    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
