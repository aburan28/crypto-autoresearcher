#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Blind re-derivation, phase 1 (TASK-20260910-19bd7b, BATCH-12ee85).

Written from the derivation packet
  experiments/EXP-ECDLP-6ac801/derivation-packet/PA-ECDLP-6ac801-v2-to-v3/
  (quantity.md = the definition, deliverables.md = the fields)
and the frozen cell list in
  coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-12ee85/blind-input.yaml
ALONE.  No other repository file was read before the seal (see the reading
attestation in blind-rederivation.yaml).

Declared conventions for the choices the packet leaves to the implementer
(quantity.md s1/s9 and prohibitions.md s4 state that the mixer, the RNG and
the insertion order need not match any other implementation):

  mix64      : splitmix64 FINALIZER (the standard 64-bit avalanche mixer
               u ^= u>>30; u *= 0xBF58476D1CE4E5B9; u ^= u>>27;
               u *= 0x94D049BB133111EB; u ^= u>>31), applied to one u64.
               K    = mix64(0x9E3779B97F4A7C15 + seed)
               K_dp = mix64(K ^ 0xD1B54A32D192ED03)
  pool RNG   : numpy default_rng([seed, 1]), fresh per cell, restart starts
               uniform via integers(0, N).
  tie-break  : numpy default_rng([seed, 100]), fresh per cell, one bulk array
               of r*T doubles, one key per pool entry in pool-insertion order
               (quantity.md s6).
  null arms  : default_rng([seed, 101]) uniform oracle subset;
               default_rng([seed, 102]) size-biased oracle subset
               (sequential draw WITHOUT replacement, weights = basin sizes);
               default_rng([seed, 103]) uniform random T-subset of the pool;
               default_rng([seed, 104]) permutation of basin sizes over the
               pool entries.  All fresh per cell, all deterministic in the
               integer seed.
  cap boundary: a pool walk examines its landing points x_0..x_cap and is
               capped iff none of them is a DP (reading A = primary).  Reading
               B examines only x_0..x_{cap-1}.  quantity.md s3b does not fix
               which; BOTH readings are run per cell and reported.

Exact arithmetic: every quantity the definition makes exact (cap,
dp_threshold, basin sizes, all shares, margins, residual fractions,
rho_ORACLE, the accounting identity, pass-counts) is computed in integer /
Fraction arithmetic.  Floats appear only where the definition itself is
irrational (W, hence weight_d = S_d + 4*W*h_d) or explicitly statistical
(null-arm sampling, bootstrap); each such use is flagged in the report.
"""

import json
import math
import platform
import sys
import time
from datetime import datetime, timezone
from fractions import Fraction

import numpy as np

M64 = (1 << 64) - 1
GOLDEN = 0x9E3779B97F4A7C15
DP_XOR = 0xD1B54A32D192ED03
MUL1 = 0xBF58476D1CE4E5B9
MUL2 = 0x94D049BB133111EB

# ----------------------------------------------------------------------------
# mix64 (scalar and vectorised), declared convention: splitmix64 finalizer.
# ----------------------------------------------------------------------------


def mix64(u):
    u &= M64
    u ^= u >> 30
    u &= M64
    u = (u * MUL1) & M64
    u ^= u >> 27
    u &= M64
    u = (u * MUL2) & M64
    u ^= u >> 31
    return u


def mix64_arr(u):
    """Vectorised splitmix64 finalizer on a uint64 numpy array (wraps mod 2^64)."""
    u = u.astype(np.uint64, copy=True)
    u ^= u >> np.uint64(30)
    u *= np.uint64(MUL1)
    u ^= u >> np.uint64(27)
    u *= np.uint64(MUL2)
    u ^= u >> np.uint64(31)
    return u


# ----------------------------------------------------------------------------
# Exact derived parameters (integer arithmetic only).
# ----------------------------------------------------------------------------


def exact_params(N, T, a_num, a_den):
    """W = sqrt(a*N/T) with a = a_num/a_den.

    dp_threshold = floor(2^64 / W) = floor(sqrt(2^128 * T / (a*N)))
                 = isqrt((2^128 * a_den * T) // (a_num * N))
       (floor(sqrt(p/q)) == isqrt(p//q) for integers p >= 0, q > 0, since the
        remainder is < 1 and the gap to the next square is >= 1).
    cap = ceil(8*W) = ceil(sqrt(64 * a*N / T));  s = isqrt((64*a_num*N)//(a_den*T)),
         cap = s if s*s*(a_den*T) == 64*a_num*N else s+1  (exact perfect-square
         test; sqrt of a rational is either an integer or irrational/non-integer,
         in which cases ceil is floor+1).
    """
    num = a_num * N          # W^2 = num / den
    den = a_den * T
    dp_thr = math.isqrt(((1 << 128) * den) // num)
    q = 64 * num
    s = math.isqrt(q // den)
    cap = s if s * s * den == q else s + 1
    W_sq = Fraction(num, den)
    W_float = math.sqrt(num / den)   # double; disclosed: weights use this
    return dp_thr, cap, W_sq, W_float


# ----------------------------------------------------------------------------
# The exact basin partition (quantity.md s4) by reverse BFS from the DP set.
# ----------------------------------------------------------------------------


def build_graph(N, K, K_dp, dp_thr):
    """Returns (f, dp_mask): the step function and the DP predicate."""
    CH = 1 << 22
    f = np.empty(N, dtype=np.int32)
    dp_mask = np.empty(N, dtype=bool)
    K64 = np.uint64(K)
    Kd64 = np.uint64(K_dp)
    N64 = np.uint64(N)
    thr = np.uint64(dp_thr)
    for i in range(0, N, CH):
        j = min(i + CH, N)
        xs = np.arange(i, j, dtype=np.uint64)
        f[i:j] = (mix64_arr(xs ^ K64) % N64).astype(np.int32)
        dp_mask[i:j] = mix64_arr(xs ^ Kd64) < thr
    return f, dp_mask


def exact_partition(N, f, dp_mask, cap):
    """dist/label by reverse BFS from all DPs over the exact reverse graph.

    dist(x) = steps from x to the first DP on x's forward orbit (INF if none);
    label(x) = that DP.  Each x is a preimage of exactly one f(x), so each node
    is gathered exactly once: total work O(N).
    """
    dp_idx = np.flatnonzero(dp_mask)                    # int64, sorted
    counts = np.bincount(f, minlength=N)                # int64
    off = np.zeros(N + 1, dtype=np.int64)
    np.cumsum(counts, out=off[1:])
    order = np.argsort(f, kind='stable')                # int64

    INF = np.iinfo(np.int32).max
    dist = np.full(N, INF, dtype=np.int32)
    label = np.full(N, -1, dtype=np.int32)
    dist[dp_idx] = 0
    label[dp_idx] = dp_idx.astype(np.int32)

    frontier = dp_idx
    level = 0
    while frontier.size:
        ln = counts[frontier]
        tot = int(ln.sum())
        if tot == 0:
            break
        starts = off[frontier]
        cum = np.cumsum(ln)
        base = np.repeat(starts - np.concatenate(([0], cum[:-1])), ln)
        flat = base + np.arange(tot, dtype=np.int64)
        children = order[flat]
        ok = dist[children] == INF
        newc = children[ok]
        dist[newc] = np.int32(level + 1)
        label[newc] = np.repeat(label[frontier], ln)[ok].astype(np.int32)
        frontier = newc
        level += 1

    reach = dist != INF
    cycle_mass = int(N - int(reach.sum()))
    capped_mass = int(((dist > cap) & reach).sum())
    assigned = reach & (dist <= cap)
    lab_asg = label[assigned]
    bfull = np.bincount(lab_asg, minlength=N)           # int64, node-indexed
    b_dps = bfull[dp_idx]                               # basin sizes, DP order
    del bfull, counts, off, order, dist, label, reach, assigned, lab_asg

    n_dps = int(dp_idx.size)
    sum_b = int(b_dps.sum())
    identity = (sum_b + cycle_mass + capped_mass == N)
    min_b = int(b_dps.min()) if n_dps else 0
    bs = np.sort(b_dps)[::-1]
    cum_b = np.cumsum(bs)                               # int64
    return dict(dp_idx=dp_idx, b_dps=b_dps, cum_b=cum_b, n_dps=n_dps,
                cycle_mass=cycle_mass, capped_mass=capped_mass,
                sum_b=sum_b, identity=identity, min_b=min_b,
                n_assigned=int(sum_b))


# ----------------------------------------------------------------------------
# Pool construction (quantity.md s5) and selection (s6).
# ----------------------------------------------------------------------------


def pool_construct(N, f, dp_mask, cap, rT, seed, examine_cap_landing):
    """Uniform random restarts until rT distinct DPs; per quantity.md s3b a
    capped walk charges its cap steps and credits no S_d and no h_d."""
    rng = np.random.default_rng([seed, 1])      # declared convention
    pool_ids = []
    pos = {}
    S = []
    h = []
    capped_walks = 0
    total_steps = 0
    n_walks = 0
    while len(pool_ids) < rT:
        x = int(rng.integers(0, N))
        steps = 0
        hit = -1
        if examine_cap_landing:
            # reading A: the landing point at step == cap IS DP-checked
            while True:
                if dp_mask[x]:
                    hit = x
                    break
                if steps == cap:
                    break
                x = int(f[x])
                steps += 1
        else:
            # reading B: the walk stops after cap steps without examining x_cap
            while True:
                if steps == cap:
                    break
                if dp_mask[x]:
                    hit = x
                    break
                x = int(f[x])
                steps += 1
        n_walks += 1
        if hit >= 0:
            total_steps += steps
            i = pos.get(hit)
            if i is None:
                pos[hit] = len(pool_ids)
                pool_ids.append(hit)
                S.append(steps)
                h.append(1)
            else:
                S[i] += steps
                h[i] += 1
        else:
            capped_walks += 1
            total_steps += cap
    return dict(pool_ids=pool_ids, S=np.array(S, dtype=np.int64),
                h=np.array(h, dtype=np.int64), capped_walks=capped_walks,
                total_steps=total_steps, n_walks=n_walks)


def select_T(pool, T, W_float, seed):
    """Top-T by weight_d = S_d + 4*W*h_d (float: W is irrational, disclosed),
    ties broken by ascending per-entry pseudorandom key in pool-insertion
    order, one bulk array from a fresh RNG seeded deterministically from the
    integer seed (quantity.md s6)."""
    rT = len(pool['pool_ids'])
    w = pool['S'].astype(np.float64) + 4.0 * W_float * pool['h'].astype(np.float64)
    rng_tb = np.random.default_rng([seed, 100])   # declared convention
    keys = rng_tb.random(rT)
    ordidx = np.lexsort((keys, -w))               # weight desc, then key asc
    sel = ordidx[:T]
    Tth_weight = float(w[ordidx[T - 1]])
    n_tied = int((w == Tth_weight).sum())
    return sel, n_tied, Tth_weight, w, keys


# ----------------------------------------------------------------------------
# Null arms (quantity.md s12), all read off the same exact partition.
# ----------------------------------------------------------------------------


def null_arms(N, T, T_sel, part, pool, sel, cov_num, share_top_Tsel_num, seed):
    dp_idx = part['dp_idx']
    b_dps = part['b_dps']
    n_dps = part['n_dps']
    pool_ids = np.array(pool['pool_ids'], dtype=np.int64)
    ppos = np.searchsorted(dp_idx, pool_ids)
    b_pool = b_dps[ppos]

    out = {}

    # NULL-ORACLE-RAND (uniform): T_sel-subset of ALL DPs of the partition.
    rng = np.random.default_rng([seed, 101])
    sub = rng.choice(n_dps, size=T_sel, replace=False)
    cov_u = int(b_dps[sub].sum())
    out['margin_null_oracle_rand_uniform'] = Fraction(cov_u - cov_num, N)

    # NULL-ORACLE-RAND (size-biased): sequential draw WITHOUT replacement with
    # probability proportional to basin size (declared convention; float
    # sampling arithmetic, disclosed).
    rng = np.random.default_rng([seed, 102])
    w = b_dps.astype(np.float64).copy()
    chosen = []
    for _ in range(T_sel):
        cw = np.cumsum(w)
        tot = float(cw[-1])
        u = rng.random() * tot
        idx = int(np.searchsorted(cw, u, side='right'))
        if idx >= n_dps:
            idx = n_dps - 1
        chosen.append(idx)
        w[idx] = 0.0
    cov_sb = int(b_dps[np.array(chosen)].sum())
    out['margin_null_oracle_rand_sizebiased'] = Fraction(cov_sb - cov_num, N)

    # NULL-RANDSEL: uniform T-subset of the r*T pool.
    rng = np.random.default_rng([seed, 103])
    rsel = rng.choice(len(pool_ids), size=T, replace=False)
    cov_rs = int(b_pool[rsel].sum())
    out['margin_null_randsel'] = Fraction(share_top_Tsel_num - cov_rs, N)

    # NULL-SHUF: permute basin sizes across the pool's DPs, weights and keys
    # held fixed; the selected set is unchanged, only the read-off sizes move.
    rng = np.random.default_rng([seed, 104])
    perm = rng.permutation(len(pool_ids))
    out['cov_static_shuf'] = Fraction(int(b_pool[perm][sel].sum()), N)

    return out


# ----------------------------------------------------------------------------
# One cell.
# ----------------------------------------------------------------------------


def compute_cell(N, T, a_num, a_den, seed, examine_cap_landing=True, pre=None):
    t0 = time.perf_counter()
    a = Fraction(a_num, a_den)
    T_sel = T // 2
    r = 2
    rT = r * T
    dp_thr, cap, W_sq, W_float = exact_params(N, T, a_num, a_den)
    K = mix64(GOLDEN + seed)
    K_dp = mix64(K ^ DP_XOR)

    if pre is None:
        f, dp_mask = build_graph(N, K, K_dp, dp_thr)
        part = exact_partition(N, f, dp_mask, cap)
    else:
        # readings A and B share the graph and the exact partition; only the
        # pool-construction cap boundary differs. 'pre' is (f, dp_mask, part)
        # built by the caller with the same (N, K, K_dp, dp_thr, cap).
        f, dp_mask, part = pre

    pool = pool_construct(N, f, dp_mask, cap, rT, seed, examine_cap_landing)
    sel, n_tied, Tth_weight, w, keys = select_T(pool, T, W_float, seed)

    dp_idx = part['dp_idx']
    b_dps = part['b_dps']
    pool_ids = np.array(pool['pool_ids'], dtype=np.int64)
    ppos = np.searchsorted(dp_idx, pool_ids)
    b_pool = b_dps[ppos]
    cov_num = int(b_pool[sel].sum())
    cov_static = Fraction(cov_num, N)

    cum_b = part['cum_b']
    st = {}
    for name, k in (('Tsel', T_sel), ('T', T), ('Tover4', T // 4), ('Tover8', T // 8)):
        st[name] = Fraction(int(cum_b[k - 1]), N)
    margin = st['Tsel'] - cov_static

    # rho_ORACLE: smallest k/T with share_top(k) >= cov_static, k in 1..T.
    # share_top(T) >= cov_static always (any T DPs' coverage <= top-T coverage),
    # so k exists; the search is exact integer arithmetic.
    target = cov_num
    kstar = None
    for k in range(1, T + 1):
        if int(cum_b[k - 1]) >= target:
            kstar = k
            break
    rho = Fraction(kstar, T) if kstar is not None else None

    nulls = null_arms(N, T, T_sel, part, pool, sel, cov_num,
                      int(cum_b[T_sel - 1]), seed)

    res_mass = part['cycle_mass'] + part['capped_mass']
    rec = dict(
        params=dict(N=N, a=f"{a_num}/{a_den}", seed=seed, T=T, T_sel=T_sel,
                    r=r, W_squared=f"{W_sq.numerator}/{W_sq.denominator}",
                    W_float=repr(W_float), cap=cap, dp_threshold=dp_thr,
                    rT=rT),
        partition=dict(n_dps=part['n_dps'], cycle_mass=part['cycle_mass'],
                       capped_mass=part['capped_mass'],
                       n_assigned=part['n_assigned'], sum_b=part['sum_b'],
                       min_basin_size=part['min_b'],
                       residual_fraction=Fraction(res_mass, N),
                       accounting_identity_holds=bool(part['identity'])),
        shares=dict(
            share_top_Tsel=st['Tsel'], share_top_T=st['T'],
            share_top_Tover4=st['Tover4'], share_top_Tover8=st['Tover8']),
        cov_static=cov_static, margin=margin,
        margin_sign=('+' if margin > 0 else '-' if margin < 0 else '0'),
        rho_ORACLE=rho,
        pool=dict(capped_walks=pool['capped_walks'],
                  n_pool_walks=pool['n_walks'],
                  total_precompute_steps=pool['total_steps'],
                  n_tied_at_Tth_weight=n_tied,
                  Tth_weight_float=repr(Tth_weight)),
        nulls=nulls,
        cap_boundary_reading=('A (x_cap examined)' if examine_cap_landing
                              else 'B (x_cap not examined)'),
        wall_time_seconds=None,
    )
    rec['wall_time_seconds'] = round(time.perf_counter() - t0, 3)
    return rec


# ----------------------------------------------------------------------------
# Aggregates (per (N,a) over seeds) and the s11 bootstrap.
# ----------------------------------------------------------------------------


def bootstrap_ci(margins_float, n_bits, a_num, a_den, B=10000):
    sd = 20260907 + 1000 * n_bits + round(10000 * a_num / a_den)
    rng = np.random.default_rng(sd)      # fresh per cell, per quantity.md s11
    n = len(margins_float)
    mf = np.array(margins_float, dtype=np.float64)
    idx = rng.integers(0, n, size=(B, n))
    means = mf[idx].mean(axis=1)
    lo, hi = np.percentile(means, [2.5, 97.5])   # linear interpolation
    return float(lo), float(hi), sd


def aggregate(cells, n_bits, a_num, a_den):
    margins = [c['margin'] for c in cells]
    k25 = sum(1 for m in margins if m >= 0)
    v25 = 'G3-FEASIBLE' if k25 >= 20 else 'G3-INFEASIBLE'
    sub = [c for c in cells if c['params']['seed'] in (1, 2, 3, 4, 5)]
    k5 = sum(1 for c in sub if c['margin'] >= 0)
    v5 = 'G3-FEASIBLE' if k5 >= 4 else 'G3-INFEASIBLE'
    mean_m = sum(margins, Fraction(0)) / len(margins)
    sign = '+' if mean_m > 0 else '-' if mean_m < 0 else '0'
    lo, hi, sd = bootstrap_ci([float(m) for m in margins], n_bits, a_num, a_den)
    out = dict(
        n_seeds=len(cells), k_25=k25, verdict_25=v25, k_5=k5, verdict_5=v5,
        mean_margin=mean_m, mean_margin_sign=sign,
        ci_lo=lo, ci_hi=hi, ci_bootstrap_seed=sd,
        ci_straddles_zero=bool(lo <= 0.0 <= hi),
        bca_variant='not computed (optional context declined)',
        max_residual_fraction=max(c['partition']['residual_fraction']
                                  for c in cells),
        mean_margin_null_oracle_rand_uniform=(
            sum((c['nulls']['margin_null_oracle_rand_uniform']
                 for c in cells), Fraction(0)) / len(cells)),
        mean_margin_null_oracle_rand_sizebiased=(
            sum((c['nulls']['margin_null_oracle_rand_sizebiased']
                 for c in cells), Fraction(0)) / len(cells)),
        mean_margin_null_randsel=(
            sum((c['nulls']['margin_null_randsel'] for c in cells),
                Fraction(0)) / len(cells)),
        mean_cov_static_shuf=(
            sum((c['nulls']['cov_static_shuf'] for c in cells),
                Fraction(0)) / len(cells)),
        n_seeds_margin_null_nonneg_oracle_rand_uniform=sum(
            1 for c in cells if c['nulls']['margin_null_oracle_rand_uniform'] >= 0),
        n_seeds_margin_null_nonneg_oracle_rand_sizebiased=sum(
            1 for c in cells
            if c['nulls']['margin_null_oracle_rand_sizebiased'] >= 0),
        n_seeds_margin_null_nonneg_randsel=sum(
            1 for c in cells if c['nulls']['margin_null_randsel'] >= 0),
    )
    return out


# ----------------------------------------------------------------------------
# Driver.
# ----------------------------------------------------------------------------

FROZEN = [  # order: 2^20 cells first, then 2^24 (prohibitions.md s4)
    (1048576, 1, 8, 1),
    (1048576, 1, 8, 7),
    (1048576, 1, 8, 13),
    (1048576, 1, 16, 5),
    (16777216, 1, 8, 3),
    (16777216, 1, 8, 11),
    (16777216, 1, 8, 25),
    (16777216, 1, 16, 17),
]

CONTROL = [(1048576, 1, 4), (16777216, 1, 4)]  # quantity.md s13: a=1/4 FIRST


def main():
    t_start = time.perf_counter()
    meta = dict(
        task='TASK-20260910-19bd7b', phase='1 (blind re-derivation, frozen)',
        started_utc=datetime.now(timezone.utc).isoformat(),
        python=sys.version, numpy=np.__version__, platform=platform.platform(),
        command=('python3 coordination/goals/GOAL-ECDLP-bbc21f/batches/'
                 'BATCH-12ee85/reviews/TASK-20260910-19bd7b/rederive.py'),
    )
    out = dict(meta=meta)

    # ---- pipeline smoke test (NOT a grid cell; correctness only, discarded
    # ---- as evidence, kept here as a record that it ran).
    t0 = time.perf_counter()
    smoke = compute_cell(1 << 12, 8, 1, 4, 1)
    assert smoke['partition']['accounting_identity_holds']
    assert smoke['partition']['min_basin_size'] >= 1
    meta['smoke_test'] = dict(N=1 << 12, T=8, a='1/4', seed=1,
                              wall_time_seconds=round(time.perf_counter() - t0, 3),
                              note='pipeline check only, not a grid cell')

    # ---- control first (quantity.md s13 / prohibitions.md s4): a = 1/4.
    control = {}
    stop_after_control = False
    for (N, an, ad) in CONTROL:
        cellsA = []
        cellsB = []
        for seed in range(1, 26):
            T = 64 if N == 1 << 20 else 256
            dp_thr, cap, W_sq, W_float = exact_params(N, T, an, ad)
            K = mix64(GOLDEN + seed)
            K_dp = mix64(K ^ DP_XOR)
            f, dp_mask = build_graph(N, K, K_dp, dp_thr)
            part = exact_partition(N, f, dp_mask, cap)
            pre = (f, dp_mask, part)
            cA = compute_cell(N, T, an, ad, seed, True, pre)
            cB = compute_cell(N, T, an, ad, seed, False, pre)
            cellsA.append(cA)
            cellsB.append(cB)
        T = 64 if N == 1 << 20 else 256
        aggA = aggregate(cellsA, 20 if N == 1 << 20 else 24, an, ad)
        control[f"{N}_{an}_{ad}"] = dict(
            cells_reading_A=cellsA, aggregate_reading_A=aggA,
            per_cell_reading_B_differences=[diff_fields(cA, cB)
                                            for cA, cB in zip(cellsA, cellsB)])
        print(f"control N={N} a={an}/{ad}: k_25={aggA['k_25']} "
              f"verdict={aggA['verdict_25']} mean={float(aggA['mean_margin']):.6f}",
              flush=True)
        if aggA['verdict_25'] == 'G3-FEASIBLE':
            stop_after_control = True

    out['control_a_quarter'] = control
    out['control_stop'] = stop_after_control

    # ---- the eight frozen cells.
    frozen = []
    if not stop_after_control:
        for (N, an, ad, seed) in FROZEN:
            T = 64 if N == 1 << 20 else 256
            dp_thr, cap, W_sq, W_float = exact_params(N, T, an, ad)
            K = mix64(GOLDEN + seed)
            K_dp = mix64(K ^ DP_XOR)
            f, dp_mask = build_graph(N, K, K_dp, dp_thr)
            part = exact_partition(N, f, dp_mask, cap)
            pre = (f, dp_mask, part)
            cA = compute_cell(N, T, an, ad, seed, True, pre)
            cB = compute_cell(N, T, an, ad, seed, False, pre)
            cA['reading_B_differences'] = diff_fields(cA, cB)
            frozen.append(cA)
            print(f"cell N={N} a={an}/{ad} seed={seed}: "
                  f"margin={float(cA['margin']):.6f} "
                  f"identity={cA['partition']['accounting_identity_holds']} "
                  f"({cA['wall_time_seconds']}s)", flush=True)
    out['frozen_cells'] = frozen

    out['meta']['finished_utc'] = datetime.now(timezone.utc).isoformat()
    out['meta']['total_wall_time_seconds'] = round(
        time.perf_counter() - t_start, 3)

    import os
    here = os.path.dirname(os.path.abspath(__file__))
    outpath = os.path.join(here, 'results.json')
    with open(outpath, 'w') as fh:
        json.dump(out, fh, indent=1, default=_jser)
    print('wrote', outpath, flush=True)


def _jser(obj):
    if isinstance(obj, Fraction):
        return dict(__fraction__=f"{obj.numerator}/{obj.denominator}",
                    __float__=repr(float(obj)))
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    raise TypeError(repr(obj))


def diff_fields(cA, cB):
    """Names of per-cell fields whose values differ between the two cap
    readings (compared on exact values where exact)."""
    differing = []
    for key in ('cov_static', 'margin', 'rho_ORACLE'):
        if cA[key] != cB[key]:
            differing.append(key)
    if cA['pool']['capped_walks'] != cB['pool']['capped_walks']:
        differing.append('capped_walks')
    if cA['pool']['n_tied_at_Tth_weight'] != cB['pool']['n_tied_at_Tth_weight']:
        differing.append('n_tied_at_Tth_weight')
    for nk in ('margin_null_oracle_rand_uniform',
               'margin_null_oracle_rand_sizebiased',
               'margin_null_randsel', 'cov_static_shuf'):
        if cA['nulls'][nk] != cB['nulls'][nk]:
            differing.append(nk)
    return sorted(set(differing))


if __name__ == '__main__':
    main()
