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

# direct numeric substitution (pre-elimination, most trustworthy), using SYMBOLIC y0 relation
p = 1009
a, b, x0 = 134, 29, 273
xv, yv = 331, 91

subs_partial = {xs: xv, ys: yv, x0s: x0, as_: a, bs: b}
Xnum_y0 = Xexpr.subs(subs_partial)
Ynum_y0 = Yexpr.subs(subs_partial)
print("X as function of y0s:", sp.simplify(Xnum_y0))
print("Y as function of y0s:", sp.simplify(Ynum_y0))

# now substitute y0s**2 = 219 (mod p) -- since y0s only appears via y0s**2 (proven), do it via series/collect
Xnum_y0 = sp.together(Xnum_y0)
Ynum_y0 = sp.together(Ynum_y0)
Xn, Xd = sp.fraction(Xnum_y0)
Yn, Yd = sp.fraction(Ynum_y0)
Xn = sp.expand(Xn)
Yn = sp.expand(Yn)

Xn_poly = sp.Poly(Xn, y0s)
Yn_poly = sp.Poly(Yn, y0s)
rel = sp.Poly(y0s**2 - 219, y0s)
_, Xn_r = sp.div(Xn_poly, rel)
_, Yn_r = sp.div(Yn_poly, rel)
Xn_r = Xn_r.as_expr()
Yn_r = Yn_r.as_expr()
print("Xn_r has y0s?", Xn_r.has(y0s), "value:", Xn_r)
print("Yn_r has y0s?", Yn_r.has(y0s), "value:", Yn_r)

print("Xd =", Xd, " Yd =", Yd)
Xval = (int(Xn_r) % p) * pow(int(Xd) % p, -1, p) % p
Yval = (int(Yn_r) % p) * pow(int(Yd) % p, -1, p) % p
print("X mod p =", Xval, " expected (oracle) 870")
print("Y mod p =", Yval, " expected (oracle) 750")
