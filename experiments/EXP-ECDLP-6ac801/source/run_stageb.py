"""STAGE B (EXECUTION) for EXP-ECDLP-6ac801.

Narrow, cheap, exact-basin-only measurement, one scale up from
EXP-ECDLP-612fb1/specification.v2.yaml's Stage 0 a-scan (N = 2^20 -> N = 2^24
here). For ONE seed, sweeps a_grid = {1/16, 1/8, 3/16, 1/4} at r = 2,
T_sel = T/2 = 128 fixed (the ORIGINAL clause (C1) value), and computes, per a:

  - exact top-T_sel (= T/2) basin share (I.Basins.top_share(T_sel))
  - STATIC(T)_{r=2} exact coverage (select top-T entries from an r*T = 512
    entry precomputation pool by the published Bernstein-Lange weight
    S_d + 4 W h_d, then read that table's exact coverage off the same
    basin partition)

Zero re-selected (RESEL-L) arms are run; this mirrors v1/v2's own Stage 0.

INSTRUMENT REUSE (per specification.yaml `instrument` and the executor
handoff's `constraints`): this script imports, by explicit, commit-pinned
path reference, the exact-basin / instrument code of
experiments/EXP-ECDLP-612fb1/source_v2/instrument.py, commit
22e80f13361a6eb307864c52f51740db419e9e54 (recorded again in each run's
manifest.yaml). Nothing in this file re-derives or re-words the exact-basin
enumeration, the DP predicate, the pool-generation procedure, or the
top-T_sel/STATIC(T) definitions: it is the SAME code path as v1/v2's own
Stage 0, invoked with this contract's own (N, a_grid, r, T_sel, seed) grid.

Certificate kind: none (no discrete-log solve or relation is claimed; this is
a pure exact-enumeration measurement, per specification.yaml `instrument`).
"""
from __future__ import annotations

import argparse
import json
import os
import resource
import sys
import time

import numpy as np

# Explicit, commit-pinned reference (NOT a copy): the v2 experiment's own
# instrument module is imported directly from its own path. The commit
# pinning this exact file's contents is recorded in this run's manifest.yaml
# (git log -1 --format=%H -- experiments/EXP-ECDLP-612fb1/source_v2/instrument.py).
V2_SOURCE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "EXP-ECDLP-612fb1", "source_v2",
)
sys.path.insert(0, os.path.abspath(V2_SOURCE_DIR))
import instrument as I  # noqa: E402  (v2 source_v2/instrument.py, commit-pinned in manifest)

A_GRID = [1 / 16, 1 / 8, 3 / 16, 1 / 4]   # specification.yaml `a`
R_FIXED = 2                                # specification.yaml `r`, fixed
N_BITS = 24                                # specification.yaml N = 2^24


def a_label(a: float) -> str:
    return f"a={a:.6f}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    t0 = time.time()
    T = I.T_OF_NBITS[N_BITS]          # 256 at N = 2^24
    T_sel = T // 2                    # 128, the ORIGINAL clause (C1) value

    summary = {
        "params": {
            "n_bits": N_BITS, "N": 1 << N_BITS, "T": T, "T_sel": T_sel,
            "r": R_FIXED, "seed": args.seed, "a_grid": A_GRID,
            "kind": "stageB_exact_ceiling",
            "seeds": {"walk_key_seed": args.seed},
        },
        "certificate": {"kind": "none", "note": "Stage B: exact-basin closed form, zero re-selected arms"},
        "cells": {},
    }
    raw = {"params": summary["params"], "certificate": {"kind": "none"}, "cells": {}}

    for a in A_GRID:
        P = I.Params(n_bits=N_BITS, a=a, seed=args.seed)
        tb = time.time()
        basins = I.exact_basins(P)

        top_T_sel_share = basins.top_share(T_sel)
        top_T_share = basins.top_share(T)   # for the non-exceedance control only

        pools = I.generate_pools(P, [R_FIXED])
        snap = pools[R_FIXED * T]
        w = np.asarray(snap.S) + 4.0 * P.W * np.asarray(snap.h)
        keys = np.random.default_rng(P.seed_tiebreak).integers(
            0, 1 << 63, size=len(snap.dps), dtype=np.int64
        )
        order = I.numpy_select(w, keys, T)
        static_T_r = np.asarray([snap.dps[i] for i in order], dtype=np.int64)
        static_T_r2_exact_coverage = basins.coverage(static_T_r)

        margin = top_T_sel_share - static_T_r2_exact_coverage

        # control (c): EXACT-COVERAGE NON-EXCEEDANCE
        exceedance = (top_T_sel_share > 1.0 + 1e-12) or (top_T_sel_share > top_T_share + 1e-9)

        cell = {
            "a": a, "W": P.W, "cap": P.cap,
            "exact_top_T_sel_share": top_T_sel_share,
            "exact_top_T_share": top_T_share,
            "static_T_r2_exact_coverage": static_T_r2_exact_coverage,
            "margin": margin,
            "pass": bool(margin >= 0.0),
            "exceedance": bool(exceedance),
            "seconds": time.time() - tb,
        }
        summary["cells"][a_label(a)] = cell
        raw["cells"][a_label(a)] = {
            "basin_sizes": basins.size.tolist(),
            "basin_dps": basins.dps.tolist(),
            "static_T_r2_dps": static_T_r.tolist(),
            "exact_top_T_sel_share": top_T_sel_share,
            "exact_top_T_share": top_T_share,
            "static_T_r2_exact_coverage": static_T_r2_exact_coverage,
            "N": P.N, "T": T, "T_sel": T_sel, "r": R_FIXED,
        }
        print(
            f"[stageB] seed={args.seed} a={a:.6f} "
            f"top_T_sel_share={top_T_sel_share:.6f} "
            f"static_T_r2_cov={static_T_r2_exact_coverage:.6f} "
            f"margin={margin:+.6f} pass={cell['pass']} "
            f"exceedance={exceedance} ({cell['seconds']:.2f}s)",
            flush=True,
        )
        if exceedance:
            # Stopping rule: an exceedance stops THIS RUN as completed_invalid
            # immediately, never folded into a pass-count.
            summary["completed_invalid"] = True
            summary["completed_invalid_reason"] = (
                f"exact top-T_sel share exceeded 1.0 or the exact top-T share at a={a}"
            )
            with open(os.path.join(args.outdir, "summary.json"), "w") as fh:
                json.dump(summary, fh, indent=1)
            with open(os.path.join(args.outdir, "raw-result.json"), "w") as fh:
                json.dump(raw, fh)
            print("[stageB] COMPLETED_INVALID: exceedance control fired", flush=True)
            return 1

    summary["elapsed_seconds"] = time.time() - t0
    peak_rss_bytes = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
    summary["peak_rss_bytes"] = peak_rss_bytes
    with open(os.path.join(args.outdir, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    with open(os.path.join(args.outdir, "raw-result.json"), "w") as fh:
        json.dump(raw, fh)
    print(f"[done] seed={args.seed} {time.time() - t0:.1f}s peak_rss={peak_rss_bytes}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
