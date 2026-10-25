"""Edge-of-bound probe (validator TASK-20261022-67902e): planted relations with max |m| = 6, and
one with max |m| = 7 that must NOT be found, on the producer's instrument and the sealed blind search.
Curves and points come from the specification's lifting rule with this script's own RNG.
Usage: python3 -B -I edge_probe.py OUT.json
"""
import json
import random
import sys
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "experiments" / "EXP-CZLIFT-ed8113" / "implementation"))
sys.path.insert(0, str(HERE / "blind"))
import run as driver  # noqa: E402
import relsearch as rs  # noqa: E402


def lifted(rng, p, r):
    while True:
        a, b = rng.randrange(p), rng.randrange(p)
        if (4 * a ** 3 + 27 * b * b) % p:
            break
    pts = [P for P in rs.affine_points(a, b, p) if P[1] != 0]
    while True:
        ch = rng.sample(pts, r)
        if len({x for x, _ in ch}) == r:
            break
    L = [(rs.sym(x, p), rs.sym(y, p)) for x, y in ch]
    E = rs.fit(L)
    return E, [(Fr(x), Fr(y)) for x, y in L]


def main():
    rng = random.Random(0x67902E + 7)
    cases = []
    # r = 2: P1 = [6]Q, P2 = [5]Q  ->  5 P1 - 6 P2 = O (max |m| = 6)
    for p in (101, 12809):
        E, T = lifted(rng, p, 2)
        Q = T[0]
        P1, P2 = E.mul(6, Q), E.mul(5, Q)
        cases.append(("r2 (6Q, 5Q) expect (5,-6)", p, E, [P1, P2], {(5, -6)}))
    # r = 2: P1 = [7]Q, P2 = [6]Q -> primitive relation (6,-7) is outside the bound: expect none
    E, T = lifted(rng, 101, 2)
    cases.append(("r2 (7Q, 6Q) expect none", 101, E, [E.mul(7, T[0]), E.mul(6, T[0])], set()))
    # r = 3: P3 = [6]P1 - [5]P2  ->  (6, -5, -1)
    E, T = lifted(rng, 101, 3)
    P3 = E.add(E.mul(6, T[0]), E.mul(-5, T[1]))
    cases.append(("r3 (P1, P2, 6P1-5P2) expect (6,-5,-1)", 101, E, [T[0], T[1], P3], {(6, -5, -1)}))
    out = []
    for name, p, E, pts, expect in cases:
        A2, A4 = E.a2, E.a4
        prod = driver.dependent(pts, A2, A4, driver.RELATION_BOUND)
        blind = rs.relation_search(E, pts, 6)
        prod_c = rs.canon(tuple(prod)) if prod is not None else None
        ok_prod = (prod_c in expect) if expect else prod is None
        ok_blind = (set(blind) == expect) if expect else blind == []
        out.append({"case": name, "p": p, "producer": prod, "blind": [list(m) for m in blind],
                    "producer_ok": ok_prod, "blind_ok": ok_blind})
        print(out[-1])
    Path(sys.argv[1]).write_text(json.dumps({"cases": out, "all_ok": all(c["producer_ok"] and c["blind_ok"] for c in out)},
                                            indent=1) + "\n")


if __name__ == "__main__":
    main()
