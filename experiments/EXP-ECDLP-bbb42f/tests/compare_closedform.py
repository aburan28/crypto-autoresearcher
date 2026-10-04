import sys
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.ecc import point_add, point_neg, scalar_mult, tonelli_shanks
from driver.isogeny3 import _raw_push_point_3

p = 1009
a, b = 417, 272
T = (886, 996)
x0, y0 = T
negT = point_neg(T, p)

def X_sum2(P):
    x, y = P
    PT = point_add(P, T, a, p)
    PmT = point_add(P, negT, a, p)
    if PT is None or PmT is None:
        return None, None
    X = (x + (PT[0]-x0) + (PmT[0]-x0)) % p
    Y = (y + (PT[1]-y0) + (PmT[1]-(-y0 % p))) % p
    return X, Y

for x in range(p):
    rhs = (x**3+a*x+b) % p
    y = tonelli_shanks(rhs, p)
    if y is None or x == x0:
        continue
    P = (x, y)
    Xd, Yd = X_sum2(P)
    closed = _raw_push_point_3(P, a, p, x0)
    if closed is None:
        print("closed None at", P, "direct=", (Xd,Yd))
        continue
    Xc, Yc = closed
    if (Xd, Yd) != (Xc, Yc):
        print("MISMATCH at P=", P, "direct=", (Xd,Yd), "closed=", (Xc,Yc))
    else:
        print("match at", P)
    break
