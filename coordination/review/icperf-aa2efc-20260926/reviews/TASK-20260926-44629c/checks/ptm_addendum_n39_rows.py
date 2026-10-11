#!/usr/bin/env python3
"""PTM addendum: characterise the rows below the N=#E shape-matched floor, and the margin over the N=r floor."""
import json, mpmath as mp
from math import comb, log2, sqrt, pi
exec(open(__file__.replace("ptm_addendum_n39_rows.py", "ptm_floor_vs_toy.py")).read().split("d = json.load(open(LEDGER))")[0])  # reuse helpers
d = json.load(open(LEDGER))
inst = [i for i in d['ledger']['instances'] if i['regime'] == 'koblitz']
print("== rows at K_0/GF(2^39): the ledger's own bookkeeping ==")
for i in inst:
    if i['curve']['name'] != 'K_0 / GF(2^39)': continue
    n = 39; N = int(i['group_order']); r = i['r']
    print(f"cofactor={i['cofactor']} cofactor_classes={i['curve']['factor_base'].get('cofactor_classes')} ceiling_uniform_m2={i['curve']['factor_base'].get('ceiling_uniform_m2')} ceiling_exact_m2={i['curve']['factor_base'].get('ceiling_exact_m2')} (ratio exact/uniform = {i['curve']['factor_base']['ceiling_exact_m2']/i['curve']['factor_base']['ceiling_uniform_m2']:.2f})")
    for v in i['variants']:
        if v['name'] != 'mitm_m2_signed_orbit_columns_frobfold_walk': continue
        F = v['signed_points']; K = v['columns']
        print(f"  trials={v['trials']} relations_found={v['relations_found']} columns={K} rank={v['rank']} independent={v['independent']} dependent={v['dependent']} "
              f"trials_floor={v['trials_floor']:.0f} trials_floor_exact={v['trials_floor_exact']:.0f} trials/floor={v['trials_over_floor']:.3f} trials/floor_exact={v['trials_over_floor_exact']:.3f} "
              f"yield/ceiling={v['yield_over_ceiling']:.2f} yield/ceiling_exact={v['yield_over_ceiling_exact']:.2f} native={v['relations']['native']} la_native={v['linear_algebra']['native']}")
        print(f"    targets-per-relation measured = {v['trials']/v['relations_found']:.0f}; model N=#E: {N/comb(F,2):.0f}; model N=r: {r/comb(F,2):.2f}; measured/model(#E) = {v['trials']/v['relations_found']/(N/comb(F,2)):.3f} (1/{(N/comb(F,2))/(v['trials']/v['relations_found']):.1f}); relations/columns = {v['relations_found']/K:.3f} (1/{K/v['relations_found']:.1f})")
print()
print("== minimum margin of every Koblitz row over the shape-matched floor with N=r (the cofactor-corrected variant) ==")
rows = []
for i in inst:
    n = i['curve']['field']['degree']; N = int(i['group_order']); r = i['r']
    for v in i['variants']:
        m = v['summands']
        fl_r = floor_min(m, r, 2 * n)[1]; fl_E = floor_min(m, N, 2 * n)[1]
        rows.append((v['total_gae'] / fl_r, i['curve']['name'], v['name'], v['total_gae'], fl_r, fl_E, v['relations']['gae'] / fl_r))
rows.sort()
for ratio, cn, vn, tot, flr, flE, relratio in rows[:8]:
    print(f"  total/floor(r) = 2^{log2(ratio):+.2f}  relations-phase-only/floor(r) = 2^{log2(relratio):+.2f}  {cn:<18} {vn}")
print(f"  rows with total below floor(r): {sum(1 for x in rows if x[0] < 1)} of {len(rows)}; rows with RELATION-PHASE-ONLY cost below floor(r): {sum(1 for x in rows if x[6] < 1)} of {len(rows)}")
print()
print("== relation-phase-only cost vs shape-matched floor (N=#E): the floor omits the table build, so this is the sharper test ==")
rows2 = []
for i in inst:
    n = i['curve']['field']['degree']; N = int(i['group_order'])
    for v in i['variants']:
        m = v['summands']; fl_E = floor_min(m, N, 2 * n)[1]
        rows2.append((v['relations']['gae'] / fl_E, i['curve']['name'], v['name'], i['cofactor']))
rows2.sort()
for ratio, cn, vn, h in rows2[:10]:
    print(f"  rel/floor(#E) = 2^{log2(ratio):+.2f}  cofactor={h:<6} {cn:<18} {vn}")
print(f"  rows with relation-phase cost below floor(#E): {sum(1 for x in rows2 if x[0] < 1)} of {len(rows2)}; their cofactors: {sorted(set(x[3] for x in rows2 if x[0] < 1))}")

print()
print("== counts of rows below each floor instantiation (216 Koblitz rows; total cost and relation-phase-only cost) ==")
for lab, div in (("no-collapse (finding table, |F| relations)", None), ("finding's collapse /n", "n"), ("signed-orbit fold /2n", "2n")):
    for Nlab in ("N=#E", "N=r"):
        below_tot = below_rel = 0; worst_tot = 99
        for i in inst:
            n = i['curve']['field']['degree']; N = int(i['group_order']); r = i['r']
            NN = N if Nlab == "N=#E" else r
            dv = 1 if div is None else (n if div == "n" else 2 * n)
            for v in i['variants']:
                fl = floor_min(v['summands'], NN, dv)[1]
                below_tot += v['total_gae'] < fl; below_rel += v['relations']['gae'] < fl
                worst_tot = min(worst_tot, log2(v['total_gae'] / fl))
        print(f"  {lab:<48} {Nlab:<5}: total below floor {below_tot:>3}/216, relation-phase below floor {below_rel:>3}/216, worst total/floor = 2^{worst_tot:+.2f}")
