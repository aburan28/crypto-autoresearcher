#!/usr/bin/env python3
"""STEP 6 -- assemble the two JSON deliverables from the recorded run results.

Reads ONLY files already written by runs 001-009.  Recomputes every reported
naive height from the minimal a-invariants alone, in stdlib-only integer
arithmetic independent of PARI, as review_plan prior P1 asks.
"""
import json, math, os, sys

T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(T, 'results')

TARGETS = [
    {'rank_threshold': 12, 'metric': 'naive_height', 'incumbent': 69.33878142645637,
     'icarm_curve_id': 157, 'falsifier_file': 'falsifier_height_004.json'},
    {'rank_threshold': 13, 'metric': 'naive_height', 'incumbent': 75.75973380404125,
     'icarm_curve_id': 158, 'falsifier_file': 'falsifier_height_005.json'},
    {'rank_threshold': 14, 'metric': 'naive_height', 'incumbent': 85.18925824647027,
     'icarm_curve_id': 244, 'falsifier_file': 'falsifier_height_006.json'},
]

def naive_height_from_ainvs(ai):
    """log max(|c4|^3, c6^2) from a-invariants, stdlib integers only."""
    a1, a2, a3, a4, a6 = [int(x) for x in ai]
    b2 = a1 * a1 + 4 * a2
    b4 = 2 * a4 + a1 * a3
    b6 = a3 * a3 + 4 * a6
    c4 = b2 * b2 - 24 * b4
    c6 = -b2 ** 3 + 36 * b2 * b4 - 216 * b6
    return {'c4': str(c4), 'c6': str(c6),
            'naive_height': math.log(max(abs(c4) ** 3, c6 * c6))}

def load(name):
    return json.load(open(os.path.join(R, name)))

def main():
    s1 = load('step1_nagao_identity.json')
    s2 = load('step2_weierstrass.json')
    s2b = load('step2b_minimalisation.json')
    fal = {t['rank_threshold']: load(t['falsifier_file'])['families'][0] for t in TARGETS}
    wide = load('falsifier_height_probe_wide.json')['families'][0]
    probe = load('step5b_rank_probe.json')

    base = fal[12]                                   # identical fit in 004/005/006
    fit = base['fit_naive_height_vs_log_param_size']
    a, b, r2 = fit['intercept'], fit['slope'], fit['r_squared']
    ok = [r for r in base['rows'] if r['status'] == 'measured']
    okw = [r for r in wide['rows'] if r['status'] == 'measured']
    all_rows = {(r['params']['t']): r for r in ok}
    all_rows.update({(r['params']['t']): r for r in okw})
    measured_min = min(r['naive_height'] for r in all_rows.values())
    argmin = min(all_rows.values(), key=lambda r: r['naive_height'])

    # independent recomputation of the reported heights
    indep = []
    for row in s2b['rows']:
        if row['status'] != 'measured':
            continue
        rc = naive_height_from_ainvs(row['minimal_a_invariants'])
        indep.append({'t': row['t'], 'minimal_a_invariants': row['minimal_a_invariants'],
                      'pari_naive_height': row['naive_height_after_minimalisation'],
                      'recomputed_naive_height': rc['naive_height'],
                      'c4': rc['c4'], 'c6': rc['c6'],
                      'agrees_to_1e-9': abs(rc['naive_height'] -
                                            row['naive_height_after_minimalisation']) < 1e-9})
    for row in probe['rows']:
        sr = row.get('submission_record') or {}
        mai = sr.get('a_invariants') or sr.get('minimal_a_invariants')
        if mai:
            rc = naive_height_from_ainvs(mai)
            indep.append({'t': row['t'], 'minimal_a_invariants': [str(x) for x in mai],
                          'pari_naive_height': row['naive_height'],
                          'recomputed_naive_height': rc['naive_height'],
                          'c4': rc['c4'], 'c6': rc['c6'],
                          'agrees_to_1e-9': abs(rc['naive_height'] - row['naive_height']) < 1e-9,
                          'certified_rank_lower_bound': row['certified_rank_lower_bound']})

    budget = {
      'task': 'TASK-20260823-f88f54', 'batch': 'BATCH-da59ec', 'goal': 'GOAL-ECQ-002',
      'hypothesis': 'H-ECQ-a609f8', 'family': 'NAGAO-1994',
      'produced_by': 'executor', 'requested_policy': 'executor-implementation',
      'resolved_model': 'claude-opus-5', 'fallback_used': False,
      'conventions': {
        'naive_height': 'log max(|c4|^3, c6^2) on the MINIMAL model (pinned by BATCH-f2341e CHECK 1)',
        'faltings_height': '-1/2 log(covolume of the period lattice); NO (1/12)log|Delta| term',
        'parameter_size_H': 'max(|num t|, den t)',
      },
      'step1_self_consistency': {
        'identity': s1['identity_tested'], 'point': s1['point_tested'],
        'n_coefficients_compared': s1['n_coefficients_compared'],
        'ratio_constant_across_all_coefficients': s1['ratio_is_constant_across_all_coefficients'],
        'ratio': s1['ratio'], 'ratio_is_1248_squared': s1['ratio_is_1248_squared'],
        'point_lies_exactly_on_transcribed_quartic': s1['point_lies_exactly_on_transcribed_quartic'],
        'coordinator_claim_reproduced': s1['coordinator_claim_reproduced'],
        'batch_f2341e_verdict_overturned': True,
        'scope': 'SELF-CONSISTENCY ONLY. This is not proof the coefficients are Nagao published '
                 'equation; source retrieval remains owed.',
        'per_coefficient': s1['per_coefficient'],
        'run': 'RUN-ECQNAG-f88f54-001',
      },
      'step2_weierstrass_conversion': {
        'method': s2['method'],
        'weierstrass_over_Qt': s2['weierstrass_over_Qt'],
        'quartic_coefficient_sizes': s2['quartic_coefficient_sizes'],
        'weierstrass_sizes_before_minimalisation': s2['weierstrass_coefficient_sizes_before_minimalisation'],
        'surface_degree_check': s2['surface_degree_check'],
        'independent_crosscheck': {
          'method': 'PARI ellfromeqn on the specialised quartic vs specialisation of the I/J model, '
                    'compared on minimal-model curve_key',
          'n_compared': s2b['n_measured'], 'agreements': s2b['crosscheck_agreements'],
          'disagreements': s2b['crosscheck_disagreements']},
        'runs': ['RUN-ECQNAG-f88f54-002', 'RUN-ECQNAG-f88f54-003'],
      },
      'minimalisation_measured': {
        'question': 'how much does minimalisation strip from the naive height',
        'naive_height_before_minimalisation_range': [
            min(r['naive_height_before_minimalisation'] for r in s2b['rows'] if r['status'] == 'measured'),
            max(r['naive_height_before_minimalisation'] for r in s2b['rows'] if r['status'] == 'measured')],
        'naive_height_after_minimalisation_range': [
            min(r['naive_height_after_minimalisation'] for r in s2b['rows'] if r['status'] == 'measured'),
            max(r['naive_height_after_minimalisation'] for r in s2b['rows'] if r['status'] == 'measured')],
        'stripped_min': min(r['naive_height_stripped_by_minimalisation'] for r in s2b['rows'] if r['status'] == 'measured'),
        'stripped_median': s2b['median_stripped'],
        'stripped_max': max(r['naive_height_stripped_by_minimalisation'] for r in s2b['rows'] if r['status'] == 'measured'),
        'per_t': [{k: r[k] for k in ('t', 'naive_height_before_minimalisation',
                                     'naive_height_after_minimalisation',
                                     'naive_height_stripped_by_minimalisation',
                                     'c4_digits_before', 'c4_digits_after',
                                     'c6_digits_before', 'c6_digits_after')}
                  for r in s2b['rows'] if r['status'] == 'measured'],
        'statement': 'Minimalisation strips a LOT (about 99-120 in naive height, i.e. the model '
                     'shrinks by ~43-52 decimal digits in c4^3/c6^2) -- review_plan prior P2 holds -- '
                     'and it is still not nearly enough: what survives is ~110-174.',
      },
      'height_fit_measured': {
        'model': 'naive_height = a + b * log H(t), least squares',
        'declared_box': base['box'],
        'n_points_measured': base['n_points_measured'],
        'n_infrastructure_timeouts': base['n_infrastructure_timeouts'],
        'a_intercept': a, 'b_slope': b, 'r_squared': r2,
        'min_naive_height_in_declared_box': base['min_naive_height'],
        'median_naive_height_in_declared_box': base['median_naive_height'],
        'max_naive_height_in_declared_box': base['max_naive_height'],
        'interpretation_of_R2': 'R^2 = %.6f: over the declared box the parameter size explains '
                                'essentially NONE of the height variation. The family constants '
                                'dominate; the small-parameter lever does not operate here. The '
                                'fit-derived budget is therefore reported but NOT used as the '
                                'deciding number -- the EXACT measured minimum is.' % r2,
        'runs': ['RUN-ECQNAG-f88f54-004', 'RUN-ECQNAG-f88f54-005', 'RUN-ECQNAG-f88f54-006'],
      },
      'wide_probe': {
        'why': 'robustness of an EMPTY box in the only direction that could overturn it: does the '
               'lower envelope keep falling outside the declared box? Recorded as a separate probe, '
               'never merged into the declared measurement.',
        'box': wide['box'], 'n_points_measured': wide['n_points_measured'],
        'fit': wide['fit_naive_height_vs_log_param_size'],
        'min_naive_height': wide['min_naive_height'],
        'argmin_t': min(okw, key=lambda r: r['naive_height'])['params'],
        'n_below_lowest_target': sum(1 for r in okw if r['naive_height'] < 69.33878142645637),
        'run': 'RUN-ECQNAG-f88f54-007',
      },
      'measured_minimum_over_all_fibres': {
        'n_distinct_parameters_measured': len(all_rows),
        'min_naive_height': measured_min,
        'argmin': argmin['params'],
        'argmin_faltings_height': argmin['faltings_height'],
      },
      'admissible_parameter_box_per_target': [],
      'independent_height_recomputation_from_a_invariants': indep,
      'rank_probe_secondary': {
        'status': 'SECONDARY. The box is empty, so no sieve and NO Mestre-Nagao ordering was run. '
                  'This probe informs review_plan P3 and falsification clause 2 only.',
        'discipline': probe['discipline'],
        'rank_time_limit_seconds': probe['rank_time_limit_seconds'],
        'rows': [{k: r[k] for k in ('t', 'certified_rank_lower_bound', 'n_points_exhibited',
                                    'pari_search_r_low', 'pari_search_r_high',
                                    'pari_search_seconds', 'naive_height', 'curve_key')}
                 for r in probe['rows']],
        'run': 'RUN-ECQNAG-f88f54-009',
        'superseded_run': 'RUN-ECQNAG-f88f54-008 (implementation_error, preserved)',
      },
    }

    reach = {'task': 'TASK-20260823-f88f54', 'hypothesis': 'H-ECQ-a609f8',
             'family': 'NAGAO-1994', 'metric': 'naive_height (minimal model)',
             'frozen_frontier': 'coordination/goals/GOAL-ECQ-002/baseline/frontier_20260823.json',
             'gate_order': 'EXACT HEIGHT GATE FIRST. Mestre-Nagao ordering was NOT run: '
                           'the admissible set is empty, so there was nothing to order.',
             'nothing_submitted_to_icarm': True,
             'targets': []}

    for t in TARGETS:
        h = t['incumbent']
        fit_budget = (h - a) / b if b > 0 else None
        n_below_decl = sum(1 for r in ok if r['naive_height'] < h)
        n_below_all = sum(1 for r in all_rows.values() if r['naive_height'] < h)
        entry = {
          'rank_threshold': t['rank_threshold'], 'incumbent_naive_height': h,
          'icarm_curve_id': t['icarm_curve_id'],
          'fit_derived_max_log_param_size': fit_budget,
          'fit_derived_max_param_size_H': (math.exp(fit_budget) if fit_budget is not None
                                           and fit_budget < 700 else None),
          'fit_derived_box_empty': (fit_budget is not None and math.exp(fit_budget) < 1),
          'exact_gate': {
            'n_fibres_tested': len(all_rows),
            'n_fibres_with_naive_height_below_incumbent': n_below_all,
            'n_in_declared_box_below_incumbent': n_below_decl,
            'measured_min_naive_height': measured_min,
            'deficit_measured_min_minus_incumbent': measured_min - h,
          },
          'admissible_box': 'EMPTY' if n_below_all == 0 else 'NON-EMPTY',
          'deciding_number': ('measured minimum naive height %.6f over %d distinct fibres exceeds '
                              'the incumbent %.6f by %.6f' % (measured_min, len(all_rows), h,
                                                              measured_min - h)),
        }
        budget['admissible_parameter_box_per_target'].append(entry)
        reach['targets'].append({
          'rank_threshold': t['rank_threshold'], 'incumbent_naive_height': h,
          'reachable_by_NAGAO_1994_as_measured': (n_below_all > 0),
          'admissible_box': entry['admissible_box'],
          'deciding_number': entry['deciding_number'],
          'measured_min_naive_height': measured_min,
          'gap_to_incumbent': measured_min - h,
          'certified_curve_taking_this_cell': None,
          'scope': 'Scoped to the transcribed NAGAO-1994 quartic, its Jacobian Weierstrass model, '
                   'and rational t with |num| <= 60, den <= 6 (declared box, 457 fibres) plus the '
                   'integer probe |t| <= 400 (801 fibres); 1258 distinct parameters, 0 infrastructure '
                   'timeouts. No statement is made about other models of the same surface, other '
                   'families, or parameters outside these boxes.',
        })
    reach['excluded_cells_not_targeted'] = [
        {'rank_threshold': 15, 'reason': 'EXCLUDED by H-ECQ-a609f8; not targeted, not claimed'},
        {'rank_threshold': 1, 'reason': 'EXCLUDED by H-ECQ-a609f8; not targeted, not claimed'}]
    reach['summary'] = ('All three pre-declared admissible boxes are EMPTY. Measured height budget: '
                        'naive_height = %.4f + %.4f log H(t) (R^2 = %.6f) over the declared box; '
                        'measured minimum %.6f over 1258 fibres, against targets 69.338781 / '
                        '75.759734 / 85.189258.' % (a, b, r2, measured_min))

    json.dump(budget, open(os.path.join(T, 'nagao_height_budget.json'), 'w'), indent=1)
    json.dump(reach, open(os.path.join(T, 'cell_reachability.json'), 'w'), indent=1)
    print(reach['summary'])
    print('independent height recomputation: %d/%d agree to 1e-9'
          % (sum(1 for x in indep if x['agrees_to_1e-9']), len(indep)))
    for e in reach['targets']:
        print('r>=%d  incumbent %.6f  box %s  gap %+.6f'
              % (e['rank_threshold'], e['incumbent_naive_height'], e['admissible_box'],
                 e['gap_to_incumbent']))

if __name__ == '__main__':
    main()
