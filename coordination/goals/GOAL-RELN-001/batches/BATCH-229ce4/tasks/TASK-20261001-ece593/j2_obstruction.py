"""J2 red-team scratch: obstruction quantity, A2-only counterfactual clauses, subcritical-rule reachability. Read-only."""
import json, math, statistics as st, sys
sys.path.insert(0, 'experiments/EXP-RELN-c5a377/implementation')
import analysis  # frozen; used read-only for lower_ci / slope_upper_ci
R = json.load(open('experiments/EXP-RELN-c5a377/runs/RUN-RELN-a695fe/raw-result.json'))
cells = sorted(R['cells'], key=lambda c: (c['fixture']['bits'], c['fixture']['seed']))
ex, var, crt, dex = 0.0, 0.0, 0, []
print("== obstruction: A2 cycle-rank excess over degree-preserving rewire null ==")
for c in cells:
    b = [x for x in c['budgets'] if x['budget'] == 'A2'][0]; g = b['graph']
    rw = [r['cycle_rank'] for r in b['null_rewire']['replicates']]
    m, s = st.fmean(rw), st.stdev(rw)
    ex += g['cycle_rank'] - m; var += s*s + s*s/len(rw); crt += g['cycle_rank']
    d = math.log(g['cycle_rank']/m)/math.log(g['L'])
    dex.append(d)
    print(c['fixture_id'], 'cr', g['cycle_rank'], 'rw_mean', round(m, 3), 'excess', round(g['cycle_rank']-m, 3), 'delta-units excess', round(d, 4))
print('total excess', round(ex, 2), '+-', round(math.sqrt(var), 2), 'cycles (1 sd, treatment single-draw + null-mean var)')
print('relative', round(ex/crt, 4), '+-', round(math.sqrt(var)/crt, 4), 'of total cycle rank', crt)
print('delta-units excess mean', round(st.fmean(dex), 4), 'sd', round(st.stdev(dex), 4), 'se', round(st.stdev(dex)/3, 4),
      '95% t CI', [round(st.fmean(dex) + k*2.306*st.stdev(dex)/3, 4) for k in (-1, 1)])
print("\n== A2-only counterfactual of supercritical clauses (frozen helper functions) ==")
xs, ys = [], []
for bits in (16, 20, 24):
    dp = [ [x for x in c['budgets'] if x['budget']=='A2'][0]['graph']['delta_proof'] for c in cells if c['fixture']['bits']==bits]
    print(bits, 'A2 delta_proof', [round(v, 3) for v in dp], 'lower95', round(analysis.lower_ci(dp), 4))
    xs += [bits]*3; ys += dp
print('A2 slope, upper95', [round(v, 4) for v in analysis.slope_upper_ci(xs, ys)])
print("\n== subcritical giant<0.05 reachability: min possible giant fraction 2/V (any graph with >=1 edge) ==")
for c in cells:
    for b in c['budgets']:
        g = b['graph']
        print(c['fixture_id'], b['budget'], 'V', g['V'], 'min_giant', round(2/g['V'], 3), 'reachable', 2/g['V'] < 0.05,
              'observed giant', round(g['giant_component_fraction'], 3), 'cr', g['cycle_rank'], 'cwc', g['components_with_cycle'],
              'rule2(cr<=2cwc)', g['cycle_rank'] <= 2*g['components_with_cycle'])
