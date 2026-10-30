"""Complete the prepared F1 extractor without changing its frozen sources.

Library entry points perform exact finite-case work. Scientific CLI execution
requires a matching frozen protocol and the real repository checkpoint gate.
"""
import argparse
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import sys

from core import AffineCurve, ExtractionUnknown, signed_recovery, write_once
from exterior import solve_stratum
from reference import domain, exhaustive


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def dimensions(depth):
    if type(depth) is not int or depth < 1:
        raise ValueError('positive integer depth required')
    S = 1 << depth
    return dict(distinct=comb(S, 3), twoequal=S*S, allequal=S)


def solve_case(parameters, case, max_dimension=560, *, stages=None):
    sizes = dimensions(case['depth'])
    if max(sizes.values()) > max_dimension:
        raise ExtractionUnknown('declared operator dimension exceeds configured resource guard')
    if case.get('kind', 'triple') != 'triple':
        raise ValueError('triple case required; arity-four has a separate enumerative control')
    p = parameters['p']
    from crypto_autoresearcher.index_calculus.curve import Curve, is_probable_prime
    if not is_probable_prime(p) or p % 4 != 3:
        raise ValueError('prepared F1 recovery requires a prime p congruent to 3 mod 4')
    Curve(p, parameters['a'], parameters['b'])  # reject singular inputs
    if not 0 <= case['terminal'] < p or case['terminal'] in (2, p-2):
        raise ValueError('Separable canonical Dickson fibre required')
    target = tuple(case['target'])
    curve = AffineCurve(parameters)
    if not curve.valid(target) or curve.multiply(parameters['r'], target) is not None:
        raise ValueError('target must lie on the stated subgroup')
    strata, solutions = [], set()
    for name, pattern in [('distinct', (1, 1, 1)), ('twoequal', (2, 1)), ('allequal', (3,))]:
        if stages is None:
            result = solve_stratum(parameters, case['depth'], case['terminal'], target, name)
            signed, recovery, counts = signed_recovery(
                result['states'], case['depth'], case['terminal'], target, parameters, pattern)
        else:
            import profiled
            stratum_stages = stages.scoped(stratum=name)
            result = profiled.solve_stratum(parameters, case['depth'], case['terminal'], target, name, stratum_stages)
            signed, recovery, counts = profiled.signed_recovery(
                result['states'], case['depth'], case['terminal'], target, parameters, pattern, stratum_stages)
        solutions.update(signed)
        result.update(recovery=recovery, recovery_counters=counts)
        strata.append(result)
    return dict(case_id=case['id'], status='complete', strata=strata,
                solutions=sorted(solutions), operator_dimensions=sizes,
                complete_coordinate_partitions=[[1, 1, 1], [2, 1], [3]],
                root_domain_enumeration_used_by_solver=False)


def check_case(parameters, case, result):
    """Recompute the complete finite reference; reject omissions and bad signs."""
    expected = exhaustive(parameters, case['depth'], case['terminal'], case['target'])
    normalize = lambda values: sorted(tuple(tuple(point) for point in row) for row in values)
    if result['status'] != 'complete' or normalize(result['solutions']) != normalize(expected['solutions']):
        raise ValueError('complete signed-solution set differs from finite reference')
    actual = [tuple(state) for stratum in result['strata'] for state in stratum['states']]
    if len(actual) != len(set(actual)) or sorted(actual) != expected['states']:
        raise ValueError('complete symmetric-state set differs from resultant reference')
    return dict(case_id=case['id'], complete_states=len(actual),
                signed_solutions=len(expected['solutions']), checked=True)


def arity_four_control(parameters, depth, terminal, max_domain=16):
    if (1 << depth) > max_domain:
        raise ExtractionUnknown('enumerative arity-four domain exceeds guard')
    curve = AffineCurve(parameters)
    liftable = [point for x in domain(depth, terminal, parameters['p'])
                if (points := curve.lifts(x)) for point in [min(points)]
                if curve.multiply(parameters['r'], point) is None]
    records = []
    for partition in [(1, 1, 1, 1), (2, 1, 1), (2, 2), (3, 1), (4,)]:
        if len(liftable) < len(partition):
            raise ValueError('not enough liftable coordinates for every arity-four control')
        target = None
        for point, count in zip(liftable, partition):
            target = curve.add(target, curve.multiply(count, point))
        if target is None:
            raise ExtractionUnknown('constructed arity-four target is infinity')
        result = exhaustive(parameters, depth, terminal, target, arity=4)
        records.append(dict(partition=list(partition), target=target, **result))
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', required=True, type=Path)
    parser.add_argument('--protocol', required=True, type=Path)
    parser.add_argument('--release', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--max-dimension', type=int, default=560)
    parser.add_argument('--profile-stages', action='store_true')
    args = parser.parse_args()
    from crypto_autoresearcher.index_calculus.execution_gate import admit
    if args.out.exists():
        raise ValueError('output directory already exists')
    sources = [HERE/'core.py', HERE/'exterior.py',
               HERE/'driver.py', HERE/'reference.py',
               ROOT/'research/p256_factor_base_parallel_20261025/baseline/s4-symmetric.json',
               ROOT/'src/crypto_autoresearcher/index_calculus/curve.py']
    parameters = {'max_dimension': args.max_dimension}
    if args.profile_stages:
        sources.append(HERE/'profiled.py')
        parameters['profile_stages'] = True
    admit(ROOT, args.protocol, args.inputs, sources, parameters, args.release)
    data = json.loads(args.inputs.read_text())
    results = []
    for case in data['cases']:
        if Path(case['id']).name != case['id']:
            raise ValueError('case IDs must be plain file names')
        stage_file = None
        stages = None
        if args.profile_stages:
            from profiled import Stages
            args.out.mkdir(parents=True, exist_ok=True)
            stage_file = (args.out/(case['id']+'.stages.jsonl')).open('x')
            def emit(record):
                stage_file.write(json.dumps(dict(case_id=case['id'], **record), sort_keys=True)+'\n')
                stage_file.flush()
            stages = Stages(emit)
        call = stages.call if stages is not None else lambda phase, function, *a, **kw: function(*a, **kw)
        try:
            if case['kind'] == 'triple':
                if stages is None:
                    result = solve_case(data['parameters'], case, args.max_dimension)
                    result['finite_reference'] = check_case(data['parameters'], case, result)
                else:
                    result = stages.call('solver_total', solve_case, data['parameters'], case,
                                         args.max_dimension, stages=stages)
                    result['finite_reference'] = stages.call('finite_oracle', check_case,
                                                             data['parameters'], case, result)
            elif case['kind'] == 'arity4':
                result = dict(case_id=case['id'], status='complete',
                              method='explicit finite enumeration control',
                              controls=call('arity_four_oracle_control', arity_four_control,
                                            data['parameters'], case['depth'], case['terminal']))
            elif case['kind'] == 'nonseparable':
                rejected = False
                try:
                    call('nonseparable_rejection_control', solve_stratum, data['parameters'],
                         case['depth'], case['terminal'], tuple(data['cases'][0]['target']), 'distinct')
                except ValueError:
                    rejected = True
                if not rejected:
                    raise AssertionError('nonseparable input was accepted')
                result = dict(case_id=case['id'], status='control_passed', expected_rejection=True)
            elif case['kind'] == 'corruption':
                from copy import deepcopy
                source_index = case['source_case']
                source = data['cases'][source_index]
                result = dict(case_id=case['id'], status='unknown', reason='source case incomplete or empty')
                if results[source_index]['status'] == 'complete' and results[source_index]['solutions']:
                    corrupted = deepcopy(results[source_index])
                    corrupted['solutions'] = []  # completeness corruption
                    try:
                        call('corruption_rejection_control', check_case, data['parameters'], source, corrupted)
                    except ValueError:
                        result = dict(case_id=case['id'], status='control_passed', expected_rejection=True)
                    else:
                        raise AssertionError('corrupt solution certificate was accepted')
            else:
                raise ValueError('unsupported case kind: '+case['kind'])
        except (ExtractionUnknown, MemoryError) as error:
            result = dict(case_id=case['id'], status='unknown', reason=str(error))
        except BaseException as error:
            write_once(args.out/(case['id']+'.json'), dict(case_id=case['id'], status='failed',
                       error_type=type(error).__name__, reason=str(error)))
            raise
        finally:
            if stage_file is not None:
                stage_file.close()
        results.append(result)
        # Each finished case survives a later failure; existing evidence is never replaced.
        write_once(args.out/(case['id']+'.json'), result)
    write_once(args.out/'summary.json', dict(schema='prime-field-f1-continuation/v1',
               results=results, scientific_promotion=False,
               inputs_sha256=sha256(args.inputs.read_bytes()).hexdigest()))
    return 0


if __name__ == '__main__':
    sys.exit(main())
