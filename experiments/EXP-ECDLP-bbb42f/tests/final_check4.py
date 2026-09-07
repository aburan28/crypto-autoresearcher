p = 1009
x, y, x0, a, b = 331, 91, 273, 134, 29

y_num_factor = (x**3 - 3*x0*x**2 - 3*x0**2*x - 3*x0**3 - 2*a*x - 6*a*x0 - 8*b) % p
print("y_num_factor mod p =", y_num_factor)
print("y * y_num_factor mod p =", (y * y_num_factor) % p)

Yn_r = 553069972
Yd = 195112
print("Yn_r mod p =", Yn_r % p)
print("Yd mod p =", Yd % p)
print("Yd expected (x0-x)^3 mod p:", ((x0 - x) ** 3) % p)

Yval_direct = (Yn_r % p) * pow(Yd % p, -1, p) % p
print("Yval direct from raw Yn_r/Yd =", Yval_direct)
