p = 1009
Xnum, Xden = -86205523, 48841
Ynum, Yden = 451220338709, 345403552

Xmod = (Xnum % p) * pow(Xden % p, -1, p) % p
Ymod = (Ynum % p) * pow(Yden % p, -1, p) % p
print("X mod p =", Xmod, " (expected 487)")
print("Y mod p =", Ymod, " (expected 135)")
