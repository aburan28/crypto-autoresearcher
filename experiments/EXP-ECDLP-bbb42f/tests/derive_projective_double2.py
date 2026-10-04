import sympy as sp

X1, Y1, Z1, a = sp.symbols("X1 Y1 Z1 a")
x1, y1 = X1 / Z1, Y1 / Z1

lam = (3 * x1**2 + a) / (2 * y1)
x3 = lam**2 - 2 * x1
y3 = lam * (x1 - x3) - y1

x3_num, x3_den = sp.fraction(sp.together(x3))
y3_num, y3_den = sp.fraction(sp.together(y3))
print("x3_den =", sp.factor(x3_den))
print("y3_den =", sp.factor(y3_den))

# common denom = lcm-ish; just multiply both by y3_den*x3_den/gcd, simplest: use den = x3_den*y3_den // gcd
den_common = sp.lcm(x3_den, y3_den)
print("den_common =", sp.factor(den_common))

X3 = sp.cancel(x3 * den_common)
Y3 = sp.cancel(y3 * den_common)
print()
print("X3 poly?", X3.is_polynomial(X1, Y1, Z1, a), " => ", sp.factor(X3))
print()
print("Y3 poly?", Y3.is_polynomial(X1, Y1, Z1, a), " => ", sp.factor(Y3))
print()
print("Z3 =", sp.factor(den_common))
