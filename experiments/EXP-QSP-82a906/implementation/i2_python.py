#!/usr/bin/env python3
"""I2: Newton interpolation of Res_Y over F_{2^n}. Independent of I1 Bareiss."""
from __future__ import annotations

from f2arith import deg, gf_eval_f2poly, gf_inv, gf_mul, polymod, clmul


def _trim_k(f: list[int]) -> list[int]:
    r = list(f)
    while r and r[-1] == 0:
        r.pop()
    return r


def eval_y_at_x(f_y: list[int], alpha: int, mod: int) -> list[int]:
    """Evaluate each F_2[X] Y-coeff at X=alpha in K; KEEP length (formal Y-degree)."""
    return [gf_eval_f2poly(c, alpha, mod) for c in f_y]


def sylvester_det_k(f: list[int], g: list[int], n: int, mod: int) -> int:
    """Sylvester determinant over K using formal lengths (zero leadings allowed)."""
    if not f or not g:
        return 0
    m, k = len(f) - 1, len(g) - 1
    if m < 0 or k < 0:
        return 0
    if m == 0 and k == 0:
        return 1
    if m == 0:
        return gf_pow_local(f[0], k, n, mod)
    if k == 0:
        return gf_pow_local(g[0], m, n, mod)
    N = m + k
    M = [[0] * N for _ in range(N)]
    for i in range(k):
        for t, c in enumerate(f):
            if i + t < N:
                M[i][i + t] = c
    for i in range(m):
        for t, c in enumerate(g):
            if i + t < N:
                M[k + i][i + t] = c
    det = 1
    for col in range(N):
        piv = None
        for r in range(col, N):
            if M[r][col]:
                piv = r
                break
        if piv is None:
            return 0
        if piv != col:
            M[col], M[piv] = M[piv], M[col]
        inv = gf_inv(M[col][col], n, mod)
        det = gf_mul(det, M[col][col], mod)
        for r in range(col + 1, N):
            if M[r][col] == 0:
                continue
            fac = gf_mul(M[r][col], inv, mod)
            for c in range(col, N):
                M[r][c] ^= gf_mul(fac, M[col][c], mod)
    return det


def gf_pow_local(a: int, e: int, n: int, mod: int) -> int:
    r = 1
    while e:
        if e & 1:
            r = gf_mul(r, a, mod)
        a = gf_mul(a, a, mod)
        e >>= 1
    return r


def newton_interpolate(xs: list[int], ys: list[int], n: int, mod: int) -> list[int]:
    k = len(xs)
    dd = ys[:]
    for j in range(1, k):
        for i in range(k - 1, j - 1, -1):
            num = dd[i] ^ dd[i - 1]
            den = xs[i] ^ xs[i - j]
            dd[i] = gf_mul(num, gf_inv(den, n, mod), mod)
    poly = []
    for i in range(k - 1, -1, -1):
        # poly := dd[i] + poly * (X + xs[i])
        shifted = [0] * (len(poly) + 1)
        for t, c in enumerate(poly):
            shifted[t + 1] ^= c
            shifted[t] ^= gf_mul(c, xs[i], mod)
        if not shifted:
            shifted = [0]
        shifted[0] ^= dd[i]
        poly = _trim_k(shifted)
    return poly


def resultant_i2(f_y: list[int], g_y: list[int], n: int, mod: int) -> tuple[int, bool, int]:
    """Return (deg_elim, identically_zero, bitpacked F_2[X] poly if in F_2).

    The bitpacked int is 0 if identically zero; if the interpolated poly has
    a coefficient outside F_2, the int is -1 and the caller must treat the
    K[X] list as the eliminant (stored separately).
    """
    f_y = [c for c in f_y]
    g_y = [c for c in g_y]
    while f_y and f_y[-1] == 0:
        f_y.pop()
    while g_y and g_y[-1] == 0:
        g_y.pop()
    if not f_y or not g_y:
        return -1, True, 0

    max_cx = 0
    for c in f_y + g_y:
        if c:
            max_cx = max(max_cx, deg(c))
    df = len(f_y) - 1
    dg = len(g_y) - 1
    bound = (df + dg) * max(max_cx, 0) + 4
    bound = max(bound, 8)
    # Distinct evaluation points: 1,2,3,... as field elements.
    xs = []
    ys = []
    alpha = 1
    while len(xs) < bound + 1:
        if alpha >= (1 << n):
            break
        fv = eval_y_at_x(f_y, alpha, mod)
        gv = eval_y_at_x(g_y, alpha, mod)
        ys.append(sylvester_det_k(fv, gv, n, mod))
        xs.append(alpha)
        alpha += 1
    if all(y == 0 for y in ys):
        return -1, True, 0
    poly_k = newton_interpolate(xs, ys, n, mod)
    # Drop leading zeros already trimmed. Check F_2 coefficients.
    packed = 0
    for i, c in enumerate(poly_k):
        if c not in (0, 1):
            return deg(packed) if packed else (len(poly_k) - 1), False, -1
        if c:
            packed |= 1 << i
    if packed == 0:
        return -1, True, 0
    return deg(packed), False, packed
