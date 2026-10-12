"""Weil descent of S_3 over an arbitrary F2-basis of a subspace (Stage 3)."""
from __future__ import annotations

from itertools import combinations

import numpy as np


def mu_order(dmax, nv):
    out = []
    for d in range(dmax + 1):
        out.extend(combinations(range(nv), d))
    return out


def mono_mask(m):
    s = 0
    for i in m:
        s |= 1 << i
    return s


def column_order(D, nv):
    mons = mu_order(D, nv)
    return sorted(mons, key=lambda m: (-len(m), mono_mask(m)))


def _pmul(F, P, Q):
    out = {}
    for m1, c1 in P.items():
        for m2, c2 in Q.items():
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
    out = {}
    for m, c in P.items():
        out[m] = out.get(m, 0) ^ F.mul(c, c)
    return out


def descend_s3(F, B, basis, xR):
    """Descend S3(x1,x2,xR) with x_i in span(basis). Returns (eqs, meta).

    eqs[k] = list of monomial bitmasks with coefficient bit k set.
    nv = 2 * len(basis).
    """
    L = len(basis)
    X1 = {(j,): basis[j] for j in range(L) if basis[j]}
    X2 = {(L + j,): basis[j] for j in range(L) if basis[j]}
    s12 = _pmul(F, X1, X2)
    e1 = _padd(s12, _pscal(F, X1, xR), _pscal(F, X2, xR))
    S = _padd(_psq(F, e1), _pscal(F, s12, xR), {(): B})
    n = F.n
    eqs = [[] for _ in range(n)]
    degs = []
    for m, c in S.items():
        if c == 0:
            continue
        mask = mono_mask(m)
        degs.append(bin(mask).count("1") if m else 0)
        for k in range(n):
            if (c >> k) & 1:
                eqs[k].append(mask)
    meta = {
        "nv": 2 * L,
        "neq": n,
        "L": L,
        "n_terms": len(S),
        "max_boolean_degree": max(degs) if degs else 0,
    }
    return eqs, meta
