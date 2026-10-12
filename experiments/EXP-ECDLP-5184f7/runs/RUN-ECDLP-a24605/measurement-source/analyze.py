#!/usr/bin/env python3
"""Prespecified clustered comparisons; no hypothesis or frontier transitions."""
import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from common import sha, write


def interval(values, rng, replicates=10000):
    values = np.asarray(values, dtype=float)
    draws = values[rng.integers(0, len(values), (replicates, len(values)))].mean(axis=1)
    return float(values.mean()), draws


def compare(blocks, value, transform='ratio'):
    rng = np.random.default_rng(2026101111)
    strata, all_values, draws_all = {}, [], []
    for bits in [24, 28, 32]:
        rows = [r[value] for r in blocks if r['bits'] == bits]
        if not rows:
            continue
        mean, draws = interval(rows, rng)
        convert = math.exp if transform == 'ratio' else float
        strata[str(bits)] = {'blocks': len(rows), 'estimate': convert(mean),
                            'CI99': [convert(x) for x in np.quantile(draws, [.005, .995])],
                            'minimum_block_requirement_met': len(rows) >= 8}
        all_values.extend(rows)
        draws_all.append((len(rows), draws))
    if not all_values:
        return None
    overall_draws = sum(n * arr for n, arr in draws_all) / len(all_values)
    convert = math.exp if transform == 'ratio' else float
    return {'estimate': convert(float(np.mean(all_values))),
            'CI99': [convert(x) for x in np.quantile(overall_draws, [.005, .995])],
            'effective_prime_blocks': len(all_values), 'strata': strata,
            'bootstrap': '10000 whole-prime-block replicates, resampled within bit-size strata',
            'scope': 'Specified finite sparse-prime ensemble and matched conditional groups'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prep', type=Path, required=True)
    parser.add_argument('--attacks', type=Path, required=True)
    parser.add_argument('--arithmetic', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    groups = json.loads((args.prep / 'public-groups.json').read_text())
    job_index = json.loads((args.attacks / 'job-index.json').read_text())
    job_lookup = {j['job_id']: j for j in job_index}
    records = []
    for path in sorted(args.attacks.glob('block-*/raw-results.jsonl')):
        for line in path.read_text().splitlines():
            r = json.loads(line)
            r.update(job_lookup[r['job_id']])
            records.append(r)
    by_group = defaultdict(list)
    for r in records:
        by_group[(r['group_id'], r['mode'])].append(r)
    group_metrics = []
    for g in groups:
        for mode in ['rho', 'oracle', 'rho32', 'bsgs']:
            rows = by_group[g['group_id'], mode]
            if not rows:
                continue
            expected = 4 if mode == 'bsgs' else 16
            work = [r['counts']['search']['group_calls'] for r in rows]
            totals = [r['counts']['search']['group_calls'] + r['counts']['setup']['group_calls'] for r in rows]
            normalized = [totals[i] / (r['M'] + g['ell'] / (2 * r['M'])) if mode == 'bsgs'
                          else min(work[i] / math.sqrt(g['ell']), 20) for i, r in enumerate(rows)]
            group_metrics.append({**{k: g[k] for k in ['group_id', 'block', 'arm', 'cohort', 'bits', 'slot', 'ell', 'kind']},
                  'mode': mode, 'attempts': len(rows), 'complete': len(rows) == expected,
                  'normalized_mean': float(np.mean(normalized)), 'search_calls_mean': float(np.mean(work)),
                  'end_to_end_calls_mean': float(np.mean(totals)),
                  'verified_solutions': sum(r['scalar'] is not None for r in rows),
                  'primary_censors': sum(r['censored'] for r in rows) if mode != 'bsgs' else 0,
                  'mean_CPU_seconds': float(np.mean([sum(r['cpu_seconds'][:2]) for r in rows])),
                  'table_bytes_mean': float(np.mean([r['table_allocated_bytes'] for r in rows]))})
    write(out / 'group-metrics.json', group_metrics)
    with (out / 'group-metrics.csv').open('x', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(group_metrics[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(group_metrics)
    matched = {(r['block'], r['slot'], r['arm'], r['mode']): r for r in group_metrics
               if r['kind'] == 'matched' and r['cohort'] == 'main' and r['complete']}
    block_metrics, attack_comparisons = [], {}
    for mode in ['rho', 'oracle', 'rho32', 'bsgs']:
        for control in ['R', 'C']:
            block_rows = []
            for block in range(36):
                pairs = [(matched.get((block, slot, 'S', mode)), matched.get((block, slot, control, mode))) for slot in range(8)]
                pairs = [(s, c) for s, c in pairs if s is not None and c is not None]
                if not pairs:
                    continue
                row = {'block': block, 'bits': pairs[0][0]['bits'], 'mode': mode, 'contrast': 'S/' + control,
                       'matched_curves': len(pairs),
                       'log_ratio': float(np.mean([math.log(s['normalized_mean'] / c['normalized_mean']) for s, c in pairs])),
                       'end_to_end_log_ratio': float(np.mean([math.log(s['end_to_end_calls_mean'] / c['end_to_end_calls_mean']) for s, c in pairs]))}
                block_rows.append(row)
            block_metrics.extend(block_rows)
            attack_comparisons[mode + '_S_' + control] = compare(block_rows, 'log_ratio')
    write(out / 'prime-block-metrics.json', block_metrics)
    sample = json.loads((args.prep / 'prime-sample.json').read_text())
    audit = []
    for m in sample['moduli']:
        curves = json.loads((args.prep / 'curves' / m['id'] / 'curves.json').read_text())['curves'][:32]
        audit.append({**m, 'audited_models': len(curves),
                      'mean_log2_ell': float(np.mean([math.log2(r['ell']) for r in curves])),
                      'mean_generic_proxy_bits': float(np.mean([math.log2(r['ell']) / 2 for r in curves])),
                      'median_cofactor': float(np.median([r['h'] for r in curves])),
                      'obvious_flag_fraction': float(np.mean([any([r['flags']['anomalous'], r['flags']['supersingular'],
                            r['flags']['j_special'], r['flags']['embedding_degree_le20'] is not None]) for r in curves]))})
    write(out / 'unconditional-audit.json', audit)
    population_comparisons = {}
    for control in ['R', 'C']:
        rows = []
        for block in range(36):
            S = next(r for r in audit if r['block'] == block and r['arm'] == 'S')
            C = next(r for r in audit if r['block'] == block and r['arm'] == control)
            rows.append({'block': block, 'bits': S['bits'], 'difference': S['mean_generic_proxy_bits'] - C['mean_generic_proxy_bits']})
        population_comparisons['S_' + control] = compare(rows, 'difference', 'difference')
    attack_result = json.loads((args.attacks / 'attack-result.json').read_text())
    controls = json.loads((args.attacks / 'control-checks.json').read_text())
    easy = [r for r in group_metrics if r['kind'] == 'easy']
    easy_positive = []
    for bits in [24, 28, 32]:
        instrument = next((r for r in easy if r['bits'] == bits and r['mode'] == 'bsgs'), None)
        usual = [r['end_to_end_calls_mean'] for r in group_metrics if r['bits'] == bits and r['mode'] == 'bsgs'
                 and r['cohort'] == 'main' and r['kind'] == 'matched']
        passed = instrument is not None and instrument['complete'] and instrument['verified_solutions'] == 4
        passed = passed and instrument['end_to_end_calls_mean'] < min(usual)
        easy_positive.append({'bits': bits, 'method': 'BSGS instrument positive control', 'pass': bool(passed),
                              'easy_group': instrument, 'minimum_main_raw_work': min(usual)})
    integrity_pass = attack_result['sham_replay_transport_pass'] and not attack_result['failures'] and all(r['pass'] for r in easy_positive)
    primary = attack_comparisons['rho_S_R']
    censoring = {}
    for arm in ['S', 'R', 'C']:
        rows = [r for r in group_metrics if r['mode'] == 'rho' and r['kind'] == 'matched' and r['cohort'] == 'main' and r['arm'] == arm]
        censoring[arm] = sum(r['primary_censors'] for r in rows) / sum(r['attempts'] for r in rows)
    decision = 'inconclusive'
    if primary and integrity_pass and all(r['minimum_block_requirement_met'] for r in primary['strata'].values()):
        lo, hi = primary['CI99']
        if lo > 1.20 and sum(r['estimate'] > 1 for r in primary['strata'].values()) >= 2:
            decision = 'higher measured rho cost; check opaque/independent-walk diagnostics before interpretation'
        elif lo >= 1 / 1.20 and hi <= 1.20:
            decision = 'practically similar normalized rho cost in the sampled scope'
    arithmetic_rows = []
    for path in args.arithmetic.glob('m*/result.json'):
        data = json.loads(path.read_text())
        for obs in data['observations']:
            arithmetic_rows.append({**data['modulus'], **obs})
    arithmetic_summary = {}
    for workload in ['products', 'inversions', 'point_additions']:
        block_values = []
        specialized_ratios = []
        for block in range(36):
            means = {}
            for arm in ['S', 'R', 'C']:
                rows = [r['seconds_per_operation'] for r in arithmetic_rows if r['block'] == block and r['arm'] == arm
                        and r['workload'] == workload and r['backend'] == 'generic']
                if rows:
                    means[arm] = float(np.median(rows))
            special = [r['seconds_per_operation'] for r in arithmetic_rows if r['block'] == block and r['arm'] == 'S'
                       and r['workload'] == workload and r['backend'] == 'sparse']
            if len(means) == 3 and special:
                block_values.append({'block': block, 'bits': next(r['bits'] for r in audit if r['block'] == block),
                                     'log_ratio_R': math.log(means['S'] / means['R']),
                                     'log_ratio_C': math.log(means['S'] / means['C'])})
                specialized_ratios.append(float(np.median(special)) / means['S'])
        arithmetic_summary[workload] = {'generic_S_R': compare(block_values, 'log_ratio_R'),
                                       'generic_S_C': compare(block_values, 'log_ratio_C'),
                                       'median_sparse_over_generic_S_seconds': float(np.median(specialized_ratios)) if specialized_ratios else None,
                                       'scope': 'Python prototype, inversions identical implementation; no deployed reduction-speed claim'}
    summary = {'experiment_id': 'EXP-ECDLP-5184f7', 'run_id': args.prep.parent.name,
               'decision': decision, 'claim_scope': 'Observed attack-specific toy benchmark; no general ECDLP-resistance or asymptotic claim',
               'main_prime_blocks': 36, 'main_moduli': 108, 'anchor_moduli': 18,
               'main_unconditional_curves': 108 * 32, 'all_prepared_curves': 61632,
               'attack_attempts': len(records), 'attack_execution': attack_result,
               'attack_comparisons': attack_comparisons, 'population_generic_proxy_difference_bits': population_comparisons,
               'primary_censor_fractions': censoring, 'restricted_horizon': 20,
               'cap_limited_inference_required': any(v > .05 for v in censoring.values()),
               'integrity_controls_pass': bool(integrity_pass), 'easy_positive_controls': easy_positive,
               'control_check_count': len(controls), 'easy_rho_observations': [r for r in easy if r['mode'] == 'rho'],
               'arithmetic': arithmetic_summary, 'arithmetic_observation_rows': len(arithmetic_rows),
               'input_hashes': {'preparation_result': sha(args.prep / 'preparation-result.json'),
                                'attack_result': sha(args.attacks / 'attack-result.json'),
                                'arithmetic_result': sha(args.arithmetic / 'arithmetic-result.json')},
               'analysis_source_sha256': sha(Path(__file__)), 'independent_scientific_review': None}
    write(out / 'summary.json', summary)
    print(json.dumps({'decision': decision, 'primary': primary, 'integrity_controls_pass': integrity_pass}, indent=2))


if __name__ == '__main__':
    main()
