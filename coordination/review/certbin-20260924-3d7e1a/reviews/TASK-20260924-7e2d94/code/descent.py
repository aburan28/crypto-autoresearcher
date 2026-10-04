"""Descent of S_3(x_1, x_2, x_R) to f_0..f_16 in B = F_2[v_0..v_17]/(v_i^2 + v_i).

TASK-20260924-7e2d94. Written from EXP-CERTBIN-4e92d7 object.unknowns and
object.descended_system only:
  x_1 = sum_{j<9} v_j t^j,  x_2 = sum_{j<9} v_{9+j} t^j,
  f_k = coefficient of t^k of the multilinearised expansion, k = 0..16.

A multilinear monomial is an 18-bit mask: bit i set <=> v_i divides it.
A Boolean polynomial is a Python set of masks (coefficient 1).

ROUTE 1 (symbolic): expand in F_2^17[v_0..v_17] with v^2 = v, using dict
  {mask: field element} and a generic polynomial product (monomial product =
  OR of masks), then read bit k of each coefficient.
ROUTE 2 (interpolation): evaluate S_3 directly in F_2^17 at all 2^18
  assignments (vectorised), then recover the algebraic normal form of each
  output bit by the binary Moebius transform (all 17 bits at once, packed).
The two routes must agree exactly.
"""
import numpy as np

import gf2n as F

NV = 18
L = 9
NPTS = 1 << NV


# ------------------------------------------------------------------ route 1
def _padd(p, q):
    r = dict(p)
    for m, c in q.items():
        r[m] = r.get(m, 0) ^ c
    return {m: c for m, c in r.items() if c}


def _pmul(p, q):
    r = {}
    for m1, c1 in p.items():
        for m2, c2 in q.items():
            m = m1 | m2                      # v_i^2 = v_i
            r[m] = r.get(m, 0) ^ F.mul(c1, c2)
    return {m: c for m, c in r.items() if c}


def _const(c):
    return {0: c} if c else {}


X1 = {1 << j: 1 << j for j in range(L)}
X2 = {1 << (L + j): 1 << j for j in range(L)}


def descend_symbolic(xR, B):
    xr = _const(xR)
    x1x2 = _pmul(X1, X2)
    s = _padd(_padd(x1x2, _pmul(X1, xr)), _pmul(X2, xr))
    S = _padd(_padd(_pmul(s, s), _pmul(x1x2, xr)), _const(B))
    eqs = []
    for k in range(F.N):
        eqs.append(frozenset(m for m, c in S.items() if (c >> k) & 1))
    return eqs, S


# ------------------------------------------------------------------ route 2
_V = np.arange(NPTS, dtype=np.uint64)
_X1V = _V & np.uint64((1 << L) - 1)                       # bit j of v -> t^j
_X2V = (_V >> np.uint64(L)) & np.uint64((1 << L) - 1)     # bit 9+j of v -> t^j
_X1X2V = F.vmul(_X1V, _X2V)


def s3_values_all(xR, B):
    """S_3(x_1(v), x_2(v), x_R) for every v in 0..2^18-1, as uint64 field elements."""
    xr = np.uint64(xR)
    s = _X1X2V ^ F.vmul(_X1V, xr) ^ F.vmul(_X2V, xr)
    return F.vmul(s, s) ^ F.vmul(_X1X2V, xr) ^ np.uint64(B)


def moebius(values):
    """ANF over F_2 of 17 packed Boolean functions on F_2^18 (XOR-linear, so packed bits work)."""
    a = values.astype(np.uint32).copy()
    for i in range(NV):
        a = a.reshape(-1, 2, 1 << i)
        a[:, 1, :] ^= a[:, 0, :]
        a = a.reshape(-1)
    return a


def descend_interpolation(xR, B):
    vals = s3_values_all(xR, B)
    anf = moebius(vals)
    nz = np.nonzero(anf)[0]
    eqs = [set() for _ in range(F.N)]
    for m in nz.tolist():
        c = int(anf[m])
        for k in range(F.N):
            if (c >> k) & 1:
                eqs[k].add(m)
    return [frozenset(e) for e in eqs], vals


def popcount(m):
    return bin(m).count("1")


def max_degree(eqs):
    return max((popcount(m) for e in eqs for m in e), default=-1)
