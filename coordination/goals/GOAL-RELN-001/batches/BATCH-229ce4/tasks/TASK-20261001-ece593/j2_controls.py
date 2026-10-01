"""J2 red-team scratch: null-discrimination, yield scaling, isolated-vertex bias, cost. Read-only."""
import json, math, statistics as st
R = json.load(open('experiments/EXP-RELN-c5a377/runs/RUN-RELN-a695fe/raw-result.json'))
cells = sorted(R['cells'], key=lambda c: (c['fixture']['bits'], c['fixture']['seed']))
def ols(xs, ys):
    mx, my = st.fmean(xs), st.fmean(ys); sxx = sum((x-mx)**2 for x in xs)
    b = sum((x-mx)*(y-my) for x, y in zip(xs, ys))/sxx; a = my-b*mx
    se = math.sqrt(sum((y-a-b*x)**2 for x, y in zip(xs, ys))/(len(xs)-2)/sxx); return b, se
print("== (b) treatment vs nulls, per fixture x budget ==")
print("fx bud cr | rw: mean sd z  pct(rw<=cr) | er: mean sd z pct | c_treat c_er_mean c_rw_mean | er_iso_pred | selfloops multi")
zs = {'A1': [], 'A2': []}; zer = {'A1': [], 'A2': []}
for c in cells:
    for b in c['budgets']:
        g = b['graph']; cr = g['cycle_rank']
        rw = [r['cycle_rank'] for r in b['null_rewire']['replicates']]
        er = [r['cycle_rank'] for r in b['null_er']['replicates'] if r is not None]
        def z(v, xs):
            s = st.stdev(xs); return (v-st.fmean(xs))/s if s > 0 else float('nan')
        pr = sum(1 for x in rw if x <= cr)/len(rw); pe = sum(1 for x in er if x <= cr)/len(er)
        zs[b['budget']].append(z(cr, rw)); zer[b['budget']].append(z(cr, er))
        crw = [r['components'] for r in b['null_rewire']['replicates']]
        cer = [r['components'] for r in b['null_er']['replicates'] if r is not None]
        iso = g['V']*math.exp(-2*g['E']/g['V'])
        # multi-edges in treatment
        print(c['fixture_id'], b['budget'], cr, '|', f"{st.fmean(rw):.2f} {st.stdev(rw):.2f} {z(cr,rw):+.2f} {pr:.2f}", '|',
              f"{st.fmean(er):.2f} {st.stdev(er):.2f} {z(cr,er):+.2f} {pe:.2f}", '|', g['components'], f"{st.fmean(cer):.2f}",
              f"{st.fmean(crw):.2f}", '|', f"{iso:.1f}", '|', g['self_loops'], b['null_rewire'].get('frac_delta_proof_gt_quarter'),
              b['null_er'].get('frac_delta_proof_gt_quarter'))
for k in zs:
    print(k, "mean z vs rewire", f"{st.fmean([x for x in zs[k] if x==x]):+.3f}", "mean z vs ER", f"{st.fmean([x for x in zer[k] if x==x]):+.3f}")
print("\n== (a) yield and budget scaling ==")
xs, y_yield, y_a1, y_a2, y_cr2 = [], [], [], [], []
for c in cells:
    h = c['header']; q = h['q']; nlp = h['n_lp_classes_liftable']
    for b in c['budgets']:
        g = b['graph']; oc = b['outcome_counts']
        rel = oc['lp2'] + oc['lp1'] + oc['full']
        if b['budget'] == 'A2':
            xs.append(math.log(q)); y_yield.append(math.log(rel/b['attempts']))
            y_a2.append(math.log(g['E']/(nlp+1))); y_cr2.append(math.log(max(g['cycle_rank'], 1)))
        else:
            y_a1.append(math.log(g['E']/(nlp+1)))
        print(c['fixture_id'], b['budget'], 'q', q, 'att', b['attempts'], 'rel', rel, oc, 'yield', f"{rel/b['attempts']:.4f}",
              'yield*q^0.2', f"{rel/b['attempts']*q**0.2:.3f}", 'E/(nLP+1)', f"{g['E']/(nlp+1):.3f}",
              'mean_deg_all', f"{2*g['E']/(nlp+1):.3f}", 'cr/L^2', f"{g['cycle_rank']/g['L']**2:.3f}",
              'cr/q^0.4', f"{g['cycle_rank']/q**0.4:.3f}", 'work/sqrtq', f"{b['charged']['charged_work_over_sqrt_q']:.1f}")
for name, ys in [('log yield vs log q (pred -0.2)', y_yield), ('log E/(nLP+1) A1 vs log q (pred -0.1)', y_a1),
                 ('log E/(nLP+1) A2 vs log q (pred 0)', y_a2), ('log cycle_rank A2 vs log q (pred 0.4)', y_cr2)]:
    b, se = ols(xs, ys); print(name, f"slope {b:+.3f} +- {se:.3f} (1 s.e., n={len(ys)})")
print("\n== rho baseline ==")
for c in cells:
    print(c['fixture_id'], 'rho walk/sqrtq', f"{c['rho']['summary']['mean_walk_ops_over_sqrt_q']:.3f}", c['rho']['summary']['n_solved'], '/', c['rho']['summary']['n_targets'])
