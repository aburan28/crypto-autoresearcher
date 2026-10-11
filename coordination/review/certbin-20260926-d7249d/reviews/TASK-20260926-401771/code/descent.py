"""Descent of S_3(x_1, x_2, x_R) to f_0..f_18 by two independent routes.

Route A (symbolic): expand S_3 in F_{2^19}[v_0..v_19]/(v^2 = v) with the
Python field (gf19.mul), monomial product = mask OR, coefficients XORed.
Route B (interpolation): evaluate S_3 directly at all 2^20 assignments with
the C field (gf2k.c gfmul), then Moebius-transform each output bit to its ANF.
Equation k is the coefficient of t^k.
"""
import numpy as np

import gf19
import kern
import layout as LY


def _pmul(p, q):
    r = {}
    for m1, c1 in p.items():
        for m2, c2 in q.items():
            m = m1 | m2
            r[m] = r.get(m, 0) ^ gf19.mul(c1, c2)
    return {m: c for m, c in r.items() if c}


def _padd(*ps):
    r = {}
    for p in ps:
        for m, c in p.items():
            r[m] = r.get(m, 0) ^ c
    return {m: c for m, c in r.items() if c}


X1 = {1 << j: 1 << j for j in range(10)}
X2 = {1 << (10 + j): 1 << j for j in range(10)}


def route_A(xR, B):
    xr = {0: xR} if xR else {}
    s1 = _padd(_pmul(X1, X2), _pmul(X1, xr), _pmul(X2, xr))
    S = _padd(_pmul(s1, s1), _pmul(_pmul(X1, X2), xr), {0: B} if B else {})
    E = np.zeros((LY.NEQ, 211), dtype=np.uint8)
    high = [m for m in S if LY.popcount(m) > 2]
    if high:
        raise AssertionError("route A: degree > 2 monomial survived: %d" % len(high))
    for m, c in S.items():
        j = LY.E_COL_OF_MASK[m]
        for k in range(LY.NEQ):
            if (c >> k) & 1:
                E[k, j] = 1
    return E


def route_B(xR, B):
    """Returns (E, s_direct): E from interpolation, s_direct = #{v : S_3 = 0}."""
    vals = kern.s3_eval_all(xR, B)
    s_direct = int(np.count_nonzero(vals == 0))
    anf = kern.mobius(vals, 20)
    nz = np.flatnonzero(anf)
    if (LY.POP[nz] > 2).any():
        raise AssertionError("route B: ANF has a monomial of degree > 2")
    E = np.zeros((LY.NEQ, 211), dtype=np.uint8)
    em = np.array(LY.E_MASKS, dtype=np.int64)
    coeff = anf[em]
    for k in range(LY.NEQ):
        E[k] = (coeff >> k) & 1
    return E, s_direct


def s_from_E(E):
    """Exhaustive evaluation over all 2^20 assignments of the Boolean system E.
    Returns (s, solutions as 20-bit integers with v_j = bit j)."""
    tt = kern.mobius(LY.anf_u32(E), 20)
    sol = np.flatnonzero(tt == 0)
    return int(sol.size), sol


def eval_system_at(E, u):
    """Naive per-assignment evaluation of f_0..f_18 at u (v_j = bit j of u)."""
    vals = []
    for k in range(LY.NEQ):
        acc = 0
        for j in np.flatnonzero(E[k]):
            m = LY.E_MASKS[j]
            if (u & m) == m:
                acc ^= 1
        vals.append(acc)
    return vals
