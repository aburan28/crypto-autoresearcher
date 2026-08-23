#!/usr/bin/env python3
"""
Assemble pipeline_validation.json from the run results.

Combines: the reproduction check against the frozen ICARM snapshot, the
height-vs-parameter-size falsifier, the Mestre-Nagao ordering vs its
uniform-random control, and the certifier's own negative controls.  Pure
aggregation of files already written by recorded runs -- it computes no new
mathematics except the control statistics below.

usage: python3 summarise_validation.py TASKDIR OUT.json
"""
import glob
import json
import os
import random
import sys

KEY_CURVES = (42, 55, 244, 273, 276, 288)


def permutation_p(a, b, iters=20000, seed=20260823):
    """Two-sided permutation test on the difference of means (exact arithmetic
    is not needed here; this is a control statistic, not a claim)."""
    obs = sum(a) / len(a) - sum(b) / len(b)
    pool = list(a) + list(b)
    rng = random.Random(seed)
    hits = 0
    for _ in range(iters):
        rng.shuffle(pool)
        d = sum(pool[:len(a)]) / len(a) - sum(pool[len(a):]) / len(b)
        if abs(d) >= abs(obs) - 1e-12:
            hits += 1
    return {'observed_mean_difference': obs, 'iterations': iters,
            'p_two_sided': (hits + 1) / (iters + 1), 'seed': seed}


def main(taskdir, outpath):
    res = os.path.join(taskdir, 'results')
    rep = json.load(open(os.path.join(res, 'reproduce_icarm_all.json')))
    retry_path = os.path.join(res, 'reproduce_icarm_conductor_retry.json')
    retry = json.load(open(retry_path)) if os.path.exists(retry_path) else None
    fals = json.load(open(os.path.join(res, 'falsifier_height.json')))
    self_t = json.load(open(os.path.join(res, 'selftest_certifier.json')))

    rows = {r['id']: r for r in rep['rows']}
    key = []
    for cid in KEY_CURVES:
        r = rows.get(cid)
        if not r:
            continue
        key.append({
            'curve_id': cid, 'submitter': r.get('submitter'),
            'rank': {'board': r['board_rank'], 'ours': r['our_certified_rank'],
                     'agrees': r['rank_agrees'],
                     'certified_from': '%d exhibited points, exact arithmetic'
                                       % r['n_board_points']},
            'naive_height': {'board': r['board_naive_height'],
                             'ours': r['our_naive_height'],
                             'abs_diff': r['naive_height_abs_diff']},
            'faltings_height': {'board': r['board_faltings_height'],
                                'ours': r['our_faltings_height'],
                                'abs_diff': r['faltings_height_abs_diff']},
            'conductor': {'board': r['board_conductor'], 'ours': r['our_conductor'],
                          'agrees': r['conductor_agrees']},
        })

    # ---- Mestre-Nagao vs random control, pooled over the pipeline runs ----
    arms = {'mestre_nagao_top': [], 'uniform_random_control': []}
    heights = {'mestre_nagao_top': [], 'uniform_random_control': []}
    per_family = []
    for p in sorted(glob.glob(os.path.join(res, 'pipeline_*.json'))):
        d = json.load(open(p))
        s = d['arm_summary']
        per_family.append({
            'family': d['family']['name'],
            'claimed_generic_rank': d['family']['claimed_generic_rank'],
            'box': d['box'], 'n_parameter_points': d['n_parameter_points'],
            'mestre_nagao_top': s['mestre_nagao_top'],
            'uniform_random_control': s['uniform_random_control'],
        })
        for a in arms:
            arms[a].extend(s[a]['certified_ranks'])
            heights[a].extend([c['invariants']['naive_height']
                               for c in d['arms'][a] if 'invariants' in c])
    pooled = {
        'n_per_arm': {a: len(arms[a]) for a in arms},
        'mean_certified_rank': {a: sum(arms[a]) / len(arms[a]) for a in arms},
        'max_certified_rank': {a: max(arms[a]) for a in arms},
        'mean_naive_height': {a: sum(heights[a]) / len(heights[a]) for a in heights},
        'min_naive_height': {a: min(heights[a]) for a in heights},
        'permutation_test_certified_rank':
            permutation_p(arms['mestre_nagao_top'],
                          arms['uniform_random_control']),
        'permutation_test_naive_height':
            permutation_p(heights['mestre_nagao_top'],
                          heights['uniform_random_control']),
        'interpretation_note': 'Reported as measured differences only. The '
                               'Mestre-Nagao statistic orders candidates and '
                               'never certifies; every rank in both arms comes '
                               'from exact_certify.py.',
    }

    # ---- what the pipeline actually certified, against the frozen frontier
    frontier = json.load(open(os.path.join(
        taskdir, '..', '..', '..', 'baseline', 'frontier_20260823.json')))
    fbt = frontier['frontier_by_rank_threshold']
    produced = []
    for p in sorted(glob.glob(os.path.join(res, 'pipeline_*.json'))):
        d = json.load(open(p))
        for arm, recs in d['arms'].items():
            for c in recs:
                r = c.get('certified_rank', 0)
                if not r or 'invariants' not in c:
                    continue
                fr = fbt.get(str(r))
                produced.append({
                    'family': d['family']['name'], 'arm': arm,
                    'params': c['params'],
                    'certified_rank': r,
                    'naive_height': c['invariants']['naive_height'],
                    'frontier_min_naive_height_at_this_rank':
                        fr['min_naive_height']['value'] if fr else None,
                    'beats_frontier_cell':
                        (c['invariants']['naive_height']
                         < fr['min_naive_height']['value']) if fr else None,
                })
    best = {}
    for c in produced:
        r = c['certified_rank']
        if r not in best or c['naive_height'] < best[r]['naive_height']:
            best[r] = c
    pareto = [best[r] for r in sorted(best)]

    out = {
        'task_id': 'TASK-20260823-01d3d9',
        'goal_id': 'GOAL-ECQ-002',
        'batch_id': 'BATCH-f2341e',
        'hypothesis_id': 'H-ECQ-d60d07',
        'nothing_submitted_to_icarm': True,
        'check_1_reproduction': {
            'snapshot': rep['snapshot'],
            'snapshot_sha256_declared': rep['snapshot_sha256_declared'],
            'definitions_used': rep['definitions'],
            'summary_all_289_curves': rep['summary'],
            'key_curves': key,
            'conductor_timeouts_first_pass': [r['id'] for r in rep['rows']
                                              if r.get('conductor_timed_out')],
            'conductor_retry': (retry['summary'] if retry else None),
            'conductor_retry_rows': ([{'id': r['id'],
                                       'ours': r['our_conductor'],
                                       'board': r['board_conductor'],
                                       'agrees': r['conductor_agrees'],
                                       'timed_out': r['conductor_timed_out']}
                                      for r in retry['rows']] if retry else None),
        },
        'check_2_falsifier_height_vs_parameter_size': {
            'target_naive_height': fals['target_naive_height'],
            'target_source': fals['target_source'],
            'families': [{k: v for k, v in f.items() if k != 'rows'}
                         for f in fals['families']],
        },
        'check_3_mestre_nagao_control': {'per_family': per_family,
                                         'pooled': pooled},
        'check_4_certifier_negative_controls': self_t,
        'check_5_produced_curves_vs_frozen_frontier': {
            'frontier_path': 'coordination/goals/GOAL-ECQ-002/baseline/'
                             'frontier_20260823.json',
            'n_certified_curves_produced': len(produced),
            'best_height_per_certified_rank': pareto,
            'any_frontier_cell_beaten': any(c['beats_frontier_cell']
                                            for c in produced),
            'note': 'These are DEMO families constructed in this task, not the '
                    'campaign base family. Nothing here is submitted.',
        },
    }
    json.dump(out, open(outpath, 'w'), indent=1)
    print('wrote', outpath)
    return out


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
