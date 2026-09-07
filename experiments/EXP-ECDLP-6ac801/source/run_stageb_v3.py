"""STAGE B'' (PRODUCTION) for EXP-ECDLP-6ac801, specification.v3.yaml.

Extends run_stageb.py (v1/v2's Stage B driver) to the full v3 grid:
  N in {2^20, 2^24}; a_grid = {1/16, 1/8, 3/16, 1/4}; r = 2;
  T_sel = T/2 (32 at N=2^20, 128 at N=2^24); seeds 1..25.
Zero online re-selected (RESEL-L) arms -- exact-enumeration measurement only,
exactly as v1/v2's own Stage B.

One invocation sweeps ONE (n_bits, seed) pair over the full a_grid, mirroring
v1's own per-seed run-directory convention (RUN-ECDLP-6ac801-001..006, one
seed per run, all four a values per run).

For each (N, a, seed) this script computes, per specification.v3.yaml
`definitions` and `stage_plan_v3` (STAGE B''):
  - exact top-T_sel, top-T, top-T/4, top-T/8 basin shares
  - STATIC(T)_{r=2} exact coverage, via the published Bernstein-Lange weight
    weight_d = S_d + 4*W*h_d (definitions item "STATIC(T)_r pool-selection
    weight formula"), ties broken by the SAME tiebreak-key stream v1/v2 use
    (np.random.default_rng(P.seed_tiebreak))
  - the G3-style margin at T_sel, T/4, T/8
  - cycle_mass, capped_mass, capped_walks, residual_fraction (definitions
    items 1-2, the WALK CAP and EXACT-BASIN RESIDUAL MASS ACCOUNTING)
  - rho_ORACLE (smallest T_sel/T at which the exact share equals STATIC(T)'s
    coverage), the tie count at the T-th largest weight, and the four
    control-arm raw quantities (i)/(j)/(k)/(n):
      (i)  NULL-ORACLE-RAND (uniform): a uniformly random T_sel-subset of
           the DPs of the WHOLE exact partition (not the pool), coverage
           read off the same basin-size array. margin_null_uniform =
           cov(random subset) - cov_static.
      (j)  NULL-ORACLE-RAND (size-biased): same substitution, subset drawn
           with probability proportional to basin size. Diagnostic only.
      (k)  NULL-RANDSEL: a uniformly random T-subset of the r*T
           precomputation pool (not the whole partition), coverage compared
           against cov_static. margin_null_pool = cov(random T-of-pool) -
           cov_static.
      (n)  NULL-SHUF: basin sizes permuted across the pool's own r*T DPs
           (holding the size multiset and the weight-based selection fixed),
           re-reading the STATIC(T) table's coverage under that shuffled
           size assignment. Diagnostic only, explicitly not a G3 null.
  - the three structural self-checks (o1) basin-mass accounting, (o2) exact-
    coverage nesting, (o3) margin nesting in T_sel -- reported as
    SATISFIED/VIOLATED per cell, per specification.v3.yaml
    `v3_r2_addendum.required_artifacts_r2` (a violation stops that cell as
    completed_invalid, never folded into any pass-count).

THIS SCRIPT DOES NOT: classify any cell PASS/FAIL, compute any per-a
pass-count or G3-style feasibility verdict, determine FIRED/NOT-FIRED for
any control, or compare against Stage A''. Per the executor handoff
(TASK-20260907-ca8b6c) that aggregation and comparison is Stage C'', a
separate later Coordinator step. This script reports raw computed fields
only, per (N, a, seed), exactly as Stage A'' is required to.

INSTRUMENT REUSE (permitted for Stage B'' production, per specification.v3.yaml
`instrument`/`instrument_v3_note` and the executor handoff's own
`instrument_reuse_note` -- the blind-derivation restriction binds Stage A''
only, never this task): this script imports, by explicit commit-pinned path
reference, experiments/EXP-ECDLP-612fb1/source_v2/instrument.py, commit
22e80f13361a6eb307864c52f51740db419e9e54 (recorded again in each run's
manifest.yaml). Nothing in this file re-derives or re-words the exact-basin
enumeration, the DP predicate, the cap, the residual accounting, the pool
generation procedure, or the weight formula: it is the SAME code path as
v1/v2's Stage B, invoked with the v3 (N, a_grid, r, T_sel, seed) grid plus
the additive control-arm computations named above.

Certificate kind: none (no discrete-log solve or relation is claimed; this is
a pure exact-enumeration measurement, per specification.v3.yaml `instrument`).
"""
from __future__ import annotations

import argparse
import json
import os
import resource
import sys
import time

import numpy as np

# Explicit, commit-pinned reference (NOT a copy): see module docstring above.
V2_SOURCE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "EXP-ECDLP-612fb1", "source_v2",
)
sys.path.insert(0, os.path.abspath(V2_SOURCE_DIR))
import instrument as I  # noqa: E402  (v2 source_v2/instrument.py, commit-pinned in manifest)

A_GRID = [1 / 16, 1 / 8, 3 / 16, 1 / 4]   # specification.v3.yaml `a`
R_FIXED = 2                                # specification.v3.yaml `r`, fixed
EPS = 1e-9                                 # tolerance for float nesting self-checks


def a_label(a: float) -> str:
    return f"a={a:.6f}"


def null_seed(base_seed: int, n_bits: int, a: float, tag: int) -> int:
    """Deterministic, disjoint RNG seed per (base seed, N, a, control-arm tag).

    Derived, never reused from any walk/DP/tiebreak stream, so a control
    arm's randomness is independent of the instrument's own seed streams.
    tag: 1=NULL-ORACLE-RAND uniform, 2=size-biased, 3=NULL-RANDSEL, 4=NULL-SHUF.
    """
    return (
        900_000_000
        + tag * 10_000_000
        + n_bits * 100_000
        + int(round(10000 * a)) * 100
        + base_seed
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-bits", type=int, required=True, choices=[20, 24])
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    t0 = time.time()
    n_bits = args.n_bits
    T = I.T_OF_NBITS[n_bits]
    T_sel = T // 2      # ORIGINAL clause (C1) value, T/2
    T4 = T // 4
    T8 = T // 8

    summary = {
        "params": {
            "n_bits": n_bits, "N": 1 << n_bits, "T": T, "T_sel": T_sel,
            "T4": T4, "T8": T8, "r": R_FIXED, "seed": args.seed,
            "a_grid": A_GRID, "kind": "stageBpp_exact_ceiling_v3",
            "seeds": {"walk_key_seed": args.seed},
        },
        "certificate": {"kind": "none", "note": "Stage B'': exact-basin closed form, zero re-selected arms"},
        "cells": {},
    }
    raw = {"params": summary["params"], "certificate": {"kind": "none"}, "cells": {}}
    any_invalid = False

    for a in A_GRID:
        P = I.Params(n_bits=n_bits, a=a, seed=args.seed)
        tb = time.time()
        N = P.N
        basins = I.exact_basins(P)
        cycle_mass = basins.cycle_mass
        capped_mass = basins.capped_mass
        residual_fraction = (cycle_mass + capped_mass) / N

        # -- structural self-check (o1): basin-mass accounting --------------
        basin_mass_sum = int(basins.size.sum())
        accounting_total = basin_mass_sum + cycle_mass + capped_mass
        min_basin_size = int(basins.size.min()) if basins.size.size else None
        o1_ok = (accounting_total == N) and (min_basin_size is not None and min_basin_size >= 1)

        top_T_sel_share = basins.top_share(T_sel)
        top_T_share = basins.top_share(T)
        top_T4_share = basins.top_share(T4)
        top_T8_share = basins.top_share(T8)

        # -- control (c) / self-check (o2) inputs ----------------------------
        exceedance = (top_T_sel_share > 1.0 + 1e-12) or (top_T_sel_share > top_T_share + 1e-9)

        pools = I.generate_pools(P, [R_FIXED])
        snap = pools[R_FIXED * T]
        capped_walks = snap.capped_walks
        pool_S = np.asarray(snap.S, dtype=np.float64)
        pool_h = np.asarray(snap.h, dtype=np.int64)
        w = pool_S + 4.0 * P.W * pool_h.astype(np.float64)
        keys = np.random.default_rng(P.seed_tiebreak).integers(
            0, 1 << 63, size=len(snap.dps), dtype=np.int64
        )
        order = I.numpy_select(w, keys, T)   # top-T pool indices, by weight desc / key tiebreak
        pool_dps_arr = np.asarray(snap.dps, dtype=np.int64)
        static_T_r = pool_dps_arr[order]
        static_T_r2_exact_coverage = basins.coverage(static_T_r)

        margin = top_T_sel_share - static_T_r2_exact_coverage
        margin_T4 = top_T4_share - static_T_r2_exact_coverage
        margin_T8 = top_T8_share - static_T_r2_exact_coverage

        # -- self-check (o2): exact-coverage nesting -------------------------
        o2_ok = (
            top_T8_share <= top_T4_share + EPS
            and top_T4_share <= top_T_sel_share + EPS
            and top_T_sel_share <= top_T_share + EPS
            and top_T_share <= 1.0 + EPS
            and static_T_r2_exact_coverage <= top_T_share + EPS
        )
        # -- self-check (o3): margin nesting in T_sel -------------------------
        o3_ok = (margin > margin_T4 - EPS) and (margin_T4 > margin_T8 - EPS) and (margin > margin_T8 - EPS)

        # -- tie count at the T-th largest weight (D4 tail check input) ------
        w_sorted_desc = np.sort(w)[::-1]
        t_th_weight = w_sorted_desc[T - 1] if len(w_sorted_desc) >= T else None
        tie_count_at_T = int(np.sum(w == t_th_weight)) if t_th_weight is not None else None

        # -- rho_ORACLE: smallest T_sel'/T with share_top(T_sel') >= cov_static
        sizes_sorted_desc = np.sort(basins.size)[::-1]
        cumsum = np.cumsum(sizes_sorted_desc)
        thresh = static_T_r2_exact_coverage * N
        idx = int(np.searchsorted(cumsum, thresh, side="left"))
        t_oracle = min(idx + 1, len(sizes_sorted_desc)) if len(sizes_sorted_desc) else None
        rho_oracle = (t_oracle / T) if t_oracle is not None else None

        # -- control (i): NULL-ORACLE-RAND (uniform), gating null ------------
        all_dps = basins.dps
        rng_i = np.random.default_rng(null_seed(args.seed, n_bits, a, 1))
        idx_unif = rng_i.choice(len(all_dps), size=T_sel, replace=False)
        cov_null_uniform = basins.coverage(all_dps[idx_unif])
        margin_null_uniform = cov_null_uniform - static_T_r2_exact_coverage

        # -- control (j): NULL-ORACLE-RAND (size-biased), diagnostic ---------
        rng_j = np.random.default_rng(null_seed(args.seed, n_bits, a, 2))
        probs = basins.size.astype(np.float64)
        probs = probs / probs.sum()
        idx_biased = rng_j.choice(len(all_dps), size=T_sel, replace=False, p=probs)
        cov_null_biased = basins.coverage(all_dps[idx_biased])
        margin_null_biased = cov_null_biased - static_T_r2_exact_coverage

        # -- control (k): NULL-RANDSEL, uniform random T-subset of the pool --
        rng_k = np.random.default_rng(null_seed(args.seed, n_bits, a, 3))
        idx_pool = rng_k.choice(len(pool_dps_arr), size=T, replace=False)
        cov_null_pool = basins.coverage(pool_dps_arr[idx_pool])
        margin_null_pool = cov_null_pool - static_T_r2_exact_coverage

        # -- control (n): NULL-SHUF, diagnostic, not a G3 null ----------------
        pool_idx_in_basins = basins.index_of(pool_dps_arr)
        pool_sizes = basins.size[pool_idx_in_basins]
        rng_n = np.random.default_rng(null_seed(args.seed, n_bits, a, 4))
        shuffled_pool_sizes = rng_n.permutation(pool_sizes)
        cov_static_shuf = float(shuffled_pool_sizes[order].sum()) / N
        margin_null_shuf = top_T_sel_share - cov_static_shuf

        cell_invalid = exceedance or not (o1_ok and o2_ok and o3_ok)
        any_invalid = any_invalid or cell_invalid

        cell = {
            "a": a, "N": N, "T": T, "T_sel": T_sel, "T4": T4, "T8": T8,
            "r": R_FIXED, "seed": args.seed, "n_bits": n_bits,
            "W": P.W, "cap": P.cap,
            "exact_top_T_sel_share": top_T_sel_share,
            "exact_top_T_share": top_T_share,
            "exact_top_T4_share": top_T4_share,
            "exact_top_T8_share": top_T8_share,
            "static_T_r2_exact_coverage": static_T_r2_exact_coverage,
            "margin": margin,
            "margin_T4": margin_T4,
            "margin_T8": margin_T8,
            "margin_geq_0": bool(margin >= 0.0),
            "rho_oracle": rho_oracle,
            "cycle_mass": cycle_mass,
            "capped_mass": capped_mass,
            "capped_walks": capped_walks,
            "residual_fraction": residual_fraction,
            "basin_mass_accounting_sum": accounting_total,
            "min_basin_size": min_basin_size,
            "tie_count_at_T_th_weight": tie_count_at_T,
            "exceedance": bool(exceedance),
            "self_check_o1_basin_mass_accounting": "SATISFIED" if o1_ok else "VIOLATED",
            "self_check_o2_exact_coverage_nesting": "SATISFIED" if o2_ok else "VIOLATED",
            "self_check_o3_margin_nesting": "SATISFIED" if o3_ok else "VIOLATED",
            "control_i_null_oracle_rand_uniform_margin": margin_null_uniform,
            "control_j_null_oracle_rand_sizebiased_margin_diagnostic": margin_null_biased,
            "control_k_null_randsel_pool_margin": margin_null_pool,
            "control_n_null_shuf_cov_static_shuf_diagnostic": cov_static_shuf,
            "control_n_null_shuf_margin_diagnostic": margin_null_shuf,
            "cell_status": "completed_invalid" if cell_invalid else "completed_valid",
            "seconds": time.time() - tb,
        }
        summary["cells"][a_label(a)] = cell
        raw["cells"][a_label(a)] = {
            "basin_sizes": basins.size.tolist(),
            "basin_dps": basins.dps.tolist(),
            "static_T_r2_dps": static_T_r.tolist(),
            "pool_dps": pool_dps_arr.tolist(),
            "pool_S": pool_S.tolist(),
            "pool_h": pool_h.tolist(),
            "pool_weights": w.tolist(),
            "null_uniform_dps": all_dps[idx_unif].tolist(),
            "null_sizebiased_dps": all_dps[idx_biased].tolist(),
            "null_randsel_pool_dps": pool_dps_arr[idx_pool].tolist(),
            "N": N, "T": T, "T_sel": T_sel, "T4": T4, "T8": T8, "r": R_FIXED,
        }
        print(
            f"[stageB''] n_bits={n_bits} seed={args.seed} a={a:.6f} "
            f"top_T_sel_share={top_T_sel_share:.6f} "
            f"static_T_r2_cov={static_T_r2_exact_coverage:.6f} "
            f"margin={margin:+.6f} cycle_mass={cycle_mass} capped_mass={capped_mass} "
            f"capped_walks={capped_walks} residual_fraction={residual_fraction:.3e} "
            f"o1={cell['self_check_o1_basin_mass_accounting']} "
            f"o2={cell['self_check_o2_exact_coverage_nesting']} "
            f"o3={cell['self_check_o3_margin_nesting']} "
            f"exceedance={exceedance} status={cell['cell_status']} ({cell['seconds']:.2f}s)",
            flush=True,
        )

    summary["elapsed_seconds"] = time.time() - t0
    peak_rss_bytes = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
    summary["peak_rss_bytes"] = peak_rss_bytes
    summary["any_cell_invalid"] = any_invalid
    with open(os.path.join(args.outdir, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    with open(os.path.join(args.outdir, "raw-result.json"), "w") as fh:
        json.dump(raw, fh)
    print(
        f"[done] n_bits={n_bits} seed={args.seed} {time.time() - t0:.1f}s "
        f"peak_rss={peak_rss_bytes} any_cell_invalid={any_invalid}",
        flush=True,
    )
    return 1 if any_invalid else 0


if __name__ == "__main__":
    sys.exit(main())
