"""J11 (2): compare own control profiles with closures.jsonl.gz; classify D-3 / T5 applicability."""
import sys, json, gzip, collections
W, run = sys.argv[1], sys.argv[2]
own = []
for s in (0, 1):
    own += [json.loads(l) for l in open(f'{W}/j11-nulls/profiles-shard{s}.jsonl')]
arch = {}
for l in gzip.open(run + '/closures.jsonl.gz', 'rt'):
    r = json.loads(l); arch[r['key']] = r
ann_keys = set()
for l in gzip.open(run + '/annihilators.jsonl.gz', 'rt'):
    r = json.loads(l); ann_keys.add(r['key'])
rows = []; nd = 0; ncmp = 0
table = collections.Counter()
neither = []
for o in own:
    a = arch[o['key']]
    diffs = {}
    for cl in ('M_3', 'M_4'):
        for f in ('rank', 'one', 'dims_by_deg'):
            ncmp += 1
            if o[cl][f] != a[cl][f]:
                diffs[cl + '.' + f] = (o[cl][f], a[cl][f])
    if o['arm'] == 'N-ELL19':
        rb = a['rc_b']
        for f, x, y in (('R3_rank', o['R3']['rank'], rb.get('R3_rank')), ('R4.rank', o['R4']['rank'], rb['R4']['rank']),
                        ('R4.one', o['R4']['one'], rb['R4']['one']), ('R4.dims_by_deg', o['R4']['dims_by_deg'], rb['R4']['dims_by_deg']),
                        ('T5_applicable', o['T5_applicable'], rb['T5_applicable']), ('jstar', o['jstar'], rb['jstar'])):
            ncmp += 1
            if x != y:
                diffs[f] = (x, y)
    nd += len(diffs)
    # applicability of a checked derivation
    if o['arm'] in ('N-F219', 'N-AFF19'):
        d3 = (o['M_4']['dims_by_deg'][3] == o['M_3']['rank']) and o['M_4']['dims_by_deg'][0] == 0
        exact_sr = o['M_4']['dims_by_deg'] == [0, 0, 19, 399, 3819]
        basis = 'D-3' if d3 else None
        table[(o['arm'], 'D-3 applies' if d3 else 'D-3 not applicable', 'exact semi-regular' if exact_sr else 'not exact')] += 1
    else:
        t5 = o['T5_applicable'] and not o['R4']['one'] and o['kernel_dim'] >= 1 and not o['row18_has_quadratic']
        ref = o['R4']['dims_by_deg'] == [0, 0, 18, 360, 3267]
        basis = 'T4+T5' if t5 else None
        table[(o['arm'], 'T4+T5 applies' if t5 else 'T5 not applicable', 'reference profile' if ref else 'not reference')] += 1
    if basis is None:
        neither.append({'key': o['key'], 'ann_v1_archived': o['key'] in ann_keys, 'engine_W4_one': a['W_4']['one']})
    rows.append({'key': o['key'], 'arm': o['arm'], 'family': o.get('family'), 'basis_for_nonrefutation': basis,
                 'M_4': o['M_4']['dims_by_deg'], 'M_3_rank': o['M_3']['rank'],
                 'R4': o.get('R4', {}).get('dims_by_deg'), 'R3_rank': o.get('R3', {}).get('rank'),
                 'engine_W4_one': a['W_4']['one'], 'engine_W4_final': a['W_4']['final_dim'],
                 'ann_v1_archived': o['key'] in ann_keys, 'diffs': diffs})
# derived W_4 value check against engine (own profile + checked derivation -> declared value)
Bp = [0, 1, 20, 191, 1160]  # dim B'_{<=d-1} in 19 variables, d = 0..4
derived_mismatch = []
n_derived = collections.Counter()
for rw in rows:
    a = arch[rw['key']]
    if rw['basis_for_nonrefutation'] == 'D-3':
        n_derived['D-3'] += 1
        pred = {'one': False, 'final_dim': rw['M_4'][4], 'iterations_to_fixpoint': 0, 'dims_by_deg': rw['M_4']}
    elif rw['basis_for_nonrefutation'] == 'T4+T5':
        n_derived['T4+T5'] += 1
        R4 = rw['R4']
        fin = R4[4] + 1160
        pred = {'one': False, 'final_dim': fin, 'iterations_to_fixpoint': 1 if rw['M_4'][4] < fin else 0,
                'dims_by_deg': [R4[d] + Bp[d] for d in range(5)]}
    else:
        continue
    got = {k: a['W_4'][k] for k in pred}
    rw['derived_W4'] = pred
    if got != pred:
        derived_mismatch.append({'key': rw['key'], 'pred': pred, 'engine': got})
summ = {'systems': len(own), 'compared_fields': ncmp, 'disagreements': nd,
        'table': {' | '.join(k): v for k, v in table.items()},
        'nonrefutation_on_neither_checked_derivation': neither,
        'n_neither': len(neither), 'derived_counts': dict(n_derived), 'derived_vs_engine_mismatches': derived_mismatch}
json.dump({'summary': summ, 'rows': rows}, open(f'{W}/j11-nulls/profiles-comparison.json', 'w'), indent=1)
print(json.dumps(summ, indent=1))
