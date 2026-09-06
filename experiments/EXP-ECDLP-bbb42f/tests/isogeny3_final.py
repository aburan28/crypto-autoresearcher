import sympy as sp

xs, ys, x0s, y0s, as_, bs = sp.symbols("xs ys x0s y0s as bs")

def add_xy(x1, y1, x2, y2):
    lam = (y2 - y1) / (x2 - x1)
    x3 = sp.together(lam**2 - x1 - x2)
    y3 = sp.together(lam * (x1 - x3) - y1)
    return x3, y3

xPT, yPT = add_xy(xs, ys, x0s, y0s)
xPmT, yPmT = add_xy(xs, ys, x0s, -y0s)

Xexpr = sp.together(xs + (xPT - x0s) + (xPmT - x0s))
Yexpr = sp.together(ys + (yPT - y0s) + (yPmT - (-y0s)))

Xn, Xd = sp.fraction(Xexpr)
Yn, Yd = sp.fraction(Yexpr)
Xn = sp.expand(Xn)
Yn = sp.expand(Yn)

curve_rel_y0 = sp.Poly(y0s**2 - (x0s**3 + as_*x0s + bs), y0s)
curve_rel_y = sp.Poly(ys**2 - (xs**3 + as_*xs + bs), ys)

_, Xn = sp.div(sp.Poly(Xn, y0s), curve_rel_y0)
Xn = Xn.as_expr()
_, Yn = sp.div(sp.Poly(Yn, y0s), curve_rel_y0)
Yn = Yn.as_expr()

_, Xn = sp.div(sp.Poly(sp.expand(Xn), ys), curve_rel_y)
Xn = Xn.as_expr()
_, Yn = sp.div(sp.Poly(sp.expand(Yn), ys), curve_rel_y)
Yn = Yn.as_expr()

print("Xn =", sp.factor(Xn))
print("Xd =", sp.factor(Xd))
print()
print("Yn =", sp.factor(Yn))
print("Yd =", sp.factor(Yd))
print()
print("Xn has y0/y?", Xn.has(y0s), Xn.has(ys))
print("Yn has y0?", Yn.has(y0s))

# ---- validate against BOTH oracles ----
p = 1009

def modval(expr, subs):
    val = sp.nsimplify(expr.subs(subs))
    n, d = sp.fraction(val)
    return (int(n) % p) * pow(int(d) % p, -1, p) % p

# oracle 1 (QR case): a=417,b=272,x0=886,y0=996, P=(2,431) -> expect (487,135)
subs1 = {xs: 2, ys: 431, x0s: 886, as_: 417, bs: 272}
X1 = modval(Xn, subs1) * pow(modval(Xd, subs1), -1, p) % p if False else None
# safer: reduce Xn,Xd,Yn,Yd separately then combine mod p
def modval2(expr, subs):
    val = expr.subs(subs)
    return int(val) % p
X1n = modval2(Xn, subs1); X1d = modval2(Xd, subs1)
Y1n = modval2(Yn, subs1); Y1d = modval2(Yd, subs1)
X1 = (X1n * pow(X1d % p, -1, p)) % p
Y1 = (Y1n * pow(Y1d % p, -1, p)) % p
print()
print("Oracle1 (QR case) expect (487,135):", (X1, Y1))

# oracle 2 (non-QR case): a=134,b=29,x0=273, P=(331,91) -> expect (870,750)
subs2 = {xs: 331, ys: 91, x0s: 273, as_: 134, bs: 29}
X2n = modval2(Xn, subs2); X2d = modval2(Xd, subs2)
Y2n = modval2(Yn, subs2); Y2d = modval2(Yd, subs2)
X2 = (X2n * pow(X2d % p, -1, p)) % p
Y2 = (Y2n * pow(Y2d % p, -1, p)) % p
print("Oracle2 (non-QR case) expect (870,750):", (X2, Y2))
