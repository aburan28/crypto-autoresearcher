"""J2 red-team scratch: read-only computations on RUN-RELN-a695fe raw-result.json."""
import json, math, statistics as st, sys
R = json.load(open('experiments/EXP-RELN-c5a377/runs/RUN-RELN-a695fe/raw-result.json'))
rows = []
for c in sorted(R['cells'], key=lambda c: (c['fixture']['bits'], c['fixture']['seed'])):
    h = c['header']
    for b in c['budgets']:
        g = b['graph']; er = b['null_er']; rw = b['null_rewire']
        q = h['q']; L = g['L']
        oc = b.get('outcome_counts')
        row = dict(fx=c['fixture_id'], bits=h['bits'], bud=b['budget'], p=h['p'], q=q, B=h['B'], B2=h['B2'],
                   L=L, nLP=h['n_lp_classes_liftable'], att=b['attempts'], E=g['E'], V=g['V'],
                   EV=g['E_over_V'], c=g['components'], cwc=g['components_with_cycle'], cr=g['cycle_rank'],
                   giant=g['giant_component_fraction'], dp=g['delta_proof'], full=b['full_relation_count'],
                   er_cr=er['summary']['cycle_rank']['mean'], er_cr_sd=er['summary']['cycle_rank']['sd'],
                   er_giant=er['summary']['giant_component_fraction']['mean'],
                   er_dp=er['summary']['delta_proof']['mean'], er_dp_n=er['summary']['delta_proof']['n'],
                   er_feas=er.get('feasible'),
                   rw_cr=rw['summary']['cycle_rank']['mean'], rw_cr_sd=rw['summary']['cycle_rank']['sd'],
                   rw_giant=rw['summary']['giant_component_fraction']['mean'],
                   rw_dp=rw['summary']['delta_proof']['mean'], rw_dp_n=rw['summary']['delta_proof']['n'],
                   kp=b['known_positive']['status'], oc=oc)
        # threshold cycle rank for delta_proof > 1/4: cr > L^{5/4}
        row['cr_needed'] = L ** 1.25
        # relations per attempt
        row['rel_per_att'] = g['E'] / b['attempts']
        rows.append(row)
hdr = "fx bud p B B2 L nLP att E V E/V c cwc cr giant dp | er_cr er_giant er_dp(n) | rw_cr rw_giant rw_dp(n) | cr_needed kp".split()
print(" ".join(hdr))
for r in rows:
    f = lambda x: 'None' if x is None else (f"{x:.3f}" if isinstance(x, float) else str(x))
    print(r['fx'], r['bud'], r['p'], r['B'], r['B2'], r['L'], r['nLP'], r['att'], r['E'], r['V'], f(r['EV']), r['c'], r['cwc'], r['cr'],
          f(r['giant']), f(r['dp']), '|', f(r['er_cr']), f(r['er_giant']), f"{f(r['er_dp'])}({r['er_dp_n']})", '|',
          f(r['rw_cr']), f(r['rw_giant']), f"{f(r['rw_dp'])}({r['rw_dp_n']})", '|', f(r['cr_needed']), r['kp'])
print()
print("outcome_counts sample:", rows[0]['oc'])
json.dump(rows, open(sys.argv[1], 'w'), indent=1, default=str)
