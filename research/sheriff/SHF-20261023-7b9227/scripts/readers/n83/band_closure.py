"""Closure step (#997, run 39335956567) priced from emitted counts: IC-vs-IC order across the 0/0.1/1 band.
U = rank probes + online probes + index stored states; explicit group additions ~ one scalar mult per rank attempt."""
import json, base64, sys, collections
d = sys.argv[1]; rows = [json.loads(l) for l in open(d + '/runs.jsonl')]
acc = collections.defaultdict(lambda: collections.defaultdict(list))
for r in rows:
    if r['arm'] not in ('kPI', 'cPI', 'kM38I', 'cM38I') or r['point_id'] == 'q0': continue
    t = open(d + '/runs/' + r['stdout_file'].split('/')[-1]).read().split('\n')[0]
    x = json.loads(base64.b64decode(t.split('=', 1)[1])); s = [y for y in x['records'] if isinstance(y, dict) and y.get('kind', '').endswith('summary')][0]
    if r['arm'][0] == 'k':
        acc[r['arm'][1:]]['rank_probes'].append(s['rank_probes_total']); acc[r['arm'][1:]]['attempts'].append(s['rank_attempts'])
    else:
        acc[r['arm'][1:]]['online_probes'].append(x['records'][0]['probes']); acc[r['arm'][1:]]['stored'].append(s['stored_states'])
m = {a: {k: sum(v) / len(v) for k, v in dd.items()} for a, dd in acc.items()}
out = dict(means={a: {k: round(v) for k, v in dd.items()} for a, dd in m.items()}, band={})
for w in (0, 0.1, 1):
    ga = lambda a: m[a]['attempts'] * 125 + w * (m[a]['rank_probes'] + m[a]['online_probes'] + m[a]['stored'])  # ~125 GAE per [a]G scalar mult
    out['band'][str(w)] = round(ga('PI') / ga('M38I'), 3)
out['wall_R'] = 7.6558
print(json.dumps(out, indent=1))
