#!/usr/bin/env python3
"""EXP-SEMBIN-35bf67 Stage 0 size worksheet (pure arithmetic, no RNG).

For a cell (n, m, t, k) the Weil descent of Semaev 2015 eq. (5) has
  N = n(t-2) + k t Boolean unknowns,
  n(t-2) cubic + n quadratic equations (t >= 3), or n quadratic equations (t = 2).
Degree-4 truncation sizes:
  M_le4 = sum_{i<=4} C(N, i)          (squarefree monomials of degree <= 4)
  M_le3 = sum_{i<=3} C(N, i)          (low region: closure multiplies these)
  initial Macaulay rows = sum_f C(N, <= 4 - deg f)
Memory figures (bits -> GiB):
  initial_dense  = rows0 * M_le4            (the matrix the IDEA quotes)
  full_dense_rref= M_le4^2                  (dense square echelon basis, upper bound)
  compact_rref   = max_r r (M_le4 - r) = M_le4^2 / 4  (RREF stored on non-pivot columns only;
                   this is the representation both rank arms of this experiment use)
  product_rows_bound = rows0 + N * M_le3    (upper bound on rows the closure can generate)
"""
import json
import sys
from math import comb


def mle(N, d):
    return sum(comb(N, i) for i in range(d + 1))


def cell_sizes(n, m, t, k):
    N = n * (t - 2) + k * t
    if t == 2:
        eq = [(2, n)]
    else:
        eq = [(3, n * (t - 2)), (2, n)]
    rows0 = sum(cnt * mle(N, 4 - d) for d, cnt in eq)
    M4 = mle(N, 4)
    M3 = mle(N, 3)
    gib = lambda bits: bits / 8 / 2**30
    return {
        "n": n, "m": m, "t": t, "k": k, "N": N,
        "equations": {f"deg{d}": cnt for d, cnt in eq},
        "excess_equations_minus_unknowns": n * (t - 1) - N,
        "M_le4": M4, "M_le3": M3,
        "initial_macaulay_rows": rows0,
        "initial_dense_GiB": round(gib(rows0 * M4), 3),
        "full_dense_square_GiB": round(gib(M4 * M4), 3),
        "compact_rref_peak_GiB": round(gib(M4 * M4 / 4), 3),
        "product_rows_upper_bound": rows0 + N * M3,
        "within_8GiB_compact": gib(M4 * M4 / 4) < 8.0,
    }


def dreg_anchor_sizes(n, t, D):
    k = (n + t - 1) // t
    N = n * (t - 2) + k * t
    rows = n * (t - 2) * mle(N, D - 3) + n * mle(N, D - 2)
    return {"n": n, "t": t, "m": t, "k": k, "D": D, "N": N, "macaulay_rows": rows,
            "C_N_le_D": mle(N, D)}


if __name__ == "__main__":
    out = {
        "stage2": [cell_sizes(*c) for c in [(30, 2, 2, 15), (40, 2, 2, 20), (21, 3, 3, 7),
                                             (45, 2, 2, 23), (25, 3, 3, 9), (50, 2, 2, 25)]],
        "stage3_offdiagonal": [cell_sizes(*c) for c in [(40, 2, 2, 21), (40, 2, 2, 22),
                                                        (25, 3, 3, 10)]],
        "stage3_ladder_k4_if_m_t_3": [cell_sizes(n, 3, 3, 4) for n in range(13, 29)],
        "stage3_ladder_k4_if_m_t_4": [cell_sizes(n, 4, 4, 4) for n in range(13, 29)],
        "stage3_ladder_k7_if_m_t_3": [cell_sizes(n, 3, 3, 7) for n in range(19, 31)],
        "stage1_dreg_anchors": [dreg_anchor_sizes(15, 3, 5), dreg_anchor_sizes(18, 3, 5)],
    }
    json.dump(out, sys.stdout, indent=1)
