"""J9 (b): record-level consistency of ell_route against dims_by_deg(R'_4)[0]
(and R'_4 `one`) on every system of S3-U400, S3-SAT100, F-RANDX19, N-CONV19.
Reads archived closures.jsonl.gz only. Imports no crypto_autoresearcher module."""
import gzip, json, sys, collections
run = sys.argv[1]; out = sys.argv[2]
recs = [json.loads(l) for l in gzip.open(run + '/closures.jsonl.gz', 'rt')]
arms = ['S3-U400', 'S3-SAT100', 'F-RANDX19', 'N-CONV19']
res = {}
disagreements = []
for arm in arms:
    rs = [r for r in recs if r['arm'] == arm]
    c = collections.Counter()
    for r in rs:
        rb = r['rc_b']
        er = r['ell_route']
        if not rb.get('applicable') or not rb.get('substituted'):
            c['not_substituted(label=%s)' % rb.get('label')] += 1
            continue
        d0 = rb['R4']['dims_by_deg'][0]
        one = rb['R4']['one']
        c[('ell_route', er, 'R4_d0', d0, 'R4_one', one)] += 1
        if (er is True) != (d0 == 1) or (one is True) != (d0 == 1) or er is None:
            disagreements.append({'key': r['key'], 'ell_route': er, 'R4_d0': d0, 'R4_one': one})
    res[arm] = {'n': len(rs), 'table': {str(k): v for k, v in c.items()}}
res['disagreements'] = disagreements
res['n_disagreements'] = len(disagreements)
json.dump(res, open(out, 'w'), indent=1)
print(json.dumps(res, indent=1))
