p = 1009
a, b, x0 = 134, 29, 273
x, y = 331, 91

x_num_general = (x**3 - 2*x0*x**2 + 7*x0**2*x + 2*a*x + 2*a*x0 + 4*b - 2*x0**3) % p
print("general-formula x_num mod p:", x_num_general)

# concrete-derivation gave Xn_r=-4769972 (before mod), Xd=1682 -> need to compare apples to apples
# Xd = (x0-x)^2 = (273-331)^2 = 3364; but earlier script printed Xd symbolically then divided; let's directly recompute
Xd_concrete = (x0 - x)**2
print("Xd_concrete:", Xd_concrete, " mod p:", Xd_concrete % p)
Xn_r_concrete = -4769972
print("Xn_r_concrete mod p:", Xn_r_concrete % p)
print("x_num_general mod p vs Xn_r_concrete mod p match?", x_num_general == (Xn_r_concrete % p))

X_via_general = (x + x_num_general * pow((x-x0)**2 % p, -1, p)) % p
print("X via general formula (using my code's inv_dx2 based on (x-x0)):", X_via_general)
