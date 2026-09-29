#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RED TEAM PROBE A2  --  TASK-20260809-444fe7 / BATCH-9e3584 / GOAL-MLKEM-005

THE RELABELLING WITNESS FOR PROBE A.

PROVENANCE, STATED PLAINLY.  This file was written AFTER probe_gvar_family.py
had been run and its output read.  It adds no new verdict: it exhibits, cell by
cell, the numbers that probe A's summary already implies, so that a reader can
check the sharpest form of probe A's objection without re-deriving it.  It is a
WITNESS, not a rescoring, and it is disclosed as post-hoc because that is what
it is.  CLAIM TIER: TOY.

THE CLAIM BEING WITNESSED.  In the nearby family F1 of probe A --

    B_i = [[I_k, A_i], [0, diag(m_i)]],  m_i[0] = q + i,  m_i[j>0] = q

-- at any fixed cell (d, k, beta) the value

    X_null(B_i, beta) = (beta/d)(1/d) * ( log(q+i) + (d-k-1) log q )

is a STRICTLY MONOTONE function of the basis index i and of NOTHING ELSE.  It
reads zero entries of A_i, exactly as in the frozen family F0.  Its entire
between-basis variation is therefore a relabelling of the basis index.  `G-VAR`
as written -- "non-zero between-basis dispersion at fixed (d,k,beta,q)",
decided by bit-identity -- ADMITS it.

WHAT COULD NOT FAIL, BOTH DIRECTIONS:
  * could-not-FIRE: if the 8 values were not distinct there would be no
    relabelling to exhibit.  Checked and reported per cell (n_distinct == 8).
  * could-not-PASS: if F0's values were also distinct, the contrast would be
    empty.  F0 is recomputed here in the same loop and must give n_distinct==1.

WRITES exactly one file: probe_gvar_relabel_witness.json, beside this script.
NO git write, NO commit.
"""

import argparse
import json
import math
import platform
import sys
import time
from collections import OrderedDict

import numpy as np

T0 = time.time()
Q = 3329
N_BASES = 8
CELLS = [("L7", 20, 6, 5), ("L8", 20, 14, 5), ("L9", 30, 9, 7),
         ("L11", 40, 12, 10), ("L1", 100, 30, 15), ("L4", 140, 40, 20)]


def make_A(d, k, q, i):
    rng = np.random.default_rng([1, d, k, i])
    return rng.integers(0, q, size=(k, d - k), dtype=np.int64)


def build(d, k, i, fam):
    B = np.zeros((d, d), dtype=np.int64)
    B[:k, :k] = np.eye(k, dtype=np.int64)
    B[:k, k:] = make_A(d, k, Q, i)
    m = np.full(d - k, Q, dtype=np.int64)
    if fam == "F1":
        m[0] = Q + i
    B[k:, k:] = np.diag(m)
    return B


def x_null(B, d, beta):
    _, la = np.linalg.slogdet(B.astype(np.float64))
    return (beta / d) * (1.0 / d) * float(la)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    R = OrderedDict()
    R["probe_id"] = "PROBE-A2 / probe_gvar_relabel_witness"
    R["task_id"] = "TASK-20260809-444fe7"
    R["role"] = "red-team"
    R["batch_id"] = "BATCH-9e3584"
    R["goal_id"] = "GOAL-MLKEM-005"
    R["claim_tier"] = "toy"
    R["provenance"] = ("WRITTEN AFTER probe_gvar_family.py was run and read. "
                       "A witness for a claim probe A's summary already "
                       "implies; adds no verdict. Disclosed as post-hoc.")
    R["environment"] = {"python": sys.version.split()[0],
                        "numpy": np.__version__,
                        "platform": platform.platform()}

    rows = []
    for name, d, k, beta in CELLS:
        row = OrderedDict([("lattice", name), ("d", d), ("k", k),
                           ("beta", beta)])
        for fam in ("F0", "F1"):
            vals = [x_null(build(d, k, i, fam), d, beta)
                    for i in range(N_BASES)]
            hexes = [float(v).hex() for v in vals]
            diffs = [b - a for a, b in zip(vals, vals[1:])]
            row[fam] = OrderedDict([
                ("X_null_per_basis_index", vals),
                ("n_distinct_ieee754_doubles", len(set(hexes))),
                ("bit_identical_G_VAR_FIRES", len(set(hexes)) == 1),
                ("strictly_increasing_in_i", bool(all(x > 0 for x in diffs))),
                ("closed_form_check_max_abs_error",
                 max(abs(v - (beta / d) * (1.0 / d)
                         * (math.log(Q + (i if fam == "F1" else 0))
                            + (d - k - 1) * math.log(Q)))
                     for i, v in enumerate(vals))),
                ("spread_max_minus_min", max(vals) - min(vals)),
            ])
        rows.append(row)
    R["cells"] = rows
    R["witness"] = {
        "F0 cells where G-VAR FIRES": sum(1 for r in rows
                                          if r["F0"]["bit_identical_G_VAR_FIRES"]),
        "F1 cells where G-VAR FIRES": sum(1 for r in rows
                                          if r["F1"]["bit_identical_G_VAR_FIRES"]),
        "F1 cells with 8 distinct values strictly increasing in i":
            sum(1 for r in rows if r["F1"]["n_distinct_ieee754_doubles"] == 8
                and r["F1"]["strictly_increasing_in_i"]),
        "n_cells": len(rows),
        "reading": "In F1 the observable's entire between-basis variation is a "
                   "strictly monotone relabelling of the basis index, and it "
                   "reads no entry of A. G-VAR admits it."}
    R["what_this_probe_does_NOT_establish"] = [
        "It does NOT adjudicate R-OUT-1 in either direction.",
        "F1's X_null is a genuine determinant functional and in F1 the "
        "determinant genuinely differs between lattices; the objection is "
        "about what G-VAR CAN SEE, not about whether F1's lattices differ.",
        "CLAIM TIER TOY.",
    ]
    R["wall_clock_seconds"] = round(time.time() - T0, 3)

    with open(args.out, "w") as fh:
        json.dump(R, fh, indent=2)
        fh.write("\n")

    print("PROBE A2 -- relabelling witness")
    for r in rows:
        print("  %-4s d=%3d k=%3d beta=%3d | F0 distinct=%d fires=%s | "
              "F1 distinct=%d fires=%s increasing=%s spread=%.3e"
              % (r["lattice"], r["d"], r["k"], r["beta"],
                 r["F0"]["n_distinct_ieee754_doubles"],
                 r["F0"]["bit_identical_G_VAR_FIRES"],
                 r["F1"]["n_distinct_ieee754_doubles"],
                 r["F1"]["bit_identical_G_VAR_FIRES"],
                 r["F1"]["strictly_increasing_in_i"],
                 r["F1"]["spread_max_minus_min"]))
    print("  witness:", json.dumps(R["witness"]))
    print("  wall clock %.2f s" % R["wall_clock_seconds"])


if __name__ == "__main__":
    main()
