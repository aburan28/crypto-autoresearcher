import sympy as sp

X1, Y1, Z1, a = sp.symbols("X1 Y1 Z1 a")
x1, y1 = X1 / Z1, Y1 / Z1

lam = (3 * x1**2 + a) / (2 * y1)
x3 = lam**2 - 2 * x1
y3 = lam * (x1 - x3) - y1

# lam denominator ~ 2*Y1/Z1, i.e. (2*y1) => clear via Z3 = (2*Y1)**3 * Z1  (generous)
Z3 = (2 * Y1)**3 * Z1

X3 = sp.cancel(x3 * Z3)
Y3 = sp.cancel(y3 * Z3)
Z3s = sp.cancel(Z3)

X3f = sp.factor(X3)
Y3f = sp.factor(Y3)
Z3f = sp.factor(Z3s)

print("X3 =", X3f)
print()
print("Y3 =", Y3f)
print()
print("Z3 =", Z3f)
print()
print("X3 poly?", X3.is_polynomial(X1, Y1, Z1, a))
print("Y3 poly?", Y3.is_polynomial(X1, Y1, Z1, a))
