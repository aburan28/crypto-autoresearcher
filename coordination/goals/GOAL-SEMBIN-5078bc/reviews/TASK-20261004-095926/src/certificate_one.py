#!/usr/bin/env python3
"""certificate_one.py SYSTEM.ms : is the constant 1 in the F_2-span of the generators AS WRITTEN (no products)?
Independent route: sparse-dictionary polynomials over the raw parse (not the C code), Gaussian elimination on the coefficient vectors with the
combination tracked; if 1 is in the span, prints the subset S of generators with sum_{i in S} g_i = 1 and VERIFIES the identity by summing the
parsed polynomials term by term (mod 2).  Prints one JSON line."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from msparse import *
ms = sys.argv[1]
N, B, R, info = parse_ms(ms)
mons = sorted({m for p in B for m in p})
idx = {m: i for i, m in enumerate(mons)}
vec = []
for p in B:
    x = 0
    for m in p: x ^= 1 << idx[m]
    vec.append(x)
piv = {}      # highest bit -> (vec, combo)
target = idx.get(0)
found = None
for i, x in enumerate(vec):
    c = 1 << i
    while x:
        h = x.bit_length() - 1
        if h in piv:
            x ^= piv[h][0]; c ^= piv[h][1]
        else:
            piv[h] = (x, c); break
    # after inserting we can test the span membership of the constant at the end
# test whether the constant polynomial 1 is in the span: reduce the vector with only bit target set
if target is None:
    print(json.dumps(dict(instance=os.path.basename(ms), one_in_span_of_generators=False, reason='constant monomial never occurs'))); sys.exit(0)
x = 1 << target; c = 0
while x:
    h = x.bit_length() - 1
    if h in piv:
        x ^= piv[h][0]; c ^= piv[h][1]
    else:
        break
if x:
    print(json.dumps(dict(instance=os.path.basename(ms), one_in_span_of_generators=False, generators=len(B), rank_of_generators=len(piv))))
else:
    S = [i for i in range(len(B)) if (c >> i) & 1]
    # verify by direct summation of the raw-parsed polynomials
    total = {}
    for i in S:
        for expo in R[i]:
            total[expo] = total.get(expo, 0) ^ 1
    nz = [e for e, v in total.items() if v]
    ok = (len(nz) == 1 and nz[0] == ())
    # and by point evaluation at 20000 random points: sum of generators in S == 1
    import random
    rng = random.Random(1)
    ok2 = all((sum(eval_raw(R[i], a) for i in S) % 2) == 1 for a in (rng.getrandbits(N) for _ in range(2000)))
    print(json.dumps(dict(instance=os.path.basename(ms), one_in_span_of_generators=True, subset_size=len(S), subset=S, verified_sum_equals_1_symbolically=ok,
                          verified_at_2000_random_points=ok2, generators=len(B), rank_of_generators=len(piv))))
