#!/usr/bin/env python3
"""Verify R8 planted family (n=6, d=(1..1)) gives deg s = 2 for all 9 plants.
Also confirm the R8 plants are the same family as R7 n=6 (non-elliptic by nature)."""
import os, sys, random
from fractions import Fraction as Fr
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "../../../../../../../.."))
SRC = os.path.join(REPO, "experiments/EXP-ECRANK-73275e/source")
sys.path.insert(0, SRC)
os.environ.setdefault("ECRANK_REPO_ROOT", REPO)
import ecrank_engine as E
import construct as CT

B_INTS = CT.B_INTS
# R8 plants exactly as run_r8() draws them (seed 760808, 9 plants x 4 from B_INTS)
rng = random.Random(760808)
used_h0 = set()
print("R8 planted family (n=6, d=(1..1)):")
for i in range(9):
    rest = rng.sample(B_INTS, 4)
    b = [Fr(0), Fr(1)] + [Fr(x) for x in rest]
    p, g, s = E.mestre_polys(list(b))
    deg_s = len(s) - 1
    r = [E.peval(g, x) for x in b]
    inst, why = E.build_instance(list(b), [1]*6, r, 6)
    print("  plant %d: b=%s deg_s=%d built=%s reason=%s" % (
        i, [str(x) for x in b], deg_s, inst is not None, why))
