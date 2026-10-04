#!/usr/bin/env python3
"""J9 O2 predictions -- TASK-20260924-d95e70. Per o2-declaration.yaml
per_instance_prediction_rule; runs BEFORE the archived engine. Own code only."""
import json
import os
import sys
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "j7-mechanism"))
import rtlib as R  # noqa: E402

EQ = []
for d in range(3):
    EQ.extend(sum(1 << i for i in c) for c in combinations(range(18), d))


def dec(hexes):
    return [frozenset(EQ[j] for j in range(172) if (int(h, 16) >> j) & 1) for h in hexes]


def cum(n, d):
    from math import comb
    return sum(comb(n, i) for i in range(d + 1)) if d >= 0 else 0


def main():
    inst = json.load(open(os.path.join(HERE, "n-ell-instances.json")))["instances"]
    sp17 = R.Space(range(1, 18), 4)
    sp18 = R.Space(range(18), 4)
    out = []
    for it in inst:
        fs = dec(it["E_hex"])
        c = it["c"]
        assert set(fs[16]) == ({1, 1 << 9} | ({0} if c else set()))
        fp = [R.substitute(f, c) for f in fs]
        assert fp[16] == set()
        R4, _ = R.macaulay(sp17, fp, 2)
        R3, _ = R.macaulay(sp17, fp, 1)
        prof = R4.dims_by_deg(sp17.coldeg, 4)
        M4, _ = R.macaulay(sp18, fs, 2)
        t5 = prof[3] == R3.rank()
        rec = {"label": it["label"], "draw": it["draw"], "c": c,
               "rank_R4p": R4.rank(), "one_in_R4p": 0 in R4.rows, "fall_profile_R4p": prof,
               "rank_R3p": R3.rank(), "T5_condition_no_nontrivial_fall": t5,
               "semi_regular_R4p": (R4.rank() == 2328 and prof == [0, 0, 16, 288, 2328]),
               "rank_M4_computed": M4.rank(), "fall_profile_M4_computed": M4.dims_by_deg(sp18.coldeg, 4)}
        if t5:
            fd = R4.rank() + 834
            rec["DECLARED"] = {"one": 0 in R4.rows, "final_dim": fd,
                               "dims_by_deg": [prof[d] + cum(17, d - 1) for d in range(5)],
                               "dims": [M4.rank(), fd] if M4.rank() < fd else [M4.rank()],
                               "iterations_to_fixpoint": 1 if M4.rank() < fd else 0}
        else:
            rec["DECLARED"] = "T5 not applicable: the substituted system has a non-trivial fall at degree 4"
        out.append(rec)
        print(json.dumps(rec), flush=True)
    json.dump({"task": "TASK-20260924-d95e70", "object": "O2 predictions (declared before the engine run)",
               "instances": out}, open(os.path.join(HERE, "o2-predictions.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
