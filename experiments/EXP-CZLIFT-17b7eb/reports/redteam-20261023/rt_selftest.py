"""Cross-check rt_padic.z_mult against exact rational arithmetic (Fractions)."""
import json, random, sys
from fractions import Fraction
sys.path.insert(0, '.')
from rt_padic import *

rng = random.Random(856638)
K = 8
out = []
for (p, A, B) in [(7, 0, 5), (11, -4458240, 3623211648), (17, -85963680, 306775458864), (19, 0, 10)]:
    pts = fp_points(p, A % p, B % p)
    assert len(pts) + 1 == p, (p, len(pts))
    for trial in range(6):
        x0, y0 = rng.choice(pts)
        # integer point on a lifted curve through (x0 + p*a, y0 + p*b): adjust B
        xi = x0 + p * rng.randrange(p)
        yi = y0 + p * rng.randrange(p)
        A2 = A + p * rng.randrange(p) * (trial % 2)
        B2 = yi * yi - xi ** 3 - A2 * xi
        assert (B2 - B) % p == 0
        P = (Fraction(xi), Fraction(yi))
        R = q_mul(p, P, Fraction(A2))
        zq = -R[0] / R[1]
        v_exact = vp_frac(zq, p)
        z_exact_mod = zq.numerator * pow(zq.denominator, -1, p ** K) % p ** K
        E = ZpK(p, K, A2, B2)
        z_mine = E.z_mult(p, (xi % E.M, yi % E.M))
        out.append({"p": p, "v_exact": v_exact, "agree_mod_pK": z_mine == z_exact_mod})
ok = all(r["agree_mod_pK"] for r in out)
print(json.dumps({"cells": len(out), "all_agree": ok, "v_hist": {str(v): sum(1 for r in out if r['v_exact'] == v) for v in sorted({r['v_exact'] for r in out})}}))
json.dump({"cells": out, "all_agree": ok}, open("rt_selftest_output.json", "w"), indent=1)
