import sys
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from sympy import symbols, GF, Poly
from driver.ecc import legendre_symbol

p, a, b, x0 = 1009, 134, 29, 273

x = symbols("x")
poly = Poly(3 * x**4 + 6 * a * x**2 + 12 * b * x - a**2, x, domain=GF(p))
print("psi_3 factorization:", poly.factor_list())

y0_sq = (x0**3 + a*x0 + b) % p
print("y0_sq =", y0_sq, "is QR:", legendre_symbol(y0_sq, p))
print("x0^3+a*x0+b mod p:", (x0**3+a*x0+b) % p, " (should be nonzero, i.e. x0 not also 2-torsion)")

# also check the isogenous_curve_3 probes: were they picked distinctly and validly?
from driver.isogeny3 import isogenous_curve_3, _raw_push_point_3
from driver.ecc import random_point
import random
rng = random.Random(repr((a, b, p, x0, "isogeny3-ab-probe")))
pts = []
while len(pts) < 2:
    cand = random_point(a, b, p, rng)
    if cand[0] != x0 and cand not in pts:
        pts.append(cand)
print("probe points used:", pts)
for P in pts:
    img = _raw_push_point_3(P, a, p, x0)
    print(P, "->", img)
