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

psi3 = 3*x0**4 + 6*a*x0**2 + 12*b*x0 - a**2

# reduce num as a polynomial in x0 modulo psi3 (polynomial in x0 over the field Q(x,a,b,Aprime,Bprime))
num_poly = sp.Poly(num, x0)
psi3_poly = sp.Poly(psi3, x0)
q, r = sp.div(num_poly, psi3_poly)
r_expr = r.as_expr()
r_expr = sp.expand(r_expr)

poly_x = sp.Poly(r_expr, x)
print("degree in x after psi3 reduction:", poly_x.degree())
coeffs = poly_x.all_coeffs()
sol = sp.solve(coeffs, [Aprime, Bprime], dict=True)
print("solutions:", sol)
