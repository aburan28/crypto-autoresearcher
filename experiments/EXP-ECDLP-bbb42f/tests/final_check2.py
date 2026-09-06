p = 1009
x, x0 = 331, 273
x_num_general = 580
Xd = 337
term = x_num_general * pow(Xd, -1, p) % p
print("x_num/Xd term =", term)
print("x + term =", (x + term) % p)
print("term alone =", term, " (compare to oracle 870)")
