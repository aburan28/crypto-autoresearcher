p = 1009
x, y, x0, a, b = 331, 91, 273, 134, 29

y_num_factor = (x**3 - 3*x0*x**2 - 3*x0**2*x - 3*x0**3 - 2*a*x - 6*a*x0 - 8*b) % p
Yd = (x0 - x)**3 % p
Y_direct = (y * y_num_factor) * pow(Yd, -1, p) % p
print("Y (direct, no +y) =", Y_direct, " expected oracle 750")
