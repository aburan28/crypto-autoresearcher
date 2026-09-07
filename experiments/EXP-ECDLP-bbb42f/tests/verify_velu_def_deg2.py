import sympy as sp

x, y, x0, a, b = sp.symbols("x y x0 a b")

def add_xy(x1, y1, x2, y2):
    lam = (y2 - y1) / (x2 - x1)
    x3 = lam**2 - x1 - x2
    y3 = lam * (x1 - x3) - y1
    return sp.together(x3), sp.together(y3)

# degree-2 kernel: {O, T=(x0,0)}
xPT, yPT = add_xy(x, y, x0, 0)

X_raw = x + (xPT - x0)
Y_raw = y + (yPT - 0)

X_s = sp.simplify(sp.together(X_raw))
Y_s = sp.simplify(sp.together(Y_raw))
print("X(P) via sum-def =", X_s)
print("Y(P) via sum-def =", Y_s)

# known-good (already verified) formula:
t = 3*x0**2 + a
X_known = x + t/(x - x0)
Y_known = y*(1 - t/(x-x0)**2)
print()
print("X match?", sp.simplify(X_s - X_known) == 0)
print("Y match?", sp.simplify(Y_s - Y_known) == 0)
