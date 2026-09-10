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

def reduce_all(expr):
    expr = sp.expand(expr)
    for _ in range(8):
        new_expr = expr.subs(y0**2, x0**3 + a*x0 + b)
        new_expr = new_expr.subs(y**2, x**3 + a*x + b)
        new_expr = sp.expand(new_expr)
        if new_expr == expr:
            break
        expr = new_expr
    return expr

X_num_r = sp.simplify(reduce_all(X_num))
Y_num_r = sp.simplify(reduce_all(Y_num))

print("X(P) numerator (over den (x-x0)^2):")
print(sp.factor(X_num_r))
print()
print("Y(P) numerator (over den (x-x0)^3, with overall sign", sp.factor(Y_den), "):")
print(sp.factor(Y_num_r))
print()
print("has y0 still?", X_num_r.has(y0), Y_num_r.has(y0))
print("has y still (non-squared)?", X_num_r.has(y), "Y has y linear factor expected: True")
