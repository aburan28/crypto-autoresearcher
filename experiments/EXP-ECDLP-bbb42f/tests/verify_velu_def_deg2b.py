import sympy as sp

x, y, x0, a, b = sp.symbols("x y x0 a b")

def add_xy(x1, y1, x2, y2):
    lam = (y2 - y1) / (x2 - x1)
    x3 = lam**2 - x1 - x2
    y3 = lam * (x1 - x3) - y1
    return sp.together(x3), sp.together(y3)

xPT, yPT = add_xy(x, y, x0, 0)

X_raw = x + (xPT - x0)
X_s = sp.simplify(sp.together(X_raw))
X_s_reduced = sp.together(X_s.subs(y**2, x**3 + a*x + b))
X_s_reduced = sp.simplify(X_s_reduced)
print("X_s (reduced) =", X_s_reduced)

t = 3*x0**2 + a
X_known = sp.together(x + t/(x - x0))
print("X_known =", sp.simplify(X_known))

print("diff (reduced) =", sp.simplify(sp.together(X_s_reduced - X_known)))

# also require x0 to be an actual 2-torsion root: x0**3+a*x0+b = 0
diff2 = X_s_reduced - X_known
diff2_num, diff2_den = sp.fraction(sp.together(diff2))
diff2_num = sp.expand(diff2_num)
# reduce modulo x0^3 = -(a*x0+b)
diff2_num_r = sp.expand(diff2_num.subs(x0**3, -(a*x0+b)))
print("diff numerator after imposing x0^3=-(a x0+b):", sp.simplify(diff2_num_r))
