"""Frozen five-case instrument; scientific execution requires separate authority.

This source is an implementation candidate. The command-line entrypoint refuses
scientific execution until the canonical LOCKED/manifest integration is resolved.
The run_case function is the complete instrument for a future admitted wrapper.
"""
from __future__ import annotations
import argparse
from collections import Counter
from itertools import combinations_with_replacement
import json
from math import comb
from pathlib import Path
import resource
import sys
import time
import traceback

import group_oracle
import incidence
import presentation_inventory

EXPERIMENT = 'EXP-ECDLP-2cb7f8'
SPEC_SHA256 = 'e7ea730e68d674a4de0ef6cdbc159d98ff4473a9b9539f9b18b1da52c936659e'
BINDINGS = (
    ('E5', 5, 1, 'RUN-ECDLP-3c6277'),
    ('E7', 7, 1, 'RUN-ECDLP-413b2a'),
    ('E11', 11, 1, 'RUN-ECDLP-b0a390'),
    ('E17', 17, 1, 'RUN-ECDLP-d7d29d'),
    ('N0-Eprime5', 5, 2, 'RUN-ECDLP-e2e77c'),
)
ARTIFACT_NAMES = ('manifest.yaml', 'inputs.json', 'points.json', 'divisors.jsonl',
                  'sections.jsonl', 'correspondence.json', 'controls.json',
                  'presentation-inventory.json', 'metrics.json', 'anomalies.jsonl',
                  'stdout.txt', 'stderr.txt')


def dumps(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def config_checked(config):
    expected = {'experiment_id', 'version', 'case_id', 'p', 'curve_constant', 'run_id'}
    if not isinstance(config, dict) or set(config) != expected:
        raise ValueError('configuration must contain exactly the frozen six fields')
    if config['experiment_id'] != EXPERIMENT or type(config['version']) is not int or config['version'] != 1:
        raise ValueError('wrong experiment/version')
    if type(config['p']) is not int or type(config['curve_constant']) is not int:
        raise ValueError('field and curve constant must be exact integers, not booleans')
    binding = tuple(config[k] for k in ('case_id', 'p', 'curve_constant', 'run_id'))
    if binding not in BINDINGS:
        raise ValueError('case/field/curve/RUN binding is not frozen')
    return config


def json_file(directory, name, value):
    with (directory / name).open('x', encoding='utf-8') as stream:
        stream.write(dumps(value) + '\n')


def add_control(rows, name, actual, expected):
    rows.append({'id': name, 'actual': actual, 'expected': expected,
                 'passed': actual == expected})


def controls(config, points, oracle):
    field, constant, rows = incidence.Field(config['p']), config['curve_constant'], []
    for name, coefficients, expected_points in (
        ('K4-infinity-positive', (1, 0, 0, 0), [None] * 4),
        ('K5-split-multiplicity-positive', (0, 0, 0, 1),
         [(0, 1)] * 2 + [(0, field.p-1)] * 2),
    ):
        # The named K4/K5 are scheduled only on the four original E cases.
        if constant != 1:
            continue
        certificate = incidence.recover(coefficients, constant, field)
        divisor = sorted(points.index(point) for point in expected_points)
        matrix = incidence.jet_matrix(divisor, points, constant, field, 'I')
        kernel = incidence.rank_kernel(matrix, field)
        actual = {'admissible': certificate['admissible'],
                  'points': certificate['recovered_divisor_points'],
                  'rank': kernel['rank'], 'section': kernel['unique_section'],
                  'group_sum': incidence.encode_point(oracle.sum4(expected_points))}
        expected = {'admissible': True,
                    'points': [incidence.encode_point(point) for point in sorted(expected_points, key=incidence.point_key)],
                    'rank': 3, 'section': list(coefficients), 'group_sum': {'infinity': True}}
        add_control(rows, name, actual, expected)
        rows[-1]['certificate'] = certificate
    if config['case_id'] == 'E5':
        vector, c = [1, 0, 0, 0], [0, 0, 0, 1]
        residuals = incidence.projective_residuals(vector, constant, field)
        linear = 0
        for x, y in zip(vector, c):
            linear = field.add(linear, field.mul(x, y))
        add_control(rows, 'K1-off-curve-ambient',
                    {'X': vector, 'c': c, 'linear': linear, 'quadrics': residuals,
                     'membership_rejected': residuals != [0, 0]},
                    {'X': vector, 'c': c, 'linear': 0, 'quadrics': [0, 4], 'membership_rejected': True})
        cert = incidence.recover((1, 4, 0, 0), constant, field)
        add_control(rows, 'K2-nonsplit-rational-section',
                    {**{k: cert[k] for k in ('admissible', 'O_multiplicity', 'unresolved_degree')},
                     'square_witnesses': cert['square_witnesses']},
                    {'admissible': False, 'O_multiplicity': 2, 'unresolved_degree': 2,
                     'square_witnesses': [{'x': 1, 'rhs': 3, 'roots_y': [], 'squares': [0, 1, 4]}]})
        rows[-1]['certificate'] = cert
        point, c = (0, 1), (0, 0, 0, 1)
        basis = incidence.local_basis(point, constant, field)
        series = incidence.section_series(c, basis, field)
        cert = incidence.recover(c, constant, field)
        group_sum = oracle.sum4([point] * 4)
        add_control(rows, 'K3-repeated-row-false-positive',
                    {'ordinary_rows': [series[0]]*4, 'series': series,
                     'order': incidence.order_of(series, field),
                     'group_sum': incidence.encode_point(group_sum),
                     'recovered': cert['recovered_divisor_points']},
                    {'ordinary_rows': [0]*4, 'series': [0, 0, 1, 0, 0], 'order': 2,
                     'group_sum': {'infinity': False, 'x': 3, 'y': 4},
                     'recovered': [{'infinity': False, 'x': 0, 'y': 1}]*2
                                  + [{'infinity': False, 'x': 0, 'y': 4}]*2})
        rows[-1]['certificate'] = cert
    if constant == 2:
        wrong_curve = []
        for point in points:
            if point is not None:
                residual = field.sub(field.mul(point[1], point[1]), incidence.rhs(point[0], 1, field))
                wrong_curve.append({'point': incidence.encode_point(point), 'original_residual': residual})
        cert = incidence.recover((1, 4, 0, 0), constant, field)
        common = incidence.recover((1, 0, 0, 0), constant, field)
        expected_points = [None, None, (1, 2), (1, 3)]
        add_control(rows, 'N0-unrelated-linear-section',
                    {'all_finite_original_residuals_one': all(row['original_residual'] == 1 for row in wrong_curve),
                     'example': cert['recovered_divisor_points'], 'example_admissible': cert['admissible'],
                     'shared_4O': common['recovered_divisor_points']},
                    {'all_finite_original_residuals_one': True,
                     'example': [incidence.encode_point(x) for x in expected_points],
                     'example_admissible': True, 'shared_4O': [{'infinity': True}]*4})
        rows[-1].update(finite_membership_certificates=wrong_curve,
                        example_certificate=cert, common_certificate=common)
    return rows, dict(field.counts)


def delta(after, before):
    return {key: after.get(key, 0)-before.get(key, 0) for key in set(after) | set(before)}


def run_case(config, directory, manifest_context):
    """Future admitted wrapper only; no invocation is made by this implementation task.

    The wrapper owns mkdir/no-clobber, process-limit enforcement, canonical locked
    plan verification, immutable manifest/log creation, actual runtime provenance,
    and exact directory binding. This instrument verifies its own directory and
    refuses missing semantic/authority gates supplied by that future wrapper.
    """
    config = config_checked(config)
    root = Path(__file__).resolve().parents[3]
    required = root / 'experiments' / EXPERIMENT / 'runs' / config['run_id']
    directory = Path(directory)
    if directory.resolve() != required or not directory.is_dir():
        raise ValueError('run directory must be precreated by the admitted wrapper at the frozen path')
    if any((directory / name).exists() for name in ARTIFACT_NAMES if name not in ('stdout.txt', 'stderr.txt')):
        raise FileExistsError('instrument artifacts already exist; reruns/overwrites are prohibited')
    gates = ('canonical_lock_verified', 'scientific_authority_verified', 'claim_verified',
             'source_snapshot_verified', 'semantic_gate_verified', 'memory_limit_enforced')
    if any(manifest_context.get(gate) is not True for gate in gates):
        raise PermissionError('future admitted wrapper has not verified all scientific execution gates')
    encoded_context = dumps(manifest_context).lower()
    if 'bedrock' in encoded_context:
        raise PermissionError('prohibited inference backend')
    started_wall, started_cpu = time.perf_counter(), time.process_time()
    timings, operations, anomalies, controls_rows = {}, {}, [], []
    field = incidence.Field(config['p'])
    constant, p = config['curve_constant'], config['p']
    oracle = group_oracle.Oracle(p, constant)
    json_file(directory, 'inputs.json', config)
    with (directory / 'anomalies.jsonl').open('x', encoding='utf-8') as anomaly_stream:
        def anomaly(value):
            anomalies.append(value)
            anomaly_stream.write(dumps(value) + '\n')
            anomaly_stream.flush()
        stage_wall, stage_cpu = time.perf_counter(), time.process_time()
        # Smoothness is checked on the actual frozen curve, including Eprime.
        disc = field.mul(-16, field.add(4, field.mul(27, field.mul(constant, constant))))
        if field.eq(disc, 0):
            anomaly({'kind': 'smoothness_gate', 'discriminant': disc})
            raise ArithmeticError('frozen curve is singular; no replacement allowed')
        points = incidence.enumerate_points(constant, field)
        independent_points = oracle.points()
        if independent_points != points:
            anomaly({'kind': 'point_enumeration_mismatch',
                     'incidence': [incidence.encode_point(q) for q in points],
                     'oracle': [incidence.encode_point(q) for q in independent_points]})
            raise ArithmeticError('point enumeration disagreement')
        embedding_certificates = []
        for point in points:
            vector = [0, 0, 0, 1] if point is None else [1, point[0], point[1], field.mul(point[0], point[0])]
            inverse = incidence.projective_inverse(vector, constant, field)
            if inverse != point:
                anomaly({'kind': 'embedding_roundtrip_failure', 'point': incidence.encode_point(point), 'vector': vector})
                raise ArithmeticError('embedding inverse roundtrip failure')
            embedding_certificates.append({'point': incidence.encode_point(point), 'quartic': vector,
                                           'inverse': incidence.encode_point(inverse)})
        json_file(directory, 'points.json', {'N_p': len(points), 'points': [incidence.encode_point(q) for q in points],
                                            'embedding_certificates': embedding_certificates})
        audit = oracle.audit(independent_points)
        controls_rows.append({'id': 'G0-geometric-group-law', **audit})
        if not audit['passed']:
            json_file(directory, 'controls.json', controls_rows)
            for failure in audit['failures']:
                anomaly(failure)
            raise ArithmeticError('group oracle audit failed')
        control_result, control_operations = controls(config, points, oracle)
        controls_rows.extend(control_result)
        timings['1-instrument-and-known-false-gate'] = {'wall_seconds': time.perf_counter()-stage_wall,
                                                       'cpu_seconds': time.process_time()-stage_cpu}
        operations['shared_setup_and_controls'] = {'incidence': dict(field.counts),
                                                   'group': dict(oracle.counts),
                                                   'control_incidence': control_operations}
        if any(not row['passed'] for row in controls_rows):
            json_file(directory, 'controls.json', controls_rows)
            for row in controls_rows:
                if not row['passed']:
                    anomaly({'kind': 'failed_control', 'control': row})
            raise ArithmeticError('known-false or positive control failed')
        stage_wall, stage_cpu = time.perf_counter(), time.process_time()
        group_before = dict(oracle.counts)
        # These group outputs stay only in the orchestrator. They are NEVER
        # passed into any incidence/recovery or symbolic compiler function.
        group_sums = dict(oracle.divisors(independent_points))
        group_divisors = {d for d, result in group_sums.items() if result is None}
        histogram = oracle.ordered_histogram(independent_points)
        operations['group_exhaustion'] = delta(oracle.counts, group_before)
        arm_fields = {'B': incidence.Field(p), 'I': incidence.Field(p)}
        accepted = {'B': {}, 'I': {}}
        rank_histograms = {'B': Counter(), 'I': Counter()}
        recovered, coefficient_to_divisor, occupancy = {}, {}, Counter()
        inverse_field = incidence.Field(p)
        partitions_seen, residual_degrees = Counter(), Counter()
        recovery_statistics = Counter(root_division_steps=0, rational_roots=0,
                                      local_membership_tests=0, square_witness_tests=0,
                                      output_coefficient_bytes=0, input_coefficient_bytes=0,
                                      recovery_certificate_bytes=0)
        baseline_mismatches = 0
        section_vectors_seen, section_rows, scale_collisions = set(), 0, []
        with (directory / 'divisors.jsonl').open('x', encoding='utf-8') as stream:
            for divisor in combinations_with_replacement(range(len(points)), 4):
                row = {'divisor': divisor, 'orbit_weight': group_oracle.orbit_weight(divisor),
                       'group_sum': incidence.encode_point(group_sums[divisor]), 'arms': {}}
                partition = ','.join(map(str, sorted(Counter(divisor).values(), reverse=True)))
                partitions_seen[partition] += 1
                for arm in ('B', 'I'):
                    f = arm_fields[arm]
                    try:
                        matrix = incidence.jet_matrix(divisor, points, constant, f, arm)
                        kernel = incidence.rank_kernel(matrix, f)
                        rank_histograms[arm][str(kernel['rank'])] += 1
                        result = {'matrix': matrix, **kernel}
                        if kernel['rank'] < 3:
                            anomaly({'kind': 'rank_below_three', 'divisor': divisor, 'arm': arm, 'certificate': result})
                        if kernel['rank'] == 3:
                            c = kernel['unique_section']
                            residual = []
                            for matrix_row in matrix:
                                value = 0
                                for a, b in zip(matrix_row, c):
                                    value = f.add(value, f.mul(a, b))
                                residual.append(value)
                            result['kernel_residual'] = residual
                            if any(not f.eq(value, 0) for value in residual):
                                anomaly({'kind': 'kernel_residual_failure', 'divisor': divisor, 'arm': arm, 'certificate': result})
                                raise ArithmeticError('A_D*c is nonzero')
                            certificate = incidence.recover(c, constant, f)
                            result['recovery'] = certificate
                            actual = certificate['recovered_divisor_points']
                            expected = [incidence.encode_point(points[i]) for i in divisor]
                            result['roundtrip_matches'] = certificate['admissible'] and actual == expected
                            if not result['roundtrip_matches']:
                                anomaly({'kind': 'forward_recovery_mismatch', 'divisor': divisor,
                                         'arm': arm, 'certificate': certificate})
                            accepted[arm][divisor] = tuple(c)
                        row['arms'][arm] = result
                    except Exception as error:
                        row['arms'][arm] = {'error': str(error), 'type': type(error).__name__}
                        anomaly({'kind': 'incidence_exception', 'divisor': divisor, 'arm': arm,
                                 'error': str(error), 'traceback': traceback.format_exc()})
                if row['arms']['B'] != row['arms']['I']:
                    baseline_mismatches += 1
                    anomaly({'kind': 'L0_arm_mismatch', 'divisor': divisor, 'certificate': row})
                stream.write(dumps(row) + '\n')
        with (directory / 'sections.jsonl').open('x', encoding='utf-8') as stream:
            for coefficients in incidence.sections(inverse_field):
                section_rows += 1
                normalized = incidence.normalize(coefficients, inverse_field)
                if normalized in section_vectors_seen:
                    scale_collisions.append(coefficients)
                    anomaly({'kind': 'coefficient_scale_collision', 'coefficients': coefficients})
                section_vectors_seen.add(normalized)
                try:
                    certificate = incidence.recover(coefficients, constant, inverse_field)
                    residual_degrees[str(certificate['unresolved_degree'])] += 1
                    recovery_statistics['root_division_steps'] += len(certificate['divisions'])
                    recovery_statistics['rational_roots'] += len(certificate['rational_roots'])
                    recovery_statistics['local_membership_tests'] += len(certificate['local_multiplicities'])
                    recovery_statistics['square_witness_tests'] += len(certificate['square_witnesses']) * p
                    recovery_statistics['input_coefficient_bytes'] += len(dumps(coefficients).encode())
                    recovery_statistics['output_coefficient_bytes'] += len(dumps({
                        'coefficients': certificate['coefficients'],
                        'polynomial': certificate['polynomial'],
                        'residual': certificate['residual_polynomial'],
                        'division_quotients': [d['quotient'] for d in certificate['divisions']],
                        'local_series': [[m['B_series'], m['I_series']] for m in certificate['local_multiplicities']]
                    }).encode())
                    recovery_statistics['recovery_certificate_bytes'] += len(dumps(certificate).encode())
                    if certificate['admissible']:
                        support = [incidence.decode_point(q) for q in certificate['recovered_divisor_points']]
                        divisor = tuple(points.index(q) for q in support)
                        certificate['divisor'] = divisor
                        # The inverse has already returned. Independent checking
                        # is here, never inside recover and never a lookup.
                        sum_point = oracle.sum4(support)
                        certificate['independent_group_sum'] = incidence.encode_point(sum_point)
                        if sum_point is not None:
                            anomaly({'kind': 'inverse_group_mismatch', 'certificate': certificate})
                        if divisor in recovered:
                            anomaly({'kind': 'multiple_sections_for_divisor', 'divisor': divisor,
                                     'first': recovered[divisor], 'second': coefficients})
                        recovered[divisor] = tuple(coefficients)
                        coefficient_to_divisor[tuple(coefficients)] = divisor
                        occupancy[presentation_inventory.occupancy_key(divisor, points, coefficients)] += 1
                        if constant == 2:
                            certificate['original_E_membership'] = [
                                incidence.membership(q, 1, inverse_field) for q in support]
                            if any(q is not None for q in support) and all(certificate['original_E_membership']):
                                anomaly({'kind': 'N0_original_E_false_accept', 'certificate': certificate})
                    stream.write(dumps(certificate) + '\n')
                except Exception as error:
                    value = {'coefficients': coefficients, 'kind': 'recovery_exception',
                             'error': str(error), 'traceback': traceback.format_exc()}
                    anomaly(value)
                    stream.write(dumps(value) + '\n')
        controls_rows.append({'id': 'L0-complete-linear-equivalence', 'passed': baseline_mismatches == 0,
                              'exact_mismatch_count': baseline_mismatches})
        json_file(directory, 'controls.json', controls_rows)
        correspondence = {'group_divisor_count': len(group_divisors),
                          'rank_three_counts': {arm: len(table) for arm, table in accepted.items()},
                          'recovered_divisor_count': len(recovered), 'mismatches': {},
                          'weighted_ordered_expected': len(points)**3,
                          'ordered_histogram': [{'divisor': d, 'count': n} for d, n in sorted(histogram.items())]}
        named_sets = {'group': group_divisors, 'B': set(accepted['B']), 'I': set(accepted['I']), 'inverse': set(recovered)}
        mismatch_count = 0
        for left, right in (('group', 'B'), ('group', 'I'), ('group', 'inverse'), ('B', 'I'), ('B', 'inverse'), ('I', 'inverse')):
            mismatch = sorted(named_sets[left] ^ named_sets[right])
            correspondence['mismatches'][left + '_vs_' + right] = mismatch
            mismatch_count += len(mismatch)
        correspondence['weighted_totals'] = {name: sum(group_oracle.orbit_weight(d) for d in domain)
                                             for name, domain in named_sets.items()}
        correspondence['ordered_histogram_total'] = sum(histogram.values())
        histogram_errors = [{'divisor': d, 'actual': histogram.get(d, 0),
                             'expected': group_oracle.orbit_weight(d) if d in group_divisors else 0}
                            for d in sorted(set(histogram) | group_divisors)
                            if histogram.get(d, 0) != (group_oracle.orbit_weight(d) if d in group_divisors else 0)]
        correspondence['orbit_histogram_errors'] = histogram_errors
        correspondence['coefficient_pair_mismatches'] = [
            {'divisor': d, 'B': accepted['B'].get(d), 'I': accepted['I'].get(d), 'inverse': recovered.get(d)}
            for d in sorted(set(accepted['B']) | set(accepted['I']) | set(recovered))
            if not (accepted['B'].get(d) == accepted['I'].get(d) == recovered.get(d))]
        correspondence['correspondence_error_count'] = (mismatch_count + len(histogram_errors)
                                                        + len(correspondence['coefficient_pair_mismatches']))
        json_file(directory, 'correspondence.json', correspondence)
        operations['B_complete_forward'] = dict(arm_fields['B'].counts)
        operations['I_complete_forward'] = dict(arm_fields['I'].counts)
        operations['shared_inverse_recovery'] = dict(inverse_field.counts)
        operations['inverse_group_verification'] = delta(oracle.counts, {key: group_before.get(key, 0) +
                                                                       operations['group_exhaustion'].get(key, 0)
                                                                       for key in oracle.counts})
        timings['2-exhaustive-correspondence'] = {'wall_seconds': time.perf_counter()-stage_wall,
                                                 'cpu_seconds': time.process_time()-stage_cpu}
        stage_wall, stage_cpu = time.perf_counter(), time.process_time()
        with (directory / 'presentation-inventory.json').open('x', encoding='utf-8') as stream:
            vectors = presentation_inventory.write_inventory(stream, p, constant, occupancy, dumps)
        timings['3-complete-presentation-and-cost'] = {'wall_seconds': time.perf_counter()-stage_wall,
                                                      'cpu_seconds': time.process_time()-stage_cpu}
        actual_divisors, actual_sections = len(group_sums), section_rows
        cardinality_ok = actual_divisors == comb(len(points)+3, 4) and actual_sections == p**3+p**2+p+1
        weighted_ok = (all(n == len(points)**3 for n in correspondence['weighted_totals'].values())
                       and sum(histogram.values()) == len(points)**3)
        if not cardinality_ok or not weighted_ok:
            anomaly({'kind': 'cardinality_or_orbit_total', 'divisors': actual_divisors,
                     'sections': actual_sections, 'weighted_totals': correspondence['weighted_totals']})
        B, I = vectors['B']['primary'], vectors['I']['primary']
        reduction = I['field_variables'] < B['field_variables'] or I['polynomial_monomials'] < B['polynomial_monomials']
        pareto = reduction and all(I[k] <= B[k] for k in B)
        all_controls = all(row['passed'] for row in controls_rows)
        candidate_science_mismatches = {'forward_recovery_mismatch', 'inverse_group_mismatch',
                                        'multiple_sections_for_divisor', 'rank_below_three'}
        operational_anomalies = [item for item in anomalies if item['kind'] not in candidate_science_mismatches]
        instrument_valid = not operational_anomalies and all_controls and cardinality_ok
        comparison_eligible = instrument_valid and weighted_ok and correspondence['correspondence_error_count'] == 0 and not anomalies
        metrics = {'experiment_id': EXPERIMENT, 'case_id': config['case_id'],
                   'N_p': len(points), 'divisor_count': actual_divisors, 'section_count': actual_sections,
                   'rank_histograms': {arm: dict(value) for arm, value in rank_histograms.items()},
                   'realized_multiplicity_partitions': dict(partitions_seen),
                   'unresolved_degree_histogram': dict(residual_degrees),
                   'coefficient_scale_collisions': len(scale_collisions),
                   'coefficient_scale_collision_witnesses': scale_collisions,
                   'coefficient_scale_collision_basis': 'observed normalized-coefficient set membership during enumeration',
                   'correspondence_error_count': correspondence['correspondence_error_count'],
                   'complete_presentation_vector': vectors,
                   'full_presentation_measure_reduction': reduction if constant == 1 and comparison_eligible else None,
                   'comparison_label': ('Pareto improvement' if pareto else 'tradeoff') if reduction and comparison_eligible
                                       else ('no registered reduction' if comparison_eligible else 'invalid; no interpretation'),
                   'N0_descriptive_only': constant == 2, 'instrument_valid': instrument_valid,
                   'comparison_eligible': comparison_eligible,
                   'potential_scoped_mismatch_certificates': [item for item in anomalies if item['kind'] in candidate_science_mismatches],
                   'controls_passed': all_controls, 'anomaly_count': len(anomalies),
                   'field_operations': operations, 'per_stage_timing': timings,
                   'recovery_inventory': presentation_inventory.recovery_inventory(),
                   'recovery_measured_work': dict(recovery_statistics),
                   'ambient_dimension': 3, 'embedding_degree': 4,
                   'total_instrument_wall_seconds': time.perf_counter()-started_wall,
                   'total_instrument_cpu_seconds': time.process_time()-started_cpu,
                   'peak_rss_raw': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                   'peak_rss_raw_unit': 'bytes' if sys.platform == 'darwin' else 'KiB',
                   'serialized_instrument_bytes_before_metrics': sum(path.stat().st_size for path in directory.iterdir() if path.is_file()),
                   'run_package_totals_owner': 'canonical wrapper after logs, metrics and manifest serialization',
                   'cost_scope': 'Measured instrument calls, no repetitions or amortization; wrapper must add setup/log/package costs; no attack-cost inference.',
                   'protocol_deviations': [], 'random_seeds': [], 'scientific_cases_executed_in_this_call': 1}
        json_file(directory, 'metrics.json', metrics)
        return metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config-json', required=True)
    parser.add_argument('--locked-plan', required=True)
    args = parser.parse_args()
    config_checked(json.loads(args.config_json))
    # Do not implement an ersatz lock or accept a caller's boolean as authority.
    # Future integration requires an additive source version and canonical lock.
    parser.exit(2, 'UNRESOLVED_CANONICAL_RUNNER_INTERFACE: candidate is not executable; '
                   'requires Coordinator integration of canonical LOCKED plan and immutable manifest schema. '
                   'No run directory created and no scientific computation started.\n')


if __name__ == '__main__':
    main()
