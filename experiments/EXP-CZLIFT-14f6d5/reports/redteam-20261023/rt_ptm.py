"""PTM-1 at the level of the INFERENCE (red team, TASK-20261023-7b5dc6).

The validator ran the frozen counter on 11a1 (count stays at torsion).  Here the question is whether
the run's rank inference -- "a record curve has fewer points at hmax than the rank-7 curve, so higher
rank does not buy small points" -- would also go through for rank-0 curves, where the conclusion
"a rank-0 curve carries as many small points as a rank >= 8 curve" is known false asymptotically
(N_E(H) is bounded for rank 0 and unbounded for rank >= 1).

Objects (rank 0, recalled labels; torsion verified here by exact point orders):
  11a1  = [0, -1, 1, -10, -20]      torsion Z/5
  210e2 = [1, 0, 0, -1070, 7812]    torsion Z/2 x Z/8
Same counter and grid as rt_count.py; output rt_ptm_output.json.
"""
import json, os, sys
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rt_lib as L

GRID = [10, 30, 100, 300, 1000, 3000, 10000, 30000, 100000, 300000]
OBJ = {"11a1": [0, -1, 1, -10, -20], "210e2": [1, 0, 0, -1070, 7812]}


def point_order(ai, P, cap=20):
    Q = P
    for k in range(1, cap + 1):
        if Q is None:
            return k
        Q = L.add(ai, Q, P)
        if Q is None:
            return k + 1
    return None


out = {}
for lab, ai in OBJ.items():
    pts = L.enumerate_points(ai, 300000)
    cnt = L.counts_from_points(pts, GRID)
    orders = []
    for a, d, c in pts:
        for s in ((1, -1) if c else (1,)):
            P = L.point_from_adc(ai, a, d, c, s)
            assert L.on_curve(ai, P)
            orders.append(point_order(ai, P))
    out[lab] = {"ainvs": ai, "counts": cnt, "affine_points": len(orders), "orders": sorted(o if o else -1 for o in orders),
                "all_torsion": all(o is not None for o in orders)}
    print(lab, cnt, "orders", sorted(o if o else -1 for o in orders), flush=True)
json.dump(out, open(os.path.join(HERE, "rt_ptm_output.json"), "w"), indent=1)
