#!/usr/bin/env python3
"""
STAGE A BLIND RE-DERIVATION -- TASK-20260907-80e198 (Validator, EXP-ECDLP-6ac801)

This is an INDEPENDENT, from-scratch implementation written ONLY from the
exact basin-partition definitions in experiments/EXP-ECDLP-6ac801/specification.yaml
(`definitions`, `blind_rederivation.quantity`) and the verbatim G3 criterion
text quoted from experiments/EXP-ECDLP-612fb1/specification.v2.yaml
`inputs.g3_gate_procedure` (read via Grep, not via opening source_v2/ or any
run artifact).

It does NOT read, import, or reference anything under:
  - experiments/EXP-ECDLP-612fb1/source_v2/
  - experiments/EXP-ECDLP-612fb1/runs/RUN-ECDLP-612fb1-v2-ascan-*/
  - experiments/EXP-ECDLP-612fb1/runs/RUN-ECDLP-612fb1-v2-analysis-001/
  - experiments/EXP-ECDLP-6ac801/runs/

Model (HEUR-BLT-1, as stated in the contract's own blind_rederivation.quantity):
  a uniformly random function f: [0,N) -> [0,N), each point independently
  marked "distinguished" (DP) with probability theta = 1/W, where
  W = sqrt(a*N/T). A "basin" of a DP node d is the set of starting points x
  whose forward orbit under f first reaches d. Basin sizes are computed by
  EXACT enumeration (pointer-doubling closure over the whole state space),
  not by online random walks and not by sampling.

Two independently-generated random streams are used per seed, deliberately
NOT mix64/hash64 (the production instrument's own generator, which this
Stage A must not reuse or consult): numpy's default_rng, seeded
deterministically from (seed, role-tag).

Quantities computed, per (a, seed):
  - exact top-T_sel(=T/2) basin share: sum of the T_sel largest basin sizes
    (by full-population knowledge) / N.
  - STATIC(T)_r exact coverage: sample an r*T-distinct-DP precomputation
    pool via uniformly random starting points (each such draw's terminal DP
    is added to the pool until r*T distinct DPs are collected -- a bigger
    basin is proportionally more likely to be discovered, exactly as the
    Bernstein-Lange oversampled-pool construction implies), then take the
    T largest-by-size DPs in that pool and sum their sizes / N.

Author: independent Validator task, sealed BEFORE any blind_from path is opened.
"""
import numpy as np
import json
import time
import hashlib
import sys

N = 2**24            # 16777216
T = 256               # N^(1/3) rounded, exact at N=2^24 since 2^24 = 2^(3*8)
T_SEL = T // 2        # 128
R = 2                 # precomputation pool ratio
A_GRID = [("1/16", 1.0/16.0), ("1/8", 1.0/8.0), ("3/16", 3.0/16.0), ("1/4", 1.0/4.0)]
SEEDS = [1, 2, 3, 4, 5]
DOUBLING_ROUNDS = 26  # 2^26 > 6.7e7 >> N; more than enough to reach any fixed point

def compute_for_seed(seed):
    # Independent RNG streams, deliberately not the production's mix64/hash64.
    rng_f = np.random.default_rng(seed=(seed * 1_000_003 + 17))
    f = rng_f.integers(0, N, size=N, dtype=np.int64)  # uniformly random function on N points

    rng_mark = np.random.default_rng(seed=(seed * 1_000_003 + 29))
    u = rng_mark.random(size=N).astype(np.float64)  # one marking value per point, reused (nested) across a

    results = {}
    idx_all = np.arange(N, dtype=np.int64)

    for a_label, a_val in A_GRID:
        W = np.sqrt(a_val * N / T)
        theta = 1.0 / W
        D = u < theta  # independent Bernoulli(1/W) marking

        g = np.where(D, idx_all, f)  # absorbing self-loop at marked (DP) nodes

        cur = g
        for _ in range(DOUBLING_ROUNDS):
            cur = cur[cur]

        terminal = cur  # terminal[x] = DP node x's orbit converges to (if it converges)

        # Correctness note (found and fixed during a small-N (N=1024) brute-force
        # cross-check against a naive per-node walk BEFORE running the N=2^24
        # computation below): a node whose forward orbit enters a cycle that
        # contains NO DP is a genuine non-termination case. Checking only
        # "g[terminal] == terminal" is NOT sufficient to detect this, because a
        # coincidental FIXED POINT of f that is itself not marked as a DP
        # (f(y) = y, D[y] = False) also self-loops under g (g(y) = f(y) = y),
        # and is therefore indistinguishable from a true DP self-loop by that
        # check alone -- it silently masquerades as a resolved terminal. The
        # correct resolution criterion is that the terminal node is ACTUALLY a
        # marked DP: resolved[x] = D[terminal[x]]. This was verified by an
        # exhaustive N=1024 brute-force walk (visited-set cycle detection)
        # matching this closure exactly (0 mismatches) after the fix; before
        # the fix, 3/1024 nodes (all funneling into one non-DP fixed point)
        # were mis-resolved.
        resolved = D[terminal]
        n_unresolved = int(N - np.count_nonzero(resolved))

        counts = np.bincount(terminal, minlength=N)
        dp_ids = np.nonzero(D)[0]
        # sanity: every dp id should self-loop
        bad_dp = np.count_nonzero(g[dp_ids] != dp_ids)

        dp_sizes = counts[dp_ids]
        sorted_sizes = np.sort(dp_sizes)[::-1]

        top_Tsel_sum = int(sorted_sizes[:T_SEL].sum())
        top_T_sum = int(sorted_sizes[:T].sum())
        top_Tsel_share = top_Tsel_sum / N
        top_T_share = top_T_sum / N

        # STATIC(T)_r exact coverage: sample r*T distinct DPs via uniformly
        # random starting points' terminal DP, until r*T distinct DPs found.
        rng_pool = np.random.default_rng(seed=(seed * 1_000_003 + 53 + hash(a_label) % 1000))
        pool_target = R * T
        seen = set()
        draws = 0
        batch = max(pool_target * 4, 4096)
        while len(seen) < pool_target:
            starts = rng_pool.integers(0, N, size=batch)
            draws += batch
            term = terminal[starts]
            res = D[term]  # only a genuinely-resolved (real DP) terminal may enter the pool
            for t, ok in zip(term.tolist(), res.tolist()):
                if ok and t not in seen:
                    seen.add(t)
                    if len(seen) >= pool_target:
                        break
        pool_dp_ids = np.array(list(seen)[:pool_target], dtype=np.int64)
        pool_sizes = counts[pool_dp_ids]
        pool_sorted = np.sort(pool_sizes)[::-1]
        static_T_sum = int(pool_sorted[:T].sum())
        static_coverage = static_T_sum / N

        margin = top_Tsel_share - static_coverage

        results[a_label] = dict(
            a=a_label,
            a_value=a_val,
            seed=seed,
            W=float(W),
            theta=float(theta),
            n_dp_nodes=int(len(dp_ids)),
            n_unresolved_nodes=n_unresolved,
            n_bad_dp_selfloop=int(bad_dp),
            max_basin_size=int(sorted_sizes[0]) if len(sorted_sizes) else None,
            top_Tsel_basin_share=top_Tsel_share,
            top_T_basin_share=top_T_share,
            static_T_r2_exact_coverage=static_coverage,
            pool_draws_used=draws,
            margin_share_minus_coverage=margin,
            pass_cell=bool(margin >= 0.0),
            control_c_ok=bool(top_Tsel_share <= 1.0 and top_Tsel_share <= top_T_share + 1e-12),
        )
    return results


def main():
    t_start = time.time()
    all_results = {}
    for seed in SEEDS:
        all_results[str(seed)] = compute_for_seed(seed)

    # Reorganize per-a, per-seed and compute pass counts / G3-style verdicts
    per_a = {}
    for a_label, a_val in A_GRID:
        cells = []
        for seed in SEEDS:
            cells.append(all_results[str(seed)][a_label])
        pass_count = sum(1 for c in cells if c["pass_cell"])
        verdict = "G3-FEASIBLE" if pass_count >= 4 else "G3-INFEASIBLE"
        per_a[a_label] = dict(
            a=a_label,
            a_value=a_val,
            pass_count=pass_count,
            n_seeds=len(cells),
            verdict=verdict,
            cells=cells,
        )

    payload = dict(
        computed_at_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        parameters=dict(N=N, T=T, T_sel=T_SEL, r=R, a_grid=[a for a, _ in A_GRID], seeds=SEEDS,
                        doubling_rounds=DOUBLING_ROUNDS),
        method_note=(
            "Independent from-scratch implementation: uniformly random function "
            "f:[0,N)->[0,N) via numpy default_rng (NOT mix64/hash64), independent "
            "Bernoulli(1/W) marking via numpy default_rng uniform draws (NOT hash64 "
            "threshold), exact basin closure via pointer-doubling (26 rounds), "
            "STATIC(T)_r coverage via a sampled r*T-distinct-DP pool drawn from "
            "uniformly random starting points' terminal DPs, largest T of that pool "
            "selected by weight (size). No path under blind_from was read before or "
            "during this computation."
        ),
        per_a=per_a,
        wall_clock_seconds=time.time() - t_start,
    )

    out_path = sys.argv[1] if len(sys.argv) > 1 else "sealed_blind_rederivation.json"
    with open(out_path, "w") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)

    with open(out_path, "rb") as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()

    print(f"WROTE {out_path}")
    print(f"SHA256 {digest}")
    print(f"WALL_CLOCK_SECONDS {payload['wall_clock_seconds']:.2f}")
    for a_label, _ in A_GRID:
        pa = per_a[a_label]
        margins = [c["margin_share_minus_coverage"] for c in pa["cells"]]
        print(f"a={a_label}: pass_count={pa['pass_count']}/5 verdict={pa['verdict']} margins={['%.5f'%m for m in margins]}")


if __name__ == "__main__":
    main()
