"""Check: on a split (degenerate) lift, for rows with vP = 2,
   next-digit success  <=>  s(dP) == [d] s(P)  in E(Z/p^2)   (the section is d-homogeneous mod p^2).
Derivation: tau = s - (torsion section) and the torsion section is a homomorphism, so
tau(dP) - d tau(P) = s(dP) - [d]s(P); the next digit compares log-digits of tau(dP) and d tau(P)."""
import json, random, sys
sys.path.insert(0, '.')
from rt_padic import *
rng = random.Random(4497)
curves = json.load(open('curves_from_raw.json'))
tot = agree = vp2 = 0
for c in curves:
    p, A, B, jcm = c["p"], c["A"], c["B"], c["j_cm"]
    if p > 400:
        continue
    L, N = cyclic_enumeration(p, A % p, B % p)
    lifts = [(A, B), ((A + p * p * rng.randrange(1, p)) if jcm else p * p * rng.randrange(1, p), B + p * p * rng.randrange(1, p))]
    for A2, B2 in lifts:
        E8 = ZpK(p, 8, A2, B2)
        E2 = ZpK(p, 2, A2, B2)
        for sec in ("naive", "teichmuller", "hensel_random"):
            for _ in range(40):
                k = rng.randrange(1, p); d = rng.randrange(2, p - 1)
                eP, eQ = rng.randrange(p), rng.randrange(p)
                Ph, Qh = E8.lift(L[k], sec, eP), E8.lift(L[d * k % p], sec, eQ)
                r, vP, vQ = ratio_digit(E8.z_mult(p, Ph), E8.z_mult(p, Qh), p, 8)
                if vP != 2:
                    continue
                vp2 += 1
                succ = (r == d)
                P2 = (Ph[0] % p ** 2, Ph[1] % p ** 2)
                Q2 = (Qh[0] % p ** 2, Qh[1] % p ** 2)
                hom = (E2.mul_small(d, P2) == Q2)
                tot += 1
                agree += int(succ == hom)
res = {"rows_vP=2": vp2, "agree_success_vs_homogeneity_mod_p2": agree, "total": tot, "all_agree": agree == tot}
print(res)
json.dump(res, open("rt_r2_homogeneity_output.json", "w"), indent=1)
