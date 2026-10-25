"""Point estimates for the block designs (#985 closure, #997 closure+index-lift):
E2E(k, c) = mean rank_stage_ms over rank arm k's processes + mean cold over cold arm c's 20 panel points (Q0 excluded).
cold = setup_ms + online_ms (wrapper fields) and, as a check, cold_in_process_ms."""
import json, sys, collections
f = json.load(open(sys.argv[1])); runs = {json.loads(l)['serial']: json.loads(l) for l in open(sys.argv[2])}
pairs = [tuple(x.split('+')) for x in sys.argv[3:]]
def mean(v): return sum(v) / len(v)
res = {}
for k, c in pairs:
    rk = [x['rank_stage_ms'] for x in f if x['arm'] == k]
    cc = [x for x in f if x['arm'] == c and x['point'] != 'q0']
    cold1 = mean([float(runs[x['serial']]['fields']['setup_ms']) + float(runs[x['serial']]['fields']['online_ms']) for x in cc])
    cold2 = mean([x['cold_in_process_ms'] for x in cc])
    res[k + '+' + c] = dict(rank_blocks=len(rk), rank_mean=round(mean(rk), 1), cold_points=len(cc), cold_setup_plus_online=round(cold1, 1),
                            cold_in_process=round(cold2, 1), E2E=round(mean(rk) + cold1, 1), E2E_cip=round(mean(rk) + cold2, 1),
                            rank_attempts=sorted({x['rank_attempts'] for x in f if x['arm'] == k}))
keys = list(res)
for i in range(1, len(keys)):
    res['R_' + keys[0] + '_over_' + keys[i]] = [round(res[keys[0]]['E2E'] / res[keys[i]]['E2E'], 4), round(res[keys[0]]['E2E_cip'] / res[keys[i]]['E2E_cip'], 4)]
json.dump(res, sys.stdout, indent=1); print()
