#!/usr/bin/env python3
"""
J2 BLIND RE-DERIVATION -- rho_ORACLE(a, r) at a in {1/4, 1/2}, N=2^20,
r in {2,4,8} (the contract's a-scan grid).

Written from the SPECIFICATION'S OWN MATHEMATICAL DEFINITIONS ALONE
(experiments/EXP-ECDLP-612fb1/specification.v2.yaml `definitions`,
`instrument`, `inputs.stage_plan` STAGE 0, `inputs.g3_gate_procedure`),
which are the only two files this script's author had open when writing it,
per the task's `inputs` allow-list (specification.v2.yaml and
amendments/v1_to_v2.yaml are explicitly NOT in `blind_from`).

This script was NOT written after reading:
  - experiments/EXP-ECDLP-612fb1/source_v2/   (blind_from)
  - experiments/EXP-ECDLP-612fb1/runs/        (blind_from)
  - coordination/.../tasks/TASK-20260906-5e78c7/ (blind_from, the executor's
    own Stage 0 report and code)

Definitions used (quoted/paraphrased from specification.v2.yaml, verbatim
field names in comments):

  N: domain size, 2^20 for this derivation.
  T: nominal table size = 2^floor(log2(N)/3). At N=2^20 this yields T=64,
     matching the spec's own worked example ("64 at 2^20, 256 at 2^24,
     1024 at 2^30" -- note 2^20 is not an exact cube, so T is NOT literally
     round(N^(1/3))=102; the worked examples are exact powers of two that
     only make sense as 2^floor(log2(N)/3), which this script therefore uses).
  W: expected walk length between DPs. a = T*W^2/N (definitions.a), so
     W = sqrt(a*N/T). At a=1/4 this reduces to W=(1/2)*sqrt(N/T), matching
     the task handoff's explicitly given formula.
  generic_walk (instrument.generic_walk):
     f(x) = mix64(x XOR K) mod N, mix64 = splitmix64 finalizer (public,
     well-known 64-bit avalanche function; not read from any producer file).
     DP predicate: hash64(x) < floor(2^64 / W), hash64 = a SECOND, independently
     keyed splitmix64 application (independent key so W need not be an
     integer, per spec).
  basin: for a fixed (K, K2, W), every domain point x in [0,N) is iterated
     under f until a DP is hit (predicate true) or a DP-less cycle is
     detected (a point revisits a node already on the current open path
     without ever satisfying the predicate -- an exact, deterministic
     computation over the finite functional graph, no walk cap needed,
     since this is the THEORETICAL/EXACT basin partition, not an online
     walk execution). "basin of DP d" = the set of x whose walk first hits
     d. Basin sizes are computed EXACTLY, once per (a, seed), by resolving
     every node of the functional graph with path compression (each edge
     visited O(1) amortized).
  r (definitions.r): STATIC(T)_r's precomputation pool ratio. The pool is
     built by drawing FRESH independent uniformly-random start points x,
     looking up each one's basin resolution (terminal DP identity and path
     length, i.e. "walk length"), crediting (length, +1) to that DP's
     (S_d, h_d), continuing until the pool contains r*T DISTINCT DPs.
  weight (definitions.weight): published Bernstein-Lange weight,
     weight(d) = S_d + 4*W*h_d.
  STATIC(T)_r exact coverage: from the r*T-distinct-DP pool, select the T
     DPs of highest weight (the published BL table-construction rule); its
     "exact coverage" = (sum of the TRUE basin sizes of those T selected
     DPs) / N -- this is what "STATIC(T)_r exact coverage" must mean for a
     G3 gate that reads it directly off exact basins (spec:
     `inputs.g3_gate_procedure`, "exact top-T_sel share >= STATIC(T)_r exact
     coverage").
  ORACLE(T_sel) exact top-T_sel basin share (definitions.rho_ORACLE): the
     T_sel LARGEST true basin sizes across the WHOLE domain partition
     (oracle knowledge, independent of any sampled pool or of r), summed
     and divided by N. This is monotone non-decreasing in T_sel.
  rho_ORACLE(a, r) (this task's target quantity, at N=2^20): the T_sel/T
     value at which ORACLE(T_sel)'s share (increasing in T_sel) equals
     STATIC(T)_r's exact coverage (a constant, once r and the pool sample
     are fixed), found by LOG-LINEAR interpolation on the T_sel grid
     {T/4, T/2, 3T/4, T, 0.65T, 0.75T} exactly as Stage 0 specifies
     (spec `inputs.stage_plan` STAGE 0), mirroring the same interpolation
     rule stated for T_resel(U)/rho_T(U).

Nothing in this file was informed by the executor's implementation. Seeds,
key derivation and RNG choice below are this script's OWN, independent of
whatever the executor used -- the point of a blind re-derivation is
agreement on the STATISTIC, not on a shared random realization.
"""
import hashlib
import json
import random
import sys
import time

MASK64 = (1 << 64) - 1


def splitmix64(x: int) -> int:
    x &= MASK64
    x = (x ^ (x >> 30)) * 0xBF58476D1CE4E5B9 & MASK64
    x = (x ^ (x >> 27)) * 0x94D049BB133111EB & MASK64
    x = x ^ (x >> 31)
    return x & MASK64


def build_walk_fn(N: int, K: int):
    def f(x: int) -> int:
        return splitmix64(x ^ K) % N
    return f


def build_dp_fn(W: float, K2: int):
    # threshold = floor(2^64 / W); predicate: hash64(x) < threshold
    threshold = int((1 << 64) // W)

    def is_dp(x: int) -> bool:
        return splitmix64(x ^ K2) < threshold
    return is_dp


def resolve_basins(N: int, f, is_dp):
    """
    Exact basin resolution over the full domain [0, N).
    Returns:
      term[x]   -> terminal DP id (an int, the DP value itself) or -1 if x
                   is on / feeds into a DP-less cycle (never hits a DP).
      steps[x]  -> path length (# of f-applications) from x to its DP,
                   or -1 if term[x] == -1.
    Implemented as a standard "functional graph" resolution with path
    compression: walk forward from each unresolved x, remembering the path;
    stop when hitting (a) a DP (resolves whole path with dist countdown),
    (b) an already-resolved node (splice), or (c) a node already on the
    CURRENT path (a newly discovered DP-less cycle: every node on the cycle,
    and the path leading to it, resolves to -1).
    """
    UNVISITED, ON_PATH, DONE = 0, 1, 2
    state = bytearray(N)  # 0 unvisited, 1 on current path, 2 done
    term = [0] * N
    steps = [0] * N
    on_path_index = [0] * N  # position in the current path list, if ON_PATH

    for start in range(N):
        if state[start] == DONE:
            continue
        path = []
        x = start
        while True:
            if is_dp(x):
                # x itself is a DP; resolves the whole path with 0-based steps
                term_dp = x
                for i, node in enumerate(reversed(path)):
                    state[node] = DONE
                    term[node] = term_dp
                    steps[node] = i + 1
                state[x] = DONE
                term[x] = x
                steps[x] = 0
                break
            if state[x] == DONE:
                # splice onto an already resolved chain
                base_term = term[x]
                base_steps = steps[x]
                for i, node in enumerate(reversed(path)):
                    state[node] = DONE
                    term[node] = base_term
                    steps[node] = base_steps + i + 1
                break
            if state[x] == ON_PATH:
                # found a cycle within the current path, with no DP in it
                idx = on_path_index[x]
                cycle_and_tail = path[idx:]
                tail = path[:idx]
                for node in cycle_and_tail:
                    state[node] = DONE
                    term[node] = -1
                    steps[node] = -1
                for i, node in enumerate(reversed(tail)):
                    state[node] = DONE
                    term[node] = -1
                    steps[node] = -1
                break
            state[x] = ON_PATH
            on_path_index[x] = len(path)
            path.append(x)
            x = f(x)
    return term, steps


def basin_sizes_from_term(term, N):
    from collections import Counter
    c = Counter(t for t in term if t != -1)
    return c  # dp_id -> basin size


def static_pool_coverage(N, T, r, term, steps, basin_size, rng):
    """
    Build the r*T-distinct-DP pool by drawing fresh independent uniform
    random start points, crediting (length, +1) to each hit DP, until
    r*T distinct DPs have been observed. Then select the T highest-weight
    DPs (weight = S_d + 4*W*h_d) and return the sum of their TRUE basin
    sizes / N as the exact coverage.
    """
    target_distinct = r * T
    S = {}
    h = {}
    seen = set()
    draws = 0
    max_draws = 200 * target_distinct + 100000  # generous safety valve
    while len(seen) < target_distinct and draws < max_draws:
        x = rng.randrange(N)
        draws += 1
        d = term[x]
        if d == -1:
            continue  # miss: charged to P in the real protocol, contributes no DP
        length = steps[x]
        S[d] = S.get(d, 0) + length
        h[d] = h.get(d, 0) + 1
        seen.add(d)
    if len(seen) < target_distinct:
        raise RuntimeError(
            f"pool generation did not reach {target_distinct} distinct DPs "
            f"within {max_draws} draws (got {len(seen)}); basin structure "
            f"may have too few large basins at this (a, seed)."
        )
    return S, h, draws


def compute_basin_structure(N, W, a, seed):
    """
    Basin resolution depends only on (N, W, seed) via the walk/DP keys, NOT
    on r -- r only governs how STATIC(T)_r's pool is sampled afterwards.
    Computed once per (a, seed) and reused across every r value.
    """
    K = splitmix64(seed ^ 0xA5A5A5A5A5A5A5A5 ^ int(a * 4))
    K2 = splitmix64(seed ^ 0x5A5A5A5A5A5A5A5A ^ int(a * 4) ^ 0x1234)
    f = build_walk_fn(N, K)
    is_dp = build_dp_fn(W, K2)
    term, steps = resolve_basins(N, f, is_dp)
    sizes = basin_sizes_from_term(term, N)
    sorted_sizes = sorted(sizes.values(), reverse=True)
    n_miss = sum(1 for t in term if t == -1)
    return term, steps, sizes, sorted_sizes, n_miss


def rho_oracle_for_cell(N, T, W, a, r, seed, T_sel_grid_fracs, basin_structure):
    term, steps, sizes, sorted_sizes, n_miss = basin_structure

    # ORACLE top-T_sel share as a function of T_sel (grid points, exact ints)
    T_sel_values = sorted(set(max(1, round(frac * T)) for frac in T_sel_grid_fracs))
    # cumulative sum of the k largest basins for k = 1..len(sorted_sizes)
    cumsum = []
    running = 0
    for s in sorted_sizes:
        running += s
        cumsum.append(running)

    def oracle_share(t_sel):
        if t_sel <= 0:
            return 0.0
        if t_sel >= len(cumsum):
            return cumsum[-1] / N if cumsum else 0.0
        return cumsum[t_sel - 1] / N

    oracle_shares = {t_sel: oracle_share(t_sel) for t_sel in T_sel_values}

    rng = random.Random((seed << 8) ^ r ^ int(a * 1000))
    S, h, draws = static_pool_coverage(N, T, r, term, steps, sizes, rng)
    W_local = W
    weights = {d: S[d] + 4 * W_local * h[d] for d in S}
    top_T_dps = sorted(weights.keys(), key=lambda d: weights[d], reverse=True)[:T]
    static_coverage = sum(sizes[d] for d in top_T_dps) / N

    # log-linear interpolation for rho_ORACLE = T_sel/T at the crossing of
    # oracle_share(T_sel) [increasing in T_sel] with static_coverage [constant]
    xs = sorted(oracle_shares.keys())
    ys = [oracle_shares[x] for x in xs]

    def log_linear_interp_crossing(xs, ys, target):
        # find bracket [xs[i], xs[i+1]] with ys[i] <= target <= ys[i+1]
        if target <= ys[0]:
            # crossing at or below smallest grid point; report smallest as
            # a floor-bound (log-linear extrapolation would be unstable at
            # very small T_sel here; flag it)
            return xs[0], "at_or_below_grid_floor"
        if target >= ys[-1]:
            return xs[-1], "at_or_above_grid_ceiling"
        for i in range(len(xs) - 1):
            if ys[i] <= target <= ys[i + 1]:
                x0, x1 = xs[i], xs[i + 1]
                y0, y1 = ys[i], ys[i + 1]
                if y0 == y1:
                    return x0, "flat_segment"
                # log-linear on T_sel (x), linear interpolation on share (y)
                import math
                lx0, lx1 = math.log(x0), math.log(x1)
                frac = (target - y0) / (y1 - y0)
                lx = lx0 + frac * (lx1 - lx0)
                return math.exp(lx), "interpolated"
        return xs[-1], "fallthrough"

    t_sel_cross, interp_flag = log_linear_interp_crossing(xs, ys, static_coverage)
    rho = t_sel_cross / T

    return {
        "a": a,
        "r": r,
        "seed": seed,
        "N": N,
        "T": T,
        "W": W,
        "n_miss": n_miss,
        "n_miss_frac": n_miss / N,
        "n_distinct_basins": len(sorted_sizes),
        "largest_basin": sorted_sizes[0] if sorted_sizes else None,
        "oracle_shares_by_T_sel": oracle_shares,
        "static_pool_draws": draws,
        "static_coverage": static_coverage,
        "rho_ORACLE": rho,
        "interp_flag": interp_flag,
    }


def main():
    N = 2 ** 20
    T = 2 ** (20 // 3)  # floor(log2(N)/3) = floor(20/3) = 6 -> T = 64
    assert T == 64, T
    T_sel_grid_fracs = [0.25, 0.5, 0.75, 1.0, 0.65, 0.75]
    a_values = [0.25, 0.5]
    r_values = [2, 4, 8]
    seeds = [1001, 2002, 3003, 4004, 5005]  # 5 seeds, independent of the executor's

    results = []
    t_start = time.time()
    for a in a_values:
        W = (a * N / T) ** 0.5
        for seed in seeds:
            basin_structure = compute_basin_structure(N, W, a, seed)
            for r in r_values:
                res = rho_oracle_for_cell(N, T, W, a, r, seed, T_sel_grid_fracs, basin_structure)
                results.append(res)
                print(
                    f"a={a:.4f} r={r} seed={seed} W={W:.3f} "
                    f"rho_ORACLE={res['rho_ORACLE']:.4f} "
                    f"static_cov={res['static_coverage']:.4f} "
                    f"flag={res['interp_flag']} "
                    f"miss_frac={res['n_miss_frac']:.5f} "
                    f"elapsed={time.time()-t_start:.1f}s",
                    file=sys.stderr,
                )

    summary = {}
    for a in a_values:
        for r in r_values:
            vals = [res["rho_ORACLE"] for res in results if res["a"] == a and res["r"] == r]
            summary[f"a={a}_r={r}"] = {
                "n": len(vals),
                "mean": sum(vals) / len(vals),
                "min": min(vals),
                "max": max(vals),
                "values": vals,
            }

    output = {
        "quantity": "rho_ORACLE(a, r) blind re-derivation, N=2^20",
        "definitions_source": "experiments/EXP-ECDLP-612fb1/specification.v2.yaml (definitions, instrument, inputs.stage_plan STAGE 0) -- read BEFORE this script was written; no other project file was read before writing/running it",
        "N": N,
        "T": T,
        "T_sel_grid_fracs": T_sel_grid_fracs,
        "a_values": a_values,
        "r_values": r_values,
        "seeds": seeds,
        "per_cell_results": results,
        "summary": summary,
        "ordering_check": {
            "claim": "rho_ORACLE(a=1/4, r) < rho_ORACLE(a=1/2, r) for each r",
            "by_r": {
                str(r): {
                    "mean_a_quarter": summary[f"a=0.25_r={r}"]["mean"],
                    "mean_a_half": summary[f"a=0.5_r={r}"]["mean"],
                    "ordering_holds": summary[f"a=0.25_r={r}"]["mean"] < summary[f"a=0.5_r={r}"]["mean"],
                }
                for r in r_values
            },
        },
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
