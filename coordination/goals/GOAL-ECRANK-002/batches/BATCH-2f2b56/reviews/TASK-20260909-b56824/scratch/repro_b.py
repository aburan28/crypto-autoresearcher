#!/usr/bin/env python3
"""Reproduce R9 b-tuples from committed seed 760912 (read-only import of
committed source). Sanity-check against the recorded n=6 x2 coefficients."""
import os, sys, random, json
from fractions import Fraction as Fr

ROOT = "/Volumes/SSD990/llm/tmp/opencode/review-e3cf55-20260909"
EXP = os.path.join(ROOT, "experiments", "EXP-ECRANK-73275e")
SRC = os.path.join(EXP, "source")
sys.path.insert(0, SRC)
os.environ.setdefault("ECRANK_REPO_ROOT", ROOT)
HERE = os.path.dirname(os.path.abspath(__file__))

import ecrank_engine as E
import construct

SEED = 760912
B_INTS = construct.B_INTS
print("B_INTS len:", len(B_INTS), "first/last:", B_INTS[0], B_INTS[-1])

rng = random.Random(SEED)
n6 = []
for bi in range(8):
    rest = rng.sample(B_INTS, 4)
    b = [Fr(0), Fr(1)] + [Fr(x) for x in rest]
    n6.append(b)
n8 = []
for bi in range(8):
    rest = rng.sample(B_INTS, 6)
    b = [Fr(0), Fr(1)] + [Fr(x) for x in rest]
    n8.append(b)

# sanity: n=6 x2 coefficients must match the recorded raw result
recorded_x2 = ['119629/64', '1421541/64', '17353/4', '225/4',
               '3969/4', '1300861/64', '11649/4', '1578325/64']
print("\n=== n=6 sanity check (x2 coeff vs recorded) ===")
ok = True
for bi, b in enumerate(n6):
    p, g, s = E.mestre_polys(list(b))
    s2 = s[2] if len(s) > 2 else Fr(0)
    match = (str(s2) == recorded_x2[bi])
    ok = ok and match
    print("b_index %d: b=%s  x2=%s  recorded=%s  match=%s"
          % (bi, [str(x) for x in b], str(s2), recorded_x2[bi], match))
print("ALL N6 X2 MATCH:", ok)

print("\n=== n=8 tuples (the IV-1C control objects) ===")
for bi, b in enumerate(n8):
    print("b_index %d: b=%s" % (bi, [str(x) for x in b]))

# save for later scripts
out = {"n6": [[str(x) for x in b] for b in n6],
       "n8": [[str(x) for x in b] for b in n8]}
with open(os.path.join(HERE, "b_tuples.json"), "w") as f:
    json.dump(out, f, indent=1)
print("\nwrote b_tuples.json")
