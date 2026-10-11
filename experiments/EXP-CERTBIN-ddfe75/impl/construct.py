"""Family construction: own S_3 descent E_S3(x_R), its parts, the union support
U and S_L, and the N-CONV17 kept part.

S_3(x_1, x_2, x_3) = (x_1x_2 + x_1x_3 + x_2x_3)^2 + x_1x_2x_3 + B with
x_1 = sum_{i<9} v_i t^i, x_2 = sum_{j<9} v_{9+j} t^j, x_3 = x_R, v Boolean.
In characteristic 2 with v^2 = v the expansion is exactly
  v_i v_{9+j}:  t^{2(i+j)} + x_R t^{i+j}      (= phi_{x_R}(t^{i+j}))
  v_i, v_{9+j}: x_R^2 t^{2i}, x_R^2 t^{2j}
  1:            B
Row k of E is bit k of every coefficient. C-SELF checks this against direct
field evaluation of S_3 on random (v, x_R).
"""
from __future__ import annotations

import gf2n
from common import COL_OF, NCOL, NEQ

_TP = [gf2n.tpow(j) for j in range(40)]


def coeffs_s3(xR, B):
    """dict column -> F_{2^17} coefficient of S_3(x_1, x_2, x_R)."""
    c = {}
    xR2 = gf2n.sq(xR)
    for i in range(9):
        for j in range(9):
            c[COL_OF[(i, 9 + j)]] = _TP[2 * (i + j)] ^ gf2n.mul(xR, _TP[i + j])
    for i in range(9):
        c[COL_OF[(i,)]] = gf2n.mul(xR2, _TP[2 * i])
        c[COL_OF[(9 + i,)]] = gf2n.mul(xR2, _TP[2 * i])
    c[0] = B
    return c


def coeffs_to_rows(c):
    rows = [0] * NEQ
    for col, v in c.items():
        for k in range(NEQ):
            if (v >> k) & 1:
                rows[k] |= 1 << col
    return rows


def e_s3(xR, B):
    return coeffs_to_rows(coeffs_s3(xR, B))


def qpart(xR, B=0):
    c = coeffs_s3(xR, B)
    return coeffs_to_rows({k: v for k, v in c.items() if k >= 19})


def lpart(xR, B=0):
    c = coeffs_s3(xR, B)
    return coeffs_to_rows({k: v for k, v in c.items() if 1 <= k <= 18})


def const_rows(B):
    return coeffs_to_rows({0: B})


def union_support(B):
    """U_k = supp(E^0_k) | union_j supp(E^j_k); E^0 = E_S3(0), E^j = E_S3(t^j) ^ E^0.
    Returns list of 17 row masks (ints)."""
    E0 = e_s3(0, B)
    U = list(E0)
    for j in range(17):
        Ej = e_s3(_TP[j], B)
        for k in range(NEQ):
            U[k] |= Ej[k] ^ E0[k]
    return U


def s_l_positions(U):
    """S_L = U cap columns 0..18 in row-major order: list of (k, col)."""
    return [(k, c) for k in range(NEQ) for c in range(19) if (U[k] >> c) & 1]


def conv17_rows():
    """Row k quadratic part Q_k = sum_{i+j=k} v_i v_{9+j} (i, j in 0..8)."""
    rows = [0] * NEQ
    for i in range(9):
        for j in range(9):
            rows[i + j] |= 1 << COL_OF[(i, 9 + j)]
    return rows


def eval_s3_direct(v_bits, xR, B):
    """Direct F_{2^17} evaluation of S_3(x_1(v), x_2(v), x_R) for an 18-bit v."""
    x1 = 0
    x2 = 0
    for i in range(9):
        if (v_bits >> i) & 1:
            x1 ^= _TP[i]
        if (v_bits >> (9 + i)) & 1:
            x2 ^= _TP[i]
    m = gf2n.mul
    s = m(x1, x2) ^ m(x1, xR) ^ m(x2, xR)
    return gf2n.sq(s) ^ m(m(x1, x2), xR) ^ B


def eval_rows(rows, u):
    """Evaluate the 17 equations at assignment u (bit i = v_i) -> 17-bit int."""
    from common import COLS
    out = 0
    for k, r in enumerate(rows):
        acc = 0
        x = r
        while x:
            b = (x & -x).bit_length() - 1
            m = COLS[b]
            val = 1
            for i in m:
                val &= (u >> i) & 1
            acc ^= val
            x &= x - 1
        out |= acc << k
    return out


def ell_coeffs(xR):
    """c_k = Tr(t^k / x_R^2) (C-ELL)."""
    ixr2 = gf2n.inv(gf2n.sq(xR))
    return [gf2n.trace(gf2n.mul(_TP[k], ixr2)) for k in range(NEQ)]


assert NCOL == 172
