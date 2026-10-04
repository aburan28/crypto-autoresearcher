import sympy as sp

X1, Y1, Z1, X2, Y2, Z2, a = sp.symbols("X1 Y1 Z1 X2 Y2 Z2 a")

x1, y1 = X1 / Z1, Y1 / Z1
x2, y2 = X2 / Z2, Y2 / Z2

lam = (y2 - y1) / (x2 - x1)
x3 = lam**2 - x1 - x2
y3 = lam * (x1 - x3) - y1

# Clear denominators with a common Z3. lam has denominator (x2-x1) = (X2*Z1 - X1*Z2)/(Z1*Z2).
# Choose Z3 = Z1*Z2*(X2*Z1-X1*Z2)**3 generously, then simplify down.
H = X2 * Z1 - X1 * Z2          # ~ (x2-x1) * Z1 * Z2
Z3 = Z1 * Z2 * H**3

X3 = sp.together(x3 * Z3)
Y3 = sp.together(y3 * Z3)

X3s = sp.simplify(sp.cancel(X3))
Y3s = sp.simplify(sp.cancel(Y3))
Z3s = sp.simplify(Z3)

print("X3 =", sp.factor(X3s))
print()
print("Y3 =", sp.factor(Y3s))
print()
print("Z3 =", sp.factor(Z3s))

# sanity: are X3s, Y3s actually polynomials (no residual denominator)?
print()
print("X3 is polynomial in X1,Y1,Z1,X2,Y2,Z2,a:", X3s.is_polynomial(X1, Y1, Z1, X2, Y2, Z2, a))
print("Y3 is polynomial:", Y3s.is_polynomial(X1, Y1, Z1, X2, Y2, Z2, a))
