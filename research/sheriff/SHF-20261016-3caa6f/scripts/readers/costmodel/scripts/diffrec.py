import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decode import load
P = '/tmp/claude-0/-home-user/bc80ee7c-3e63-5cdc-8921-64b426219182/scratchpad/cryptanalysis/experiments/koblitz-n83-stacked-20261016/run_github_38862448935/panel/'
rows = {str(json.loads(l)['serial']): json.loads(l) for l in open(P + 'runs.jsonl')}
a, b = sys.argv[1], sys.argv[2]
oa, ob = load(P + rows[a]['stdout_file']), load(P + rows[b]['stdout_file'])
def flat(o, p=''):
    out = {}
    if isinstance(o, dict):
        for k, v in o.items(): out.update(flat(v, p + '.' + k))
    elif isinstance(o, list):
        if len(o) > 6: out[p] = 'list[%d]' % len(o)
        else: out[p] = json.dumps(o)
    else: out[p] = o
    return out
for i in range(max(len(oa['records']), len(ob['records']))):
    fa = flat(oa['records'][i]) if i < len(oa['records']) else {}
    fb = flat(ob['records'][i]) if i < len(ob['records']) else {}
    for k in sorted(set(fa) | set(fb)):
        if fa.get(k) != fb.get(k):
            print('rec%d %s: %s | %s' % (i, k, str(fa.get(k))[:90], str(fb.get(k))[:90]))
