"""J3 (iii) strongest form: in-process re-execution of the executor's curve cell (seed 1, U = 8T, basins
skipped) with the producer's UNMODIFIED modules imported from the snapshot source tree, plus an
in-process hook that registers every Pool the arm engine creates.  After each arm: (1) every pool
entry's stored logarithm L must satisfy key([L]G) == entry key, checked with MY OWN double-and-add;
(2) every table of every round is a subset of the pool (so no table entry lacks a known log);
(3) the per-round table hashes and k_found equal the ones recorded in RUN-ECDLP-612fb1-34/raw-result.json
(reproduction check).  Review control; writes only into the red-team task directory."""
import sys, json, time, hashlib
import numpy as np
SRC = '/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-612fb1/source'
sys.path.insert(0, SRC)
import instrument as I, curve as C, verify_certificate as V
TD = '/home/user/crypto-autoresearcher/coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-289698/tasks/TASK-20260906-90e7cf'
REC = '/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-612fb1/runs/RUN-ECDLP-612fb1-033/curve_record.json'
RAW = json.load(open('/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-612fb1/runs/RUN-ECDLP-612fb1-34/raw-result.json'))
pools_seen = []
_orig_init = I.Pool.__init__
def _hook(self, *a, **k):
    _orig_init(self, *a, **k); pools_seen.append(self)
I.Pool.__init__ = _hook

def inv(a, p): return pow(a % p, p - 2, p)
def add(P1, P2, p, a):
    if P1 is None: return P2
    if P2 is None: return P1
    x1, y1 = P1; x2, y2 = P2
    if x1 == x2:
        if (y1 + y2) % p == 0: return None
        lam = (3 * x1 * x1 + a) * inv(2 * y1, p) % p
    else: lam = (y2 - y1) * inv(x2 - x1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)
def mul(k, P, p, a):
    R = None; Q = P
    while k:
        if k & 1: R = add(R, Q, p, a)
        Q = add(Q, Q, p, a); k >>= 1
    return R
def mykey(pt, p): return 2 * pt[0] + (1 if pt[1] > p // 2 else 0)

t0 = time.time()
rec = json.load(open(REC)); E = C.Curve(p=rec['p'], a=rec['a'], b=rec['b'], N=rec['N'], G=tuple(rec['P']))
P = I.Params(n_bits=24, a=0.25, seed=1, N_override=E.N); P.U_max = 8 * P.T
walk = C.CurveWalk(E, P)
# --- precomputation pool exactly as run_curve.py (r = 2, logs known)
rng_pre = np.random.default_rng(P.seed)
dps, S, h, logs = [], [], [], []; index = {}; walks = P_cost = capped = 0; batch = 512
while len(dps) < 2 * P.T:
    rs = rng_pre.integers(1, E.N, size=batch, dtype=np.int64)
    pts = [E.mul(int(r), E.G) for r in rs]
    x0 = np.asarray([q[0] for q in pts], dtype=np.int64); y0 = np.asarray([q[1] for q in pts], dtype=np.int64)
    term, length, sc, ih = walk.walk(x0, y0, rs)
    for i in range(batch):
        walks += 1; t = int(term[i]); L = int(length[i]); P_cost += L
        if t < 0: capped += 1
        else:
            j = index.get(t)
            if j is None: index[t] = len(dps); dps.append(t); S.append(float(L)); h.append(1); logs.append(int(sc[i]))
            else:
                S[j] += L; h[j] += 1
                assert logs[j] == int(sc[i])
        if len(dps) == 2 * P.T: break
pools = {2 * P.T: I.PoolSnapshot(r=2, dps=dps, S=S, h=h, walks=walks, P_cost=P_cost, capped_walks=capped, logs=logs)}
# independent check of the precomputation logs
bad_pre = sum(1 for d, L in zip(dps, logs) if mykey(mul(L, E.G, E.p, E.a), E.p) != d)
print(f'precomputation pool: {len(dps)} entries, walks {walks}, P {P_cost}; entries whose log fails key([L]G)==dp: {bad_pre}', flush=True)
# --- targets exactly as run_curve.py
rng_t = np.random.default_rng(P.seed_targets); U = P.U_max
secret_x = rng_t.integers(1, E.N, size=U, dtype=np.int64)
c = rng_t.integers(0, E.N, size=(U, P.k), dtype=np.int64)
Q = [E.mul(int(x), E.G) for x in secret_x]
sx = np.empty((U, P.k), dtype=np.int64); sy = np.empty((U, P.k), dtype=np.int64)
for u in range(U):
    for j in range(P.k):
        S0 = E.add(Q[u], E.mul(int(c[u, j]), E.G)); S0 = S0 if S0 is not None else (-1, -1)
        sx[u, j], sy[u, j] = S0
term, length, sc, ih = walk.walk(sx.reshape(-1), sy.reshape(-1), c.reshape(-1))
term = term.reshape(U, P.k); length = length.reshape(U, P.k); ws = sc.reshape(U, P.k)
print(f'targets and walks ready ({time.time() - t0:.1f}s)', flush=True)
T = P.T
arms = [I.ArmConfig(name='STATIC(T)', mode='static', t_sel=T), I.ArmConfig(name='RESEL-L(T)', mode='resel_lower', t_sel=T, twin='STATIC(T)'),
        I.ArmConfig(name='RESEL-L(T/2)', mode='resel_lower', t_sel=T // 2, twin='STATIC(T/2)'), I.ArmConfig(name='NULL-A(T/2)', mode='null_a', t_sel=T // 2, twin='STATIC(T/2)')]
out = {'curve_id': rec['curve_id'], 'precomp_entries': len(dps), 'precomp_bad_logs': bad_pre, 'arms': {}}
for cfg in arms:
    n0 = len(pools_seen)
    res = I.run_arm(P, cfg, pools, term, length, None, None, None, walk_scalar=ws, group_order=E.N)
    pool = pools_seen[-1]; assert len(pools_seen) == n0 + 1
    # (1) every pool entry's log verifies under my own arithmetic
    none_logs = sum(1 for L in pool.logs if L is None)
    bad = [d for d, L in zip(pool.dps, pool.logs) if L is None or mykey(mul(int(L), E.G, E.p, E.a), E.p) != d]
    # (2) every round's table is a subset of the pool
    pool_set = set(pool.dps)
    tables_subset = all(set(tb.tolist()) <= pool_set for tb in res.table_at_round)
    # (3) reproduction against the committed run: table hashes and k_found
    rec_hash = [r['table_hash'] for r in RAW['arms'][cfg.name]['rounds']]
    my_hash = [I.table_hash(tb) for tb in res.table_at_round]
    kf_ok = (res.k_found.tolist() == RAW['arms'][cfg.name]['k_found'])
    solved_ok = (res.solved.astype(int).tolist() == RAW['arms'][cfg.name]['solved'])
    # (4) LOWER-bracket admission: pool growth == entries from solved targets only (count new entries vs DPs of solved targets' used walks)
    new_entries = len(pool.dps) - len(dps)
    solved_walk_dps = set()
    for u in np.flatnonzero(res.solved):
        for j in range(int(res.used[u])):
            if term[u, j] >= 0: solved_walk_dps.add(int(term[u, j]))
    unsolved_walk_dps = set()
    for u in np.flatnonzero(~res.solved):
        for j in range(int(res.used[u])):
            if term[u, j] >= 0: unsolved_walk_dps.add(int(term[u, j]))
    new_set = set(pool.dps[len(dps):])
    leak = new_set - solved_walk_dps          # new entries not explained by a solved target's walk
    from_unsolved_only = new_set & (unsolved_walk_dps - solved_walk_dps)
    out['arms'][cfg.name] = {'pool_entries_final': len(pool.dps), 'new_entries': new_entries, 'entries_with_None_log': none_logs,
                             'entries_failing_key([L]G)==dp': len(bad), 'all_round_tables_subset_of_pool': tables_subset,
                             'n_rounds': len(res.table_at_round), 'table_hashes_match_committed_run': my_hash == rec_hash,
                             'k_found_matches_committed_run': kf_ok, 'solved_matches_committed_run': solved_ok,
                             'new_entries_not_from_a_solved_targets_walk': len(leak), 'new_entries_only_reachable_from_unsolved_walks': len(from_unsolved_only),
                             'solved': int(res.solved.sum())}
    print(cfg.name, json.dumps(out['arms'][cfg.name]), f'({time.time() - t0:.1f}s)', flush=True)
out['elapsed_s'] = time.time() - t0
json.dump(out, open(f'{TD}/results/j3_curve_pool_hook_seed1.json', 'w'), indent=1)
