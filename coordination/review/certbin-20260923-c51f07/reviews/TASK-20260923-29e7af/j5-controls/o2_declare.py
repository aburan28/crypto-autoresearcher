#!/usr/bin/env python3
"""J5 / proves-too-much object O2, step 1: DECLARATION AND PREDICTION, written
BEFORE the archived pipeline is run on O2 (RT-3).

O2 -- synthetic constant-column family, where "instability is generic from the
first step" is KNOWN FALSE. E(r) = E^0 + sum_j r_j (c_j (x) e_const), with
E^0 = E(x_R = 0) of the RUN-CERTBIN-3b7e05 curve and e_const the constant-
monomial column (column 0 of the 17 x 172 matrix E, EQ_MONS[0] = ()).

Declared seed: S_O2 = 0x29e7af = 2746287 (the task token), generator
numpy.random.Generator(numpy.random.PCG64(S_O2)), draws consumed in order:
  1. c = g.integers(0, 2**17, size=17)            -> c_0 .. c_16
  2. r draws g.integers(1, 2**17) one at a time, duplicates skipped, until
     199 distinct values                           -> targets idx 1..199
Reference R0: r = 0 (E^0 itself). Instances: 1 reference + 199 targets = 200.

Prediction (computed here with MY OWN GF(2) rank code on the matrix built by
the archived constructor; the pipeline's elimination is NOT called):
  b      = number of columns of degree >= 3 in column-order-D4.json (they are
           the leading, contiguous block; the first degree-2 column is b).
  P_hi   = rank of M_4(E^0)[:, :b] = number of pivot steps of the column-major
           elimination on columns < b, for EVERY O2 instance (that block of
           M_4(E(r)) does not depend on r).
  L_ref  = rank of M_4(E^0) = length of the R0 trace.
  Every target: identical T_strict and T_ops prefix for steps 0..P_hi-1;
  kdiv >= P_hi; f_div >= P_hi / L_ref; any divergence column has degree <= 2;
  a_k = 0 and a_{k,0} = 1 for k < P_hi; replay_first_zero >= P_hi.
"""
import hashlib
import json
import os
import sys

import numpy as np

REPO = "/home/user/crypto-autoresearcher"
IMPL = os.path.join(REPO, "experiments/EXP-CERTBIN-4e92d7/impl")
RUN = os.path.join(REPO, "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, IMPL)

from gf2n import TableField  # noqa: E402
from macaulay import MacaulayShape, affine_basis, EQ_MONS  # noqa: E402

S_O2 = 0x29e7af


def my_rank(rows_int):
    piv = {}
    for v in rows_int:
        while v:
            h = v.bit_length() - 1
            if h in piv:
                v ^= piv[h]
            else:
                piv[h] = v
                break
    return len(piv)


def main():
    assert EQ_MONS[0] == ()
    g = np.random.Generator(np.random.PCG64(S_O2))
    c = [int(x) for x in g.integers(0, 2 ** 17, size=17)]
    rs, seen = [], set()
    draws = 0
    while len(rs) < 199:
        x = int(g.integers(1, 2 ** 17))
        draws += 1
        if x in seen:
            continue
        seen.add(x)
        rs.append(x)
    cols = json.load(open(os.path.join(RUN, "column-order-D4.json")))["columns"]
    degs = [cc["degree"] for cc in cols]
    b = sum(1 for d in degs if d >= 3)
    assert all(d >= 3 for d in degs[:b]) and all(d <= 2 for d in degs[b:])
    b4 = sum(1 for d in degs if d == 4)
    F = TableField()
    B = json.load(open(os.path.join(RUN, "curve.json")))["B"]
    E0, _ = affine_basis(F, B)
    S = MacaulayShape(4)
    M = S.build(E0)
    C = S.C
    dense = np.unpackbits(M.view(np.uint8), axis=1, bitorder="little")[:, :C]
    # row -> int with column 0 as the MOST significant bit
    def to_int(row):
        return int("".join("1" if x else "0" for x in row), 2) if row.any() else 0
    full_ints = [to_int(r) for r in dense]
    L_ref = my_rank(full_ints)
    P_hi = my_rank([v >> (C - b) for v in full_ints])
    P_4 = my_rank([v >> (C - b4) for v in full_ints])
    decl = {"S_O2": S_O2, "generator": "numpy.random.Generator(numpy.random.PCG64(S_O2))",
            "numpy": np.__version__, "c_j": c, "c_j_hex": [hex(x) for x in c],
            "r_targets_idx_1_to_199": rs, "r_draws_consumed": draws, "reference": {"label": "R0", "r": 0},
            "instances_total": 200}
    pred = {"column_boundary_b_first_degree2_col": b, "n_degree4_cols": b4,
            "P_hi_rank_of_degree_ge3_block": P_hi, "rank_of_degree4_block": P_4, "L_ref_rank_M4_E0": L_ref,
            "f_div_lower_bound": P_hi / L_ref,
            "predicted": ("every O2 target: identical T_strict and T_ops prefix for steps 0..P_hi-1; kdiv >= P_hi; "
                          "f_div >= P_hi/L_ref; divergence column degree <= 2; a_k = 0 and a_k0 = 1 for k < P_hi; "
                          "replay_first_zero >= P_hi")}
    sd = json.dumps(decl, indent=1)
    sp = json.dumps(pred, indent=1)
    open(os.path.join(HERE, "o2-declaration.json"), "w").write(sd)
    open(os.path.join(HERE, "o2-prediction.json"), "w").write(sp)
    print(sp)
    print("sha256 declaration", hashlib.sha256(sd.encode()).hexdigest())
    print("sha256 prediction", hashlib.sha256(sp.encode()).hexdigest())


if __name__ == "__main__":
    main()
