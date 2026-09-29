import sympy as sp

x, y, x0, a, b = sp.symbols("x y x0 a b")

X_num2 = x**3 - 2*x**2*x0 + 7*x*x0**2 + 2*a*x + 2*a*x0 + 4*b - 2*x0**3
Xden = (x - x0)**2
Xp = x + X_num2 / Xden

Y_num_factor = -2*a*x - 6*a*x0 - 8*b + x**3 - 3*x**2*x0 - 3*x*x0**2 - 3*x0**3
Yden = (x - x0)**3
Yp = y + y * Y_num_factor / Yden

Yp2 = sp.expand(Yp**2)
Yp2 = Yp2.subs(y**2, x**3 + a*x + b)
Yp2 = sp.simplify(Yp2)

Xp3 = sp.simplify(Xp**3)

Aprime, Bprime = sp.symbols("Aprime Bprime")
expr = sp.together(Yp2 - Xp3 - Aprime*Xp - Bprime)
num, den = sp.fraction(expr)
num = sp.expand(num)
print("den =", sp.factor(den))
print("num degree in x0 (raw):", sp.Poly(num, x0).degree())
print("num degree in x (raw):", sp.Poly(num, x).degree())

psi3 = 3*x0**4 + 6*a*x0**2 + 12*b*x0 - a**2
num_poly = sp.Poly(num, x0)
psi3_poly = sp.Poly(psi3, x0)
q, r = sp.div(num_poly, psi3_poly)
r_expr = sp.expand(r.as_expr())
print("r degree in x0 (should be <4):", sp.Poly(r_expr, x0).degree())
print("r degree in x:", sp.Poly(r_expr, x).degree())
print()
print("r_expr =", r_expr)
