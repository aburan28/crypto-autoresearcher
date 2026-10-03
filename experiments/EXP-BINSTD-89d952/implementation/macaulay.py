"""Monomial orders and helpers for Closure (from EXP-CERTBIN-e94b27/impl/macaulay.py).

Only the generic order utilities are retained; S_3 Weil-descent builders for
n=17 are not used by this experiment (Stage 1 builds S_4 over n=19).
"""
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
