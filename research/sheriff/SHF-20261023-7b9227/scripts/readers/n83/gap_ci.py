"""Gap to matched rho (rT770) with a point-level bootstrap CI, plus S, from the raw wrapper rows.
The n=83 row reports the gap as a point estimate only (ci95 null). rho runs once per point, so its
variance (geometric-like step count) dominates the gap's uncertainty."""
import json, random, sys, collections
runs = [json.loads(l) for l in open(sys.argv[1])]; flat = json.load(open(sys.argv[2])); sideB = sys.argv[3]
sqrt_r = 92573139.235
rho = {r['point_id']: r for r in runs if r['arm'] == 'rT'}
steps = {p: int(r['fields']['ops']) for p, r in rho.items()}
on = {p: float(r['fields']['online_ms']) for p, r in rho.items()}
cold = {p: float(r['fields']['online_ms']) + float(r['fields']['setup_ms']) for p, r in rho.items()}
ms_per_step = sum(on.values()) / sum(steps.values())
icB = collections.defaultdict(list); icO = collections.defaultdict(list)
g = collections.defaultdict(dict)
for x in flat:
    if x['role'] == 'primary' and x['side'] == sideB:
        g[(x['point'], x['pair'])]['rank' if x['arm'].startswith('k') else 'cold'] = x
for (p, j), s in g.items():
    icB[p].append(s['rank']['rank_stage_ms'] + s['cold']['cold_in_process_ms']); icO[p].append(s['cold']['online_ms'])
pts = sorted(rho)
def gap(sample):
    A = sum(sum(icB[p]) / len(icB[p]) for p in sample) / len(sample); B = sum(cold[p] for p in sample) / len(sample); return A / B
def gapo(sample):
    A = sum(sum(icO[p]) / len(icO[p]) for p in sample) / len(sample); B = sum(on[p] for p in sample) / len(sample); return A / B
rng = random.Random(7); G = []; GO = []
for _ in range(10000):
    s = [pts[rng.randrange(len(pts))] for _ in pts]; G.append(gap(s)); GO.append(gapo(s))
G.sort(); GO.sort()
unit = ms_per_step * sqrt_r
mIC = sum(v for p in pts for v in icB[p]) / sum(len(icB[p]) for p in pts)
out = dict(rho_points=len(pts), rho_ms_per_step=ms_per_step, unit_ms=round(unit, 1),
           rho_mean_steps_over_sqrt_r=round(sum(steps.values()) / len(steps) / sqrt_r, 5),
           rho_steps_cv=round((sum((v - sum(steps.values()) / len(steps)) ** 2 for v in steps.values()) / (len(steps) - 1)) ** 0.5 / (sum(steps.values()) / len(steps)), 3),
           theory_frob_neg_rho_steps_over_sqrt_r=round((3.141592653589793 / (2 * 166)) ** 0.5, 5),
           rho_cold_mean_ms=round(sum(cold.values()) / len(cold), 1), rho_online_mean_ms=round(sum(on.values()) / len(on), 1),
           S_ic_cold=round(mIC / unit, 4), S_rho_cold=round(sum(cold.values()) / len(cold) / unit, 4),
           gap_cold=dict(est=round(gap(pts), 4), ci95=[round(G[250], 3), round(G[9749], 3)]),
           gap_online=dict(est=round(gapo(pts), 4), ci95=[round(GO[250], 4), round(GO[9749], 4)]))
json.dump(out, sys.stdout, indent=1); print()
