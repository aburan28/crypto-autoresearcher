"""Red-team PTM-1 on the plan's object (TASK-20261023-62eb31): the 389a1
generators are independent (regulator != 0), and a dependent pair with a
coefficient 7 on the same curve is scored 'no relation' by the producer's
bound-6 search. Short model [0,0,0,-3024,46224] (isomorphic to 389a1, used by
VAL-20261022-b08129) with generators (-24, 324), (12, 108)."""
from __future__ import annotations

import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
PYENV = os.environ.get("RT_PYENV")
if PYENV:
    sys.path.insert(0, PYENV)
import cypari2  # noqa: E402

pari = cypari2.Pari()
pari("default(realprecision, 77)")


def main():
    sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "implementation")))
    import run as driver
    out = {}
    out["regulator_389a1_lmfdb_model"] = str(pari("matdet(ellheightmatrix(ellinit([0,1,1,-2,0]),[[0,0],[1,0]]))"))
    out["regulator_short_model_pair"] = str(pari("matdet(ellheightmatrix(ellinit([0,0,0,-3024,46224]),[[-24,324],[12,108]]))"))
    out["j_and_conductor_short"] = str(pari("my(E=ellinit([0,0,0,-3024,46224]),F=ellinit([0,1,1,-2,0])); [E.j == F.j, ellglobalred(E)[1], ellglobalred(F)[1]]"))
    G = pari("my(E=ellinit([0,0,0,-3024,46224]),G=elladd(E,[-24,324],[12,108])); [ellmul(E,G,7), ellmul(E,G,3)]")
    P1 = (Fraction(str(G[0][0])), Fraction(str(G[0][1])))
    P2 = (Fraction(str(G[1][0])), Fraction(str(G[1][1])))
    out["object_7G_3G_where_G_is_G1_plus_G2"] = {
        "producer_bound6": driver.dependent([P1, P2], Fraction(0), Fraction(-3024), 6),
        "producer_bound7": driver.dependent([P1, P2], Fraction(0), Fraction(-3024), 7),
        "log_height_x": [driver.naive_log_height(P1[0]), driver.naive_log_height(P2[0])],
    }
    print(json.dumps(out, indent=1))
    json.dump(out, open(os.path.join(HERE, "rt_ptm_389a1.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
