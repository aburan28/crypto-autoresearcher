#!/usr/bin/env python3
"""C4: which square root of b^2 the published b is.

p = 3 (mod 4): is b == (b^2)^((p+1)/4) mod p?   (nine published curves)
P-224 (p = 1 mod 4): Tonelli-Shanks as in ../specs/tonelli_shanks_excerpt.txt, with z the
smallest positive quadratic non-residue; is b == -R mod p? Positive control: the excerpt's
worked example (n = 5, p = 41, z = 3) must return 28. Also reported: the result with the
next few non-residues z, to show the claim is specific to z = 11.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

P = load_params()


def tonelli_shanks(n, p, z):
    Q, S = p - 1, 0
    while Q % 2 == 0:
        Q //= 2; S += 1
    M, c, t, R = S, pow(z, Q, p), pow(n, Q, p), pow(n, (Q + 1) // 2, p)
    while True:
        if t == 0:
            return 0
        if t == 1:
            return R
        i, tt = 0, t
        while tt != 1:
            tt = tt * tt % p; i += 1
            if i == M:
                raise ValueError("not a residue")
        b = pow(c, 1 << (M - i - 1), p)
        M, c, t, R = i, b * b % p, t * b * b % p, R * b % p


assert tonelli_shanks(5, 41, 3) == 28
res = {"positive_control_5_mod_41": tonelli_shanks(5, 41, 3), "curves": {}}
for name in PRIME_CURVES:
    p, b = P[name]["p"], P[name]["b"]
    bsq = b * b % p
    e = {"p_mod_4": p % 4}
    if p % 4 == 3:
        r = pow(bsq, (p + 1) // 4, p)
        e["b_equals_(p+1)/4_root"] = (r == b)
        e["b_equals_minus_(p+1)/4_root"] = (r == p - b)
    else:
        nr = [z for z in range(2, 200) if pow(z, (p - 1) // 2, p) == p - 1][:6]
        e["smallest_nonresidues"] = nr
        e["by_z"] = {}
        for z in nr:
            R = tonelli_shanks(bsq, p, z)
            assert R * R % p == bsq
            e["by_z"][str(z)] = {"b_equals_R": R == b, "b_equals_minus_R": (p - R) == b}
        e["claim_z11_negative"] = nr[0] == 11 and e["by_z"]["11"]["b_equals_minus_R"]
    res["curves"][name] = e
n3 = sum(1 for c in res["curves"].values() if c["p_mod_4"] == 3)
res["n_p3mod4_curves"] = n3
res["all_p3mod4_b_is_root"] = all(c.get("b_equals_(p+1)/4_root") for c in res["curves"].values() if c["p_mod_4"] == 3)
res["chance_2^-n"] = n3
with open(os.path.join(ROOT, "out", "c4_roots.json"), "w") as f:
    json.dump(res, f, indent=1, sort_keys=True)
print(json.dumps(res, indent=1, sort_keys=True))
