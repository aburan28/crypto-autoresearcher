"""
Full blind re-derivation run for PA-ECDLP-6ac801-v2-to-v3, Stage A''.
Grid, definitions and formulas taken exclusively from quantity.md.
"""
import json
import time
import hashlib
import sys
from decimal import Decimal
from fractions import Fraction as F

import numpy as np

from instrument import (
    derive_keys, compute_W, compute_cap, compute_dp_threshold,
    build_graph, bfs_partition,
)

SEEDS = list(range(1, 26))
N_LIST = [2**20, 2**24]
T_TABLE = {2**20: 64, 2**24: 256}
A_LIST_ORDERED_FOR_REPORT = [F(1, 4), F(1, 16), F(1, 8), F(3, 16)]  # a=1/4 first, per instructions
R = 2


def rng_for(seed, tag, N, a: F):
    key = f"{seed}|{tag}|{N}|{a.numerator}|{a.denominator}"
    h = hashlib.sha256(key.encode()).digest()
    seed64 = int.from_bytes(h[:8], "little")
    return np.random.default_rng(seed64)


def pool_construct(N, dist, root, cap, rT, rng_restart):
    pool = {}  # dp_id -> [h_d, S_d, insertion_order]
    insertion_order = []
    capped_walks = 0
    draws = 0
    # draw in reasonably sized batches for speed, but logic is per-draw
    batch = 4096
    while len(insertion_order) < rT:
        xs = rng_restart.integers(0, N, size=batch)
        for x0 in xs:
            draws += 1
            d = dist[x0]
            if d != -1 and d <= cap:
                dp_id = int(root[x0])
                Lsteps = int(d)
                if dp_id not in pool:
                    pool[dp_id] = [0, 0, len(insertion_order)]
                    insertion_order.append(dp_id)
                pool[dp_id][0] += 1
                pool[dp_id][1] += Lsteps
            else:
                capped_walks += 1
            if len(insertion_order) >= rT:
                break
    return pool, insertion_order, capped_walks, draws


def compute_cell(N, a: F, seed, T, verbose_tag=""):
    t_start = time.time()
    K, K_dp = derive_keys(seed)
    W = compute_W(a, N, T)
    cap = compute_cap(W)
    dp_threshold = compute_dp_threshold(W)
    T_sel = T // 2
    rT = R * T

    fx, is_dp = build_graph(N, K, K_dp, dp_threshold)
    dist, root = bfs_partition(N, fx, is_dp, cap)

    dp_nodes = np.nonzero(is_dp)[0]
    n_dps = int(dp_nodes.size)

    assigned_mask = (dist != -1) & (dist <= cap)
    cycle_mass = int((dist == -1).sum())
    capped_mass = int(((dist != -1) & (dist > cap)).sum())

    basin_counts = np.bincount(root[assigned_mask], minlength=N)
    sizes_all_dps = basin_counts[dp_nodes]  # exact basin size per DP, class(1) only
    sum_b = int(sizes_all_dps.sum())
    accounting_identity_holds = bool(sum_b + cycle_mass + capped_mass == N)
    min_basin_size = int(sizes_all_dps.min()) if n_dps > 0 else None

    # share_top(k) machinery: sort all DP basin sizes descending, cumulative sum (exact ints)
    order_desc = np.argsort(sizes_all_dps)[::-1]
    sorted_sizes = sizes_all_dps[order_desc]
    sorted_dp_ids = dp_nodes[order_desc]
    cumsum = np.cumsum(sorted_sizes)

    def share_top(k):
        if k <= 0:
            return 0.0, 0
        k = min(k, n_dps)
        num = int(cumsum[k - 1]) if k > 0 else 0
        return num / N, num

    share_top_Tsel, share_top_Tsel_num = share_top(T_sel)
    share_top_T, _ = share_top(T)
    share_top_Tover4, _ = share_top(T // 4)
    share_top_Tover8, _ = share_top(T // 8)

    # Pool construction (uniform random restarts), using precomputed dist/root
    rng_restart = rng_for(seed, "restart", N, a)
    pool, insertion_order, capped_walks, draws = pool_construct(N, dist, root, cap, rT, rng_restart)
    assert len(pool) == rT, f"pool size mismatch: {len(pool)} vs {rT}"

    # weight_d = S_d + 4*W*h_d, computed with Decimal for exact tie detection
    pool_ids = insertion_order[:]  # index -> dp_id, by insertion order
    weights_dec = []
    S_list = []
    H_list = []
    for dp_id in pool_ids:
        h_d, S_d, ins_ord = pool[dp_id]
        wt = Decimal(S_d) + 4 * W * Decimal(h_d)
        weights_dec.append(wt)
        S_list.append(S_d)
        H_list.append(h_d)

    order_idx = list(range(rT))
    # rank purely by weight (descending) to find n_tied_at_Tth_weight
    ranked_by_weight = sorted(order_idx, key=lambda i: weights_dec[i], reverse=True)
    weight_at_T = weights_dec[ranked_by_weight[T - 1]]
    n_tied_at_Tth_weight = sum(1 for i in order_idx if weights_dec[i] == weight_at_T)

    # tie-break keys: bulk array from a fresh PRNG seeded from the seed, indexed by insertion order
    rng_tie = rng_for(seed, "tiebreak", N, a)
    tie_keys = rng_tie.random(rT)

    final_order = sorted(order_idx, key=lambda i: (-weights_dec[i], tie_keys[i]))
    sel_positions = final_order[:T]  # positions (indices into pool arrays) selected
    sel_dp_ids = [pool_ids[i] for i in sel_positions]

    cov_static_num = int(sum(int(basin_counts[d]) for d in sel_dp_ids))
    cov_static = cov_static_num / N

    margin = share_top_Tsel - cov_static

    # rho_ORACLE: smallest k (in units of k/T) such that share_top(k) >= cov_static (exact int compare)
    idx_reach = np.searchsorted(cumsum, cov_static_num, side="left")
    k_needed = idx_reach + 1
    k_needed = min(k_needed, n_dps)
    rho_ORACLE = k_needed / T

    residual_fraction = (cycle_mass + capped_mass) / N

    # ---- control arms, all read off the same exact partition ----
    pool_sizes_arr = np.array([int(basin_counts[d]) for d in pool_ids], dtype=np.int64)

    # NULL-ORACLE-RAND (uniform): random T_sel-subset of ALL DPs
    rng_nu = rng_for(seed, "null_uniform", N, a)
    idx_u = rng_nu.choice(n_dps, size=min(T_sel, n_dps), replace=False)
    cov_null_uniform = int(sizes_all_dps[idx_u].sum()) / N
    margin_null_oracle_rand_uniform = cov_null_uniform - cov_static

    # NULL-ORACLE-RAND (size-biased): weighted sampling w/o replacement, prob prop to basin size
    rng_nb = rng_for(seed, "null_sizebiased", N, a)
    u = rng_nb.random(n_dps)
    u = np.clip(u, 1e-300, 1.0)
    keys = np.log(u) / sizes_all_dps.astype(np.float64)
    top_idx = np.argpartition(keys, -min(T_sel, n_dps))[-min(T_sel, n_dps):]
    cov_null_sizebiased = int(sizes_all_dps[top_idx].sum()) / N
    margin_null_oracle_rand_sizebiased = cov_null_sizebiased - cov_static

    # NULL-RANDSEL: uniform random T-subset of the r*T pool
    rng_rs = rng_for(seed, "null_randsel", N, a)
    idx_rs = rng_rs.choice(rT, size=T, replace=False)
    cov_null_randsel = int(pool_sizes_arr[idx_rs].sum()) / N
    margin_null_randsel = share_top_Tsel - cov_null_randsel

    # NULL-SHUF: permute basin sizes across pool entries, keep weight-based selection fixed
    rng_sh = rng_for(seed, "null_shuf", N, a)
    shuffled_sizes = rng_sh.permutation(pool_sizes_arr)
    cov_static_shuf = int(shuffled_sizes[sel_positions].sum()) / N
    margin_null_shuf = share_top_Tsel - cov_static_shuf  # derived by us; disclosed as such

    elapsed = time.time() - t_start

    cell = dict(
        N=N, a_num=a.numerator, a_den=a.denominator, seed=seed, T=T, T_sel=T_sel, r=R,
        W=str(W), cap=cap,
        share_top_Tsel=share_top_Tsel, cov_static=cov_static, margin=margin,
        share_top_T=share_top_T, share_top_Tover4=share_top_Tover4, share_top_Tover8=share_top_Tover8,
        rho_ORACLE=rho_ORACLE,
        n_dps=n_dps, cycle_mass=cycle_mass, capped_mass=capped_mass,
        capped_walks=capped_walks, residual_fraction=residual_fraction,
        accounting_identity_holds=accounting_identity_holds,
        min_basin_size=min_basin_size,
        n_tied_at_Tth_weight=n_tied_at_Tth_weight,
        margin_null_oracle_rand_uniform=margin_null_oracle_rand_uniform,
        margin_null_oracle_rand_sizebiased=margin_null_oracle_rand_sizebiased,
        margin_null_randsel=margin_null_randsel,
        cov_static_shuf=cov_static_shuf,
        margin_null_shuf=margin_null_shuf,
        pool_draws=draws,
        elapsed_sec=elapsed,
    )
    print(f"  [{verbose_tag}] N={N} a={a} seed={seed} margin={margin:+.6f} "
          f"cov_static={cov_static:.6f} share_top_Tsel={share_top_Tsel:.6f} "
          f"cycle_mass={cycle_mass} capped_mass={capped_mass} elapsed={elapsed:.2f}s", flush=True)
    return cell


def aggregate(cells):
    margins = np.array([c["margin"] for c in cells])
    k_25 = int((margins >= 0).sum())
    verdict_25 = "G3-FEASIBLE" if k_25 >= 20 else "G3-INFEASIBLE"
    margins5 = margins[:5]
    k_5 = int((margins5 >= 0).sum())
    verdict_5 = "G3-FEASIBLE" if k_5 >= 4 else "G3-INFEASIBLE"
    mean_margin = float(margins.mean())
    mean_margin_sign = "+" if mean_margin > 0 else ("-" if mean_margin < 0 else "0")

    N = cells[0]["N"]
    a = F(cells[0]["a_num"], cells[0]["a_den"])
    n_bits = N.bit_length() - 1
    boot_seed = 20260907 + 1000 * n_bits + round(10000 * float(a))
    rng_boot = np.random.default_rng(boot_seed)
    B = 10000
    resample_idx = rng_boot.integers(0, 25, size=(B, 25))
    resample_means = margins[resample_idx].mean(axis=1)
    ci_lo = float(np.percentile(resample_means, 2.5))
    ci_hi = float(np.percentile(resample_means, 97.5))
    ci_straddles_zero = bool(ci_lo <= 0.0 <= ci_hi)

    def null_stats(field):
        vals = np.array([c[field] for c in cells])
        return float(vals.mean()), int((vals >= 0).sum())

    mmn_u, nsn_u = null_stats("margin_null_oracle_rand_uniform")
    mmn_b, nsn_b = null_stats("margin_null_oracle_rand_sizebiased")
    mmn_r, nsn_r = null_stats("margin_null_randsel")
    mmn_s, nsn_s = null_stats("margin_null_shuf")

    max_residual_fraction = float(max(c["residual_fraction"] for c in cells))

    return dict(
        N=N, a_num=a.numerator, a_den=a.denominator,
        k_25=k_25, verdict_25=verdict_25, k_5=k_5, verdict_5=verdict_5,
        mean_margin=mean_margin, mean_margin_sign=mean_margin_sign,
        ci_lo=ci_lo, ci_hi=ci_hi, ci_straddles_zero=ci_straddles_zero,
        bootstrap_seed_used=boot_seed, bootstrap_B=B, bootstrap_n_bits_convention="log2(N)",
        mean_margin_null_oracle_rand_uniform=mmn_u, n_seeds_margin_null_nonneg_oracle_rand_uniform=nsn_u,
        mean_margin_null_oracle_rand_sizebiased=mmn_b, n_seeds_margin_null_nonneg_oracle_rand_sizebiased=nsn_b,
        mean_margin_null_randsel=mmn_r, n_seeds_margin_null_nonneg_randsel=nsn_r,
        mean_margin_null_shuf=mmn_s, n_seeds_margin_null_nonneg_shuf=nsn_s,
        max_residual_fraction=max_residual_fraction,
    )


def main():
    out_cells_path = sys.argv[1] if len(sys.argv) > 1 else "cells.jsonl"
    out_summary_path = sys.argv[2] if len(sys.argv) > 2 else "summary.json"

    all_cells = []
    all_summaries = []
    stopped_early = False
    stop_reason = None

    with open(out_cells_path, "w") as fcells:
        for N in N_LIST:
            T = T_TABLE[N]
            for a in A_LIST_ORDERED_FOR_REPORT:
                tag = f"N={N} a={a}"
                print(f"=== {tag} ===", flush=True)
                cells = []
                for seed in SEEDS:
                    cell = compute_cell(N, a, seed, T, verbose_tag=tag)
                    cells.append(cell)
                    all_cells.append(cell)
                    fcells.write(json.dumps(cell) + "\n")
                    fcells.flush()
                summ = aggregate(cells)
                all_summaries.append(summ)
                print(f"  -> k_25={summ['k_25']} verdict_25={summ['verdict_25']} "
                      f"k_5={summ['k_5']} verdict_5={summ['verdict_5']} "
                      f"mean_margin={summ['mean_margin']:+.6f} ci=({summ['ci_lo']:+.6f},{summ['ci_hi']:+.6f})",
                      flush=True)
                if a == F(1, 4) and summ["verdict_25"] == "G3-FEASIBLE":
                    stopped_early = True
                    stop_reason = f"a=1/4 reading at N={N} came out G3-FEASIBLE; halting per instructions."
                    print("!!!", stop_reason, flush=True)
                    break
            if stopped_early:
                break

    with open(out_summary_path, "w") as fsum:
        json.dump(dict(
            summaries=all_summaries,
            stopped_early=stopped_early,
            stop_reason=stop_reason,
            n_cells_computed=len(all_cells),
        ), fsum, indent=2)

    print("DONE", "stopped_early=", stopped_early, "n_cells=", len(all_cells))


if __name__ == "__main__":
    main()
