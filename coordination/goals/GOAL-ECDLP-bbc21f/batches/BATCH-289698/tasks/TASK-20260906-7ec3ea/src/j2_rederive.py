#!/usr/bin/env python3
"""BLIND re-derivation for TASK-20260906-7ec3ea joint J2, written from the
statements in ledger/handoffs/TASK-20260906-7ec3ea.yaml only (no producer code read).

(a) exact global oracle top-T basin share at N=2^20, a=1/4 (T=64, W=64, cap 8W=512)
    by full enumeration of the functional graph of f(x)=mix64(x^K) mod N, DP predicate
    hash64(x) < floor(2^64/W) with an independent key.  Basin of DP d = {x : forward orbit
    reaches d before any other DP within cap}; DP d belongs to its own basin (distance 0);
    cycle mass and capped mass excluded from every basin and reported.
(b) Bernstein-Lange fixture: pool of 2T DISTINCT DPs from uniform-start walks capped at 8W,
    generation continuing until 2T distinct DPs, every walk charged to P (capped walks at the
    cap) and each walk's (length,+1) credited to its DP; weight S_d + 4 W h_d; table = top-T
    (ties by seeded permutation); M single-walk uniform-start trials, cap 8W;
    scaled cost = total steps / hits / sqrt(N/T); scaled P = P / sqrt(N T).
Own instrument: primary mixer murmur3 fmix64 (NOT the splitmix64 example), own keys from
sha256; sensitivity variants: splitmix64 mixer, fixed-2T-walk pool, duplicate-discard pool,
capped walks not charged, start-is-DP requiring one step, cap 20W / uncapped for basins.
"""
import numpy as np, hashlib, json, time, sys, math, os

U64 = np.uint64
def key(s):
    return U64(int.from_bytes(hashlib.sha256(s.encode()).digest()[:8], 'big'))

def fmix64(h):
    h = h.astype(U64, copy=True)
    h ^= h >> U64(33); h *= U64(0xff51afd7ed558ccd)
    h ^= h >> U64(33); h *= U64(0xc4ceb9fe1a85ec53)
    h ^= h >> U64(33)
    return h
def splitmix64(z):
    z = z.astype(U64, copy=True)
    z = (z ^ (z >> U64(30))) * U64(0xbf58476d1ce4e5b9)
    z = (z ^ (z >> U64(27))) * U64(0x94d049bb133111eb)
    return z ^ (z >> U64(31))
MIX = {'murmur3_fmix64': fmix64, 'splitmix64': splitmix64}

def build(N, W, mixname, kwalk, kdp):
    mix = MIX[mixname]
    x = np.arange(N, dtype=U64)
    f = (mix(x ^ kwalk) & U64(N - 1)).astype(np.int64)
    thr = U64((1 << 64) // W)
    isdp = mix(x ^ kdp) < thr
    return f, isdp

def enumerate_basins(N, f, isdp, cap):
    """pointer jumping; returns dict of results and arrays (target, d, in_basin)."""
    x = np.arange(N, dtype=np.int64)
    target = np.where(isdp, x, f).astype(np.int64)
    d = np.where(isdp, 0, 1).astype(np.int64)
    resolved = isdp[target]
    rounds = 0
    for k in range(22):
        idx = np.nonzero(~resolved)[0]
        if idx.size == 0: break
        t = target[idx]
        d[idx] = d[idx] + d[t]          # RHS fully evaluated before assignment (Jacobi)
        target[idx] = target[t]
        resolved = isdp[target]
        rounds += 1
    # cyclic points = image of f^(2^k) for 2^k >= N
    g = f.copy()
    for _ in range(int(math.ceil(math.log2(N)))): g = g[g]
    cyclic = np.zeros(N, bool); cyclic[g] = True
    never = ~resolved                              # never reaches a DP (DP-free cycle or tail into one)
    out = {}
    out['n_dp'] = int(isdp.sum())
    out['cyclic_points_total'] = int(cyclic.sum())
    out['cycle_mass_dpfree_cycle_points'] = int((cyclic & never).sum())
    out['tail_into_dpfree_cycle_points'] = int((~cyclic & never).sum())
    res = {}
    for capname, capv in [('cap8W', cap), ('cap20W', (cap * 20) // 8), ('uncapped', None)]:
        inb = resolved.copy() if capv is None else (resolved & (d <= capv))
        sizes = np.bincount(target[inb], minlength=N)[isdp]
        srt = np.sort(sizes)[::-1]
        r = {'capped_mass_points': int(N - inb.sum()),
             'capped_mass_excluding_never': int(N - inb.sum() - never.sum()),
             'basin_mass_points': int(inb.sum()),
             'dp_with_basin_size_1': int((sizes == 1).sum()),
             'dp_with_basin_size_0': int((sizes == 0).sum()),
             'largest_basin': int(srt[0]),
             'top_k_share_over_N': {str(k): float(srt[:k].sum() / N) for k in (16, 32, 48, 64, 96, 128, 256, 512)},
             'top_k_share_over_basin_mass': {str(k): float(srt[:k].sum() / inb.sum()) for k in (16, 32, 48, 64, 96, 128, 256, 512)},
             'top_1000_sizes': [int(v) for v in srt[:1000]]}
        res[capname] = r
    out['by_cap'] = res
    return out, target, d, resolved

def walk_batch(starts, f, isdp, cap, min_one_step=False):
    x = starts.astype(np.int64).copy(); n = x.size
    length = np.zeros(n, np.int64); term = np.full(n, -1, np.int64)
    active = np.ones(n, bool)
    if not min_one_step:
        dp0 = isdp[x]
        term[dp0] = x[dp0]; active[dp0] = False
    for step in range(1, cap + 1):
        ia = np.nonzero(active)[0]
        if ia.size == 0: break
        xi = f[x[ia]]; x[ia] = xi
        dp = isdp[xi]
        hit = ia[dp]
        term[hit] = xi[dp]; length[hit] = step; active[hit] = False
    ia = np.nonzero(active)[0]
    length[ia] = cap; term[ia] = -1
    return length, term

def fixture(N, T, W, f, isdp, cap, M, rng_pool, rng_trial, tie_seed, mode='distinct', charge_capped=True, min_one_step=False, exact=None):
    """mode: 'distinct' (paper: continue until 2T distinct DPs, every walk charged/credited);
             'fixed2T' (exactly 2T walks, table from whatever distinct DPs);
             'discard_dup' (continue until 2T distinct; duplicate-DP walks neither charged nor credited)."""
    rT = 2 * T
    S = {}; H = {}; P = 0; nwalks = 0; ncapped = 0; ndup = 0
    done = False
    while not done:
        starts = rng_pool.integers(0, N, size=64)
        L, D = walk_batch(starts, f, isdp, cap, min_one_step)
        for l, dd in zip(L.tolist(), D.tolist()):
            if mode == 'fixed2T' and nwalks >= rT: done = True; break
            nwalks += 1
            if dd < 0:
                ncapped += 1
                if charge_capped: P += cap
                continue
            if dd in S:
                ndup += 1
                if mode == 'discard_dup':
                    nwalks -= 1; continue
                P += l; S[dd] += l; H[dd] += 1
            else:
                P += l; S[dd] = l; H[dd] = 1
            if mode != 'fixed2T' and len(S) >= rT: done = True; break
    dps = np.array(sorted(S), dtype=np.int64)
    w = np.array([S[d] + 4 * W * H[d] for d in dps.tolist()], dtype=np.int64)
    perm = np.random.default_rng(tie_seed).permutation(dps.size)
    order = np.lexsort((perm, -w))
    table = dps[order[:T]]
    tset = np.zeros(N, bool); tset[table] = True
    starts = rng_trial.integers(0, N, size=M)
    L, D = walk_batch(starts, f, isdp, cap, min_one_step)
    hits = int(((D >= 0) & tset[np.maximum(D, 0)]).sum())
    tot = int(L.sum())
    out = {'pool_walks': nwalks, 'pool_distinct_dps': int(len(S)), 'pool_capped_walks': ncapped, 'pool_duplicate_walks': ndup,
           'P': int(P), 'scaled_P': P / math.sqrt(N * T), 'M': M, 'hits': hits, 'trial_total_steps': tot,
           'trial_capped_walks': int((D < 0).sum()), 'mean_trial_length': tot / M,
           'hit_rate': hits / M, 'scaled_cost': (tot / hits / math.sqrt(N / T)) if hits else None,
           'table_size': int(table.size), 'table_id_hash': hashlib.sha256(np.sort(table).tobytes()).hexdigest()[:16]}
    if exact is not None:
        target, dd, resolved = exact
        inb = resolved & (dd <= cap)
        sizes = np.bincount(target[inb], minlength=N)
        out['exact_coverage_table'] = float(sizes[table].sum() / N)
        pool_sizes = sizes[dps]
        out['exact_coverage_whole_pool_2T'] = float(pool_sizes.sum() / N)
        out['exact_coverage_pool_oracle_topT'] = float(np.sort(pool_sizes)[::-1][:T].sum() / N)
    return out

def main():
    cells = [dict(N=1 << 20, T=64, W=64), dict(N=1 << 24, T=256, W=128)]
    if len(sys.argv) > 1 and sys.argv[1] == 'quick': cells = cells[:1]
    nkeys_primary = 8; nkeys_sens = 5; M = 40000
    results = {'instrument': 'own implementation; mixer class mix64(x XOR K) mod N; DP hash64(x) < floor(2^64/W) with independent key; keys sha256-derived', 'cells': []}
    t0 = time.time()
    for c in cells:
        N, T, W = c['N'], c['T'], c['W']; cap = 8 * W
        cell = dict(N=N, log2N=int(math.log2(N)), T=T, W=W, a=T * W * W / N, theta=1 / W, cap=cap, M=M, keys=[])
        for mixname, nk in [('murmur3_fmix64', nkeys_primary), ('splitmix64', nkeys_sens)]:
            for i in range(1, nk + 1):
                tk = time.time()
                kw = key(f'validator-7ec3ea|{mixname}|walk|N{N}|{i}'); kd = key(f'validator-7ec3ea|{mixname}|dp|N{N}|{i}')
                f, isdp = build(N, W, mixname, kw, kd)
                rec = dict(mixer=mixname, key_index=i, walk_key_hex=f'{int(kw):016x}', dp_key_hex=f'{int(kd):016x}')
                if N <= (1 << 24):
                    b, target, d, resolved = enumerate_basins(N, f, isdp, cap)
                    rec['basins'] = b
                    ex = (target, d, resolved)
                else:
                    ex = None
                fx = {}
                base = dict(N=N, T=T, W=W, f=f, isdp=isdp, cap=cap, M=M, tie_seed=7000 + i, exact=ex)
                seeds = lambda tag: (np.random.default_rng(int(key(f'pool|{mixname}|{N}|{i}|{tag}')) % (1 << 63)), np.random.default_rng(int(key(f'trial|{mixname}|{N}|{i}|{tag}')) % (1 << 63)))
                rp, rt = seeds('p'); fx['primary_distinct_charged'] = fixture(rng_pool=rp, rng_trial=rt, **base)
                if mixname == 'murmur3_fmix64':
                    rp, rt = seeds('p'); fx['var_fixed2T_walks'] = fixture(rng_pool=rp, rng_trial=rt, mode='fixed2T', **base)
                    rp, rt = seeds('p'); fx['var_discard_duplicates'] = fixture(rng_pool=rp, rng_trial=rt, mode='discard_dup', **base)
                    rp, rt = seeds('p'); fx['var_capped_not_charged'] = fixture(rng_pool=rp, rng_trial=rt, charge_capped=False, **base)
                    rp, rt = seeds('p'); fx['var_min_one_step'] = fixture(rng_pool=rp, rng_trial=rt, min_one_step=True, **base)
                rec['fixture'] = fx
                rec['seconds'] = round(time.time() - tk, 2)
                cell['keys'].append(rec)
                print(f"N=2^{cell['log2N']} {mixname} key{i}: topT/N={rec.get('basins',{}).get('by_cap',{}).get('cap8W',{}).get('top_k_share_over_N',{}).get(str(T))} "
                      f"cost={fx['primary_distinct_charged']['scaled_cost']:.4f} scaledP={fx['primary_distinct_charged']['scaled_P']:.4f} "
                      f"hit={fx['primary_distinct_charged']['hit_rate']:.4f} P={fx['primary_distinct_charged']['P']} walks={fx['primary_distinct_charged']['pool_walks']} ({rec['seconds']}s)", flush=True)
        # aggregates
        def agg(sel, label):
            vals = [sel(k) for k in cell['keys'] if sel(k) is not None]
            if not vals: return None
            v = np.array(vals, float)
            return {'label': label, 'n': int(v.size), 'mean': float(v.mean()), 'std': float(v.std(ddof=1)) if v.size > 1 else None, 'min': float(v.min()), 'max': float(v.max()), 'values': [float(x) for x in v]}
        A = {}
        for mixname in ('murmur3_fmix64', 'splitmix64'):
            pk = lambda k: k if k['mixer'] == mixname else None
            A[mixname] = {
                'topT_share_over_N_cap8W': agg(lambda k: k['basins']['by_cap']['cap8W']['top_k_share_over_N'][str(T)] if (pk(k) and 'basins' in k) else None, 'exact global top-T share, cap 8W, over N'),
                'topT_share_over_N_cap20W': agg(lambda k: k['basins']['by_cap']['cap20W']['top_k_share_over_N'][str(T)] if (pk(k) and 'basins' in k) else None, 'cap 20W'),
                'topT_share_over_N_uncapped': agg(lambda k: k['basins']['by_cap']['uncapped']['top_k_share_over_N'][str(T)] if (pk(k) and 'basins' in k) else None, 'uncapped'),
                'topT_share_over_basin_mass_cap8W': agg(lambda k: k['basins']['by_cap']['cap8W']['top_k_share_over_basin_mass'][str(T)] if (pk(k) and 'basins' in k) else None, 'over non-capped mass'),
                'topT2_share_over_N_cap8W': agg(lambda k: k['basins']['by_cap']['cap8W']['top_k_share_over_N'][str(T // 2)] if (pk(k) and 'basins' in k) else None, 'exact global top-T/2 share'),
                'capped_mass_fraction_cap8W': agg(lambda k: k['basins']['by_cap']['cap8W']['capped_mass_points'] / N if (pk(k) and 'basins' in k) else None, 'capped mass fraction'),
                'cycle_mass_fraction': agg(lambda k: k['basins']['cycle_mass_dpfree_cycle_points'] / N if (pk(k) and 'basins' in k) else None, 'DP-free cycle mass fraction'),
                'fixture_scaled_cost_per_key': agg(lambda k: k['fixture']['primary_distinct_charged']['scaled_cost'] if pk(k) else None, 'scaled cost per key'),
                'fixture_scaled_P_per_key': agg(lambda k: k['fixture']['primary_distinct_charged']['scaled_P'] if pk(k) else None, 'scaled P per key'),
                'fixture_hit_rate_per_key': agg(lambda k: k['fixture']['primary_distinct_charged']['hit_rate'] if pk(k) else None, 'single-walk hit rate of STATIC(T)'),
                'fixture_exact_coverage_per_key': agg(lambda k: k['fixture']['primary_distinct_charged'].get('exact_coverage_table') if pk(k) else None, 'exact coverage of STATIC(T)'),
                'pool_walks_per_key': agg(lambda k: k['fixture']['primary_distinct_charged']['pool_walks'] if pk(k) else None, 'generation walks to 2T distinct'),
            }
            ks = [k for k in cell['keys'] if k['mixer'] == mixname]
            tot = sum(k['fixture']['primary_distinct_charged']['trial_total_steps'] for k in ks); hits = sum(k['fixture']['primary_distinct_charged']['hits'] for k in ks)
            A[mixname]['fixture_scaled_cost_pooled'] = tot / hits / math.sqrt(N / T)
            A[mixname]['fixture_scaled_P_pooled_mean'] = float(np.mean([k['fixture']['primary_distinct_charged']['scaled_P'] for k in ks]))
            for var in ('var_fixed2T_walks', 'var_discard_duplicates', 'var_capped_not_charged', 'var_min_one_step'):
                vs = [k for k in ks if var in k['fixture']]
                if vs:
                    tot = sum(k['fixture'][var]['trial_total_steps'] for k in vs); hits = sum(k['fixture'][var]['hits'] for k in vs)
                    A[mixname][var] = {'scaled_cost_pooled': tot / hits / math.sqrt(N / T), 'scaled_P_mean': float(np.mean([k['fixture'][var]['scaled_P'] for k in vs])), 'pool_walks_mean': float(np.mean([k['fixture'][var]['pool_walks'] for k in vs])), 'pool_distinct_mean': float(np.mean([k['fixture'][var]['pool_distinct_dps'] for k in vs]))}
        cell['aggregates'] = A
        results['cells'].append(cell)
        print(f"cell N=2^{cell['log2N']} done; elapsed {time.time()-t0:.1f}s", flush=True)
    results['elapsed_seconds'] = round(time.time() - t0, 1)
    import resource; results['peak_rss_kb_ru_maxrss'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print('peak_rss_kb', results['peak_rss_kb_ru_maxrss'])
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs', 'j2_rederive_output.json')
    json.dump(results, open(out, 'w'), indent=1)
    print('wrote', out)

if __name__ == '__main__':
    main()
