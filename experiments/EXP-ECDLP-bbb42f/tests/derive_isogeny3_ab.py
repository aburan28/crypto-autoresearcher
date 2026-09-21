import sympy as sp

x, y, x0, a, b = sp.symbols("x y x0 a b")

X_num2 = x**3 - 2*x**2*x0 + 7*x*x0**2 + 2*a*x + 2*a*x0 + 4*b - 2*x0**3
Xden = (x - x0)**2
Xp = x + X_num2 / Xden

Y_num_factor = -2*a*x - 6*a*x0 - 8*b + x**3 - 3*x**2*x0 - 3*x*x0**2 - 3*x0**3
Yden = (x - x0)**3
Yp = y + y * Y_num_factor / Yden

# Y(P)^2, using y^2 = x^3+a*x+b
Yp2 = sp.expand(Yp**2)
Yp2 = Yp2.subs(y**2, x**3 + a*x + b)
Yp2 = sp.simplify(Yp2)

Xp3 = sp.simplify(Xp**3)

Aprime, Bprime = sp.symbols("Aprime Bprime")
expr = sp.together(Yp2 - Xp3 - Aprime*Xp - Bprime)
num, den = sp.fraction(expr)
num = sp.expand(num)

# num should be identically 0 (as a polynomial in x, treating x0,a,b,Aprime,Bprime as parameters)
poly = sp.Poly(num, x)
coeffs = poly.all_coeffs()
print("degree in x:", poly.degree())
sol = sp.solve(coeffs, [Aprime, Bprime], dict=True)
print("solutions:", sol)
