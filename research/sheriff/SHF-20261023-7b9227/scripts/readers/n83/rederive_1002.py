"""Blind re-derivation of #1002's primary R from raw producer records + protocol text only.
Protocol (statistics.primary): R = sum_pairs E2E(A) / sum_pairs E2E(B); E2E(side) = timing_ms.rank_stage of the
side's rank process + cold_in_process_ms of the side's cold process. Two-stage paired bootstrap, 10000 draws,
random.Random(20261020): points with replacement, then each drawn point's pairs with replacement.
The exact RNG call sequence is not given in the protocol text, so the CI here is an independent implementation.
Controls: A/A (B vs Baa; known-false improvement), swapped labels, rank-only and cold-only components, planted."""
import json, random, sys, math, collections
f = json.load(open(sys.argv[1]))
def sides(role, sideA, sideB):
    # group by (point, pair, side): rank + cold process
    g = collections.defaultdict(dict)
    for x in f:
        if x['role'] != role: continue
        k = (x['point'], x['pair'], x['side'])
        kind = 'rank' if x['arm'].startswith('k') else 'cold'
        assert kind not in g[k]; g[k][kind] = x
    pairs = collections.defaultdict(list)
    keys = sorted({(p, j) for (p, j, s) in g})
    for (p, j) in keys:
        a = g.get((p, j, sideA)); b = g.get((p, j, sideB))
        assert a and b and 'rank' in a and 'cold' in a and 'rank' in b and 'cold' in b, (p, j)
        assert a['rank']['seed'] == b['rank']['seed']
        assert a['rank']['scalar'] == a['cold']['scalar'] == b['rank']['scalar'] == b['cold']['scalar']
        e = lambda s: s['rank']['rank_stage_ms'] + s['cold']['cold_in_process_ms']
        pairs[p].append(dict(EA=e(a), EB=e(b), rA=a['rank']['rank_stage_ms'], rB=b['rank']['rank_stage_ms'],
                             cA=a['cold']['cold_in_process_ms'], cB=b['cold']['cold_in_process_ms'],
                             wA=a['rank']['process_wall_ms'] + a['cold']['process_wall_ms'],
                             wB=b['rank']['process_wall_ms'] + b['cold']['process_wall_ms'],
                             uA=a['rank']['cpu_ms'] + a['cold']['cpu_ms'], uB=b['rank']['cpu_ms'] + b['cold']['cpu_ms'],
                             first=('A' if a['rank']['serial'] < b['rank']['serial'] else 'B')))
    return pairs
def ratio(pairs, ka, kb):
    A = sum(q[ka] for p in pairs for q in pairs[p]); B = sum(q[kb] for p in pairs for q in pairs[p]); return A / B
def boot(pairs, ka, kb, draws=10000, seed=20261020):
    rng = random.Random(seed); pts = sorted(pairs); out = []
    for _ in range(draws):
        A = B = 0.0
        for _p in range(len(pts)):
            p = pts[rng.randrange(len(pts))]; L = pairs[p]
            for _q in range(len(L)):
                q = L[rng.randrange(len(L))]; A += q[ka]; B += q[kb]
        out.append(A / B)
    out.sort(); return out[int(0.025 * draws)], out[int(0.975 * draws) - 1]
def gm(pairs, ka, kb):
    v = [math.log(q[ka] / q[kb]) for p in pairs for q in pairs[p]]; return math.exp(sum(v) / len(v)), len(v)
res = {}
P = sides('primary', 'A', 'B')
n = sum(len(v) for v in P.values())
res['primary_pairs'] = n; res['points'] = len(P)
for name, ka, kb in [('R_e2e', 'EA', 'EB'), ('rank_stage', 'rA', 'rB'), ('cold', 'cA', 'cB'), ('process_wall', 'wA', 'wB'), ('process_cpu', 'uA', 'uB')]:
    res[name] = dict(est=round(ratio(P, ka, kb), 4), ci95=[round(x, 4) for x in boot(P, ka, kb)])
res['R_e2e_geomean'] = round(gm(P, 'EA', 'EB')[0], 4)
res['mean_EA_ms'] = round(sum(q['EA'] for p in P for q in P[p]) / n, 1)
res['mean_EB_ms'] = round(sum(q['EB'] for p in P for q in P[p]) / n, 1)
res['by_order'] = {o: round(sum(q['EA'] for p in P for q in P[p] if q['first'] == o) / sum(q['EB'] for p in P for q in P[p] if q['first'] == o), 4) for o in 'AB'}
res['per_point'] = {p: round(sum(q['EA'] for q in P[p]) / sum(q['EB'] for q in P[p]), 3) for p in sorted(P)}
# proves-too-much 1: A/A (B vs Baa), conclusion 'improvement' known false
AA = sides('aa', 'B', 'Baa')
res['AA_e2e'] = dict(est=round(ratio(AA, 'EA', 'EB'), 4), ci95=[round(x, 4) for x in boot(AA, 'EA', 'EB')], pairs=sum(len(v) for v in AA.values()))
res['AA_cold'] = dict(est=round(ratio(AA, 'cA', 'cB'), 4), ci95=[round(x, 4) for x in boot(AA, 'cA', 'cB')])
# proves-too-much 2: swap the arms within every primary pair (B over A): must give 1/R, not >1
res['swapped_B_over_A'] = round(ratio(P, 'EB', 'EA'), 4)
# proves-too-much 3: random within-pair label flips (null of no arm effect cannot hold here; report spread)
rng = random.Random(1); flips = []
for _ in range(2000):
    A = B = 0.0
    for p in P:
        for q in P[p]:
            if rng.random() < 0.5: A += q['EA']; B += q['EB']
            else: A += q['EB']; B += q['EA']
    flips.append(A / B)
flips.sort(); res['label_flip_null_2.5_97.5'] = [round(flips[50], 3), round(flips[1949], 3)]
json.dump(res, sys.stdout, indent=1); print()
