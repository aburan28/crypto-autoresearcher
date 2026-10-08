"""Monomial-order helpers for Closure (from CERTBIN macaulay)."""
from itertools import combinations


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
