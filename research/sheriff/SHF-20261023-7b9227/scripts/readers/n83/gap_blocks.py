"""Gap to rT770 for the block designs (#985, #997): E2E(k,c)/mean rho cold; CI by resampling points (rank blocks resampled too)."""
import json, sys, random
f = json.load(open(sys.argv[1])); runs = {json.loads(l)['serial']: json.loads(l) for l in open(sys.argv[2])}
k, c = sys.argv[3].split('+')
rk = [x['rank_stage_ms'] for x in f if x['arm'] == k]
cold = {x['point']: float(runs[x['serial']]['fields']['setup_ms']) + float(runs[x['serial']]['fields']['online_ms']) for x in f if x['arm'] == c and x['point'] != 'q0'}
rho = {x['point']: float(runs[x['serial']]['fields']['setup_ms']) + float(runs[x['serial']]['fields']['online_ms']) for x in f if x['arm'] == 'rT'}
pts = sorted(set(cold) & set(rho))
def g(ps, rs): return (sum(rs) / len(rs) + sum(cold[p] for p in ps) / len(ps)) / (sum(rho[p] for p in ps) / len(ps))
rng = random.Random(3); B = sorted(g([pts[rng.randrange(len(pts))] for _ in pts], [rk[rng.randrange(len(rk))] for _ in rk]) for _ in range(10000))
print(json.dumps(dict(arm=sys.argv[3], points=len(pts), gap=round(g(pts, rk), 4), ci95=[round(B[250], 3), round(B[9749], 3)])))
