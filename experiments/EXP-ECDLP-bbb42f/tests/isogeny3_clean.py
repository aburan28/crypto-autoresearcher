import sys
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.ecc import point_add, point_neg, scalar_mult, tonelli_shanks
import sympy as sp

# ---- oracle: direct sum via verified point_add ----
p = 1009
a, b = 417, 272
T = (886, 996)
x0v, y0v = T
negT = point_neg(T, p)

def oracle(P):
    x, y = P
    PT = point_add(P, T, a, p)
    PmT = point_add(P, negT, a, p)
    X = (x + (PT[0] - x0v) + (PmT[0] - x0v)) % p
    Y = (y + (PT[1] - y0v) + (PmT[1] - ((-y0v) % p))) % p
    return X, Y

Pt = (2, 431)
oracle_result = oracle(Pt)
print("oracle:", oracle_result)

# ---- fresh symbolic derivation ----
xs, ys, x0s, y0s, as_, bs = sp.symbols("xs ys x0s y0s as bs")

def add_xy(x1, y1, x2, y2):
    lam = (y2 - y1) / (x2 - x1)
    x3 = sp.together(lam**2 - x1 - x2)
    y3 = sp.together(lam * (x1 - x3) - y1)
    return x3, y3

xPT, yPT = add_xy(xs, ys, x0s, y0s)
xPmT, yPmT = add_xy(xs, ys, x0s, -y0s)

Xexpr = xs + (xPT - x0s) + (xPmT - x0s)
Yexpr = ys + (yPT - y0s) + (yPmT - (-y0s))

Xexpr = sp.together(Xexpr)
Yexpr = sp.together(Yexpr)

# numeric substitution FIRST (avoid any further symbolic simplification bugs), THEN reduce mod p
subs_map = {xs: Pt[0], ys: Pt[1], x0s: x0v, y0s: y0v, as_: a, bs: b}
Xnum_val = Xexpr.subs(subs_map)
Ynum_val = Yexpr.subs(subs_map)
Xfrac = sp.nsimplify(Xnum_val)
Yfrac = sp.nsimplify(Ynum_val)
Xn, Xd = sp.fraction(Xfrac)
Yn, Yd = sp.fraction(Yfrac)
Xmod = (int(Xn) % p) * pow(int(Xd) % p, -1, p) % p
Ymod = (int(Yn) % p) * pow(int(Yd) % p, -1, p) % p
print("fresh symbolic (direct substitution, no y0 elimination needed):", (Xmod, Ymod))
