import sys
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.isogeny3 import psi_3_roots

p = 1009
a, b = 417, 272
roots = psi_3_roots(a, b, p)
print("psi_3 roots for a=417,b=272:", roots)
print("886 in roots?", 886 in roots)

# also check the OTHER curve that's failing
a2, b2 = 134, 29
roots2 = psi_3_roots(a2, b2, p)
print("psi_3 roots for a=134,b=29:", roots2)
print("273 in roots2?", 273 in roots2)
