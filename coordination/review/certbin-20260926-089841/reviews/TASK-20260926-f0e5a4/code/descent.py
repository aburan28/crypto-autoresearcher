"""Weil descent of S_3(x_1, x_2, x_R) to 17 Boolean equations, by two routes.

Route A (symbolic): expand S_3 in F_{2^17}[v_0..v_17] with v^2 = v
(multilinear products, coefficients in F_{2^17}); equation k = bit k of each
monomial's coefficient.
Route B (interpolation): evaluate S_3(x_1(u), x_2(u), x_R) directly in
F_{2^17} at all 2^18 assignments u, then take the binary Moebius transform
(algebraic normal form) of each of the 17 output bits.

x_1 = sum_{j<9} v_j t^j, x_2 = sum_{j<9} v_{9+j} t^j (EXP-CERTBIN-4e92d7
object.unknowns). Imports nothing from this repository.
"""
import numpy as np

from gf2_17 import mul, vmul, vsq, N
from layout import MASK_TO_COL, NCOL, NEQ, NV

L = 9


# ---------------- Route A: symbolic ----------------

def padd(*polys):
    out = {}
    for P in polys:
        for m, c in P.items():
            v = out.get(m, 0) ^ c
            if v:
                out[m] = v
            elif m in out:
                del out[m]
    return out


def pmul(P, Q):
    out = {}
    for m1, c1 in P.items():
        for m2, c2 in Q.items():
            m = m1 | m2
            v = out.get(m, 0) ^ mul(c1, c2)
            if v:
                out[m] = v
            elif m in out:
                del out[m]
    return out


X1 = {1 << j: 1 << j for j in range(L)}
X2 = {1 << (L + j): 1 << j for j in range(L)}


def symbolic_S3(xR, B):
    X3 = {0: xR} if xR else {}
    s1 = padd(pmul(X1, X2), pmul(X1, X3), pmul(X2, X3))
    S = padd(pmul(s1, s1), pmul(pmul(X1, X2), X3), ({0: B} if B else {}))
    return S


def poly_to_rows(S):
    """F_{2^17}-coefficient multilinear polynomial -> 17 row ints.
    Raises if a monomial of degree > 2 survives."""
    rows = [0] * NEQ
    for m, c in S.items():
        if m not in MASK_TO_COL:
            raise ValueError("monomial of degree > 2 in descent: mask %x" % m)
        j = MASK_TO_COL[m]
        for k in range(NEQ):
            if (c >> k) & 1:
                rows[k] |= 1 << j
    return rows


def descent_symbolic(xR, B):
    return poly_to_rows(symbolic_S3(xR, B))


# ---------------- Route B: interpolation from direct evaluation ----------------

NA = 1 << NV
_U = np.arange(NA, dtype=np.int64)


def x1_of_u(u):
    out = np.zeros_like(u)
    for j in range(L):
        out ^= ((u >> j) & 1) << j
    return out


def x2_of_u(u):
    out = np.zeros_like(u)
    for j in range(L):
        out ^= ((u >> (L + j)) & 1) << j
    return out


_X1U = x1_of_u(_U)
_X2U = x2_of_u(_U)
_X1X2U = vmul(_X1U, _X2U)


def eval_S3_all(xR, B):
    """S_3(x1(u), x2(u), xR) = (x1x2 + x1xR + x2xR)^2 + x1x2xR + B, literally,
    for all u in [0, 2^18)."""
    x3 = np.int64(xR)
    s1 = _X1X2U ^ vmul(_X1U, x3) ^ vmul(_X2U, x3)
    return vsq(s1) ^ vmul(vmul(_X1U, _X2U), x3) ^ np.int64(B)


def moebius(vals):
    a = vals.copy()
    for i in range(NV):
        step = 1 << i
        v = a.reshape(-1, 2 * step)
        v[:, step:] ^= v[:, :step]
    return a


_POP = np.array([bin(i).count("1") for i in range(NA)], dtype=np.int64)
DEG_LE2 = np.flatnonzero(_POP <= 2)


def descent_interpolated(xR, B):
    vals = eval_S3_all(xR, B)
    anf = moebius(vals)
    high = np.flatnonzero((anf != 0) & (_POP > 2))
    if high.size:
        raise ValueError("ANF has %d monomials of degree > 2" % high.size)
    rows = [0] * NEQ
    for m in DEG_LE2.tolist():
        c = int(anf[m])
        if c:
            j = MASK_TO_COL[m]
            for k in range(NEQ):
                if (c >> k) & 1:
                    rows[k] |= 1 << j
    return rows, vals


def count_zeros_direct(vals):
    """s by direct field evaluation: #{u : S_3(x1(u), x2(u), xR) = 0}."""
    idx = np.flatnonzero(vals == 0)
    return int(idx.size), idx


# ---------------- convolution forms and union support ----------------

def Q_rows():
    """Q_k = sum_{i+j=k} v_i v_{9+j}, i, j in 0..8, as 17 row ints."""
    rows = [0] * NEQ
    for i in range(L):
        for j in range(L):
            m = (1 << i) | (1 << (L + j))
            rows[i + j] ^= 1 << MASK_TO_COL[m]
    return rows


def union_support(B, descent_fn):
    """U_k = supp(E^0_k) union (union_j supp(E^j_k)), E^0 = E_S3(0),
    E^j = E_S3(t^j) xor E^0 (object.union_support)."""
    E0 = descent_fn(0, B)
    U = list(E0)
    Ej = []
    for j in range(N):
        Etj = descent_fn(1 << j, B)
        D = [a ^ b for a, b in zip(Etj, E0)]
        Ej.append(D)
        for k in range(NEQ):
            U[k] |= D[k]
    return U, E0, Ej


def S_L_positions(U):
    """S_L = U cap (columns 0..18), row-major (k ascending, then column)."""
    out = []
    for k in range(NEQ):
        for j in range(19):
            if (U[k] >> j) & 1:
                out.append((k, j))
    return out
