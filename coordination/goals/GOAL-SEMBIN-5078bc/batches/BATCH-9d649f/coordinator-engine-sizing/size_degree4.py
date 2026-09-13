#!/usr/bin/env python3
"""Exact sizing of the degree-4 F_2 Macaulay blocks EXP-SEMBIN-c2c312 and
EXP-SEMBIN-7e1371 declare, to decide whether IMP-SEMBIN-ENGINE as recorded is
wider than the facts.

IMP-SEMBIN-ENGINE says the degree lane is blocked because no Groebner engine is
installed. But neither experiment asks for a Groebner completion:
EXP-SEMBIN-7e1371's own title is "using degree-4 Macaulay rank certificates
INSTEAD OF Groebner completions", and EXP-SEMBIN-c2c312 instruments a Macaulay
rank. A degree-D Macaulay rank over F_2 needs a Boolean system and GF(2)
linear algebra -- not an F4 implementation.

This script computes, per declared cell, the exact shape of that block:

  N     = n(t-2) + kt          variables, per both specifications
  cols  = sum_{d<=D} C(N, d)   Boolean monomials of degree <= D
  rows  = n(t-1) cubic generators, each multiplied by every monomial of degree
          <= D-3, i.e. n(t-1) * sum_{d<=D-3} C(N,d)

and the memory a dense bitset elimination needs (one Python int per row,
cols bits wide), plus the XOR traffic of a full elimination as a runtime proxy.

NOTHING HERE IS MEASURED and no degree is asserted. These are exact
combinatorial counts at the parameters the two frozen contracts declare. They
decide feasibility, not any research question: whether the resulting rank
equals or differs from any published value is exactly what the experiments are
for, and this script computes no rank.
"""

from math import comb

D = 4        # both contracts fix the certificate at total degree 4
GEN_DEG = 3  # the chained S_3 system is cubic over F_2 per both specifications


def shape(n: int, t: int, k: int, degree: int = D) -> dict:
    n_vars = n * (t - 2) + k * t
    cols = sum(comb(n_vars, d) for d in range(0, degree + 1))
    generators = n * (t - 1)
    multipliers = sum(comb(n_vars, d) for d in range(0, degree - GEN_DEG + 1))
    rows = generators * multipliers
    row_bytes = (cols + 7) // 8
    dense_gb = rows * row_bytes / 2**30
    # A full elimination XORs O(rank * rows) row pairs; rank <= min(rows, cols).
    rank_bound = min(rows, cols)
    xor_bytes = rank_bound * rows * row_bytes / 2
    return {
        "n": n, "t": t, "k": k, "N": n_vars,
        "cols": cols, "generators": generators, "rows": rows,
        "row_KiB": row_bytes / 1024, "dense_GB": dense_gb,
        "xor_traffic_GB": xor_bytes / 2**30,
    }


CELLS = [
    # EXP-SEMBIN-c2c312 reproduction cells (paper-reported d_F4 = 4)
    ("c2c312 reproduction", 13, 4, 4),
    ("c2c312 reproduction", 17, 3, 6),
    # c2c312 separation cells
    ("c2c312 separation", 15, 3, 3),
    ("c2c312 separation", 19, 3, 7),
    ("c2c312 separation", 21, 3, 7),
    ("c2c312 separation", 12, 6, 2),
    # c2c312 off-diagonal
    ("c2c312 off-diagonal", 17, 3, 7),
    ("c2c312 off-diagonal", 17, 3, 8),
    # EXP-SEMBIN-7e1371 diagonal baselines and the m = 2 window
    ("7e1371 baseline", 17, 3, 6),
    ("7e1371 baseline", 40, 2, 20),
    ("7e1371 m=2 window", 41, 2, 21),
    ("7e1371 m=2 window", 43, 2, 22),
    ("7e1371 m=2 window", 45, 2, 23),
    # 7e1371 off-diagonal sweep extremes
    ("7e1371 sweep", 19, 3, 10),
    ("7e1371 sweep", 21, 3, 10),
    ("7e1371 sweep", 13, 4, 6),
]


def main() -> None:
    print(f"Degree-{D} F_2 Macaulay block shape at every declared cell.")
    print("N = n(t-2) + kt; cols = #monomials of degree <= 4; "
          "rows = n(t-1) generators x #monomials of degree <= 1.")
    print()
    header = (f"{'cell':22s} {'n':>3s} {'t':>2s} {'k':>3s} {'N':>4s} "
              f"{'cols':>10s} {'rows':>8s} {'row KiB':>8s} {'dense GB':>9s} "
              f"{'XOR GB':>9s}")
    print(header)
    print("-" * len(header))
    worst_mem = worst_xor = None
    for label, n, t, k in CELLS:
        s = shape(n, t, k)
        print(f"{label:22s} {s['n']:3d} {t:2d} {k:3d} {s['N']:4d} "
              f"{s['cols']:10d} {s['rows']:8d} {s['row_KiB']:8.1f} "
              f"{s['dense_GB']:9.3f} {s['xor_traffic_GB']:9.1f}")
        if worst_mem is None or s["dense_GB"] > worst_mem[0]:
            worst_mem = (s["dense_GB"], label, n, t, k)
        if worst_xor is None or s["xor_traffic_GB"] > worst_xor[0]:
            worst_xor = (s["xor_traffic_GB"], label, n, t, k)

    print()
    print(f"worst dense footprint: {worst_mem[0]:.3f} GB at {worst_mem[1]} "
          f"n={worst_mem[2]} t={worst_mem[3]} k={worst_mem[4]}")
    print(f"worst XOR traffic:     {worst_xor[0]:.1f} GB at {worst_xor[1]} "
          f"n={worst_xor[2]} t={worst_xor[3]} k={worst_xor[4]}")
    print()
    print("Both contracts declare maximum_memory_gb: 8 and a per-run wall clock of")
    print("3600 s (c2c312) / 5400 s (7e1371), single worker.")

    print()
    print("For contrast, the degree-5 block src/h012c_block_m4ri.py was written for")
    print("(its header records exact validation ranks 28096 at n=12 and 143882 at n=18),")
    print("which is why that engine chunks columns and carries a staircase basis:")
    for n, t, k in ((12, 6, 2), (18, 3, 6)):
        s5 = shape(n, t, k, degree=5)
        print(f"  degree 5, n={n} t={t} k={k}: N={s5['N']}, cols={s5['cols']}, "
              f"rows={s5['rows']}, dense {s5['dense_GB']:.1f} GB")
    print()
    print("CONCLUSION THIS SCRIPT SUPPORTS, AND ONLY THIS: the degree-4 blocks the two")
    print("frozen contracts declare fit in their own declared budgets under a dense")
    print("bitset elimination, so neither needs a Groebner engine and neither needs the")
    print("column-chunking machinery degree 5 forces. It says nothing about what rank")
    print("those blocks have, nor about d_F4, nor about Assumption 1.")


if __name__ == "__main__":
    main()
