import sys
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
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

curve_rel_y0 = y0s**2 - (x0s**3 + as_*x0s + bs)

# proper polynomial reduction of Xn, Yn modulo curve_rel_y0, treating y0s as the variable
Xn_poly = sp.Poly(Xn, y0s)
Yn_poly = sp.Poly(Yn, y0s)
rel_poly = sp.Poly(curve_rel_y0, y0s)

_, Xn_rem = sp.div(Xn_poly, rel_poly)
_, Yn_rem = sp.div(Yn_poly, rel_poly)
Xn_r = sp.expand(Xn_rem.as_expr())
Yn_r = sp.expand(Yn_rem.as_expr())

print("Xn_r has y0s?", Xn_r.has(y0s))
print("Yn_r has y0s?", Yn_r.has(y0s))
print()
print("Xn_r =", sp.factor(Xn_r))
print("Xd   =", sp.factor(Xd))
print()
print("Yn_r =", sp.factor(Yn_r))
print("Yd   =", sp.factor(Yd))

# now also reduce ys**2 -> xs**3+as_*xs+bs in Yn_r and Xn_r (P's own curve relation)
curve_rel_y = ys**2 - (xs**3 + as_*xs + bs)
rel_y_poly = sp.Poly(curve_rel_y, ys)

Yn_r_poly = sp.Poly(Yn_r, ys)
_, Yn_r2 = sp.div(Yn_r_poly, rel_y_poly)
Yn_r2e = sp.expand(Yn_r2.as_expr())
print()
print("Yn_r2 (y reduced) =", sp.factor(Yn_r2e))

Xn_r_poly = sp.Poly(Xn_r, ys)
_, Xn_r2 = sp.div(Xn_r_poly, rel_y_poly)
Xn_r2e = sp.expand(Xn_r2.as_expr())
print("Xn_r2 (y reduced) =", sp.factor(Xn_r2e))

# ---- numeric cross-check against oracle (487, 135) at P=(2,431), T=(886,996), a=417,b=272,p=1009 ----
p = 1009
subs_map = {xs: 2, x0s: 886, as_: 417, bs: 272}
Xval = Xn_r2e.subs(subs_map)
Xdval = Xd.subs(subs_map)
Xmod = int(Xval) % p * pow(int(Xdval) % p, -1, p) % p
print()
print("X check:", Xmod, "expected 487")

subs_map_y = {xs: 2, ys: 431, x0s: 886, as_: 417, bs: 272}
Yval = Yn_r2e.subs(subs_map_y)
Ydval = Yd.subs(subs_map_y)
Ymod = int(Yval) % p * pow(int(Ydval) % p, -1, p) % p
print("Y check:", Ymod, "expected 135")
