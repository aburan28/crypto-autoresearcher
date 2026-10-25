"""Ratchet chain consistency: product of paired within-run step ratios (from ratchet_history cold_gap pairs)
vs the cross-run landed gap ratio, and the host-dependence of one producer's gap."""
import json, sys
d = json.load(open(sys.argv[1]))
rh = [e for e in d['ratchet_history'] if e.get('n') == 83]
steps = []
for e in rh:
    cg = e.get('cold_gap')
    to = str(e.get('to'))[:60]
    if isinstance(cg, list) and len(cg) == 2 and all(isinstance(x, (int, float)) for x in cg) and str(e.get('baseline_row_replaced')) not in ('False', 'None', 'none: not promoted') and not str(e.get('baseline_row_replaced', '')).startswith('none'):
        steps.append((to, cg[0], cg[1], round(cg[0] / cg[1], 5), e.get('cross_run_context_cold_gap')))
prod = 1.0
for s in steps:
    prod *= s[3]
out = dict(row_replacing_steps=[dict(to=s[0], paired_from=s[1], paired_to=s[2], ratio=s[3], landed_context=s[4]) for s in steps],
           product_of_paired_ratios=round(prod, 3))
# landed gaps: first landed 'from' (B) to the current row
out['current_row_gap'] = d['baselines'][4]['gap_cold_ic_over_rho']['value']
json.dump(out, sys.stdout, indent=1); print()
