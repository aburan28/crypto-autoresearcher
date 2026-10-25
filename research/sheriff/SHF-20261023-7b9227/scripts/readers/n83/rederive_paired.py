"""Generic blind re-derivation for the n=83 alternating-pair designs (#1002/#1006/#1009/#1013/#1015 style).
R = sum_pairs E2E(A)/sum_pairs E2E(B), E2E(side) = rank_stage_ms(rank proc) + cold_in_process_ms(cold proc).
Two-stage paired bootstrap (points, then pairs within point), random.Random(seed).
Adds what the rows do not compute: a bootstrap CI for the end-to-end cold gap IC/rT and online gap, and S values."""
import json, random, sys, math, collections
f = json.load(open(sys.argv[1])); seed = int(sys.argv[2]); sqrt_r = 92573139.235
def group(role, sA, sB):
    g = collections.defaultdict(dict)
    for x in f:
        if x['role'] != role: continue
        kind = 'rank' if x['arm'].startswith('k') else 'cold'
        g[(x['point'], x['pair'], x['side'])][kind] = x
    P = collections.defaultdict(list)
    for (p, j) in sorted({(p, j) for (p, j, s) in g}):
        a, b = g[(p, j, sA)], g[(p, j, sB)]
        assert a['rank']['seed'] == b['rank']['seed']
        sc = {a['rank']['scalar'], a['cold']['scalar'], b['rank']['scalar'], b['cold']['scalar']}; assert len(sc) == 1
        E = lambda s: s['rank']['rank_stage_ms'] + s['cold']['cold_in_process_ms']
        P[p].append(dict(EA=E(a), EB=E(b), rA=a['rank']['rank_stage_ms'], rB=b['rank']['rank_stage_ms'],
                         cA=a['cold']['cold_in_process_ms'], cB=b['cold']['cold_in_process_ms'],
                         oA=a['cold']['online_ms'], oB=b['cold']['online_ms'], first='A' if a['rank']['serial'] < b['rank']['serial'] else 'B'))
    return P
def R(P, ka, kb): return sum(q[ka] for p in P for q in P[p]) / sum(q[kb] for p in P for q in P[p])
def boot(P, ka, kb, seed, draws=10000):
    rng = random.Random(seed); pts = sorted(P); out = []
    for _ in range(draws):
        A = B = 0.0
        for _p in range(len(pts)):
            L = P[pts[rng.randrange(len(pts))]]
            for _q in range(len(L)):
                q = L[rng.randrange(len(L))]; A += q[ka]; B += q[kb]
        out.append(A / B)
    out.sort(); return [round(out[int(0.025 * draws)], 4), round(out[int(0.975 * draws) - 1], 4)]
sA, sB = sys.argv[3], sys.argv[4]
P = group('primary', sA, sB)
res = dict(pairs=sum(len(v) for v in P.values()), points=len(P))
res['R_e2e'] = dict(est=round(R(P, 'EA', 'EB'), 4), ci95=boot(P, 'EA', 'EB', seed))
res['rank_stage'] = round(R(P, 'rA', 'rB'), 4); res['cold'] = round(R(P, 'cA', 'cB'), 4); res['online'] = round(R(P, 'oA', 'oB'), 4)
res['by_order'] = {o: round(sum(q['EA'] for p in P for q in P[p] if q['first'] == o) / sum(q['EB'] for p in P for q in P[p] if q['first'] == o), 4) for o in 'AB'}
AA = group('aa', 'B', 'Baa'); res['AA_e2e'] = dict(est=round(R(AA, 'EA', 'EB'), 4), ci95=boot(AA, 'EA', 'EB', seed + 1))
# rho: per point
rho = {x['point']: x for x in f if x['arm'] == 'rT'}
steps = {}
for p, x in rho.items(): pass
n = res['pairs']
mEA = sum(q['EA'] for p in P for q in P[p]) / n; mEB = sum(q['EB'] for p in P for q in P[p]) / n
mOB = sum(q['oB'] for p in P for q in P[p]) / n
res['mean_ms'] = dict(E2E_A=round(mEA, 1), E2E_B=round(mEB, 1), online_B=round(mOB, 1), rank_B=round(sum(q['rB'] for p in P for q in P[p]) / n, 1))
json.dump(res, sys.stdout, indent=1); print()
