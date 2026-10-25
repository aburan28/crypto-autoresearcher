"""Reader's section-5a style band for the current n=83 row (run 39527997793), from emitted counters only.
NOT a sealed ECBND1h bound: a model. IC explicit group additions are negligible (16 rank-attempt scalar
multiplications, ~592 closure images built outside the run), so IC_GAE(w) ~= w * U, U = unpriced native
operations the producer DOES count: rank probes + rank root calls + online probes + online root calls +
index states (stored or logical). Rho step = 1 GAE (+ w for its Frobenius canonicalization in variant b).
Scan self-test (843.8 ms wall) emits no count and is excluded (so IC side is a lower bound)."""
import json, base64, sys, collections
d = sys.argv[1]
rows = [json.loads(l) for l in open(d + '/runs.jsonl')]
def raw(r):
    t = open(d + '/runs/' + r['stdout_file'].split('/')[-1]).read().split('\n')[0]
    return json.loads(base64.b64decode(t.split('=', 1)[1]))
acc = collections.defaultdict(list)
for r in rows:
    if r['role'] != 'primary' or r['side'] != 'B': continue
    x = raw(r); tgt = x['records'][0]; s = [y for y in x['records'] if isinstance(y, dict) and y.get('kind', '').endswith('summary')][0]
    if r['arm'].startswith('k'):
        acc['rank_probes'].append(s['rank_probes_total']); acc['rank_root_calls'].append(s['rank_root_calls_total'])
    else:
        acc['online_probes'].append(tgt['probes']); acc['online_root_calls'].append(tgt['root_calls'])
        acc['stored_states'].append(s['stored_states']); acc['logical_states'].append(s['regular_states'])
m = {k: sum(v) / len(v) for k, v in acc.items()}
rho_steps = [int(r['fields']['ops']) for r in rows if r['arm'] == 'rT']; rs = sum(rho_steps) / len(rho_steps)
U_stored = m['rank_probes'] + m['rank_root_calls'] + m['online_probes'] + m['online_root_calls'] + m['stored_states']
U_logical = U_stored - m['stored_states'] + m['logical_states']
out = dict(means={k: round(v) for k, v in m.items()}, rho_steps_mean=round(rs), U_stored=round(U_stored), U_logical=round(U_logical), band={})
for w in (0, 0.1, 1):
    out['band'][str(w)] = dict(gap_rho_step_1GAE=[round(w * U_stored / rs, 4), round(w * U_logical / rs, 4)],
                               gap_rho_step_1plusw=[round(w * U_stored / (rs * (1 + w)), 4), round(w * U_logical / (rs * (1 + w)), 4)])
out['wall_time_gap_for_reference'] = 3.9242
out['implied_GAE_per_unpriced_op_at_wall_gap'] = [round(3.9242 * rs / U_logical, 3), round(3.9242 * rs / U_stored, 3)]
out['reading'] = 'IC/rho order flips inside [0,1] GAE per unpriced op: not ranked by the 5a rule; the 3.92 gap is a wall-time figure only.'
json.dump(out, sys.stdout, indent=1); print()
