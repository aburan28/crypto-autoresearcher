import sympy as sp

x, y, x0, y0, a, b = sp.symbols("x y x0 y0 a b")

def add_xy(x1, y1, x2, y2):
    lam = (y2 - y1) / (x2 - x1)
    x3 = lam**2 - x1 - x2
    y3 = lam * (x1 - x3) - y1
    return sp.together(x3), sp.together(y3)

xPT, yPT = add_xy(x, y, x0, y0)
xPmT, yPmT = add_xy(x, y, x0, -y0)

X_raw = x + (xPT - x0) + (xPmT - x0)
Y_raw = y + (yPT - y0) + (yPmT - (-y0))

X_num, X_den = sp.fraction(sp.together(X_raw))
Y_num, Y_den = sp.fraction(sp.together(Y_raw))
X_num = sp.expand(X_num)
Y_num = sp.expand(Y_num)

print("X_den raw =", sp.factor(X_den))
print("Y_den raw =", sp.factor(Y_den))

# eliminate y0 using y0**2 -> x0**3+a*x0+b (apply repeatedly to catch y0**2 buried inside expanded powers)
def elim_y0(expr):
    expr = sp.expand(expr)
    changed = True
    while changed:
        new_expr = sp.expand(expr.subs(y0**2, x0**3 + a*x0 + b))
        changed = (new_expr != expr)
        expr = new_expr
    return expr

X_num2 = elim_y0(X_num)
Y_num2 = elim_y0(Y_num)
print("X_num2 has y0?", X_num2.has(y0))
print("Y_num2 has y0?", Y_num2.has(y0))

# eliminate y**2 (P's own curve relation) similarly, but only inside Y_num2 (X_num2 has y**2 too, from y*y earlier? check)
def elim_ysq(expr):
    expr = sp.expand(expr)
    changed = True
    while changed:
        new_expr = sp.expand(expr.subs(y**2, x**3 + a*x + b))
        changed = (new_expr != expr)
        expr = new_expr
    return expr

X_num3 = elim_ysq(X_num2)
Y_num3 = elim_ysq(Y_num2)
print("X_num3 has y?", X_num3.has(y))
print("Y_num3 has y (should be True, linear)?", Y_num3.has(y))

X_num3 = sp.factor(X_num3)
Y_num3 = sp.factor(Y_num3)
print()
print("FINAL X_num3 =", X_num3)
print("FINAL X_den  =", sp.factor(X_den))
print()
print("FINAL Y_num3 =", Y_num3)
print("FINAL Y_den  =", sp.factor(Y_den))

# ---- numeric cross-check ----
p = 1009
av, bv = 417, 272
x0v, y0v = 886, 996

def ev(expr, xv, yv):
    val = expr.subs({x: xv, y: yv, x0: x0v, y0: y0v, a: av, b: bv})
    return int(val) % p

import random
rnd = random.Random(1)
from sympy import Rational
Xf = X_num3 / X_den
Yf = Y_num3 / Y_den

# test at the SAME numeric point where the earlier transcription mismatched: P=(2,431)
xv, yv = 2, 431
Xval = sp.nsimplify(Xf.subs({x: xv, y: yv, x0: x0v, y0: y0v, a: av, b: bv}))
Yval = sp.nsimplify(Yf.subs({x: xv, y: yv, x0: x0v, y0: y0v, a: av, b: bv}))
Xnum_ = int(sp.fraction(sp.nsimplify(Xval))[0])
print()
print("Xval (rational) =", Xval)
print("Yval (rational) =", Yval)
