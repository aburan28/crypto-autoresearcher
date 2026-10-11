#!/usr/bin/env python3
"""J8 (2) and (5) -- TASK-20260924-d95e70. Exact integer power series of the
Boolean semi-regular Hilbert series (1+z)^n / (1+z^2)^m, the degree of
regularity D_reg (index of the first non-positive coefficient), the cumulative
quotient dimension through degree D, and the implied plain-Macaulay rank
dim B_{<=D} - sum_{d<=D} h_d for D < D_reg. Pure integer arithmetic.

Also: the bilinear-support ceiling on rank(M_5) for systems whose quadratic
part lies in the bilinear monomials v_i v_{9+j} (the S_3 support and both null
supports), and the fixture dimensions."""
import json
import os
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))


def series(n, m, upto=8):
    # (1+z)^n * (1+z^2)^(-m); (1+z^2)^(-m) = sum_i (-1)^i C(m+i-1, i) z^(2i)
    a = [comb(n, d) for d in range(upto + 1)]
    b = [0] * (upto + 1)
    for i in range(upto // 2 + 1):
        b[2 * i] = (-1) ** i * comb(m + i - 1, i)
    h = [sum(a[j] * b[d - j] for j in range(d + 1)) for d in range(upto + 1)]
    dreg = next(d for d, x in enumerate(h) if x <= 0)
    return h, dreg


def cum(n, D):
    return sum(comb(n, d) for d in range(D + 1))


cases = [
    {"label": "Stage-1 cell: 17 quadratics, 18 Boolean variables", "n": 18, "m": 17},
    {"label": "after ell substitution: 16 quadratics, 17 variables (H-CERTBIN-5e71c9)", "n": 17, "m": 16},
    {"label": "n = 19, l = 10: 19 quadratics, 20 variables (Coordinator's unchecked series)", "n": 20, "m": 19},
    {"label": "n = 19 after a linear substitution: 18 quadratics, 19 variables", "n": 19, "m": 18},
]
out = {"task": "TASK-20260924-d95e70", "joint": "J8 (2), (5)", "cases": []}
for c in cases:
    h, dreg = series(c["n"], c["m"])
    rec = dict(c)
    rec["coefficients_h0_to_h8"] = h
    rec["D_reg"] = dreg
    for D in (3, 4):
        rows = cum(c["n"], D - 2) * c["m"]
        cols = cum(c["n"], D)
        quo = sum(h[: D + 1])
        rec[f"D{D}"] = {"rows": rows, "cols": cols, "sum_h_le_D": quo,
                        "semi_regular_rank": cols - quo, "row_dependencies": rows - (cols - quo),
                        "refuted_expected": quo <= 0}
    out["cases"].append(rec)

# trivial-syzygy count at D = 4 for 17 quadratics: Koszul C(17,2) + field 17
out["trivial_syzygies_D4_m17"] = {"koszul": comb(17, 2), "field": 17, "total": comb(17, 2) + 17,
                                  "R4_rows": 2924, "R4_minus_trivial": 2924 - (comb(17, 2) + 17),
                                  "equals_series_rank": 2924 - (comb(17, 2) + 17) == out["cases"][0]["D4"]["semi_regular_rank"]}
# bilinear-support ceiling at D = 5 (18 vars, blocks of 9): pure-block degree-5 monomials never occur in M_5
pure5 = 2 * comb(9, 5)
out["bilinear_support_ceiling_M5"] = {"pure_block_degree5_monomials": pure5,
                                      "dim_B_le5": cum(18, 5), "rank_M5_ceiling": cum(18, 5) - pure5,
                                      "degree5_top_ceiling": comb(18, 5) - pure5}
out["fixtures"] = {"M4": [cum(18, 2) * 17, cum(18, 4)], "M5": [cum(18, 3) * 17, cum(18, 5)],
                   "R4prime": [cum(17, 2) * 17, cum(17, 4)], "dim_B'_le3_17vars": cum(17, 3),
                   "n19_M4": [cum(20, 2) * 19, cum(20, 4)]}
json.dump(out, open(os.path.join(HERE, "series.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
