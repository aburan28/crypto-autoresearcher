"""EXP-DREG-001 §10 — degree-resolved deficit.

The instrument (h012c_block_m4ri.py) reports one cumulative number at D=5. That
cross-section mixes regularity regimes across n. This probe resolves the deficit
degree by degree: exact GF(2) rank of the degree-<=D Macaulay matrix vs the
semi-regular prediction pred[D], for D = 2..Dmax.

Produces the §10 table and checks the closed forms
    graded deficit at D=3 = 1        (full systems, n >= 12)
    graded deficit at D=4 = 8k - 1   (k = dim V = (n+2)//3)
equivalently cumulative deficit at D=4 = 8k.

Run:
  DOT_SAGE=experiments/EXP-DREG-001/runtime/sage TMPDIR=/Volumes/Volume/tmp \
  sage -python experiments/EXP-DREG-001/characterization/deficit_by_degree.py \
       --n-list 9,12,15,17,18,21 --dmax 4
"""
import argparse
import sys
import time
from math import comb
from pathlib import Path

# Authoritative construction = the per-run archived code snapshot (the workspace
# src/ was relocated 2026-07-20; run snapshots are pinned by manifest sha256).
CODE = (Path(__file__).resolve().parent.parent
        / "runs" / "RUN-DREG-001-VALIDATE-N12-A" / "code")
sys.path.insert(0, str(CODE))

from h012_peel_rank import build_system, semireg_rank_pred, peel_and_rank  # noqa: E402
from macaulay_export import macaulay_rows  # noqa: E402


def profile(n, t, ti, seed, dmax):
    k = (n + t - 1) // t
    built = build_system(n, t, ti, seed)
    if built is None:
        print(f"n={n}: build_system failed")
        return
    _rng, nb, monosets, eq_degs = built
    pred, _HF = semireg_rank_pred(eq_degs, nb, dmax + 1)
    nq = eq_degs.count(2)
    nc = eq_degs.count(3)
    # "Full" = the regular shape: exactly n quadrics + n cubics in nb = 2n variables.
    # n=9 has only 8 quadrics and n=17 has nb = 2n+1 with 34 equations; both are
    # deficient and are the two cells that break the low-degree closed forms (§10).
    full = (nq == n and nc == n and nb == 2 * n and len(monosets) == 2 * n)
    print(f"\nn={n} k={k} nb={nb} eqs={len(monosets)} ({nq} quadric, {nc} cubic)"
          f"  {'FULL' if full else 'DEFICIENT (nb != 2n or m != 2n)'}")
    print(f"  {'D':>2} {'rows':>8} {'cols':>8} {'rank':>9} {'pred[D]':>9}"
          f" {'def_cum':>8} {'def_graded':>10}")
    defcum_prev = 0
    for D in range(2, dmax + 1):
        t0 = time.time()
        rows, colidx, _ = macaulay_rows(monosets, nb, D)
        rank = peel_and_rank(rows, colidx)["rank"]
        defcum = pred[D] - rank
        defgr = defcum - defcum_prev
        note = ""
        if D == 3 and full:
            note = "  [expect 1]" + ("" if defgr == 1 else "  <-- MISMATCH")
        if D == 4 and full:
            note = (f"  [expect 8k-1={8 * k - 1}]"
                    + ("" if defgr == 8 * k - 1 else "  <-- MISMATCH"))
        print(f"  {D:>2} {len(rows):>8} {len(colidx):>8} {rank:>9} {pred[D]:>9}"
              f" {defcum:>8} {defgr:>10}  ({time.time() - t0:.0f}s){note}")
        defcum_prev = defcum
    if dmax >= 4 and full:
        print(f"  => cumulative deficit at D=4 = {defcum_prev}"
              f"  (8k = {8 * k})"
              f"  {'OK' if defcum_prev == 8 * k else '<-- MISMATCH'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-list", default="12,15,18")
    ap.add_argument("--t", type=int, default=3)
    ap.add_argument("--ti", type=int, default=0)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--dmax", type=int, default=4,
                    help="4 is cheap at every n; 5 is expensive past n=12")
    args = ap.parse_args()
    for n in [int(x) for x in args.n_list.split(",")]:
        profile(n, args.t, args.ti, args.seed, args.dmax)


if __name__ == "__main__":
    main()
