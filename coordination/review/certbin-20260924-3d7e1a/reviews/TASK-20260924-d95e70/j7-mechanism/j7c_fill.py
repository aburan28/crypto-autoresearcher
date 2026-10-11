#!/usr/bin/env python3
"""J7 (c) -- TASK-20260924-d95e70. The first-iteration fill, with MY OWN literal
W_4 (rtlib.literal_W semantics, re-implemented inline here so that each
component is recorded): on U62 (all 62), C20 (all 20) and S10.

Per instance (original 18-variable system, own descent):
  M4      = rowspace(M_4): rank, fall profile dim(M4 cap B_{<=d}), d = 0..4
  M3      = rowspace(M_3) rank
  ELLLOW  = rowspace(M_3) + ell * B_{<=2}   (the "expected" low part)
  F       = M4 cap B_{<=3} (the fallen space; spanned by low-lead echelon rows)
  other   = dim F - dim(ELLLOW)  (fallen dimensions not explained by M_3 rows or ell multiples)
  ELLROUTE= M4 + ell * B_{<=3}; dim must equal rank R'_4 + 834 (theorem T1 check)
  W1      = M4 + span{v_j * b : b in a basis of F, j = 0..17}  (LITERAL first iteration)
  W2      = W1 + span{v_j * b : b in a basis of W1 cap B_{<=3}} (fixpoint check)
  Also: does W1 fill B_{<=4} using ONLY products of F's non-ell part plus
  M4 (i.e. is ell needed for the fill?), reported as dim of
  M4 + v_*(complement of ell*B_{<=2} in F).
Writes fill.json.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rtlib as R  # noqa: E402
from j7b_substitution import load_sets  # noqa: E402

pred = {(p["set"], p["idx"]): p for p in json.load(open(os.path.join(HERE, "predictions.json")))["instances"]}


def mono_list(space, dmax):
    return [m for m in space.mons if bin(m).count("1") <= dmax]


def run_one(B, xR, sp, low3):
    fs = R.descent(B, xR)
    c, ell = R.ell_of(B, xR, fs)
    t = time.time()
    M4, _ = R.macaulay(sp, fs, 2)
    prof4 = M4.dims_by_deg(sp.coldeg, 4)
    M3, _ = R.macaulay(sp, fs, 1)
    # ELLLOW = M3 + ell*B_{<=2}
    el = R.Echelon()
    el.rows = dict(M3.rows)
    ellmults = {}
    for m in low3:
        ellmults[m] = sp.to_int(R.pmul(ell, {m}))
    for m in low3:
        if bin(m).count("1") <= 2:
            el.add(ellmults[m])
    # ELLROUTE = M4 + ell*B_{<=3}
    er = R.Echelon()
    er.rows = dict(M4.rows)
    for m in low3:
        er.add(ellmults[m])
    # F basis: low-lead rows of M4's echelon
    F = [r for lb, r in M4.rows.items() if sp.coldeg[lb] <= 3]
    # literal W1
    w1 = R.Echelon()
    w1.rows = dict(M4.rows)
    for r in F:
        for j in range(18):
            w1.add(R.times_var(sp, r, j))
    # fill without ell: complement of ell*B_{<=2} in F -- reduce F rows modulo
    # the span of ell*B_{<=2} and keep the non-zero residues as the "non-ell" part
    e2 = R.Echelon()
    for m in low3:
        if bin(m).count("1") <= 2:
            e2.add(ellmults[m])
    nonell = []
    tmp = R.Echelon()
    tmp.rows = dict(e2.rows)
    for r in F:
        rr = tmp.reduce(r)
        if rr:
            tmp.add(rr)
            nonell.append(rr)
    wn = R.Echelon()
    wn.rows = dict(M4.rows)
    for r in nonell:
        for j in range(18):
            wn.add(R.times_var(sp, r, j))
    # W2 fixpoint check (only if W1 is not already everything)
    if w1.rank() < sp.C:
        low1 = [r for lb, r in w1.rows.items() if sp.coldeg[lb] <= 3]
        w2 = R.Echelon()
        w2.rows = dict(w1.rows)
        for r in low1:
            for j in range(18):
                w2.add(R.times_var(sp, r, j))
        w2rank = w2.rank()
        w2one = 0 in w2.rows
    else:
        w2rank, w2one = w1.rank(), True
    return {"rank_M4": M4.rank(), "one_in_M4": 0 in M4.rows, "fall_profile_M4": prof4,
            "rank_M3": M3.rank(), "dim_F": len(F), "dim_ELLLOW": el.rank(),
            "other_fallen_dims": len(F) - el.rank(),
            "dim_ELLROUTE": er.rank(), "one_in_ELLROUTE": 0 in er.rows,
            "dim_W1_literal": w1.rank(), "one_in_W1_literal": 0 in w1.rows,
            "fall_profile_W1": w1.dims_by_deg(sp.coldeg, 4),
            "dim_W1_without_ell_products": wn.rank(), "one_in_W1_without_ell_products": 0 in wn.rows,
            "dim_nonell_part_of_F": len(nonell),
            "dim_W2_literal": w2rank, "one_in_W2_literal": w2one,
            "seconds": round(time.time() - t, 1)}


def main():
    which = sys.argv[1:] or ["U62", "C20", "S10"]
    curve, by, sets = load_sets()
    B = curve["B"]
    sp = R.Space(range(18), 4)
    assert sp.C == 4048
    low3 = mono_list(sp, 3)
    assert len(low3) == 988
    out = []
    fn = os.path.join(HERE, "fill.json")
    if os.path.exists(fn):
        out = json.load(open(fn))["instances"]
    done = {(o["set"], o["idx"]) for o in out}
    for sname in which:
        for idx in sets[sname]:
            if (sname, idx) in done:
                continue
            xR = by[idx]["x_R"]
            rec = run_one(B, xR, sp, low3)
            p = pred[(sname, idx)]
            rec.update({"set": sname, "idx": idx, "x_R": xR,
                        "T1_check_dim_ELLROUTE_eq_rankR4p_plus_834": rec["dim_ELLROUTE"] == p["rank_R4p"] + 834,
                        "T1_check_one": rec["one_in_ELLROUTE"] == p["one_in_R4p"]})
            out.append(rec)
            print(json.dumps(rec), flush=True)
            json.dump({"task": "TASK-20260924-d95e70", "joint": "J7(c)", "instances": out}, open(fn, "w"), indent=1)


if __name__ == "__main__":
    main()
