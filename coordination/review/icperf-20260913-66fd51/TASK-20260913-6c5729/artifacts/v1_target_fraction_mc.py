"""Monte-Carlo cross-check of v1_target_fractions.py by a second route: draw
random targets xR in F_{2^n} and run the F_{2^{2n}} exhaustive search of
v1_decomp_search.py on each. The two routes share only val_gf2n.py.
usage: python3 v1_target_fraction_mc.py n15l5 400"""
import json, os, random, re, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
cell, N_SAMPLES = sys.argv[1], int(sys.argv[2])
src = open(os.path.join(HERE, "v1_decomp_search.py")).read()
# reuse the search machinery up to (not including) the per-instance loop
prefix = src.split("\nout = []")[0]
sys.argv = [sys.argv[0], cell]
exec(prefix)
rng = random.Random(20260915)
hits = {"E": 0, "twist": 0, "mixed_only": 0, "none": 0}
t0 = time.time()
for _ in range(N_SAMPLES):
    xR = rng.getrandbits(n)
    if xR == 0:
        R = ((0, 0), (1, 0))
    else:
        R = ((xR, 0), EK.ys_for_base_x(xR)[0])
    found = set()
    for P3 in S:
        Q = ext_add_fast(R, EK.neg(P3))
        key = None if Q is None else Q[0]
        for (x1, x2) in D.get(key, ()):
            found.add(tuple(sorted((x1, x2, P3[0][0]))))
    kinds = {kind(list(tr) + [xR]) for tr in found}
    if "E" in kinds:
        hits["E"] += 1
    elif "twist" in kinds:
        hits["twist"] += 1
    elif kinds:
        hits["mixed_only"] += 1
    else:
        hits["none"] += 1
res = {"cell": cell, "samples": N_SAMPLES, "hits": hits,
       "fraction_E_or_twist": (hits["E"] + hits["twist"]) / N_SAMPLES,
       "fraction_any": 1 - hits["none"] / N_SAMPLES, "seconds": round(time.time() - t0, 2)}
json.dump(res, open(os.path.join(HERE, f"v1_target_fraction_mc_{cell}.json"), "w"), indent=1)
print(json.dumps(res))
