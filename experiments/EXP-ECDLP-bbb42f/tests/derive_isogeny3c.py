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

X_num2 = sp.expand(X_num).subs(y0**2, x0**3 + a*x0 + b)
X_num2 = sp.expand(X_num2)
Y_num2 = sp.expand(Y_num).subs(y0**2, x0**3 + a*x0 + b)
Y_num2 = sp.expand(Y_num2)
# now substitute y**2 (P's own curve relation) inside Y_num2 -- expand fully first, y appears at most as y**1 * (poly in x,x0,a,b) plus a y**3 term
Y_num2 = Y_num2.subs(y**3, y*(x**3+a*x+b))
Y_num2 = sp.expand(Y_num2)

print("X_den =", sp.factor(X_den))
print("X_num2 =", sp.factor(X_num2))
print("X_num2 has y or y0?", X_num2.has(y), X_num2.has(y0))
print()
print("Y_den =", sp.factor(Y_den))
print("Y_num2 =", sp.factor(Y_num2))
print("Y_num2 has y0?", Y_num2.has(y0), " degree in y:", sp.Poly(Y_num2, y).degree() if Y_num2.has(y) else None)
