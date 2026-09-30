"""s = number of v in F_2^18 satisfying all 17 descended equations (card BR-3).

Route 1 (both kinds): exhaustive evaluation of the 17 Boolean equations at all
2^18 assignments (numpy, bitwise over the whole cube).
Route 2 (curve kind only; never touches the descended equations): for each
x_1 in V, solve S_3(x_1, x_2, x_R) = 0 for x_2 in F_{2^17} as the quadratic
    a x_2^2 + b x_2 + c = 0,  a = (x_1 + x_R)^2, b = x_1 x_R, c = x_1^2 x_R^2 + B,
handling every degenerate case, and count the roots x_2 lying in V. Each root is
re-checked by direct evaluation of S_3 in F_{2^17}.
"""
import numpy as np

import gf2n as F
from ec import S3

NV = 18
L = 9
_CUBE = None


def _cube_bits():
    global _CUBE
    if _CUBE is None:
        v = np.arange(1 << NV, dtype=np.uint32)
        _CUBE = [((v >> i) & 1).astype(np.uint8) for i in range(NV)]
    return _CUBE


def route1_exhaustive(eqs):
    bits = _cube_bits()
    ones = np.ones(1 << NV, dtype=np.uint8)
    cache = {}

    def mono(m):
        r = cache.get(m)
        if r is None:
            r = ones.copy()
            for i in range(NV):
                if (m >> i) & 1:
                    r &= bits[i]
            cache[m] = r
        return r

    alive = np.ones(1 << NV, dtype=bool)
    for eq in eqs:
        acc = np.zeros(1 << NV, dtype=np.uint8)
        for m in eq:
            acc ^= mono(m)
        alive &= (acc == 0)
    sols = np.nonzero(alive)[0].tolist()
    return len(sols), sols


def route2_rootfinding(xR, B):
    """Returns (s, sorted list of v = x_1 | x_2 << 9, number of roots failing direct re-check)."""
    sols = []
    bad = 0
    for x1 in range(1 << L):
        a = F.sq(x1 ^ xR)
        b = F.mul(x1, xR)
        c = F.mul(F.sq(x1), F.sq(xR)) ^ B
        roots = []
        if a == 0:
            if b != 0:
                roots = [F.mul(c, F.inv(b))]
            else:
                roots = [] if c != 0 else list(range(1 << F.N))  # c = B != 0 here
        elif b == 0:
            roots = [F.sqrt(F.mul(c, F.inv(a)))]
        else:
            w = F.mul(F.mul(a, c), F.inv(F.sq(b)))
            if F.trace(w) == 0:
                z = F.half_trace(w)
                s_ = F.mul(b, F.inv(a))
                roots = [F.mul(s_, z), F.mul(s_, z ^ 1)]
        for x2 in roots:
            if S3(x1, x2, xR, B) != 0:
                bad += 1
                continue
            if x2 < (1 << L):
                sols.append(x1 | (x2 << L))
    sols = sorted(set(sols))
    return len(sols), sols, bad
