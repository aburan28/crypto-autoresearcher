"""Deterministic artificial metadata checks; never evaluates scientific fixtures."""
import argparse
from contextlib import redirect_stdout
from copy import deepcopy
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import sys
import time

import driver
import panel_scoring as scoring


def f(a, b=1):
    return {'numerator': a, 'denominator': b}


def fixture(qualifiers=()):
    rows = []
    for n, q, k in scoring.PANEL_IDS:
        positive = (n, q, k) in qualifiers
        rows.append({'N': n, 'q': q, 'kernel': k, 'coordinate_delta': f(0),
                     'nulls': [{'seed': s, 'delta': f(1, 6) if positive and s < 24
                               else f(0)} for s in range(32)]})
    return {'panels': rows, 'validity': True,
            'controls': {k: True for k in scoring.CONTROL_NAMES}}


def summarize(result):
    return {'outcome': result['outcome'],
            'paired_qualifier_count': result['paired_qualifier_count'],
            'counts': [result['panel_count'], result['null_entry_count'], result['pair_count']],
            'first_gap': result['panels'][0]['gap'],
            'first_wins': result['panels'][0]['strict_wins'],
            'gating_reasons': result['gating_reasons']}


def run_checks(scratch):
    cases = []
    started = time.time()
    positive = fixture(((11, 2, 'R1'), (17, 2, 'R1')))

    def record(case_id, family, data, outcome=None, gap=None, wins=None, reject=False):
        before = deepcopy(data)
        entry = {'case_id': case_id, 'family': family,
                 'expected': {'schema_rejection': reject, 'outcome': outcome,
                              'first_gap': gap, 'first_wins': wins},
                 'input': data}
        try:
            try:
                actual = scoring.score_panel_advantage(data)
            except scoring.SchemaError as exc:
                entry['actual'] = {'schema_rejection': True, 'error': str(exc)}
                assert reject, str(exc)
            else:
                entry['actual'] = actual
                assert not reject, 'expected schema rejection'
                assert actual['outcome'] == outcome, summarize(actual)
                assert len(actual['panels']) == 32 and len(actual['pairs']) == 16
                assert sum(len(p['nulls']) for p in actual['panels']) == 1024
                assert [(p['N'], p['q'], p['kernel']) for p in actual['panels']] == list(scoring.PANEL_IDS)
                assert [(p['q'], p['kernel']) for p in actual['pairs']] == [(q, k) for q in scoring.QS for k in scoring.KERNELS]
                assert all([n['seed'] for n in p['nulls']] == list(range(32)) for p in actual['panels'])
                if gap is not None:
                    assert actual['panels'][0]['gap'] == gap, summarize(actual)
                if wins is not None:
                    assert actual['panels'][0]['strict_wins'] == wins, summarize(actual)
                assert actual == scoring.score_panel_advantage(deepcopy(data))
            assert before == data, 'input mutated'
            entry['passed'] = True
        except Exception as exc:
            entry['passed'] = False
            entry['failure'] = f'{type(exc).__name__}: {exc}'
        cases.append(entry)

    record('gap_equality_24_wins', 1, positive, scoring.POSITIVE, f(1, 8), 24)
    data = deepcopy(positive)
    for n in data['panels'][0]['nulls'][:24]:
        n['delta'] = f(1, 7)
    record('gap_below_with_24_wins', 1, data, scoring.NEGATIVE, f(3, 28), 24)
    data = deepcopy(positive)
    for n in data['panels'][0]['nulls']:
        n['delta'] = f(1, 5) if n['seed'] < 23 else f(0)
    record('gap_above_but_23_wins', 1, data, scoring.NEGATIVE, f(23, 160), 23)
    record('ties_do_not_win_repeated_values_retained', 2, positive, scoring.POSITIVE, f(1, 8), 24)
    data = deepcopy(positive)
    data['panels'][0]['coordinate_delta'] = f(1, 4)
    for n in data['panels'][0]['nulls']:
        n['delta'] = f(1, 2) if n['seed'] < 24 else f(1, 4)
    record('nonzero_coordinate_ties', 2, data, scoring.POSITIVE, f(3, 16), 24)
    record('single_size_only', 3, fixture(((11, 2, 'R1'),)), scoring.NEGATIVE)
    record('mismatched_q', 3, fixture(((11, 2, 'R1'), (17, 3, 'R1'))), scoring.NEGATIVE)
    record('mismatched_kernel', 3, fixture(((11, 2, 'R1'), (17, 2, 'R2'))), scoring.NEGATIVE)
    record('no_pair_valid', 3, fixture(), scoring.NEGATIVE, f(0), 0)
    record('all_pairs', 3, fixture(scoring.PANEL_IDS), scoring.POSITIVE)
    record('last_pair_only', 3, fixture(((11, 5, 'R4'), (17, 5, 'R4'))), scoring.POSITIVE)
    for operation in ('missing_panel', 'extra_panel', 'duplicate_panel', 'missing_seed', 'extra_seed', 'duplicate_seed'):
        data = deepcopy(positive)
        if operation == 'missing_panel': data['panels'].pop()
        if operation == 'extra_panel': data['panels'].append(deepcopy(data['panels'][0]))
        if operation == 'duplicate_panel': data['panels'][-1] = deepcopy(data['panels'][0])
        if operation == 'missing_seed': data['panels'][0]['nulls'].pop()
        if operation == 'extra_seed': data['panels'][0]['nulls'].append({'seed': 32, 'delta': f(0)})
        if operation == 'duplicate_seed': data['panels'][0]['nulls'][-1]['seed'] = 0
        record(operation, 4, data, reject=True)
    for field, values in [('N', [13, True, 11.0, '11']), ('q', [1, False, 2.0, '2']),
                          ('kernel', ['P', 'R5', 1, True])]:
        for i, value in enumerate(values):
            data = deepcopy(positive); data['panels'][0][field] = value
            record(f'bad_{field}_{i}', 4, data, reject=True)
    for i, seed in enumerate([-1, 32, True, 0.0, '0']):
        data = deepcopy(positive); data['panels'][0]['nulls'][0]['seed'] = seed
        record(f'bad_seed_{i}', 4, data, reject=True)
    bad_fractions = [f(2, 4), f(0, 2), f(1, 0), f(-1, 2), f(2, 1), f(1, -2),
                     f(True, 1), f(1, True), f(1.0, 2), f(1, 2.0), f('1', 2),
                     0.5, True, [1, 2], {'numerator': 1},
                     {'numerator': 1, 'denominator': 2, 'extra': 1}]
    for target in ('coordinate', 'null'):
        for i, value in enumerate(bad_fractions):
            data = deepcopy(positive)
            if target == 'coordinate': data['panels'][0]['coordinate_delta'] = value
            else: data['panels'][0]['nulls'][0]['delta'] = value
            record(f'bad_fraction_{target}_{i}', 4, data, reject=True)
    for field in ('N', 'q', 'kernel', 'coordinate_delta', 'nulls'):
        data = deepcopy(positive); del data['panels'][0][field]
        record(f'missing_field_{field}', 4, data, reject=True)
    for label, value in [('false', False), ('unknown', None), ('integer', 1), ('string', 'true'), ('float', 1.0)]:
        data = deepcopy(positive); data['validity'] = value
        record(f'validity_{label}', 5, data, scoring.INVALID)
    data = deepcopy(positive); del data['validity']
    record('validity_missing', 5, data, scoring.INVALID)
    for name in scoring.CONTROL_NAMES:
        for label, value in [('false', False), ('unknown', None), ('integer', 1), ('missing', None)]:
            data = deepcopy(positive)
            if label == 'missing': del data['controls'][name]
            else: data['controls'][name] = value
            record(f'control_{name}_{label}', 5, data, scoring.INVALID)
    for label, value in [('missing', None), ('malformed', []), ('unknown_name', {'extra': True})]:
        data = deepcopy(positive)
        if label == 'missing': del data['controls']
        elif label == 'malformed': data['controls'] = value
        else: data['controls'].update(value)
        record(f'controls_{label}', 5, data, scoring.INVALID)
    data = fixture(); data['validity'] = False
    record('no_pair_invalid_never_negative', 5, data, scoring.INVALID)
    data = deepcopy(positive); data['panels'].reverse()
    for row in data['panels']: row['nulls'].reverse()
    record('reversed_input_canonical_output', 6, data, scoring.POSITIVE, f(1, 8), 24)
    assert scoring.score_panel_advantage(data) == scoring.score_panel_advantage(positive)
    data = fixture()
    for row in data['panels']: row['coordinate_delta'] = f(1)
    record('negative_gaps_exact', 6, data, scoring.NEGATIVE, f(-1), 0)

    # Only artificial inert files in the authorized scratch directory.
    paths = {}
    for name in ('spec', 'manifest', 'review', 'lock'):
        path = scratch / (name + '.synthetic.json')
        with path.open('x') as out:
            json.dump({'synthetic': True, 'name': name}, out)
        paths[name] = str(path)
    paths['spec_sha256'] = hashlib.sha256(Path(paths['spec']).read_bytes()).hexdigest()
    before_files = sorted(str(p.relative_to(scratch)) for p in scratch.rglob('*'))
    # This hook is active only after artificial inputs exist. It catches write,
    # process and network attempts while calling the new driver entry points.
    forbidden_events = []
    def audit(event, args):
        forbidden = event.startswith(('subprocess.', 'socket.')) or event in ('os.system', 'os.posix_spawn', 'os.fork', 'os.mkdir', 'os.remove', 'os.rename')
        if event == 'open':
            mode = args[1]
            flags = args[2]
            forbidden = (isinstance(mode, str) and any(c in mode for c in 'wax+')) or (isinstance(flags, int) and flags & (1 | 2 | 64 | 512 | 1024))
        if guard[0] and forbidden:
            forbidden_events.append(event)
            raise AssertionError(f'driver attempted forbidden side effect: {event}')
    guard = [True]
    sys.addaudithook(audit)
    try:
        for name, binding in [('missing', None), ('malformed', {'invalid': object()}), ('fully_populated_synthetic', paths)]:
            entry = {'case_id': f'driver_{name}', 'family': 7, 'expected': {'refusals': 2, 'cli_exit': 3}}
            results = []
            try:
                for entrypoint in (driver.check_launch_admission, driver.launch_scientific):
                    try: entrypoint(binding)
                    except driver.ScientificLaunchUnavailable as exc: results.append(str(exc))
                    else: raise AssertionError('driver admitted launch')
                out = io.StringIO()
                with redirect_stdout(out): code = driver.main([] if binding is None else ['--synthetic-binding', str(binding)])
                assert code == 3 and len(results) == 2
                entry['actual'] = {'refusals': results, 'cli_exit': code, 'stdout': out.getvalue()}
                entry['passed'] = True
            except Exception as exc:
                entry.update(passed=False, failure=f'{type(exc).__name__}: {exc}')
            cases.append(entry)
    finally:
        guard[0] = False
    after_files = sorted(str(p.relative_to(scratch)) for p in scratch.rglob('*'))
    old_imports = [str(getattr(m, '__file__', '')) for m in tuple(sys.modules.values())
                   if '/EXP-CRYPTO-5e8beb/implementation/' in str(getattr(m, '__file__', ''))]
    side_effects = {'driver_forbidden_events': forbidden_events, 'scratch_before': before_files,
                    'scratch_after': after_files, 'old_scientific_module_imports': old_imports}
    okay = all(c['passed'] for c in cases) and not forbidden_events and not old_imports and before_files == after_files
    return {'schema': 'synthetic_correction_evidence.v1', 'scientific_runs': 0,
            'synthetic_only': True, 'randomness': 'none; fixed artificial arrays',
            'elapsed_seconds_measured': time.time() - started,
            'case_count': len(cases), 'passed': okay,
            'family_counts': {str(i): sum(c['family'] == i for c in cases) for i in range(1, 8)},
            'cases': cases, 'side_effects': side_effects}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scratch', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    args = parser.parse_args()
    args.scratch.mkdir(parents=True, exist_ok=False)
    result = run_checks(args.scratch)
    with args.evidence.open('x') as out:
        json.dump(result, out, sort_keys=True, separators=(',', ':'))
        out.write('\n')
    print(json.dumps({k: result[k] for k in ('case_count', 'passed', 'family_counts', 'scientific_runs', 'side_effects')}, sort_keys=True))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
