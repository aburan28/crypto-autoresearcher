"""J13: check the pinned-engine outputs on O1-O3 against the failure signatures:
O1: no M_3 / M_4 / W_4 refutation, codim(W_4) >= s (equality reported for s <= 31);
O2/O3: engine W_4 equals the DECLARED values (one, final_dim, iterations_to_fixpoint, dims_by_deg).
Also: engine outputs equal the archived closures.jsonl.gz records (determinism of the pinned engine; not independence)."""
import sys, json, gzip, collections
W, run = sys.argv[1], sys.argv[2]
eng = {json.loads(l)['key']: json.loads(l) for l in open(W + '/j13-ptm/engine-o1-o3.jsonl')}
decl = {d['key']: d for d in json.load(open(W + '/j13-ptm/o2-o3-declaration.json'))['o2_o3_declaration']['systems']}
inst = {}
for l in gzip.open(run + '/instances.jsonl.gz', 'rt'):
    r = json.loads(l); inst[r['key']] = r
arch = {}
for l in gzip.open(run + '/closures.jsonl.gz', 'rt'):
    r = json.loads(l); arch[r['key']] = r
out = {'O1': collections.Counter(), 'O2': collections.Counter(), 'O3': collections.Counter(), 'failures': [], 'archive_mismatch': []}
eq_s = collections.Counter()
for k, e in eng.items():
    a = arch[k]
    for cl in ('M_3', 'M_4', 'W_4'):
        for f in e[cl]:
            if f in a[cl] and e[cl][f] != a[cl][f]:
                out['archive_mismatch'].append((k, cl, f))
    if inst[k]['role'] == 'sat':
        s = inst[k]['s']
        codim = 6196 - e['W_4']['final_dim']
        refuted = e['M_3']['one'] or e['M_4']['one'] or e['W_4']['one']
        out['O1']['n'] += 1
        if refuted or codim < s:
            out['failures'].append({'key': k, 'object': 'O1', 'refuted': refuted, 'codim': codim, 's': s})
        if s <= 31:
            eq_s[(inst[k]['arm'], codim == s)] += 1
    else:
        d = decl[k]
        obj = d['object']
        out[obj]['n'] += 1
        got = {f: e['W_4'][f] for f in d['declared']}
        if got != d['declared']:
            out['failures'].append({'key': k, 'object': obj, 'declared': d['declared'], 'engine': got})
        else:
            out[obj]['exact_match'] += 1
out['O1_codim_eq_s_by_arm'] = {f'{a}|{b}': v for (a, b), v in eq_s.items()}
out['n_failures'] = len(out['failures'])
out['n_archive_mismatch'] = len(out['archive_mismatch'])
out = {k: (dict(v) if isinstance(v, collections.Counter) else v) for k, v in out.items()}
json.dump(out, open(W + '/j13-ptm/o1-o3-engine-check.json', 'w'), indent=1)
print(json.dumps(out, indent=1)[:3000])
