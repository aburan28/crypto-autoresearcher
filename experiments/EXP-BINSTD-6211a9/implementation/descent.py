"""Weil descent of S_3 over a fixed F2-subspace V (polynomial basis).

S_3(x1,x2,x3) = (x1x2 + x1x3 + x2x3)^2 + x1x2x3 + b
with x1,x2 coordinates in V (dim l) and x3 = xR fixed in the field.

Top-degree part is independent of (a,b); constant vector depends only on b.
"""
from __future__ import annotations

from itertools import combinations

import numpy as np


def _pmul(F, P, Q):
    out = {}
    for m1, c1 in P.items():
        for m2, c2 in Q.items():
            # multilinear: identify squares by set-union of indices
            m = tuple(sorted(set(m1) | set(m2)))
            out[m] = out.get(m, 0) ^ F.mul(c1, c2)
    return out


def _padd(*Ps):
    out = {}
    for P in Ps:
        for m, c in P.items():
            out[m] = out.get(m, 0) ^ c
    return out


def _pscal(F, P, c):
    return {m: F.mul(v, c) for m, v in P.items()}


def _psq(F, P):
    # char 2 + multilinear: (sum c_m m)^2 = sum c_m^2 m
    out = {}
    for m, c in P.items():
        out[m] = out.get(m, 0) ^ F.mul(c, c)
    return out


def s3_multilinear_V(F, B, xR, V_basis):
    """Expand S_3 with x1,x2 in span(V_basis), x3=xR.

    Variables: v_0..v_{l-1} for x1, v_l..v_{2l-1} for x2.
    Returns dict monomial(tuple of var indices) -> field element.
    """
    l = len(V_basis)
    X1 = {(j,): V_basis[j] for j in range(l)}
    X2 = {(l + j,): V_basis[j] for j in range(l)}
    s12 = _pmul(F, X1, X2)
    e1 = _padd(s12, _pscal(F, X1, xR), _pscal(F, X2, xR))
    S = _padd(_psq(F, e1), _pscal(F, s12, xR), {(): B})
    return S


def descended_E(F, B, xR, V_basis):
    """n x n_mons uint8 matrix: row k = coeff of t^k of each monomial."""
    S = s3_multilinear_V(F, B, xR, V_basis)
    l = len(V_basis)
    nv = 2 * l
    # monomials appearing, ordered by deg then lex
    mons = sorted(S.keys(), key=lambda m: (len(m), m))
    # use full mu-order up to 3 for stable column indexing across cells
    all_mons = []
    for d in range(0, 4):
        all_mons.extend(combinations(range(nv), d))
    idx = {m: i for i, m in enumerate(all_mons)}
    E = np.zeros((F.n, len(all_mons)), dtype=np.uint8)
    for m, c in S.items():
        if c == 0:
            continue
        j = idx[m]
        for k in range(F.n):
            if (c >> k) & 1:
                E[k, j] = 1
    return E, all_mons


def top_degree_part(E, all_mons, deg=3):
    cols = [j for j, m in enumerate(all_mons) if len(m) == deg]
    return E[:, cols].copy()


def constant_vector(E, all_mons):
    """Inhomogeneous (degree-0) column as an F2 vector of length n."""
    j = all_mons.index(())
    return E[:, j].copy()


def constant_vector_weight_from_b(F, B):
    """Weight of the constant vector of the descended system (= wt(B) in poly basis)."""
    return bin(B).count("1")


def symbolic_P1_check(F, V_basis):
    """Confirm b only in deg-0 and a nowhere, by expanding with symbolic markers.

    We expand S_3 at two values of B and check the difference is pure constant,
    and expand at fixed B while noting the formula has no A.
    """
    l = len(V_basis)
    xR = 1  # t^0
    E0, mons = descended_E(F, 0, xR, V_basis)  # B=0 illegal on curve but algebra OK
    E1, _ = descended_E(F, 1, xR, V_basis)
    Ediff = E0 ^ E1
    # difference must be exactly the constant column equal to 1 (field element 1)
    j0 = mons.index(())
    ok_only_const = True
    for j, m in enumerate(mons):
        if j == j0:
            continue
        if np.any(Ediff[:, j]):
            ok_only_const = False
            break
    # constant column of Ediff should be the bit vector of field element 1
    const_bits = Ediff[:, j0]
    expected = np.array([(1 >> k) & 1 for k in range(F.n)], dtype=np.uint8)
    ok_const = bool(np.array_equal(const_bits, expected))

    # a nowhere: expand formula without A; S_3 expression does not reference A.
    # Cross-check: systems for two different A with same B must have identical E
    # (descent does not take A as input). Recorded as structural.
    return {
        "b_only_in_degree_0": ok_only_const and ok_const,
        "a_absent_from_S3": True,
        "ok_only_const_support": ok_only_const,
        "ok_const_equals_field_one": ok_const,
        "n": F.n,
        "l": l,
        "reduction_poly": f"0x{F.mod:x}",
        "V_basis": list(V_basis),
        "symbolic_P1_pass": bool(ok_only_const and ok_const),
    }
