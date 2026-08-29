"""
Baby-step giant-step: an independent secondary solver used only as a
cross-check on the smallest instance (the contract's bsgs_cross_check
control), to validate the transferred DLP instance and the certificate
path against a solver with no shared walk logic with rho_solver.py.
"""
from __future__ import annotations
import math

from ec_affine import ec_add, ec_scalar_mult, negate


def bsgs(P, Q, a, p, N):
    m = math.isqrt(N) + 1
    table = {}
    cur = None
    for j in range(m):
        table[cur] = j
        cur = ec_add(cur, P, a, p)
    neg_mP = negate(ec_scalar_mult(m, P, a, p), p)
    gamma = Q
    for i in range(m + 1):
        if gamma in table:
            j = table[gamma]
            k = (i * m + j) % N
            return k
        gamma = ec_add(gamma, neg_mP, a, p)
    return None
