"""PTM-1 on the PRODUCER's instrument (run.py dependent / q_add / q_mul), validator TASK-20261022-67902e.

Object: the two Mordell-Weil generators of 389a1 (rank 2, independent in E(Q)), in the two
a1 = a3 = 0 models the instrument supports:
  integral a2-model  Y^2 = X^3 + 4X^2 - 32X + 16  (X = 4x, Y = 8y + 4 from [0,1,1,-2,0]); points (-4,12), (0,4)
  short model        y^2 = x^3 - 3024x + 46224                                         ; points (-24,324), (12,108)
Expected failure signature: no relation with max |m| <= 6.
Same-curve positive checks (so a null is not an instrument failure on these models):
  (P1, [2]P1) must give (2,-1) up to sign; (P1, P2, P3) with P3 the image of (1,0) must give a relation.
The sealed blind search is run on the same inputs for comparison.
Usage: python3 -B -I ptm1_producer_instrument.py OUT.json
"""
import json
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

MODELS = [
    {"name": "389a1 integral a2-model [0,4,0,-32,16]", "A2": 4, "A4": -32, "A6": 16,
     "gens": [(-4, 12), (0, 4)], "third": (4, 4)},
    {"name": "389a1 short model [0,0,0,-3024,46224]", "A2": 0, "A4": -3024, "A6": 46224,
     "gens": [(-24, 324), (12, 108)], "third": None},
]


def on_curve(P, A2, A4, A6):
    x, y = P
    return y * y == x ** 3 + A2 * x * x + A4 * x + A6


def main():
    out = []
    for M in MODELS:
        A2, A4, A6 = Fr(M["A2"]), Fr(M["A4"]), Fr(M["A6"])
        G = [(Fr(x), Fr(y)) for x, y in M["gens"]]
        E = rs.Curve(0, A2, 0, A4, A6)
        row = {"model": M["name"], "disc_blind": str(E.disc()),
               "gens_on_curve": all(on_curve(P, A2, A4, A6) for P in G)}
        # the PTM object itself
        row["producer_dependent_bound6"] = driver.dependent(G, A2, A4, driver.RELATION_BOUND)
        row["producer_dependent_bound12"] = driver.dependent(G, A2, A4, 12)
        row["blind_relations_bound6"] = [list(m) for m in rs.relation_search(E, G, 6)]
        # same-curve positive: planted doubling
        P2 = driver.q_mul(2, G[0], A2, A4)
        row["producer_q_mul_2_equals_blind"] = P2 == E.mul(2, G[0])
        row["producer_planted_(P1,[2]P1)"] = driver.dependent([G[0], P2], A2, A4, driver.RELATION_BOUND)
        # same-curve positive: sum of generators as a third point
        S = driver.q_add(G[0], G[1], A2, A4)
        row["producer_q_add_equals_blind"] = S == E.add(G[0], G[1])
        row["P1_plus_P2"] = [str(S[0]), str(S[1])]
        row["producer_(P1,P2,P1+P2)"] = driver.dependent([G[0], G[1], S], A2, A4, driver.RELATION_BOUND)
        if M["third"] is not None:
            T = (Fr(M["third"][0]), Fr(M["third"][1]))
            row["third_point_on_curve"] = on_curve(T, A2, A4, A6)
            row["producer_(P1,P2,image_of_(1,0))"] = driver.dependent([G[0], G[1], T], A2, A4, driver.RELATION_BOUND)
            row["blind_(P1,P2,image_of_(1,0))"] = [list(m) for m in rs.relation_search(E, [G[0], G[1], T], 6)][:3]
        out.append(row)
    verdict = all(r["producer_dependent_bound6"] is None for r in out)
    positives = all(r["producer_planted_(P1,[2]P1)"] in ([2, -1], [-2, 1]) and r["producer_(P1,P2,P1+P2)"] is not None
                    for r in out)
    res = {"ptm_id": "PTM-1", "rows": out,
           "instrument_returns_no_relation_on_PTM_object": verdict,
           "same_curve_positive_checks_pass": positives}
    Path(sys.argv[1]).write_text(json.dumps(res, indent=1, default=str) + "\n")
    print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
