import sys
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.isogeny3 import isogenous_curve_3, push_point_3
from driver.ecc import on_curve, random_point
import random

p, a, b, x0 = 1009, 134, 29, 273

a3, b3 = isogenous_curve_3(a, b, p, x0)
print("a3,b3 =", a3, b3, "singular?", (4*a3**3+27*b3*b3) % p == 0)

rng = random.Random(7)
for _ in range(10):
    P = random_point(a, b, p, rng)
    img = push_point_3(P, a, p, x0)
    ok = on_curve(img, a3, b3, p)
    print(P, "->", img, "on_curve:", ok)
