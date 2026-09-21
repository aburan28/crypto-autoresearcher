p = 1009
a, b = 417, 272
x0 = 886
x, y = 2, 431

n = p
dx = (x - x0) % n
inv_dx = pow(dx, -1, n)
inv_dx2 = (inv_dx * inv_dx) % n
inv_dx3 = (inv_dx2 * inv_dx) % n

x_num = (x**3 - 2 * x**2 * x0 + 7 * x * x0**2 + 2 * a * x + 2 * a * x0 + 4 * b - 2 * x0**3) % n
y_num_factor = (-2 * a * x - 6 * a * x0 - 8 * b + x**3 - 3 * x**2 * x0 - 3 * x * x0**2 - 3 * x0**3) % n

x_img = (x + x_num * inv_dx2) % n
y_img = (y + y * y_num_factor * inv_dx3) % n
print("my code result:", x_img, y_img, " expected: 487 135")

# now compute via direct fraction (sympy-verified rational), fresh, independently:
import sympy as sp
xs, ys, x0s, a_s, b_s = sp.symbols("xs ys x0s as bs")
X_num3 = 2*a_s*xs + 2*a_s*x0s + 4*b_s + xs**3 - 2*xs**2*x0s + 7*xs*x0s**2 - 2*x0s**3
X_den = (xs - x0s)**2
Xexpr = xs + X_num3/X_den
Xval = Xexpr.subs({xs: x, x0s: x0, a_s: a, b_s: b})
Xval_mod = int(sp.fraction(sp.nsimplify(Xval))[0]) * pow(int(sp.fraction(sp.nsimplify(Xval))[1]) % p, -1, p) % p
print("independent X =", Xval_mod)

Y_num3 = ys*(6*a_s*x0s + 6*b_s - 3*xs**3 + 3*xs**2*x0s + 3*xs*x0s**2 + 3*x0s**3 + 2*ys**2)
Y_den = -(xs - x0s)**3
Yexpr = ys + Y_num3/Y_den
Yval = Yexpr.subs({xs: x, ys: y, x0s: x0, a_s: a, b_s: b})
Yval_mod = int(sp.fraction(sp.nsimplify(Yval))[0]) * pow(int(sp.fraction(sp.nsimplify(Yval))[1]) % p, -1, p) % p
print("independent Y =", Yval_mod)
