"""J3 (i)/(ii)/(iv): frontier table, borrowed precomputation and cumulative
break-even, recomputed from the snapshot-committed run records of
EXP-ECDLP-612fb1 (raw-result.json solved arrays + summary.json counts).
Read-only; writes only into the red-team task directory."""
import json, math, os, sys
import numpy as np
BASE = 'experiments/EXP-ECDLP-612fb1/runs'
OUT = sys.argv[1]
CELLS = {'2^20,a=1/4': range(1, 6), '2^24,a=1/4': range(13, 18), '2^30,a=1/4': range(23, 28),
         '2^24,a=1/2': range(18, 23), '2^30,a=1/2': range(28, 33)}
ARMS = ['STATIC(T)', 'STATIC(T/2)', 'RESEL-L(T/2)', 'RESEL-L(T)', 'CAP(4T,T/2)', 'CAP(2T,T/2)', 'CAP(4T,T)', 'CAP(2T,T)',
        'STATIC2T', 'RHO', 'NULL-A(T/2)', 'RESEL-U(T/2)', 'RESEL-U(T)',
        'RSWEEP-STATIC(r=4,T/2)', 'RSWEEP-STATIC(r=8,T/2)', 'RSWEEP-STATIC(r=4,T)', 'RSWEEP-STATIC(r=8,T)',
        'RSWEEP-RESEL-L(r=4,T/2)', 'RSWEEP-RESEL-L(r=8,T/2)', 'ORACLE(T)', 'ORACLE(T/2)']
out = {}
md = []
for cell, rr in CELLS.items():
    runs = []
    for i in rr:
        d = f'{BASE}/RUN-ECDLP-612fb1-{i:03d}'
        runs.append((json.load(open(f'{d}/summary.json')), json.load(open(f'{d}/raw-result.json'))))
    T = runs[0][0]['params']['T']; N = runs[0][0]['params']['N']; W = runs[0][0]['params']['W']
    bits_e = runs[0][0]['params']['bits_per_table_entry']; bits_p = runs[0][0]['params']['bits_per_pool_entry']
    rc = runs[0][0]['params']['restart_scalar_mult_group_ops']
    pools = {r: {'P_mean': float(np.mean([s['pools'][r]['P_group_ops'] for s, _ in runs])),
                 'P_over_sqrtNT_mean': float(np.mean([s['pools'][r]['P_over_sqrt_NT'] for s, _ in runs])),
                 'walks_mean': float(np.mean([s['pools'][r]['walks'] for s, _ in runs]))} for r in ('2', '4', '8')}
    cellout = {'T': T, 'N': N, 'W': W, 'bits_table_entry': bits_e, 'bits_pool_entry': bits_p, 'pools': pools, 'arms': {}}
    md.append(f'\n### {cell}  (T={T}, W={W:.1f}; P(r=2)={pools["2"]["P_mean"]:.0f} = {pools["2"]["P_over_sqrtNT_mean"]:.3f} sqrt(NT); P(r=4)={pools["4"]["P_over_sqrtNT_mean"]:.3f} sqrt(NT); P(r=8)={pools["8"]["P_over_sqrtNT_mean"]:.3f} sqrt(NT))')
    md.append('| arm | P/sqrt(NT) | S adv bits (entries) | S_peak bits (entries, xT) | L/target | L/solved | restart ops/target | eps_ss 4T | eps_ss 8T | eps_ss 16T | eps_cum 8T | eps_cum 16T | early10% |')
    md.append('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for a in ARMS:
        if a not in runs[0][0]['arms']:
            continue
        S = [s['arms'][a] for s, _ in runs]
        sol = [np.asarray(raw['arms'][a]['solved'], dtype=float) for _, raw in runs]
        def pooled(lo, hi):
            return float(np.concatenate([x[max(0, lo):hi] for x in sol]).mean())
        r = S[0]['config']['r']
        Pr = pools[str(r)]['P_over_sqrtNT_mean'] if S[0]['config']['mode'] not in ('rho', 'oracle') else 0.0
        speak = float(np.mean([x['S_peak_bits'] for x in S])); pent = float(np.mean([x['max_pool_entries'] for x in S]))
        rec = {'P_over_sqrtNT': Pr, 'S_bits': S[0]['S_bits'], 'S_entries': S[0]['S_bits'] // bits_e if bits_e else 0,
               'S_peak_bits_mean': speak, 'S_peak_entries_mean': pent, 'S_peak_entries_over_T': pent / T,
               'S_peak_bits_per_seed': [x['S_peak_bits'] for x in S],
               'L_per_target_mean': float(np.mean([x['L_mean_per_target'] for x in S])),
               'L_per_solved_mean': float(np.mean([x['L_mean_per_solved_target'] or float('nan') for x in S])),
               'restart_ops_per_target': float(np.mean([x['restart_group_ops_total'] for x in S])) / (16 * T),
               'eps_ss': {'4T': pooled(2 * T, 4 * T), '8T': pooled(6 * T, 8 * T), '16T': pooled(14 * T, 16 * T)},
               'eps_cum': {'4T': pooled(0, 4 * T), '8T': pooled(0, 8 * T), '16T': pooled(0, 16 * T)},
               'early10pct_of_8T': pooled(0, int(0.8 * T)),
               'solved_total_per_seed': [int(x.sum()) for x in sol],
               'reselection_int_ops_total_mean': float(np.mean([x['reselection_int_ops_total'] for x in S]))}
        cellout['arms'][a] = rec
        md.append(f"| {a} | {Pr:.3f} | {rec['S_bits']} ({rec['S_entries']}) | {speak:.0f} ({pent:.0f}, {pent / T:.2f}T) | {rec['L_per_target_mean']:.1f} | {rec['L_per_solved_mean']:.1f} | {rec['restart_ops_per_target']:.1f} | {rec['eps_ss']['4T']:.4f} | {rec['eps_ss']['8T']:.4f} | {rec['eps_ss']['16T']:.4f} | {rec['eps_cum']['8T']:.4f} | {rec['eps_cum']['16T']:.4f} | {rec['early10pct_of_8T']:.4f} |")
    # ---- (iv) cumulative curves and break-even
    def cum_curve(a):
        sol = [np.asarray(raw['arms'][a]['solved'], dtype=float) for _, raw in runs]
        return {f'{u // T}T': float(np.concatenate([x[:u] for x in sol]).mean()) for u in range(T, 16 * T + 1, T)}
    def ss_curve(a):
        sol = [np.asarray(raw['arms'][a]['solved'], dtype=float) for _, raw in runs]
        return {f'{u // T}T': float(np.concatenate([x[u - 2 * T:u] for x in sol]).mean()) for u in range(2 * T, 16 * T + 1, T)}
    cellout['eps_cum_by_U'] = {a: cum_curve(a) for a in ('STATIC(T)', 'STATIC(T/2)', 'RESEL-L(T/2)', 'RESEL-L(T)', 'STATIC2T', 'CAP(2T,T/2)') if a in runs[0][0]['arms']}
    cellout['eps_ss_by_U'] = {a: ss_curve(a) for a in ('STATIC(T)', 'STATIC(T/2)', 'RESEL-L(T/2)', 'RESEL-L(T)', 'STATIC2T') if a in runs[0][0]['arms']}
    # cumulative deficit in SOLVED TARGETS of RESEL-L(T/2) vs STATIC(T) after U targets (per seed mean)
    solA = [np.asarray(raw['arms']['RESEL-L(T/2)']['solved'], dtype=float) for _, raw in runs]
    solB = [np.asarray(raw['arms']['STATIC(T)']['solved'], dtype=float) for _, raw in runs]
    cellout['cum_solved_deficit_RESEL_T2_minus_STATIC_T'] = {f'{u // T}T': float(np.mean([a[:u].sum() - b[:u].sum() for a, b in zip(solA, solB)])) for u in range(T, 16 * T + 1, T)}
    # extrapolated U*: with the steady-state gap g_ss at 16T and cumulative deficit D at 16T, the cumulative gap closes only if g_ss > 0
    g16 = cellout['eps_ss_by_U']['RESEL-L(T/2)']['16T'] - cellout['eps_ss_by_U']['STATIC(T)']['16T']
    cellout['U_star_extrapolation'] = {'ss_gap_at_16T': g16, 'note': 'cumulative break-even is unreachable while the steady-state gap stays negative; U* = infinity on this record' if g16 < 0 else 'positive ss gap; U* finite'}
    # ---- (ii) borrowed precomputation
    bp = {}
    for arm in ('RESEL-L(T/2)', 'RESEL-L(T)'):
        sol = [np.asarray(raw['arms'][arm]['solved'], dtype=float) for _, raw in runs]
        k = 4
        bp[arm] = {}
        for lab, U in (('4T', 4 * T), ('8T', 8 * T), ('16T', 16 * T)):
            ps = float(np.concatenate([x[:U] for x in sol]).mean())
            r_eff = 2 + U * k * ps / T
            # admitted walks in LOWER bracket: solved targets x walks used (hit walk included)
            used = [np.asarray(raw['arms'][arm]['walks_used'], dtype=float) for _, raw in runs]
            admitted = float(np.mean([(u[:U] * x[:U]).sum() for u, x in zip(used, sol)]))
            bp[arm][lab] = {'p_s_cum': ps, 'r_eff_formula': r_eff, 'admitted_walks_mean': admitted,
                            'admitted_walks_over_T': admitted / T,
                            'r_eff_from_admitted_walks': 2 + admitted / T}
        # pool entries actually present (uncapped) at the end and at 8T
        bp[arm]['max_pool_entries_over_T'] = float(np.mean([s['arms'][arm]['max_pool_entries'] for s, _ in runs])) / T
    # measured static P at r in {2,4,8} versus hit rate of STATIC tables (last-round pooled)
    def last_round_p(a):
        h = sum(s['arms'][a]['rounds'][-1]['hits'] for s, _ in runs); w = sum(s['arms'][a]['rounds'][-1]['walks'] for s, _ in runs)
        return h / w
    def all_round_p(a):
        h = sum(r_['hits'] for s, _ in runs for r_ in s['arms'][a]['rounds']); w = sum(r_['walks'] for s, _ in runs for r_ in s['arms'][a]['rounds'])
        return h / w
    bp['static_hit_rate_by_r'] = {lab: {'2': all_round_p(f'STATIC({lab})'), '4': all_round_p(f'RSWEEP-STATIC(r=4,{lab})'), '8': all_round_p(f'RSWEEP-STATIC(r=8,{lab})')} for lab in ('T', 'T/2')}
    bp['static_eps_ss_8T_by_r'] = {lab: {'2': cellout['arms'][f'STATIC({lab})']['eps_ss']['8T'], '4': cellout['arms'][f'RSWEEP-STATIC(r=4,{lab})']['eps_ss']['8T'], '8': cellout['arms'][f'RSWEEP-STATIC(r=8,{lab})']['eps_ss']['8T']} for lab in ('T', 'T/2')}
    bp['resel_hit_rate_last_round'] = {a: last_round_p(a) for a in ('RESEL-L(T/2)', 'RESEL-L(T)')}
    bp['resel_hit_rate_rounds_6_7_pooled'] = {a: (sum(s['arms'][a]['rounds'][r_]['hits'] for s, _ in runs for r_ in (6, 7)) / sum(s['arms'][a]['rounds'][r_]['walks'] for s, _ in runs for r_ in (6, 7))) for a in ('RESEL-L(T/2)', 'RESEL-L(T)')}
    bp['P_by_r_over_sqrtNT'] = {r: pools[r]['P_over_sqrtNT_mean'] for r in ('2', '4', '8')}
    if 'heur_blt7_regression' in runs[0][0]:
        bp['executor_HEUR_BLT7_r_eff_pools'] = {arm: {U: {k_: v[k_] for k_ in ('r_eff', 'precomp_pool_r_eff_P', 'precomp_pool_r_eff_walks', 'exact_coverage_precomp_r_eff_top_t_sel', 'exact_coverage_reselected_table_after_U', 'pool_entries')}
                                                      for U, v in runs[0][0]['heur_blt7_regression'][arm].items()} for arm in runs[0][0]['heur_blt7_regression']}
        bp['executor_HEUR_BLT7_note'] = 'seed 1 only, from RUN-013 summary.json; P of an r_eff pool in group ops'
    cellout['borrowed_precomputation'] = bp
    out[cell] = cellout
json.dump(out, open(os.path.join(OUT, 'j3_frontier.json'), 'w'), indent=1)
open(os.path.join(OUT, 'j3_frontier.md'), 'w').write('\n'.join(md) + '\n')
print('\n'.join(md))
for cell in ('2^24,a=1/4', '2^30,a=1/4'):
    c = out[cell]
    print(f'\n== {cell} cumulative eps by U ==')
    for a, cv in c['eps_cum_by_U'].items():
        print(f'  {a:14s}', ' '.join(f'{k}:{v:.3f}' for k, v in cv.items()))
    print('  ss RESEL-L(T/2):', ' '.join(f'{k}:{v:.3f}' for k, v in c['eps_ss_by_U']['RESEL-L(T/2)'].items()))
    print('  ss STATIC(T)   :', ' '.join(f'{k}:{v:.3f}' for k, v in c['eps_ss_by_U']['STATIC(T)'].items()))
    print('  cum solved deficit RESEL-L(T/2) - STATIC(T):', {k: round(v, 1) for k, v in c['cum_solved_deficit_RESEL_T2_minus_STATIC_T'].items()})
    print('  U* extrapolation:', c['U_star_extrapolation'])
    print('  borrowed precomputation:', json.dumps(c['borrowed_precomputation'], indent=None)[:3000])
