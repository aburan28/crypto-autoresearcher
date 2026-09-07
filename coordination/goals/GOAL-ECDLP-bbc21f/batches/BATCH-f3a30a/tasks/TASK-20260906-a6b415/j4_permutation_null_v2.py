"""
J4 Part 2 (Red Team, TASK-20260906-a6b415): fresh permutation-null check of
the V2-CORRECTED pipeline specifically (HEUR-BLT-7 v2 / admitted-walk count,
frontier tuple gain), using the real source_v2/instrument.py production code
(Pool, CountedSelector, run_arm, exact_basins, generate_pools) with the walk
function replaced by a KEYED BIJECTION (numpy permutation of [0, N)) instead
of the producer's keyed random function -- exactly the construction the red
team used for the permanent negative fixture in BATCH-289698
(src/pipeline_perm/instrument.py.diff), reproduced here against v2's own
code and v2's own T_sel_grid_v2 = {0.65T, 0.75T}, which the BATCH-289698
fixture (built before v2 existed) does not exercise.

Nothing here modifies experiments/EXP-ECDLP-612fb1/source_v2/ on disk; the
walk override is a per-instance monkeypatch applied only inside this script.
"""
import sys
import types
import numpy as np

SRC = "/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-612fb1/source_v2"
sys.path.insert(0, SRC)
import instrument as I  # noqa: E402


def make_permutation_params(n_bits, a, seed):
    P = I.Params(n_bits=n_bits, a=a, seed=seed)
    rng = np.random.default_rng(P.K)   # keyed by the same walk-key K as the real walk
    perm = rng.permutation(P.N).astype(np.uint64)
    assert len(np.unique(perm)) == P.N, "not a bijection"

    def step_override(self, x):
        return perm[x.astype(np.int64)]

    P.step = types.MethodType(step_override, P)
    return P


def run_seed(seed, n_bits=20, a=0.25, r=2):
    P = make_permutation_params(n_bits, a, seed)
    T = P.T
    basins = I.exact_basins(P)
    top_T_share = basins.top_share(T)
    largest = int(basins.size.max())

    pools = I.generate_pools(P, [r])
    rng_t = np.random.default_rng(P.seed_targets)
    starts = rng_t.integers(0, P.N, size=(P.U_max, P.k), dtype=np.int64)
    term, length = I.walk_to_dp(P, starts.reshape(-1))
    term = term.reshape(P.U_max, P.k)
    length = length.reshape(P.U_max, P.k)

    grid = {"0.65T": int(round(0.65 * T)), "0.75T": int(round(0.75 * T)), "T": T}
    results = {}
    for name, mode, ts, cap in [
        ("STATIC(T)", "static", grid["T"], None),
        ("STATIC(0.65T)", "static", grid["0.65T"], None),
        ("STATIC(0.75T)", "static", grid["0.75T"], None),
        ("RESEL-L(0.65T)", "resel_lower", grid["0.65T"], None),
        ("RESEL-L(0.75T)", "resel_lower", grid["0.75T"], None),
        ("CAP(2T,0.65T)", "resel_lower", grid["0.65T"], 2 * T),
        ("RHO", "rho", 0, None),
    ]:
        cfg = I.ArmConfig(name=name, mode=mode, t_sel=ts, r=r, pool_cap=cap)
        snapshot_U = [T, 2 * T, 4 * T, 8 * T]
        res = I.run_arm(P, cfg, pools, term, length, basins, oracle_share=None, snapshot_U=snapshot_U)
        results[name] = res

    U_grid = {"4T": 4 * T, "8T": 8 * T, "16T": 16 * T}

    def eps_ss(res, U):
        R = T
        return float(res.solved[max(0, U - 2 * R):U].mean())

    out = {"seed": seed, "top_T_share": top_T_share, "largest_basin": largest, "cap_at_8W": P.cap}
    for lab in ("0.65T", "0.75T"):
        rname = f"RESEL-L({lab})"
        sname = "STATIC(T)"
        gain8T = eps_ss(results[rname], 8 * T) - eps_ss(results[sname], 8 * T)
        gain16T = eps_ss(results[rname], 16 * T) - eps_ss(results[sname], 16 * T)
        out[f"gain_{lab}_8T"] = gain8T
        out[f"gain_{lab}_16T"] = gain16T
        cap_res = results[f"CAP(2T,{lab})"] if lab == "0.65T" else None
        if cap_res is not None:
            out[f"CAP_2T_{lab}_S_peak_bits"] = cap_res.S_peak_bits
            out[f"CAP_2T_{lab}_S_peak_le_2T_bits"] = cap_res.S_peak_bits <= 2 * T * P.bits_pool_entry

    # v2-corrected HEUR-BLT-7 r_eff at U=8T for RESEL-L(0.65T): r_eff = r + admitted_walk_count/T
    res65 = results["RESEL-L(0.65T)"]
    round_idx = (8 * T) // T - 1
    admitted = res65.rounds[round_idx]["admitted_walks_cumulative"]
    r_eff_v2 = r + admitted / T
    out["HEUR_BLT7_v2_r_eff_at_8T"] = r_eff_v2
    out["admitted_walk_count_at_8T"] = admitted

    # exact coverage of the re-selected table vs its STATIC(T) twin (does re-selection
    # find a genuinely better-than-static table on this null?)
    table65 = res65.table_at_round[-1]
    tableStatic = results["STATIC(T)"].table_at_round[-1]
    out["exact_coverage_RESEL-L(0.65T)_final"] = basins.coverage(table65)
    out["exact_coverage_STATIC(T)_final"] = basins.coverage(tableStatic)
    return out


def main():
    print(f"{'seed':>4} {'top_T_share':>12} {'largest_bas':>12} {'gain_0.65T_8T':>14} {'gain_0.75T_8T':>14} "
          f"{'gain_0.65T_16T':>15} {'r_eff_v2':>10} {'admitted':>9} {'cap_S_peak<=2T*bpp':>18}")
    gains = []
    for seed in (1, 2, 3):
        r = run_seed(seed)
        gains.append(r["gain_0.65T_8T"])
        gains.append(r["gain_0.75T_8T"])
        print(f"{r['seed']:>4} {r['top_T_share']:>12.5f} {r['largest_basin']:>12d} "
              f"{r['gain_0.65T_8T']:>14.5f} {r['gain_0.75T_8T']:>14.5f} {r['gain_0.65T_16T']:>15.5f} "
              f"{r['HEUR_BLT7_v2_r_eff_at_8T']:>10.3f} {r['admitted_walk_count_at_8T']:>9d} "
              f"{str(r['CAP_2T_0.65T_S_peak_le_2T_bits']):>18}")
        print(f"      exact_coverage RESEL-L(0.65T)={r['exact_coverage_RESEL-L(0.65T)_final']:.5f} "
              f"vs STATIC(T)={r['exact_coverage_STATIC(T)_final']:.5f}")
    import numpy as np
    print(f"\nmean gain across seeds x T_sel: {np.mean(gains):.5f}  (expect ~0, no positive re-selection "
          f"advantage on a bijection null with no tree/convergence structure)")
    print("all gains:", [round(g, 5) for g in gains])
    any_meaningfully_positive = any(g > 0.03 for g in gains)  # compare to the real object's measured gain ~0.06-0.08
    print(f"any gain > 0.03 (well below the real object's measured 0.06-0.08 RESEL-L gain): {any_meaningfully_positive}")


if __name__ == "__main__":
    main()
