#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VAL TASK-20260812-55056b probe H -- THE FIBRE CLAUSE AT ITS DECLARED WEAK POINT.

PREREG-1 3.5 concedes before the run that VAR-F moves the free parameter from
FAMILY to DECLARED ARGUMENT SET, and invites attack exactly there. This probe
checks every declared argument set of PREREG-1 2.4 for the property the fibre
clause needs: THAT THE FIBRE FAMILY ACTUALLY HOLDS THE DECLARED NUISANCE
ARGUMENTS FIXED ACROSS THE BASIS INDEX.

  2.4 declares, per candidate, "nuisance args held fixed on the fibre":
      X_null    : abs(det B)
      rdet      : abs(det B)
      V_evade   : abs(det B), A[0,0]        <-- TWO arguments
      X_lambda  : abs(det B), A[0,0]        <-- TWO arguments
      lam1n/hkz/rawtail/X_gso_k : d, k, beta, q, abs(det B)

  2.3 defines the fibre families F0|fib and F1|fib as NEW DRAWS of A (seed
  prefix 2/3/4) with the modulus block held fixed. They hold abs(det B) fixed.
  THEY DO NOT HOLD A[0,0] FIXED, and 6.4's could-not-PASS guard asserts and
  prints only that abs(det B_i) is bit-identical -- it says nothing about
  A[0,0].

MEASURED HERE: whether A'[0,0] varies across the 8 fibre bases, and what a
DIFFERENT BUT EQUALLY DEFENSIBLE fibre declaration -- one that honours 2.4's
own nuisance list for V_evade/X_lambda by holding A[0,0] fixed -- does to every
verdict this batch reports.

EVERYTHING COMPUTED UNDER THE ALTERNATIVE DECLARATION IS POST-HOC AND IS NOT
CITABLE AS A RESULT OF THIS BATCH. It is reported to answer the completion
gate's question "would a different but equally defensible declaration flip any
verdict", and for no other purpose.

Run from the repository root.
"""
import importlib.util
import math
import os
import sys
from collections import OrderedDict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LEADPY = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/"
          "TASK-20260812-56b9da/measure_gvar2.py")


def load(p, n):
    s = importlib.util.spec_from_file_location(n, p)
    m = importlib.util.module_from_spec(s)
    sys.modules[n] = m
    s.loader.exec_module(m)
    return m


LEAD = load(LEADPY, "lead2")
Q, NB, LAT, BG = LEAD.Q, LEAD.N_BASES, LEAD.LATTICES, LEAD.BETA_GRID


def A_of(d, k, i, prefix):
    return np.random.default_rng([prefix, d, k, i]).integers(
        0, Q, size=(k, d - k), dtype=np.int64)


def main():
    print("=" * 78)
    print("PROBE H -- THE FIBRE CLAUSE AT ITS DECLARED WEAK POINT")
    print("=" * 78)

    print("\n### 1. DOES THE FIBRE FAMILY HOLD abs(det B) FIXED?  (6.4 guard)")
    for fam in ("F0|fib_s2", "F1|fib_s2", "F0|fib_s3", "F1|fib_s3",
                "F0|fib_s4", "F1|fib_s4"):
        worst = 0
        for lat, (d, k) in LAT.items():
            ads = set()
            for i in range(NB):
                m = LEAD.moduli(d, k, i, LEAD.FAMILIES[fam][1])
                ad = 1
                for v in m.tolist():
                    ad *= int(v)
                ads.add(ad)
            worst = max(worst, len(ads))
        print(f"   {fam:12s} max distinct exact |det| over 8 bases = {worst}"
              f"   {'HELD FIXED' if worst == 1 else 'NOT FIXED'}")

    print("\n### 2. DOES THE FIBRE FAMILY HOLD A[0,0] FIXED?")
    print("###    2.4 declares A[0,0] a NUISANCE ARGUMENT for V_evade and")
    print("###    X_lambda. 6.4's could-not-PASS guard NEVER CHECKS IT.")
    for fam in ("F0|fib_s2", "F1|fib_s2", "F0|fib_s3", "F0|fib_s4"):
        prefix = LEAD.FAMILIES[fam][0]
        nonfixed = 0
        example = None
        for lat, (d, k) in LAT.items():
            vals = {int(A_of(d, k, i, prefix)[0, 0]) for i in range(NB)}
            if len(vals) > 1:
                nonfixed += 1
                if example is None:
                    example = (lat, sorted(vals))
        print(f"   {fam:12s} lattices where A'[0,0] VARIES across the 8 "
              f"fibre bases: {nonfixed} of {len(LAT)}")
        if example:
            print(f"                example {example[0]}: A'[0,0] over i = "
                  f"{example[1]}")

    print("\n### 3. CONSEQUENCE, MEASURED: V_evade's VAR-F on the DECLARED")
    print("###    fibre family (A[0,0] free -- as frozen) vs on an ALTERNATIVE")
    print("###    fibre family that honours 2.4 by pinning A[0,0].")
    print("###    THE ALTERNATIVE IS POST-HOC AND UNCITABLE.")

    def vals_V(lat, d, k, beta, i, prefix, pin_A00):
        A = A_of(d, k, i, prefix).copy()
        if pin_A00:
            A[0, 0] = A_of(d, k, 0, prefix)[0, 0]      # pin to basis 0's value
        B = np.zeros((d, d), dtype=np.int64)
        B[:k, :k] = np.eye(k, dtype=np.int64)
        B[:k, k:] = A
        B[k:, k:] = Q * np.eye(d - k, dtype=np.int64)
        m = np.full(d - k, Q, dtype=np.int64)
        r, _ = LEAD.logdet_routes_fam(B, d, k, m, "F0|fib_s2")
        return {rt: (beta / d) * (1.0 / d) * r[rt] + 1e-9 * int(A[0, 0]) / Q
                for rt in LEAD.ROUTES6}

    for pin in (False, True):
        tag = ("ALTERNATIVE (A[0,0] PINNED) -- POST-HOC" if pin
               else "AS FROZEN (A[0,0] free)")
        print(f"\n   --- fibre declaration: {tag} ---")
        for rt in LEAD.ROUTES6:
            stats = OrderedDict()
            for lat, (d, k) in LAT.items():
                stats[lat] = OrderedDict()
                for beta in BG[d]:
                    v = [vals_V(lat, d, k, beta, i, 2, pin)[rt]
                         for i in range(NB)]
                    s, mm = LEAD.sd_mean(v)
                    stats[lat][beta] = {"s": s, "m": mm,
                                        "bit_identical": LEAD.bit_identical(v),
                                        "n_distinct": len({float(x).hex()
                                                           for x in v}),
                                        "seed_prefix": 2}
            vf = LEAD.var_f_from_cells(stats)
            npass = sum(1 for c in vf if vf[c]["VAR_F"] == "PASS")
            print(f"     {rt:36s} VAR_F PASS = {npass:2d} of 38   "
                  f"max s_fib = {max(vf[c]['s_c_fib'] for c in vf):.3e}")

    print("\n### 4. DOES ANY SCORED VERDICT FLIP UNDER THE ALTERNATIVE?")
    print("###    V_evade's FULL G-VAR2 verdict is REFUSE at 38/38 on all six")
    print("###    routes BECAUSE VAR-S REFUSES (max D_c 1.24e-09 << tau_var);")
    print("###    the conjunction 3.4 needs VAR-S ADMIT or scale_degenerate,")
    print("###    so VAR-F cannot rescue it whatever the fibre declaration.")
    print("###    P-V1 is adjudicated on VAR-S ALONE and never touches VAR-F.")
    print("###    P-G1 is adjudicated on VAR-S ALONE (crossing amplitude).")
    print("###    => NO SCORED VERDICT OF THIS BATCH FLIPS. The defect is")
    print("###       LATENT: it is a guard that does not guard, and it would")
    print("###       bind the moment a candidate with a non-determinant")
    print("###       nuisance argument reached VAR-S ADMIT or")
    print("###       scale_degenerate.")

    print("\n### 5. THE SAME QUESTION FOR THE OTHER DECLARED ARGUMENT SETS")
    print("   X_null   nuisance = abs(det B)              -> HELD FIXED  (ok)")
    print("   rdet     nuisance = abs(det B)              -> HELD FIXED  (ok)")
    print("   V_evade  nuisance = abs(det B), A[0,0]      -> A[0,0] NOT FIXED")
    print("   X_lambda nuisance = abs(det B), A[0,0]      -> A[0,0] NOT FIXED")
    print("   lam1n/hkz/rawtail/X_gso_k")
    print("            nuisance = d,k,beta,q,abs(det B)   -> all held fixed")
    print("            (d,k,beta,q are cell coordinates and cannot vary with i)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
