#!/usr/bin/env python3
"""Final declared-cell budget for EXP-SEMBIN-4fa22c, on the MEASURED constant.

size_macaulay.py charged the elimination at 20.87 GB/s, which is what a bare
Python int-XOR microbenchmark reports.  bench_rank.py then measured the WHOLE
inner loop (pivot scan, dict lookup, interpreter overhead) on random matrices of
the declared shapes and reported 14.93 GB/s at the narrowest declared row.  That
narrow figure is the conservative one and is the constant used here, so the
contract's wall clock rests on a measured worst case rather than on the
throughput of one instruction.

Nothing here is a rank and nothing here is a degree.  These are exact
combinatorial counts times a measured throughput.
"""

from __future__ import annotations

from math import comb

# bench_rank.py, narrowest declared shape (n=20 m=2 k=10): 14.93 GB/s.
XOR_GBPS = 14.93

# Declared arms.  A4 is a SYSTEM-LEVEL identity gate, not a rank: at v = 0 the
# descended EQS4 must equal the descended EQS2 coefficient-for-coefficient, and
# that is checked on the polynomial systems before any linear algebra.  It
# therefore costs no Macaulay block, which is why RANK_ARMS excludes it.
RANK_ARMS = [
    "A1-EQS2",           # Semaev baseline, Nagao Definition 4
    "A2-EQS4-famA",      # disjoint coset family {v_i}, Nagao Definition 8
    "A3-EQS4-famB",      # second disjoint family {v_i'} -- prediction P3
    "A5-null-equal",     # all v_i = c != 0 (a measurement, not a gate)
    "A6-random-shape",   # random system, identical shape and support
    "A7-U-shift",        # U_i -> U_i + w_i, provably invariant (instrument)
]


def mono_exact(n_vars: int, d: int) -> int:
    return comb(n_vars, d) if 0 <= d <= n_vars else 0


def mono_le(n_vars: int, d: int) -> int:
    return sum(mono_exact(n_vars, i) for i in range(d + 1))


def profile(n: int, m: int, k: int) -> tuple[int, int, int]:
    return k * m + n * max(m - 2, 0), n * max(m - 2, 0), n


def block(n: int, m: int, k: int, D: int) -> dict:
    n_vars, cubic, quad = profile(n, m, k)
    rows = cubic * mono_exact(n_vars, D - 3) + quad * mono_exact(n_vars, D - 2)
    cols = mono_le(n_vars, D)
    row_bytes = (cols + 7) // 8
    rank_bound = min(rows, cols)
    mem = rank_bound * (row_bytes + 40) / 2**30
    xor_gb = rows * (rank_bound / 2) * row_bytes / 2**30
    return {"rows": rows, "cols": cols, "top": mono_exact(n_vars, D),
            "N": n_vars, "cubic": cubic, "quad": quad,
            "mem_GB": mem, "xor_GB": xor_gb, "sec": xor_gb / XOR_GBPS}


MEM_CAP = 1.5   # GB, inside the contract's 2 GB declaration
SEEDS_MAX = 3

# (n, m, k, seeds, rank_arms, tier)
#   seeds     = independent (curve a_6, target R, coset family) draws
#   rank_arms = how many of RANK_ARMS run at this cell
# Degrees D = 2, 3, 4 are MANDATORY at every cell.  D = 5 is CONDITIONAL: since
# d'_F = min{D : nu_D > 0}, a cell that falls at D <= 4 never needs D = 5, and
# Nagao Proposition 2 predicts exactly that at p = 2.  D = 5 is therefore
# budgeted as a reserve, reported separately below.
CELLS = [
    # TIER A -- diagonal k = ceil(n/m), the Semaev/Nagao parameter regime.
    # m = 2 carried as far as budget allows: this family sets the recorded
    # scope limit in n, and it is the cheapest family because at m = 2 every
    # descended generator is quadratic.
    (8,  2,  4, 3, 6, "A"),
    (12, 2,  6, 3, 6, "A"),
    (16, 2,  8, 3, 6, "A"),
    (20, 2, 10, 3, 6, "A"),
    (24, 2, 12, 3, 6, "A"),
    (28, 2, 14, 3, 6, "A"),
    (32, 2, 16, 3, 6, "A"),
    (36, 2, 18, 2, 6, "A"),
    (40, 2, 20, 2, 6, "A"),
    (44, 2, 22, 1, 4, "A"),
    # longer chains: m is the chain length Nagao's construction varies, so the
    # claim must be probed along m and not only along n.
    (6,  3,  2, 3, 6, "A"),
    (9,  3,  3, 3, 6, "A"),
    (12, 3,  4, 3, 6, "A"),
    (15, 3,  5, 3, 6, "A"),
    (18, 3,  6, 3, 6, "A"),
    (21, 3,  7, 2, 6, "A"),
    (24, 3,  8, 1, 4, "A"),
    (8,  4,  2, 3, 6, "A"),
    (12, 4,  3, 3, 6, "A"),
    (16, 4,  4, 2, 6, "A"),
    (10, 5,  2, 3, 6, "A"),
    # TIER B -- off-diagonal k > ceil(n/m).  Semaev's own analysis is sensitive
    # to k relative to n/m, so a claim probed only on the diagonal is probed on
    # a measure-zero slice of the parameter space.
    (12, 2,  7, 2, 6, "B"),
    (12, 2,  8, 2, 6, "B"),
    (16, 2,  9, 2, 6, "B"),
    (16, 2, 12, 2, 6, "B"),
    (20, 2, 13, 2, 6, "B"),
    (9,  3,  4, 2, 6, "B"),
    (12, 3,  5, 2, 6, "B"),
    (15, 3,  7, 2, 6, "B"),
    (8,  4,  3, 2, 6, "B"),
    # TIER C -- reach cell: largest N inside the memory cap at D = 4.
    (12, 6,  2, 1, 4, "C"),
]


def d5_fits(n: int, m: int, k: int) -> bool:
    return block(n, m, k, 5)["mem_GB"] <= MEM_CAP


def main() -> None:
    print(f"MEASURED constant: {XOR_GBPS} GB/s (bench_rank.py, narrowest "
          f"declared shape).")
    print(f"Memory cap used for admission: {MEM_CAP} GB.  Mandatory degrees "
          f"D = 2,3,4; D = 5 conditional.\n")
    hdr = (f"{'tier':4s} {'n':>3s} {'m':>2s} {'k':>3s} {'N':>3s} {'sd':>2s} "
           f"{'arm':>3s} {'blocks':>6s} {'peakMemGB':>9s} {'mandSec':>8s} "
           f"{'d5?':>4s} {'d5Sec':>8s}")
    print(hdr)
    print("-" * len(hdr))
    total = 0.0
    reserve = 0.0
    peak = 0.0
    per_tier: dict[str, float] = {}
    nblocks = 0
    for (n, m, k, seeds, arms, tier) in CELLS:
        sec = 0.0
        cell_peak = 0.0
        for D in (2, 3, 4):
            b = block(n, m, k, D)
            sec += b["sec"] * seeds * arms
            cell_peak = max(cell_peak, b["mem_GB"])
        assert cell_peak <= MEM_CAP, (n, m, k, cell_peak)
        blocks = 3 * seeds * arms
        nblocks += blocks
        total += sec
        peak = max(peak, cell_peak)
        per_tier[tier] = per_tier.get(tier, 0.0) + sec
        # reserve: 2 arms (EQS2 + EQS4-A), 1 seed, only where memory allows
        ok5 = d5_fits(n, m, k)
        s5 = block(n, m, k, 5)["sec"] * 2 if ok5 else 0.0
        reserve += s5
        print(f"{tier:4s} {n:3d} {m:2d} {k:3d} {block(n,m,k,2)['N']:3d} "
              f"{seeds:2d} {arms:3d} {blocks:6d} {cell_peak:9.3f} "
              f"{sec:8.0f} {'yes' if ok5 else 'no':>4s} {s5:8.0f}")
    print("-" * len(hdr))
    for tier in sorted(per_tier):
        print(f"  tier {tier}: {per_tier[tier]:9.0f} s = "
              f"{per_tier[tier]/3600:5.2f} h")
    print(f"\nMANDATORY TOTAL   {total:8.0f} s = {total/3600:5.2f} h "
          f"({nblocks} blocks)")
    print(f"D=5 RESERVE (all)  {reserve:8.0f} s = {reserve/3600:5.2f} h "
          f"(charged only where nu_4 = 0)")
    print(f"PEAK RESIDENT      {peak:.3f} GB (one block resident at a time)")
    print(f"CELLS              {len(CELLS)}  "
          f"(tier A {sum(1 for c in CELLS if c[5]=='A')}, "
          f"B {sum(1 for c in CELLS if c[5]=='B')}, "
          f"C {sum(1 for c in CELLS if c[5]=='C')})")

    print("\nPER-CELL D=4 SHAPE (the block the claim is read from)")
    h2 = (f"{'tier':4s} {'n':>3s} {'m':>2s} {'k':>3s} {'N':>3s} {'cub':>4s} "
          f"{'qud':>3s} {'rows':>7s} {'cols':>8s} {'topcols':>8s} "
          f"{'rowKiB':>7s} {'memGB':>7s} {'sec':>8s}")
    print(h2)
    print("-" * len(h2))
    for (n, m, k, seeds, arms, tier) in CELLS:
        b = block(n, m, k, 4)
        print(f"{tier:4s} {n:3d} {m:2d} {k:3d} {b['N']:3d} {b['cubic']:4d} "
              f"{b['quad']:3d} {b['rows']:7d} {b['cols']:8d} {b['top']:8d} "
              f"{(b['cols']+7)//8/1024:7.1f} {b['mem_GB']:7.3f} {b['sec']:8.1f}")

    print("\nPER-CELL D=5 SHAPE (conditional escalation; 'no' = refused on "
          "memory)")
    print(h2)
    print("-" * len(h2))
    for (n, m, k, seeds, arms, tier) in CELLS:
        b = block(n, m, k, 5)
        flag = "" if d5_fits(n, m, k) else "   REFUSED"
        print(f"{tier:4s} {n:3d} {m:2d} {k:3d} {b['N']:3d} {b['cubic']:4d} "
              f"{b['quad']:3d} {b['rows']:7d} {b['cols']:8d} {b['top']:8d} "
              f"{(b['cols']+7)//8/1024:7.1f} {b['mem_GB']:7.3f} "
              f"{b['sec']:8.1f}{flag}")

    print("\nWHAT STOPPED EACH FAMILY GROWING (D = 4, cap "
          f"{MEM_CAP} GB / declared per-block wall clock)")
    for (m, nlist) in ((2, (44, 48, 52)), (3, (24, 27)), (4, (16, 20)),
                       (5, (10, 15)), (6, (12, 14)), (7, (14,))):
        for n in nlist:
            k = -(-n // m)
            b = block(n, m, k, 4)
            verdict = ("declared" if (n, m, k) in [(c[0], c[1], c[2])
                                                  for c in CELLS]
                       else ("over memory cap" if b["mem_GB"] > MEM_CAP
                             else "fits memory, excluded on time"))
            print(f"  m={m:2d} n={n:3d} k={k:3d} N={b['N']:3d} "
                  f"mem={b['mem_GB']:7.3f} GB sec={b['sec']:9.0f}  {verdict}")

    print("\nRECORDED SCOPE LIMITS")
    print(f"  largest n declared : n = 44 (cell 44,2,22), N = 44")
    print(f"  largest N declared : N = 60 (cell 12,6,2), n = 12, m = 6")
    print(f"  largest m declared : m = 6 (cell 12,6,2)")
    print("  These are BUDGET limits, not degrees.  A bound observed at these")
    print("  cells is evidence about these cells only.")


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
