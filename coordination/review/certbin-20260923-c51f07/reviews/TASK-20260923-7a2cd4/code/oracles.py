"""Routes to s = #{v in F_2^18 satisfying all 17 descended equations}
= #{(x_1, x_2) in V x V : S_3(x_1, x_2, x_R) = 0}, V = {deg < 9}.

Route A (does NOT pass through the descended equations): for each x_1 in V
  solve a X^2 + b X + c = 0 over F_{2^17}, with
  a = x_1^2 + x_R^2, b = x_1 x_R, c = x_1^2 x_R^2 + B
  (S_3(x_1, X, x_R) = (x_1X + x_1x_R + Xx_R)^2 + x_1Xx_R + B expanded; char 2),
  and count roots in V. Scalar carry-less arithmetic.
Route B (exhaustive over the descended system): evaluate the 17 Boolean
  equations at all 2^18 assignments; count assignments where all vanish.
Route C (does NOT pass through the descended equations): evaluate S_3 directly
  in F_{2^17} (log/exp-table arithmetic) at all (x_1, x_2) in V x V.
Routes B and C are also compared VALUE BY VALUE (the 17-bit word of equation
values vs the field element S_3), which pins the descended multilinear system
exactly (a multilinear Boolean polynomial is determined by its truth table).
Assignment u in [0, 2^18): v_i = bit i of u; x_1 = u & 511, x_2 = u >> 9.
"""
import numpy as np

import gf2n as F

NV = 18
VSIZE = 1 << 9


def s_route_A(B: int, xR: int):
    cnt = 0
    per_x1 = []
    for x1 in range(VSIZE):
        a = F.sq(x1) ^ F.sq(xR)
        b = F.mul(x1, xR)
        c = F.mul(F.sq(x1), F.sq(xR)) ^ B
        k = 0
        if a == 0 and b == 0:
            k = VSIZE if c == 0 else 0
        elif a == 0:
            X = F.mul(c, F.inv(b))
            k = int(X < VSIZE)
        elif b == 0:
            X = F.sqrt(F.mul(c, F.inv(a)))
            k = int(X < VSIZE)
        else:
            d = F.mul(F.mul(a, c), F.inv(F.sq(b)))
            if F.trace(d) == 0:
                z = F.half_trace(d)
                base = F.mul(b, F.inv(a))
                Xa = F.mul(base, z)
                Xb = Xa ^ base
                k = int(Xa < VSIZE) + int(Xb < VSIZE)
        per_x1.append(k)
        cnt += k
    return cnt, per_x1


_U = np.arange(1 << NV, dtype=np.int64)


def values_route_B(coef):
    val = np.full(1 << NV, coef.get(0, 0), dtype=np.int64)
    for m, c in coef.items():
        if m == 0:
            continue
        sel = (_U & m) == m
        val[sel] ^= c
    return val


def values_route_C(B: int, xR: int):
    x1 = _U & (VSIZE - 1)
    x2 = _U >> 9
    xr = np.full_like(_U, xR)
    t = F.vmul(x1, x2) ^ F.vmul(x1, xr) ^ F.vmul(x2, xr)
    return F.vsq(t) ^ F.vmul(F.vmul(x1, x2), xr) ^ B
