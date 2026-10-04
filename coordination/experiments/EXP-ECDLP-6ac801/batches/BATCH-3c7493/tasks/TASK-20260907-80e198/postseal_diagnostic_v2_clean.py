#!/usr/bin/env python3
"""
POST-SEAL DIAGNOSTIC v2 (corrected) -- NOT part of the frozen Stage A sealed
artifact (sealed_blind_rederivation.json, sha256
9127cabc803bb5fdbb90342bb7724810c6d5d5cfea0a83d6e4cfe40762fa90d3, sealed
2026-09-07T01:27:58Z).

Two bugs found in the sealed script during post-seal root-cause analysis of
the a=1/8 disagreement, disclosed here and fixed ONLY in this diagnostic
copy (the sealed artifact and blind_rederivation.py that produced it are
left exactly as sealed -- an immutable record -- per AGENTS.md rule 2):

  BUG 1 (non-determinism): the sealed script's STATIC(T)_r pool-sampling RNG
  was seeded in part with `hash(a_label) % 1000`, where a_label is a Python
  str ("1/8" etc). CPython randomizes str hashing per process by default
  (PYTHONHASHSEED), so this seed offset is DIFFERENT on every fresh process
  invocation. The sealed JSON is a fixed, legitimate data point (one
  particular realization), but the sealed code is NOT exactly reproducible
  bit-for-bit from a re-run -- confirmed directly: `hash('1/8') % 1000`
  returns 287, 396, 762 on three successive bare `python3 -c` invocations in
  this same environment. This is disclosed as a found limitation of Stage
  A's own implementation, not corrected retroactively in the seal.

  BUG 2 (apples-to-oranges in the first diagnostic pass,
  postseal_diagnostic_weight_formula.py): that script computed the
  size-ranked and weight-ranked selections from two SEPARATELY drawn pools
  (different batch sizes advance the shared-seed RNG differently), so their
  difference conflated "which pool was sampled" with "which selection rule
  was applied". This v2 script draws ONE shared pool of raw
  (start, terminal, walk-length) triples per (a, seed) and applies BOTH
  selection rules to the SAME pool, isolating the selection-rule effect.

Substantive finding under test: instrument.py's Pool.weights() (read AFTER
the seal, per this task's own procedure -- the blind_from prohibition binds
before sealing, not after) computes the "published Bernstein-Lange weight"
of a pool entry d as

    weight_d = S_d + 4 * W * h_d

(S_d = sum of GENERATING-WALK LENGTHS that terminated at d; h_d = hit
count), NOT the DP's true exact basin size. specification.yaml's own
`definitions.STATIC(T)_r exact coverage` names "the published
Bernstein-Lange weight" but never states this formula, so Stage A's sealed
computation (built only from the plain HEUR-BLT-1 statistical model, with no
access to this literature-specific estimator) selected the T pool entries by
TRUE EXACT SIZE instead -- an oracle-optimal selection within the pool that
is NOT the same operational quantity the production computes.
"""
import numpy as np
import blind_rederivation as B

N = B.N
T = B.T
T_SEL = B.T_SEL
R = B.R
A_INDEX = {"1/16": 0, "1/8": 1, "3/16": 2, "1/4": 3}  # deterministic replacement for hash(a_label)


def draw_shared_pool(seed, a_label, a_val, pool_target):
    rng_f = np.random.default_rng(seed=(seed * 1_000_003 + 17))
    f = rng_f.integers(0, N, size=N, dtype=np.int64)
    rng_mark = np.random.default_rng(seed=(seed * 1_000_003 + 29))
    u = rng_mark.random(size=N)

    W = np.sqrt(a_val * N / T)
    theta = 1.0 / W
    D = u < theta
    idx_all = np.arange(N, dtype=np.int64)
    g = np.where(D, idx_all, f)

    cur = g
    for _ in range(B.DOUBLING_ROUNDS):
        cur = cur[cur]
    terminal = cur
    counts = np.bincount(terminal, minlength=N)

    # DETERMINISTIC pool-sampling seed (fixes BUG 1)
    rng_pool = np.random.default_rng(seed=(seed * 1_000_003 + 53 + A_INDEX[a_label]))
    S = {}
    h = {}
    batch = 4 * T
    while len(S) < pool_target:
        starts = rng_pool.integers(0, N, size=batch, dtype=np.int64)
        cur_b = starts.copy()
        length = np.zeros(batch, dtype=np.int64)
        active = np.ones(batch, dtype=bool)
        for _ in range(20000):
            if not active.any():
                break
            nxt = g[cur_b]
            moved = active & (nxt != cur_b)
            length[moved] += 1
            cur_b[moved] = nxt[moved]
            active = active & (g[cur_b] != cur_b)
        term_b = cur_b
        ok_b = D[term_b] & (~active)
        for i in range(batch):
            if not ok_b[i]:
                continue
            t = int(term_b[i])
            L = int(length[i])
            if t in S:
                S[t] += L
                h[t] += 1
            else:
                S[t] = float(L)
                h[t] = 1
            if len(S) >= pool_target:
                break

    dps = np.array(list(S.keys())[:pool_target], dtype=np.int64)
    S_arr = np.array([S[int(d)] for d in dps], dtype=np.float64)
    h_arr = np.array([h[int(d)] for d in dps], dtype=np.float64)
    true_sizes = counts[dps]
    return dps, S_arr, h_arr, true_sizes, W, counts, terminal, D


def top_T_share(counts, D, t):
    dp_ids = np.nonzero(D)[0]
    sizes = np.sort(counts[dp_ids])[::-1]
    return sizes[:t].sum() / N


def main():
    for a_label, a_val in [("1/16", 1/16), ("1/8", 1/8), ("3/16", 3/16), ("1/4", 1/4)]:
        print(f"\n=== a={a_label} (SAME shared pool, two selection rules) ===")
        print("seed  top_Tsel_share  cov_by_size  cov_by_weight(S+4Wh)  margin_by_size  margin_by_weight")
        for seed in [1, 2, 3, 4, 5]:
            dps, S_arr, h_arr, true_sizes, W, counts, terminal, D = draw_shared_pool(
                seed, a_label, a_val, R * T)
            share = top_T_share(counts, D, T_SEL)

            order_size = np.argsort(-true_sizes)
            cov_by_size = true_sizes[order_size[:T]].sum() / N

            weight = S_arr + 4.0 * W * h_arr
            order_weight = np.argsort(-weight)
            selected_by_weight = dps[order_weight[:T]]
            cov_by_weight = counts[selected_by_weight].sum() / N

            m_size = share - cov_by_size
            m_weight = share - cov_by_weight
            print(f"{seed:4d}  {share:.6f}       {cov_by_size:.6f}     {cov_by_weight:.6f}             {m_size:+.6f}       {m_weight:+.6f}")


if __name__ == "__main__":
    main()
