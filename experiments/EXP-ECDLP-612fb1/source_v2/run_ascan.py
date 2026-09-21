"""STAGE 0 (NEW, item h): the a-scan, run FIRST, before any other v2 stage
is interpreted.

Generic instrument, N = 2^20 only, exact basins.  a_scan_grid = {1/16, 1/8,
3/16, 1/4, 5/16, 3/8, 7/16, 1/2, 5/8, 3/4, 7/8, 1} (12 points), r in
{2, 4, 8}, ONE seed per run (5 runs total cover the 5-seed replication).

Zero re-selected arms are run: for every (a, r) this is a closed-form-from-
exact-basins computation -- generate the r*T-entry precomputation pool,
select its top-T entries by the published weight (STATIC(T)_r), and read
its exact coverage off the SAME exact-basin table used for the exact
top-T_sel share at every T_sel in {T/4, T/2, 3T/4, T, 0.65T, 0.75T}.

Deliverable: rho_ORACLE(a, r, T_sel) at every grid point (log-linear
interpolation of the oracle top-share curve to the level of STATIC(T)_r's
own exact coverage, the SAME interpolation rule as T_resel(U)/rho_T(U)),
and the ordering check rho_ORACLE(a=1/4, r) vs rho_ORACLE(a=1/2, r).

Observations only.  Certificate kind: none.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import instrument as I  # noqa: E402

A_SCAN_GRID = [1 / 16, 1 / 8, 3 / 16, 1 / 4, 5 / 16, 3 / 8, 7 / 16, 1 / 2, 5 / 8, 3 / 4, 7 / 8, 1]
R_GRID = [2, 4, 8]
T_SEL_LABELS = ["T/4", "T/2", "3T/4", "T", "0.65T", "0.75T"]


def t_sel_of(lab: str, T: int) -> int:
    return {"T/4": T // 4, "T/2": T // 2, "3T/4": 3 * T // 4, "T": T,
            "0.65T": int(round(0.65 * T)), "0.75T": int(round(0.75 * T))}[lab]


def rho_oracle_interp(share_by_tsel: dict, target: float, T: int):
    """T_sel/T at which the oracle top-share curve equals `target`
    (log-linear interpolation on the T_sel grid, the SAME rule as
    rho_from_eps in analysis.py; the oracle share curve is monotone
    increasing in t_sel, unlike an arm's eps_ss, so no non-monotone-grid
    branch is needed here)."""
    order = ["T/4", "T/2", "3T/4", "T"]
    xs = np.log2(np.array([t_sel_of(l, T) for l in order]) / T)
    ys = np.array([share_by_tsel[l] for l in order])
    if ys[0] >= target:
        return 0.25, "<=T/4"
    for i in range(3):
        if ys[i] < target <= ys[i + 1]:
            x = xs[i] + (target - ys[i]) / (ys[i + 1] - ys[i]) * (xs[i + 1] - xs[i])
            return float(2 ** x), None
    if ys[-1] < target:
        x = xs[-2] + (target - ys[-2]) / (ys[-1] - ys[-2]) * (xs[-1] - xs[-2])
        return float(2 ** x), ">T (extrapolated)"
    return 1.0, None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()
    t0 = time.time()
    n_bits = 20
    T = I.T_OF_NBITS[n_bits]

    summary = {"params": {"n_bits": n_bits, "T": T, "seed": args.seed, "kind": "ascan",
                          "a_scan_grid": A_SCAN_GRID, "r_grid": R_GRID,
                          "seeds": {"walk_key_seed": args.seed}},
               "certificate": {"kind": "none", "note": "STAGE 0 a-scan: exact-basin closed form, zero re-selected arms"},
               "cells": {}}
    raw = {"params": summary["params"], "certificate": {"kind": "none"}, "cells": {}}

    for a in A_SCAN_GRID:
        P = I.Params(n_bits=n_bits, a=a, seed=args.seed)
        tb = time.time()
        basins = I.exact_basins(P)
        top_share = {lab: basins.top_share(t_sel_of(lab, T)) for lab in T_SEL_LABELS}
        cell = {"a": a, "W": P.W, "cap": P.cap, "top_share": top_share, "static_by_r": {}}
        for r in R_GRID:
            pools = I.generate_pools(P, [r])
            snap = pools[r * T]
            w = np.asarray(snap.S) + 4.0 * P.W * np.asarray(snap.h)
            keys = np.random.default_rng(P.seed_tiebreak).integers(0, 1 << 63, size=len(snap.dps), dtype=np.int64)
            order = I.numpy_select(w, keys, T)
            static_T_r = np.asarray([snap.dps[i] for i in order], dtype=np.int64)
            static_cov = basins.coverage(static_T_r)
            rho_oracle_val, censor = rho_oracle_interp(top_share, static_cov, T)
            cell["static_by_r"][str(r)] = {
                "static_T_r_exact_coverage": static_cov,
                "rho_ORACLE(a,r)": rho_oracle_val,
                "rho_ORACLE_censor": censor,
                "P_group_ops": snap.P_cost,
                "P_over_sqrt_NT": snap.P_cost / math.sqrt(P.N * T),
            }
        cell["seconds"] = time.time() - tb
        summary["cells"][f"a={a:.6f}"] = cell
        raw["cells"][f"a={a:.6f}"] = {"top_share": top_share,
                                      "static_by_r": {k: v["static_T_r_exact_coverage"] for k, v in cell["static_by_r"].items()}}
        print(f"[ascan] a={a:.4f} top_T_share={top_share['T']:.4f} "
              + " ".join(f"rho_ORACLE(r={r})={cell['static_by_r'][str(r)]['rho_ORACLE(a,r)']:.4f}" for r in R_GRID)
              + f" ({cell['seconds']:.2f}s)", flush=True)

    # ordering check: rho_ORACLE(a=1/4, r) vs rho_ORACLE(a=1/2, r), every r (F6_v2)
    ordering = {}
    for r in R_GRID:
        v_14 = summary["cells"]["a=0.250000"]["static_by_r"][str(r)]["rho_ORACLE(a,r)"]
        v_12 = summary["cells"]["a=0.500000"]["static_by_r"][str(r)]["rho_ORACLE(a,r)"]
        ordering[str(r)] = {"rho_ORACLE(a=1/4)": v_14, "rho_ORACLE(a=1/2)": v_12,
                            "ordering_holds_(1/4_lt_1/2)": bool(v_14 < v_12)}
    summary["ordering_check_F6_v2"] = ordering
    summary["elapsed_seconds"] = time.time() - t0
    print(f"[ordering_check] {json.dumps(ordering)}", flush=True)

    with open(os.path.join(args.outdir, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    with open(os.path.join(args.outdir, "raw-result.json"), "w") as fh:
        json.dump(raw, fh)
    print(f"[done] {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
