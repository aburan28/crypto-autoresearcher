#!/usr/bin/env python3
"""
J1 -- independent re-enumeration of exact basins at N=2^24, a=1/4, r=2,
to recompute the G3 ceiling-feasibility test (exact top-T_sel basin share
vs STATIC(T)_r exact coverage) at T_sel in {0.65T, 0.75T}, FROM SCRATCH,
using the SAME primitive functions already written for J2
(j2_blind_derivation.py), WITHOUT having opened
experiments/EXP-ECDLP-612fb1/source_v2/ before writing or running this
script (per the J1 attack plan's explicit instruction: "do not read the
executor's G3 implementation before doing this computation").

This reuses this task's own splitmix64 / basin-resolution / pool-sampling
code (already written independently for J2, itself derived only from
specification.v2.yaml's definitions), not the executor's instrument.py.

G3 rule under test (specification.v2.yaml `inputs.g3_gate_procedure`,
quoted): "G3 PASSES iff exact top-T_sel basin share >= STATIC(T)_r exact
coverage ... in at least 4 of the 5 seeds."

Only after this script is written and run is source_v2/ opened, to check
the UNTESTABLE branch's reachability (separate step, recorded in the
validation report).
"""
import importlib.util
import json
import sys
import time
import os

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "j2_blind_derivation", os.path.join(HERE, "j2_blind_derivation.py")
)
j2 = importlib.util.module_from_spec(spec)
sys.modules["j2_blind_derivation"] = j2
spec.loader.exec_module(j2)


def main():
    N = 2 ** 24
    T = 2 ** (24 // 3)  # 2^8 = 256
    assert T == 256, T
    a = 0.25
    r = 2
    W = (a * N / T) ** 0.5  # = 128.0 at a=1/4
    T_sel_grid_fracs = [0.65, 0.75]
    # my own independent seeds, distinct from both J2's and the executor's
    seeds = [777001, 888002]

    results = []
    t0 = time.time()
    for seed in seeds:
        basin_structure = j2.compute_basin_structure(N, W, a, seed)
        term, steps, sizes, sorted_sizes, n_miss = basin_structure
        for r_here in [r]:
            res = j2.rho_oracle_for_cell(N, T, W, a, r_here, seed, T_sel_grid_fracs, basin_structure)
            # G3 comparison at each T_sel grid point directly:
            g3_by_tsel = {}
            for frac in T_sel_grid_fracs:
                t_sel = max(1, round(frac * T))
                oracle_share = res["oracle_shares_by_T_sel"][t_sel]
                static_cov = res["static_coverage"]
                g3_by_tsel[frac] = {
                    "T_sel": t_sel,
                    "oracle_top_T_sel_share": oracle_share,
                    "STATIC_T_r_exact_coverage": static_cov,
                    "margin_oracle_minus_static": oracle_share - static_cov,
                    "G3_this_seed_pass": oracle_share >= static_cov,
                }
            results.append({
                "seed": seed,
                "n_miss_frac": n_miss / N,
                "n_distinct_basins": len(sorted_sizes),
                "static_coverage": res["static_coverage"],
                "g3_by_tsel": g3_by_tsel,
                "elapsed_s": time.time() - t0,
            })
            print(f"seed={seed} done at {time.time()-t0:.1f}s: "
                  f"static_cov={res['static_coverage']:.4f} "
                  + " ".join(f"T_sel_frac={frac}:margin={g3_by_tsel[frac]['margin_oracle_minus_static']:+.4f}"
                             for frac in T_sel_grid_fracs),
                  file=sys.stderr)

    # aggregate: G3 PASS requires >=4/5 seeds; we only ran 2 seeds (attack
    # plan requires "at least 2 of the tested cells", not a full 5-seed
    # replication) -- report per-seed outcome, do not force a 5-seed verdict
    summary = {"N": N, "T": T, "a": a, "r": r, "W": W,
               "T_sel_grid_fracs": T_sel_grid_fracs,
               "seeds_run": seeds,
               "per_seed_results": results}
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
