"""Satisfiability oracles for EXP-CERTBIN-e94b27 (C-ORACLE). Written fresh for
this experiment (EXP-CERTBIN-4e92d7/impl/oracles.py is NOT copied: the
handoff allows copying gf2n.py, curve.py, macaulay.py and elim.py only).

Oracle B: exhaustive evaluation of the Boolean equations over all 2^nv
assignments, via the Moebius (zeta) transform of each equation's monomial
support (truth table value at u = XOR of the coefficients of monomials m
contained in u). An assignment u encodes v_i = bit i of u.

Oracle A: for curve-algebra instances, root finding of S_3(x_1, x_2, x_R) = 0
over V x V (V = polynomials of degree < 9): for each x_1 in V, solve the
quadratic a X^2 + b X + c = 0 in X = x_2 with a = x_1^2 + x_R^2,
b = x_1 x_R, c = x_1^2 x_R^2 + B (expansion of S_3 in x_2) and keep roots in V.
"""
import numpy as np

L = 9


def truth_tables(eqs, nv):
    """(neq, 2^nv) uint8 truth tables."""
    n = 1 << nv
    out = np.zeros((len(eqs), n), dtype=np.uint8)
    for k, f in enumerate(eqs):
        a = np.zeros(n, dtype=np.uint8)
        for m in f:
            a[m] ^= 1
        for i in range(nv):
            v = a.reshape(-1, 2, 1 << i)
            v[:, 1, :] ^= v[:, 0, :]
        out[k] = a
    return out


def oracle_B(eqs, nv=18):
    tt = truth_tables(eqs, nv)
    fail = np.bitwise_or.reduce(tt, axis=0)
    return [int(u) for u in np.flatnonzero(fail == 0)]


def _roots_quadratic(F, a, b, c):
    if a == 0 and b == 0:
        return None if c == 0 else []          # None = every X
    if a == 0:
        return [F.div(c, b)]
    if b == 0:
        return [F.sqrt(F.div(c, a))]
    d = F.div(F.mul(a, c), F.mul(b, b))       # X = (b/a) Z, Z^2 + Z = d
    if F.trace(d):
        return []
    z = F.half_trace(d)
    s = F.div(b, a)
    return [F.mul(s, z), F.mul(s, z ^ 1)]


def oracle_A(F, B, xR):
    out = []
    xR2 = F.mul(xR, xR)
    for x1 in range(1 << L):
        x12 = F.mul(x1, x1)
        roots = _roots_quadratic(F, x12 ^ xR2, F.mul(x1, xR), F.mul(x12, xR2) ^ B)
        if roots is None:
            roots = range(1 << L)
        for x2 in roots:
            if x2 < (1 << L):
                out.append(x1 | (x2 << L))
    return sorted(set(out))
