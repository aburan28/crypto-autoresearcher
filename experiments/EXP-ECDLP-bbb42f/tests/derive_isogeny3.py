import sympy as sp

x, y, x0, y0, a, b = sp.symbols("x y x0 y0 a b")

def add_xy(x1, y1, x2, y2):
    lam = (y2 - y1) / (x2 - x1)
    x3 = lam**2 - x1 - x2
    y3 = lam * (x1 - x3) - y1
    return sp.together(x3), sp.together(y3)

# P + T
xPT, yPT = add_xy(x, y, x0, y0)
# P + (-T) = P - T
xPmT, yPmT = add_xy(x, y, x0, -y0)

# Velu: X(P) = x + [x(P+T) - x0] + [x(P-T) - x0]
X_raw = x + (xPT - x0) + (xPmT - x0)
Y_raw = y + (yPT - y0) + (yPmT - (-y0))

X_s = sp.simplify(sp.together(X_raw))
Y_s = sp.simplify(sp.together(Y_raw))

# substitute y0**2 -> x0**3+a*x0+b wherever it appears, to remove y0-dependence
subs_curve = {y0**2: x0**3 + a*x0 + b}

def reduce_y0sq(expr):
    expr = sp.expand(expr)
    # repeatedly replace y0**2 with the curve relation
    for _ in range(6):
        new_expr = expr.subs(y0**2, x0**3 + a*x0 + b)
        new_expr = sp.expand(new_expr)
        if new_expr == expr:
            break
        expr = new_expr
    return expr

X_num, X_den = sp.fraction(sp.together(X_s))
Y_num, Y_den = sp.fraction(sp.together(Y_s))

X_num_r = reduce_y0sq(sp.expand(X_num))
Y_num_r = reduce_y0sq(sp.expand(Y_num))

print("X_den =", sp.factor(X_den))
print("X_num (y0-reduced) has y0 linear terms?", X_num_r.has(y0))
print("X_num_r =", sp.simplify(X_num_r))
print()
print("Y_den =", sp.factor(Y_den))
print("Y_num (y0-reduced) has y0 linear terms?", Y_num_r.has(y0))
print("Y_num_r =", sp.simplify(Y_num_r))
