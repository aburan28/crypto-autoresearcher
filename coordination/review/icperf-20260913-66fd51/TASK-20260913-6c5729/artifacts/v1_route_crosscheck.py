"""Per-target agreement between the two decomposability routes:
(A) v1_target_fractions.py -- base-field arithmetic on E(F_{2^n}) and on the
    quadratic twist E': y^2 + xy = x^3 + 1 (x-preserving model of the twist coset);
(B) v1_decomp_search.py -- the F_{2^{2n}} exhaustive search used for the 60 shipped
    instances (the load-bearing route for V1).
The MC cross-check (v1_target_fraction_mc.py) came out 2.7 sigma above route A's
exact 'either kind' fraction on n17l6 (0.326 vs 0.287); this script compares the
two routes target by target, and for every disagreement verifies the explicit
decomposition by point addition over F_{2^{2n}} and by f3, so the disagreement is
attributed to a named route. usage: python3 v1_route_crosscheck.py n17l6 1500"""
import json, os, random, re, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
cell, N_SAMPLES = sys.argv[1], int(sys.argv[2])
src = open(os.path.join(HERE, "v1_decomp_search.py")).read()
prefix = src.split("\nout = []")[0]
sys.argv = [sys.argv[0], cell]
exec(prefix)                      # gives F (table field), E, K, EK, S, D, ext_add_fast, kind, n, l
from val_gf2n import BinaryCurve, summation_poly_f3

# ---- route A: exact target sets on E and on E' (same construction as v1_target_fractions.py)
Et = BinaryCurve(F, a2=0, a6=1)
def add_fast(C, P, Q):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        if y1 ^ y2 == x1: return None
        lam = x1 ^ F.mul(y1, F.inv(x1))
        x3 = F.sq(lam) ^ lam ^ C.a2
        return (x3, F.sq(x1) ^ F.mul(lam ^ 1, x3))
    lam = F.mul(y1 ^ y2, F.inv(x1 ^ x2))
    x3 = F.sq(lam) ^ lam ^ x1 ^ x2 ^ C.a2
    return (x3, F.mul(lam, x1 ^ x3) ^ x3 ^ y1)
targets = {}
for name, C in (("E", E), ("twist", Et)):
    Spts = [(xv, y) for xv in range(1 << l) for y in C.ys(xv)]
    pairs = set()
    for i in range(len(Spts)):
        for j in range(i, len(Spts)):
            pairs.add(add_fast(C, Spts[i], Spts[j]))
    T = set()
    for Q in pairs:
        for P3 in Spts:
            R = add_fast(C, Q, P3)
            if R is not None: T.add(R[0])
    targets[name] = T
routeA_any = targets["E"] | targets["twist"]

# ---- route B per target, with explicit verification of each found triple
def routeB(xR):
    R = ((0, 0), (1, 0)) if xR == 0 else ((xR, 0), EK.ys_for_base_x(xR)[0])
    found = set()
    for P3 in S:
        Q = ext_add_fast(R, EK.neg(P3))
        key = None if Q is None else Q[0]
        for (x1, x2) in D.get(key, ()):
            found.add(tuple(sorted((x1, x2, P3[0][0]))))
    return found

def explicit_sum_ok(tr, xR):
    """some choice of points over (x1,x2,x3) in E(F_{2^{2n}}) sums to a point over xR"""
    pts = []
    for x in tr:
        pts.append([((0, 0), (1, 0))] if x == 0 else [((x, 0), y) for y in EK.ys_for_base_x(x)])
    for P1 in pts[0]:
        for P2 in pts[1]:
            for P3 in pts[2]:
                Rr = ext_add_fast(ext_add_fast(P1, P2), P3)
                if Rr is not None and Rr[0] == (xR, 0):
                    return True
    return False

rng = random.Random(20260915)
t0 = time.time()
agree = disagree = 0
disagreements = []
kinds_B = {"E": 0, "twist": 0, "mixed_only": 0, "none": 0}
for _ in range(N_SAMPLES):
    xR = rng.getrandbits(n)
    fb = routeB(xR)
    ks = {kind(list(tr) + [xR]) for tr in fb}
    a_any = xR in routeA_any
    b_any = bool(fb)
    if "E" in ks: kinds_B["E"] += 1
    elif "twist" in ks: kinds_B["twist"] += 1
    elif ks: kinds_B["mixed_only"] += 1
    else: kinds_B["none"] += 1
    if a_any == b_any and (not b_any or ((xR in targets["E"]) == ("E" in ks) and (xR in targets["twist"]) == ("twist" in ks))):
        agree += 1
    else:
        disagree += 1
        if len(disagreements) < 40:
            disagreements.append({"xR_hex": hex(xR), "xR_kind": "E" if E.x_criterion(xR) in (0, None) else "twist",
                                  "routeA": {"E": xR in targets["E"], "twist": xR in targets["twist"]},
                                  "routeB_kinds": sorted(ks),
                                  "routeB_triples": [{"x_hex": [hex(x) for x in tr], "kind": kind(list(tr) + [xR]),
                                                      "f3_zero": summation_poly_f3(F, tr[0], tr[1], tr[2], xR) == 0,
                                                      "explicit_F_2^2n_sum_verified": explicit_sum_ok(tr, xR)} for tr in sorted(fb)]})
# larger-sample membership rates against route A's exact set, several seeds: the MC file
# (seed 20260915, 1000 draws) and the loop above (same seed, first 1500 draws) share one
# random sequence, so a fluctuation in its prefix appears in both; independent seeds settle it
rates = {}
for seed in (20260915, 1, 2, 3):
    r = random.Random(seed)
    rates[f"seed_{seed}_50000"] = sum(1 for _ in range(50000) if r.getrandbits(n) in routeA_any) / 50000
res = {"cell": cell, "samples": N_SAMPLES, "agree": agree, "disagree": disagree,
       "disagreements_are_label_only_(both_routes_decomposable)": all(d["routeA"]["E"] or d["routeA"]["twist"] for d in disagreements) and disagree == len(disagreements),
       "routeB_kinds": kinds_B,
       "routeB_any_rate_this_sample": 1 - kinds_B["none"] / N_SAMPLES,
       "routeA_exact_fractions": {k: len(v) / (1 << n) for k, v in targets.items()},
       "routeA_exact_either": len(routeA_any) / (1 << n),
       "routeA_membership_rate_50000_draws_by_seed": rates,
       "disagreements_first_40": disagreements, "seconds": round(time.time() - t0, 2)}
json.dump(res, open(os.path.join(HERE, f"v1_route_crosscheck_{cell}.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "disagreements_first_40"}, indent=1))
for d in disagreements[:8]:
    print(json.dumps(d))
