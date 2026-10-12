"""J9 (c) comparison of own-code results with archived closures.jsonl.gz (after the declaration)."""
import sys, json, gzip, collections
own_p, run, outp = sys.argv[1], sys.argv[2], sys.argv[3]
own = [json.loads(l) for l in open(own_p)]
arch = {}
for l in gzip.open(run + '/closures.jsonl.gz', 'rt'):
    r = json.loads(l); arch[r['key']] = r
rows = []; ndiff = 0; ncmp = 0
for o in own:
    a = arch[o['key']]
    cmp = {}
    def c(name, x, y):
        global ndiff, ncmp
        ncmp += 1
        cmp[name] = 'agree' if x == y else {'own': x, 'archived': y}
        if x != y:
            ndiff += 1
    for cl in ('M_3', 'M_4'):
        for f in ('rank', 'one', 'dims_by_deg'):
            c(cl + '.' + f, o[cl][f], a[cl][f])
    rb = a['rc_b']
    c('rc_b.kernel_dim', o['kernel_dim'], rb['kernel_dim'])
    c('ell_route', o['ell_route_direct'], a['ell_route'])
    if 'R4' in o:
        c('rc_b.jstar', o['jstar'], rb['jstar'])
        c('rc_b.R3_rank', o['R3']['rank'], rb['R3_rank'])
        for f in ('rank', 'one', 'dims_by_deg'):
            c('rc_b.R4.' + f, o['R4'][f], rb['R4'][f])
        c('rc_b.sigma', o['sigma'], rb['sigma'])
        c('rc_b.T5_applicable', o['T5_applicable'], rb['T5_applicable'])
    for f in ('dims', 'iterations_to_fixpoint', 'final_dim', 'one', 'one_first_iteration', 'dims_by_deg'):
        c('W_4.' + f, o['W_4'][f], a['W_4'][f])
    if 'T4' in a and "W'_4" in a['T4']:
        for f in ('dims', 'iterations_to_fixpoint', 'final_dim', 'one', 'one_first_iteration', 'dims_by_deg'):
            c("W'_4." + f, o["W'_4"][f], a['T4']["W'_4"][f])
    # own-internal T4 check
    t4 = (o['W_4']['final_dim'] == o["W'_4"]['final_dim'] + 1160) and (o['W_4']['one'] == o["W'_4"]['one'])
    rows.append({'key': o['key'], 'own_T4_holds': t4, 'comparisons': cmp})
summ = {'systems': len(own), 'compared_fields': ncmp, 'disagreements': ndiff,
        'own_T4_holds_all': all(r['own_T4_holds'] for r in rows)}
json.dump({'summary': summ, 'rows': rows}, open(outp, 'w'), indent=1)
print(json.dumps(summ))
for r in rows:
    bad = {k: v for k, v in r['comparisons'].items() if v != 'agree'}
    if bad:
        print(r['key'], bad)
