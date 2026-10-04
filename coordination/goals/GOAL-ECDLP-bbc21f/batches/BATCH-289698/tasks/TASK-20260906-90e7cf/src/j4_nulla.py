"""J4(iii): NULL-A relabelled evidence. Apply the contract's S1-S4 acceptance
logic with NULL-A(T/2) in the role of RESEL-L(T/2), from the producer's
own ci_tables.json (RUN-037) and raw solved arrays; report NULL-A's gain per
round with CI; also the 'random T/2 subset of the pool' reference level."""
import json, sys
import numpy as np
sys.path.insert(0, 'experiments/EXP-ECDLP-612fb1/source')
from analysis import Boot, pooled_mean
ci = json.load(open('experiments/EXP-ECDLP-612fb1/runs/RUN-ECDLP-612fb1-037/ci_tables.json'))
BASE = 'experiments/EXP-ECDLP-612fb1/runs'
CELLS = {'2^24,a=1/4': range(13, 18), '2^30,a=1/4': range(23, 28)}
boot = Boot(2000, seed=7)
out = {}
for cell, rr in CELLS.items():
    c = ci['cells'][cell]; T = c['T']
    runs = [json.load(open(f'{BASE}/RUN-ECDLP-612fb1-{i:03d}/raw-result.json')) for i in rr]
    sums = [json.load(open(f'{BASE}/RUN-ECDLP-612fb1-{i:03d}/summary.json')) for i in rr]
    sol = {a: [np.asarray(raw['arms'][a]['solved'], float) for raw in runs] for a in ('NULL-A(T/2)', 'NULL-A(T)', 'STATIC(T)', 'STATIC(T/2)', 'RESEL-L(T/2)', 'STATIC2T')}
    def ps(names, lo, hi):
        return [{n: sol[n][i][lo:hi] for n in names} for i in range(len(runs))]
    # S1 with NULL-A(T/2) in place of RESEL-L(T/2)
    d8 = boot.ci(ps(['NULL-A(T/2)', 'STATIC(T)'], 6 * T, 8 * T), lambda d: pooled_mean(d, 'NULL-A(T/2)') - pooled_mean(d, 'STATIC(T)'))
    s1 = {'diff_8T': d8, 'S1_met_on_NULL_A': bool(d8['hi'] >= 0 and d8['point'] >= -0.03)}
    # NULL-A gain per round (producer's CI table) and my recomputation
    rounds = c['S2_NULL_A']['T/2']['rounds']
    per_round = [{'round': r['round'], 'point': r['point'], 'lo': r['lo'], 'hi': r['hi'], 'ci_contains_zero': r['ci_contains_zero'], 'ci_above_zero': (r['lo'] is not None and r['lo'] > 0)} for r in rounds]
    # S4 for NULL-A: max pooled hit rate vs oracle share / 0.42
    s4 = c['S4_exceedance'].get('NULL-A(T/2)')
    # random-subset reference: expected single-walk coverage of a uniformly random T/2 subset of the r=2 pool = (T/2)/(2T) * STATIC2T coverage
    p2t = c['STATIC2T']['single_walk_hit_rate_pooled_all_rounds']
    p_rand = 0.25 * p2t
    eps_rand = 1 - (1 - p_rand) ** 4
    null_p_last = c['S4_exceedance']['NULL-A(T/2)']['pooled_hit_rate_per_round'][-1]['p']
    out[cell] = {'T': T, 'S1_applied_to_NULL_A': s1,
                 'S2_NULL_A_T2_gain_ss_8T_producer': c['S2_NULL_A']['T/2']['gain_ss_8T'],
                 'S2_NULL_A_T_gain_ss_8T_producer': c['S2_NULL_A']['T']['gain_ss_8T'],
                 'NULL_A_T2_gain_per_round': per_round,
                 'any_round_ci_above_zero': any(r['ci_above_zero'] for r in per_round),
                 'S3_applicable_to_NULL_A': False,
                 'S4_NULL_A': {'max_pooled_hit_rate': s4['max_pooled_hit_rate'], 'any_exact_exceedance': s4.get('any_exact_exceedance'), 'exceeds_0.42': s4.get('exceeds_0.42')},
                 'reference_levels': {'STATIC2T_single_walk_p': p2t, 'random_T2_subset_of_pool_single_walk_p_expected': p_rand,
                                      'random_T2_subset_eps_per_target_k4_expected': eps_rand,
                                      'NULL_A_T2_last_round_single_walk_p': null_p_last,
                                      'NULL_A_T2_eps_ss_16T': float(np.concatenate([x[14 * T:16 * T] for x in sol['NULL-A(T/2)']]).mean()),
                                      'STATIC_T2_eps_ss_16T': float(np.concatenate([x[14 * T:16 * T] for x in sol['STATIC(T/2)']]).mean()),
                                      'RESEL_L_T2_gain_ss_8T': float(np.concatenate([x[6 * T:8 * T] for x in sol['RESEL-L(T/2)']]).mean() - np.concatenate([x[6 * T:8 * T] for x in sol['STATIC(T/2)']]).mean())},
                 'invalidation_rule_5_fires_producer': c['S2_NULL_A']['T/2']['invalidation_rule_5_fires']}
    print(f"\n== {cell} == S1 on NULL-A(T/2): diff {d8['point']:.4f} [{d8['lo']:.4f}, {d8['hi']:.4f}] -> S1 met on NULL-A: {s1['S1_met_on_NULL_A']}")
    print('  NULL-A(T/2) gain per round (point [lo,hi]):', ' '.join(f"r{r['round']}:{r['point']:+.3f}[{r['lo']:+.3f},{r['hi']:+.3f}]" for r in per_round))
    print('  any round CI above zero:', out[cell]['any_round_ci_above_zero'], '| rule 5 fires (producer):', out[cell]['invalidation_rule_5_fires_producer'])
    print('  reference:', {k: round(v, 4) for k, v in out[cell]['reference_levels'].items()})
    print('  S4 on NULL-A:', out[cell]['S4_NULL_A'])
json.dump(out, open(sys.argv[1] + '/j4_nulla.json', 'w'), indent=1)
