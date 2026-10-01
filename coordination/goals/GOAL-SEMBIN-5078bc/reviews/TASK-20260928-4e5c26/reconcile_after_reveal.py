#!/usr/bin/env python3
"""POST-REVEAL reconciliation for TASK-20260928-4e5c26.

Written AFTER blind_derivation.md was saved and hashed (pre_reveal_hashes.txt) and
AFTER reading experiments/EXP-SEMBIN-04ec3c/runs/RUN-SEMBIN-c68773/raw-result.json.
It is NOT part of the blind derivation. It re-runs the blind model's formulas under
the three conventions that raw-result.json exposes, to check that every disagreement
is a convention difference and not an arithmetic error on either side:

  C1  K = |F|            (blind primary: K = |F|/2)
  C2  LA = |F|^2         (blind primary: m * K^2), per the raw result's
                         inherited_assumptions "Sparse linear algebra at |F|^2 time"
  C3  real d on a grid   (blind primary: integer d in [1, n-1]); the grid is 0.05
                         for the min-store rows and 0.25 for the store-free rows,
                         both over [1, n], as read off the raw result's d values

Nothing else changes: RC = K * m! * N / |F|^s, uncapped trials, build not charged,
B = log2(0.886) + N_bits/2, N = r at n = 131 and 2^n otherwise.
"""

import json
import math
import sys

R131 = 680564733841876926932320129493409985129
RAW = "experiments/EXP-SEMBIN-04ec3c/runs/RUN-SEMBIN-c68773/raw-result.json"


def nbits(n):
    return math.log2(R131) if n == 131 else float(n)


def B(n):
    return math.log2(0.886) + nbits(n) / 2


def lse(a, b):
    mx = max(a, b)
    return mx + math.log2(2 ** (a - mx) + 2 ** (b - mx))


def total(n, m, d, s):
    rc = d + math.log2(math.factorial(m)) + nbits(n) - s * d   # C1
    la = 2 * d                                                  # C2
    return lse(rc, la), rc, la


def grid(n, step):
    k = int(round((n - 1) / step))
    return [round(1 + i * step, 10) for i in range(k + 1)]


def min_store(n, m, step=0.05):
    best = None
    for s in range(0, m // 2 + 1):
        for d in grid(n, step):
            t, _, _ = total(n, m, d, s)
            if t < B(n):
                st = round(s * d, 10)
                if best is None or st < best[0] - 1e-12:
                    best = (st, d, s, t)
                break
    return best


def store_free_min_total(n, m, step=0.25):
    best = None
    for s in range(0, m // 2 + 1):
        for d in grid(n, step):
            t, rc, la = total(n, m, d, s)
            if best is None or t < best[0] - 1e-12:
                best = (t, d, s, rc, la)
    return best


def main(repo):
    raw = json.load(open(f"{repo}/{RAW}"))
    ok = bad = 0
    mismatches = []
    for r in raw["min_store_for_subrho"]:
        n, m = r["n"], r["m"]
        mine = min_store(n, m)
        if not r["reachable"]:
            if mine is None:
                ok += 1
            else:
                bad += 1
                mismatches.append(("unreachable_vs_found", n, m, mine))
            continue
        if mine is None:
            bad += 1
            mismatches.append(("found_vs_unreachable", n, m, r))
            continue
        st, d, s, t = mine
        if (abs(st - r["log2_store_entries"]) < 1e-6 and abs(d - r["d"]) < 1e-6
                and abs(t - r["log2_total"]) < 6e-5):
            ok += 1
        else:
            bad += 1
            mismatches.append(("value", n, m, (st, d, s, round(t, 4)),
                               (r["log2_store_entries"], r["d"], r["log2_total"])))
    print(f"min_store_for_subrho rows reproduced under C1+C2+C3: {ok} ok, {bad} mismatched")
    for x in mismatches:
        print("  MISMATCH", x)

    ok = bad = 0
    for r in raw["mitm_store_free"]:
        if r["n"] != 131:
            continue
        t, d, s, rc, la = store_free_min_total(131, r["m"])
        good = (abs(t - r["log2_total"]) < 6e-5 and abs(d - r["d"]) < 1e-6
                and s == r["s_tabulated"])
        ok += good
        bad += not good
        if not good:
            print("  n=131 store-free MISMATCH m=%d mine=(%.4f,d=%.2f,s=%d) raw=(%.4f,d=%.2f,s=%d)"
                  % (r["m"], t, d, s, r["log2_total"], r["d"], r["s_tabulated"]))
    print(f"n=131 mitm_store_free rows reproduced (grid 0.25): {ok} ok, {bad} mismatched")

    print("\nPer-n minimum over m (C1+C2+C3) vs raw min_store_by_degree:")
    for n in [97, 109, 131, 163, 191, 233, 239, 283, 409, 571]:
        cands = [(min_store(n, m), m) for m in range(2, 17)]
        cands = [(c, m) for c, m in cands if c is not None]
        (st, d, s, t), m = min(cands, key=lambda x: (x[0][0], x[0][3]))
        rr = raw["min_store_by_degree"][str(n)]
        print(f"  n={n:3d} mine m={m:2d} store={st:7.2f} total={t:.4f} excess={st - B(n):.4f} | "
              f"raw m={rr['m_minimising_store']:2d} store={rr['min_log2_store_entries']:7.2f} "
              f"total={rr['at_that_cell_log2_total']:.4f} excess={rr['store_exceeds_baseline_work_by_bits']:.4f}")

    print("\nm = 3 at n = 131 under C1+C2 (s = 1), d = 10..60:",
          [round(total(131, 3, d, 1)[0], 4) for d in (10, 30, 60)])


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/home/user/crypto-autoresearcher")
