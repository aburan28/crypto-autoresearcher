#!/usr/bin/env python3
"""Exact sizing of the GF(2) Macaulay blocks EXP-SEMBIN-4fa22c declares.

WHY THIS SCRIPT EXISTS RATHER THAN A CITATION OF THE PARENT SIZING.
DEC-20260913-47bbb7's sizing (coordinator-engine-sizing/size_degree4.py under
GOAL-SEMBIN-5078bc BATCH-9d649f) assumed EVERY descended generator is cubic and
counted multipliers of degree <= D-3.  Reading Nagao Definition 2 against
Definition 3 shows that is wrong in a way that matters:

  * S_3(X_a, X_b, X_c) with three VARIABLE arguments descends to total degree 3
    at p = 2.  The Semaev polynomial for a binary curve is
    S_3 = (x_a x_b + x_a x_c + x_b x_c)^2 + x_a x_b x_c + a_6; squaring is the
    Frobenius, hence F_2-linear on descent coordinates, and for a polynomial P
    over F_2, P^2 == P mod S_fe, so the squared symmetric term descends to
    degree 2 and the cubic term to degree 3.  Total degree 3.  CUBIC.
  * The LAST link of EQS1/EQS3, S_3(U_{m-2}, X_m, x(R)), has a CONSTANT third
    argument.  Both surviving terms are then bilinear in the two variable
    arguments, so the descent has total degree 2.  QUADRATIC.
  * At m = 2 the chain degenerates to that single link, so at m = 2 EVERY
    generator is quadratic and there are no cubic generators at all.

So the generator profile is: n(m-2) cubic descended generators and n quadratic
ones, for a total of n(m-1) as Nagao's Definition 4 remark states.  This changes
the degree-4 row count by a factor of ~N/2, because a quadratic generator takes
DEGREE-2 multipliers to reach total degree 4 while a cubic one takes degree-1.
It is also not a detail: Semaev's own degree-4 fall is read off x*u*S_3(x,u,R_X),
a degree-2 multiplier on a quadratic generator (Nagao, text above Lemma 3), so a
degree-4 block that omits degree-2 multipliers CANNOT see the fall the claim is
about.

WHAT IS COMPUTED.  For the operational definition fixed in the contract,

    R      = F_2[X_1..X_N]/(X_i^2 - X_i)          (squarefree monomials)
    A_D    = rows NF(m * f), one per (monomial m, generator f) with
             deg m + deg f = D EXACTLY, columns = squarefree monomials deg <= D
    A_D^t  = the submatrix of A_D on the degree-EXACTLY-D columns
    nu_D   = rank(A_D) - rank(A_D^t)             (independent nonzero falls)
    d'_F   = min { D : nu_D > 0 }

this script reports rows, columns, the dense-bitset footprint of an incremental
pivot-basis rank (memory = rank * rowbytes, rank <= min(rows, cols)), and the
XOR traffic of that elimination (rows * rank / 2 row-XORs) as a runtime proxy.

NOTHING HERE IS MEASURED AND NO DEGREE IS ASSERTED.  These are exact
combinatorial counts plus a measured Python big-int XOR throughput.  What rank
these blocks have -- and therefore what d'_F is -- is exactly what the
experiment is for, and this script computes no rank.
"""

from __future__ import annotations

import random
import time
from math import comb

# Measured on this host by bench_xor() below; overwritten at runtime.
XOR_GBPS = 3.0


def mono_exact(n_vars: int, d: int) -> int:
    """Squarefree monomials of degree exactly d in n_vars variables."""
    return comb(n_vars, d) if 0 <= d <= n_vars else 0


def mono_le(n_vars: int, d: int) -> int:
    return sum(mono_exact(n_vars, i) for i in range(0, d + 1))


def profile(n: int, m: int, k: int) -> tuple[int, int, int]:
    """(N, #cubic generators, #quadratic generators) for EQS2/EQS4 at (n,m,k).

    N = k*m + n*(m-2): the X_i contribute k F_2-variables each, the U_i
    contribute n each.  Nagao's remark to Definition 4 quotes n(m-1), which is
    this count specialised to the diagonal k*m = n.
    """
    n_vars = k * m + n * max(m - 2, 0)
    cubic = n * max(m - 2, 0)
    quad = n
    return n_vars, cubic, quad


def block(n: int, m: int, k: int, D: int) -> dict:
    n_vars, cubic, quad = profile(n, m, k)
    rows = cubic * mono_exact(n_vars, D - 3) + quad * mono_exact(n_vars, D - 2)
    cols = mono_le(n_vars, D)
    top = mono_exact(n_vars, D)
    row_bytes = (cols + 7) // 8
    rank_bound = min(rows, cols)
    # incremental pivot basis: only the basis is resident
    mem_bytes = rank_bound * (row_bytes + 40)
    xor_bytes = rows * (rank_bound / 2) * row_bytes
    return {
        "n": n, "m": m, "k": k, "N": n_vars, "D": D,
        "cubic": cubic, "quad": quad,
        "rows": rows, "cols": cols, "top": top,
        "row_KiB": row_bytes / 1024,
        "mem_GB": mem_bytes / 2**30,
        "xor_GB": xor_bytes / 2**30,
        "seconds": xor_bytes / 2**30 / XOR_GBPS,
    }


def bench_xor() -> float:
    """Measured throughput of Python int XOR at the row widths in play."""
    random.seed(20260913)
    best = []
    for bits in (41449, 124314, 342541):
        nbytes = (bits + 7) // 8
        a = random.getrandbits(bits)
        b = random.getrandbits(bits)
        reps = 20000
        t0 = time.perf_counter()
        for _ in range(reps):
            a ^= b
        dt = time.perf_counter() - t0
        gbps = reps * nbytes / dt / 2**30
        best.append(gbps)
        print(f"  XOR bench: row {nbytes/1024:8.1f} KiB  "
              f"{reps/dt:12,.0f} xor/s  {gbps:5.2f} GB/s")
    return min(best)


HDR = (f"{'n':>3} {'m':>2} {'k':>3} {'N':>4} {'cub':>5} {'qud':>4} "
       f"{'rows':>8} {'cols':>9} {'topcols':>9} {'rowKiB':>7} "
       f"{'memGB':>7} {'xorGB':>9} {'sec':>8}")


def show(cells, D):
    print(HDR)
    print("-" * len(HDR))
    out = []
    for (n, m, k) in cells:
        s = block(n, m, k, D)
        out.append(s)
        print(f"{s['n']:3d} {s['m']:2d} {s['k']:3d} {s['N']:4d} "
              f"{s['cubic']:5d} {s['quad']:4d} {s['rows']:8d} {s['cols']:9d} "
              f"{s['top']:9d} {s['row_KiB']:7.1f} {s['mem_GB']:7.3f} "
              f"{s['xor_GB']:9.1f} {s['seconds']:8.0f}")
    return out


def sweep(m, D, mem_cap_gb, sec_cap, n_hi=64):
    """Largest n at m with k = ceil(n/m) inside both caps."""
    ok = None
    for n in range(4, n_hi + 1):
        if m == 2 and n % 2:
            continue
        k = -(-n // m)
        s = block(n, m, k, D)
        if s["mem_GB"] <= mem_cap_gb and s["seconds"] <= sec_cap:
            ok = s
    return ok


def main() -> None:
    global XOR_GBPS
    print("Measuring Python big-int XOR throughput on this host "
          "(the rank inner loop):")
    XOR_GBPS = bench_xor()
    print(f"  conservative throughput used below: {XOR_GBPS:.2f} GB/s\n")

    MEM_CAP = 1.5      # GB, inside the contract's 2 GB declaration
    SEC_CAP = 5400.0   # s per arm, inside the contract's per-run wall clock

    print("=" * 118)
    print("D = 4 BLOCK, DIAGONAL k = ceil(n/m): largest n inside "
          f"{MEM_CAP} GB and {SEC_CAP:.0f} s")
    print("=" * 118)
    print(HDR)
    print("-" * len(HDR))
    for m in (2, 3, 4, 5, 6, 7, 8):
        s = sweep(m, 4, MEM_CAP, SEC_CAP)
        if s is None:
            print(f"  m={m}: no n fits")
            continue
        print(f"{s['n']:3d} {s['m']:2d} {s['k']:3d} {s['N']:4d} "
              f"{s['cubic']:5d} {s['quad']:4d} {s['rows']:8d} {s['cols']:9d} "
              f"{s['top']:9d} {s['row_KiB']:7.1f} {s['mem_GB']:7.3f} "
              f"{s['xor_GB']:9.1f} {s['seconds']:8.0f}")

    print()
    print("=" * 118)
    print("DECLARED CELL LIST, D = 4")
    print("=" * 118)
    cells_d4 = [
        # tier A: diagonal k = ceil(n/m), the Semaev/Nagao parameter regime
        (8, 2, 4), (12, 2, 6), (16, 2, 8), (20, 2, 10), (24, 2, 12),
        (9, 3, 3), (12, 3, 4), (15, 3, 5),
        (8, 4, 2), (12, 4, 3),
        (10, 5, 2),
        (12, 6, 2),
        # tier B: off-diagonal k > ceil(n/m) -- Semaev section 4.4 discrimination
        (12, 2, 7), (12, 2, 8), (16, 2, 9),
        (9, 3, 4), (12, 3, 5),
    ]
    d4 = show(cells_d4, 4)

    print()
    print("=" * 118)
    print("SAME CELLS AT D = 5 (the escalation arm, run only where it fits)")
    print("=" * 118)
    d5 = show(cells_d4, 5)

    print()
    print("=" * 118)
    print("D = 3 AND D = 2 PRESCANS (cheap; every cell runs these first)")
    print("=" * 118)
    for D in (2, 3):
        print(f"-- D = {D}")
        show(cells_d4, D)
        print()

    print("=" * 118)
    print("BUDGET CHECK")
    print("=" * 118)
    worst_mem_4 = max(d4, key=lambda s: s["mem_GB"])
    worst_sec_4 = max(d4, key=lambda s: s["seconds"])
    print(f"D=4 worst memory: {worst_mem_4['mem_GB']:.3f} GB at "
          f"n={worst_mem_4['n']} m={worst_mem_4['m']} k={worst_mem_4['k']}")
    print(f"D=4 worst time:   {worst_sec_4['seconds']:.0f} s at "
          f"n={worst_sec_4['n']} m={worst_sec_4['m']} k={worst_sec_4['k']}")
    fits5 = [s for s in d5 if s["mem_GB"] <= MEM_CAP and s["seconds"] <= SEC_CAP]
    print(f"D=5 cells inside {MEM_CAP} GB and {SEC_CAP:.0f} s: "
          + ", ".join(f"({s['n']},{s['m']},{s['k']})" for s in fits5))
    print()
    print("Arms per cell: EQS2, EQS4 family A, EQS4 family B, null-equal,")
    print("random-shape control  = 5 blocks, each run at D = 2,3,4 (and 5 where")
    print("declared).  Only ONE block is resident at a time, so the memory")
    print("figure above is the run's peak, not a sum.")


if __name__ == "__main__":
    main()
