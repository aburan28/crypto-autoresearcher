"""Monomial layouts, the descended S_3 system E_S3(x_R), the union support U
and S_L, written from EXP-CERTBIN-ddfe75 object (E_layout, parts,
union_support) and EXP-CERTBIN-4e92d7 object (descended_system).

E_layout: a system is a 17 x 172 F_2 matrix E; column j is the j-th monomial
of mu_order(2, 18) (degree ascending, then ascending sorted index tuple).
"""
from itertools import combinations
import numpy as np

import br_field as F

NV = 18
NEQ = 17


def mu_order(d, nv):
    """Multilinear monomials of degree <= d in nv variables, ordered by degree
    ascending, then ascending sorted index tuple (lexicographic)."""
    out = []
    for deg in range(d + 1):
        out.extend(combinations(range(nv), deg))
    return out


def mask_of(mono):
    m = 0
    for i in mono:
        m |= 1 << i
    return m


def tuple_of(mask):
    out = []
    i = 0
    while mask:
        if mask & 1:
            out.append(i)
        mask >>= 1
        i += 1
    return tuple(out)


E_MONOS = mu_order(2, NV)                       # 172
E_MASKS = [mask_of(m) for m in E_MONOS]
E_COL = {m: j for j, m in enumerate(E_MASKS)}   # mask -> column
NCOL_E = len(E_MONOS)
assert NCOL_E == 172
QUAD_COLS = list(range(1 + NV, NCOL_E))         # 19..171
LIN_COLS = list(range(1, 1 + NV))               # 1..18
CONST_COL = 0
BILINEAR_COLS = sorted(E_COL[mask_of((i, 9 + j))] for i in range(9) for j in range(9))


def x1_of(v):
    return v & 0x1FF


def x2_of(v):
    return (v >> 9) & 0x1FF


# ----------------------------------------------------------------------------
# Route A: algebraic expansion of S_3(x_1, x_2, x_R) in v_0..v_17.
# In characteristic 2, (x1x2 + x1xR + x2xR)^2 = x1^2x2^2 + x1^2xR^2 + x2^2xR^2,
# x1^2 = sum_i v_i t^{2i} after v^2 = v, and x1x2 = sum_{i,j} v_i v_{9+j} t^{i+j}.
# ----------------------------------------------------------------------------
def coefficients_S3(xR, B):
    """Map E-column -> F_2^17 coefficient of that monomial in the multilinear
    expansion of S_3(x1, x2, xR)."""
    coef = {}

    def acc(col, c):
        coef[col] = coef.get(col, 0) ^ c

    xR2 = F.sqr(xR)
    acc(CONST_COL, B)
    for i in range(9):
        acc(E_COL[1 << i], F.mul(F.t_pow(2 * i), xR2))            # x1^2 xR^2
        acc(E_COL[1 << (9 + i)], F.mul(F.t_pow(2 * i), xR2))      # x2^2 xR^2
    for i in range(9):
        for j in range(9):
            col = E_COL[(1 << i) | (1 << (9 + j))]
            acc(col, F.t_pow(2 * (i + j)))                      # x1^2 x2^2
            acc(col, F.mul(F.t_pow(i + j), xR))                  # x1 x2 xR
    return coef


def E_S3(xR, B):
    """17 x 172 uint8 matrix; E[k, col] = bit k (coefficient of t^k)."""
    E = np.zeros((NEQ, NCOL_E), dtype=np.uint8)
    for col, c in coefficients_S3(xR, B).items():
        for k in range(NEQ):
            if (c >> k) & 1:
                E[k, col] = 1
    return E


# ----------------------------------------------------------------------------
# Route B (self-test only): evaluate S_3 at all 2^18 assignments with
# vectorized field arithmetic and read the algebraic normal form by a Moebius
# transform (XOR over F_2^17 values acts bitwise).
# ----------------------------------------------------------------------------
def anf_S3_direct(xR, B):
    u = np.arange(1 << NV, dtype=np.uint64)
    x1 = u & np.uint64(0x1FF)
    x2 = (u >> np.uint64(9)) & np.uint64(0x1FF)
    xr = np.uint64(xR)
    s = F.vmul(x1, x2) ^ F.vmul(x1, xr) ^ F.vmul(x2, xr)
    val = F.vmul(s, s) ^ F.vmul(F.vmul(x1, x2), xr) ^ np.uint64(B)
    a = val.copy()
    for i in range(NV):
        a = a.reshape(-1, 2, 1 << i)
        a[:, 1, :] ^= a[:, 0, :]
        a = a.reshape(-1)
    return a      # a[mask] = F_2^17 coefficient of the monomial with that mask


def E_from_anf(anf):
    """Returns (E, max_degree_with_nonzero_coefficient)."""
    nz = np.flatnonzero(anf)
    maxdeg = max((bin(int(m)).count("1") for m in nz), default=-1)
    E = np.zeros((NEQ, NCOL_E), dtype=np.uint8)
    for m in nz:
        m = int(m)
        if bin(m).count("1") > 2:
            continue
        c = int(anf[m])
        col = E_COL[m]
        for k in range(NEQ):
            if (c >> k) & 1:
                E[k, col] = 1
    return E, maxdeg


# ----------------------------------------------------------------------------
# Union support U and S_L
# ----------------------------------------------------------------------------
def union_support(B):
    E0 = E_S3(0, B)
    U = E0.astype(bool).copy()
    for j in range(F.N):
        Ej = E_S3(1 << j, B) ^ E0
        U |= Ej.astype(bool)
    return U


def S_L_positions(U):
    """S_L = U cap (columns 0..18), row-major: k ascending, then column ascending."""
    return [(k, c) for k in range(NEQ) for c in range(0, 1 + NV) if U[k, c]]


# ----------------------------------------------------------------------------
# encodings
# ----------------------------------------------------------------------------
def row_ints(E):
    out = []
    for k in range(E.shape[0]):
        x = 0
        for j in np.flatnonzero(E[k]):
            x |= 1 << int(j)
        out.append(x)
    return out


def row_hex(E):
    """17 rows, bit j = column j, lowercase hex without prefix (no padding)."""
    return [format(x, "x") for x in row_ints(E)]


def E_from_equations(equations, nv=NV):
    cols = {mask_of(m): j for j, m in enumerate(mu_order(2, nv))}
    E = np.zeros((len(equations), len(cols)), dtype=np.uint8)
    for k, eq in enumerate(equations):
        for mono in eq:
            c = cols[mask_of(mono)]
            E[k, c] ^= 1
    return E


def equations_from_E(E, nv=NV):
    monos = mu_order(2, nv)
    return [[list(monos[j]) for j in np.flatnonzero(E[k])] for k in range(E.shape[0])]


def conv17_quadratic():
    """Q_k = sum_{i+j=k} v_i v_{9+j} on the quadratic columns, k = 0..16."""
    Q = np.zeros((NEQ, NCOL_E), dtype=np.uint8)
    for i in range(9):
        for j in range(9):
            Q[i + j, E_COL[(1 << i) | (1 << (9 + j))]] ^= 1
    return Q


def eval_system_at(E, v, nv=NV):
    """Evaluate the rows of E (columns in mu_order(2, nv)) at assignment v
    (bit i = v_i). Returns a list of bits."""
    monos = mu_order(2, nv)
    vals = [1 if all((v >> i) & 1 for i in m) else 0 for m in monos]
    out = []
    for k in range(E.shape[0]):
        s = 0
        for j in np.flatnonzero(E[k]):
            s ^= vals[j]
        out.append(s)
    return out
