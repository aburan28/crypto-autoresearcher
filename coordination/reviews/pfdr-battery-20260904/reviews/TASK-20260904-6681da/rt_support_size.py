#!/usr/bin/env python3
"""rt_support_size.py -- RED TEAM derivation aid for TASK-20260904-6681da (R4).

How many nonzero terms does the digit-substituted, multilinearly reduced
generator S~ = S_{m+1}(ell_1, ..., ell_m, x_R) have, at the balance point of
each headline cell of EXP-PFDR-c04716?

The top-degree part of S~ is the image in A = F_p[a]/(a^2) of the top form of
S_{m+1}.  With the top form c prod_k x_k^e, e = 2^(m-1) (verified symbolically
at m = 3 by EXP-PFDR-5726af and consistent with the total degree m 2^(m-1)
measured for m = 2..5 in rt_degree_probe.py), that image is

    c prod_k [ e! sum_{|I_k| = e} (prod_{i in I_k} 2^i) a_{I_k} ],

which has EXACTLY binom(s, e)^m nonzero terms (each coefficient is a nonzero
product of a constant, e!^m and powers of 2, and no two terms share a
monomial).  So

    #terms(S~) >= binom(s, 2^(m-1))^m,

a lower bound on the cost of WRITING DOWN the generator, hence on the cost of
building one row of the degree-D_0 Macaulay matrix the table prices.

Standard library only.  Deterministic.  Not an experiment.
"""
import json
from math import comb, log2

# balanced (s, n) and tabulated log2 T per cell, recomputed by rt_cost_recheck.py
CELLS = [
    # (log2N, m, D_0, omega, s, n, log2T)
    (256, 3, 4, 2.0, 78.8753, 237, 158.7506),
    (256, 4, 4, 2.0, 63.8695, 255, 128.7391),
    (256, 5, 4, 2.0, 53.8813, 269, 108.7625),
    (256, 5, 4, 2.807, 57.7996, 289, 116.5991),
    (256, 5, 6, 2.0, 57.8222, 289, 116.6443),
    (256, 5, 8, 2.0, 61.5650, 308, 124.1300),
    (128, 5, 4, 2.0, 31.5220, 158, 64.0439),
    (64, 5, 4, 2.0, 19.9721, 100, 40.9443),
]

rows = []
for (log2N, m, D0, om, s, n, log2T) in CELLS:
    e = 2 ** (m - 1)
    s_int = int(round(s))
    terms_top = comb(s_int, e) ** m if s_int >= e else 0
    ncols_delta = sum(comb(n, i) for i in range(0, min(m * e, n) + 1))
    rows.append({
        "log2N": log2N, "m": m, "D_0": D0, "omega": om,
        "s_rounded": s_int, "n": n,
        "e_equals_2^(m-1)": e,
        "delta": m * e,
        "log2_terms_in_top_part_binom(s,e)^m":
            (round(m * log2(comb(s_int, e)), 2) if terms_top else None),
        "log2_Ncols(n, delta)_upper_bound_on_support":
            round(log2(ncols_delta), 2),
        "tabulated_log2T_for_the_WHOLE_attack": log2T,
        "generator_write_down_exceeds_total_T_by_log2":
            (round(m * log2(comb(s_int, e)) - log2T, 2) if terms_top else None),
    })

print(json.dumps({"note": "lower bound on the number of nonzero terms of the "
                          "reduced digit-substituted generator, against the "
                          "cell's own total cost",
                  "cells": rows}, indent=1))
