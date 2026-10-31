#!/usr/bin/env python3
"""Fixed software contract; all invocations and source revisions retained."""
import argparse
import ast
import copy
import datetime
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
META = ROOT / 'coordination/prime_sat_active_support_implementation_20261030'
CONTRACT = json.loads((META / 'software-contract.json').read_text())
SOURCES = json.loads((META / 'source-inputs.json').read_text())['sources']
NEW = [HERE / name for name in ('active_refute.py', 'engine_bridge.py', 'test_active_support.py', 'README.md')]
STATE = {'assertions': [], 'cold_results': {}, 'native_slots': [], 'scientific_runs': 0}


def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def emit(value):
    print(json.dumps(value, sort_keys=True), flush=True)


def demand(name, condition):
    row = {'name': name, 'passed': bool(condition)}
    STATE['assertions'].append(row)
    emit({'assertion': row})
    if not condition:
        raise AssertionError(name)


def polys(case):
    return [{int(k): v for k, v in f.items()} for f in case['polynomials']]


def memory_limit():
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))


def frozen_hashes():
    return {item['path']: hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() for item in SOURCES}


def write_json(path, value):
    # The receipt itself is the only retained output path; replacement is atomic.
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    temporary.replace(path)


def imported():
    import active_refute as ar
    import engine_bridge as bridge
    sys.path.insert(0, str(ROOT / 'research/prime_sat_prefix_search_20261030'))
    import engine
    import check
    return ar, bridge, engine, check


def expected_diagnostics(d, mode, p, fs, label):
    terms = [(m, c) for f in fs for m, c in f.items()]
    validation = {'generator_count': len(fs), 'term_count': len(terms),
                  'mask_type_range_checks': len(terms), 'coefficient_type_checks': len(terms)}
    demand(label + '/validation_events', d['input_validation'] == validation)
    demand(label + '/mode', d['mode'] == mode)
    if mode == 'baseline':
        demand(label + '/no_support_pass', d['support_setup'] == {'performed': False} and d['active_indices'] is None)
        return
    live = [(m, c) for m, c in terms if c % p]
    active = sorted({i for m, _ in live for i in range(m.bit_length()) if m >> i & 1})
    expected = {'performed': True, 'generators_scanned': len(fs), 'input_terms_scanned': len(terms),
                'coefficient_mod_reductions': len(terms), 'zero_coefficients_discarded': len(terms)-len(live),
                'nonzero_terms_scanned': len(live), 'set_bit_visits': sum(m.bit_count() for m, _ in live),
                'active_variable_count': len(active)}
    demand(label + '/support_events', d['support_setup'] == expected)
    demand(label + '/indices', d['active_indices'] == active)


def cold_suite(ar, engine):
    old_source = Path(ar.core.__file__).read_text()
    old = next(f for f in ast.parse(old_source).body if isinstance(f, ast.FunctionDef) and f.name == 'refute')
    new = next(f for f in ast.parse((HERE / 'active_refute.py').read_text()).body if isinstance(f, ast.FunctionDef) and f.name == '_kernel')
    class LoopChange(ast.NodeTransformer):
        count = 0
        def visit_For(self, node):
            if ast.dump(node.iter) == ast.dump(ast.parse('range(ring.n)', mode='eval').body):
                self.count += 1
                node.iter = ast.Name(id='active_indices', ctx=ast.Load())
            return self.generic_visit(node)
    transform = LoopChange()
    expected = transform.visit(copy.deepcopy(old))
    demand('source/single_loop', transform.count == 1)
    demand('source/kernel_body', ast.dump(ast.Module(body=expected.body, type_ignores=[])) ==
           ast.dump(ast.Module(body=new.body, type_ignores=[])))
    demand('source/kernel_signature', [a.arg for a in new.args.args] ==
           ['ring', 'generators', 'degree_cap', 'row_cap', 'active_indices'])
    exact_rows = {'empty_n0': (0, 0), 'empty_rows': (2, 2), 'early_constant_later_support': (1, 1),
                  'zero_row_cap': (1, 1), 'gapped_active_order': (5, 4), 'gapped_exact_cap': (5, 4),
                  'all_active_order': (4, 4), 'mod_p_zero_support': (2, 2), 'all_zero_mod_p': (2, 2),
                  'degree_zero_rejection': (2, 2), 'characteristic_two': (2, 2)}
    expected_certs = {'early_constant_later_support': [{0: 3}, {}],
                      'gapped_active_order': [{2: 1}, {0: 4}, {}],
                      'gapped_exact_cap': [{2: 1}, {0: 4}, {}],
                      'all_active_order': [{1: 1}, {0: 4}, {}],
                      'mod_p_zero_support': [{0: 1}, {0: 4}],
                      'characteristic_two': [{0: 1}, {0: 1}]}
    unknown = {'empty_n0', 'empty_rows', 'zero_row_cap', 'above_cap_support',
               'all_zero_mod_p', 'degree_zero_rejection', 'free_inactive_models'}
    for case in CONTRACT['fixed_cold_cases']:
        name, p, n, fs = case['id'], case['p'], case['n'], polys(case)
        args = (fs, case['degree_cap'], case['row_cap'])
        raw = ar.core.refute(ar.core.BoolRing(n, p), *args)
        row = {'raw_baseline': raw, 'modes': {}}
        STATE['cold_results'][name] = row
        for mode in CONTRACT['native_modes']:
            diag = {}
            answer = ar.checked_refute(mode, ar.core.BoolRing(n, p), *args, diagnostics=diag)
            row['modes'][mode] = {'answer': answer, 'diagnostics': diag}
            expected_diagnostics(diag, mode, p, fs, name + '/' + mode)
            demand(name + '/' + mode + '/schema', set(answer) == set(raw))
            if mode == 'baseline':
                demand(name + '/raw_baseline_equality', answer == raw)
            else:
                demand(name + '/declared_support', diag['active_indices'] == case['expected_support'])
                if raw['status'] == 'refuted':
                    demand(name + '/conditional_refutation', answer['status'] == 'refuted')
                    demand(name + '/ordered_certificate', answer['certificate'] == raw['certificate'])
                    demand(name + '/cap_preserved', answer['attempted_rows'] <= raw['attempted_rows'] <= case['row_cap'])
            if answer['status'] == 'refuted':
                demand(name + '/' + mode + '/core_identity', ar.core.check_refutation(p, n, fs, answer['certificate']))
                demand(name + '/' + mode + '/independent_identity', engine.legacy.certificate_check(p, fs, answer['certificate'])[0])
            if name in unknown:
                demand(name + '/' + mode + '/unknown', answer['status'] == 'unknown' and answer['certificate'] is None)
            if name in exact_rows:
                demand(name + '/' + mode + '/exact_attempts', answer['attempted_rows'] == exact_rows[name][mode == 'active_support'])
            if name in expected_certs and not (name == 'gapped_exact_cap' and mode == 'baseline'):
                demand(name + '/' + mode + '/fixed_certificate', answer['certificate'] == expected_certs[name])
        active = row['modes']['active_support']['answer']
        public_diag = {}
        public_answer = ar.refute_active(ar.core.BoolRing(n, p), *args, diagnostics=public_diag)
        demand(name + '/public_api', public_answer == active and
               public_diag == row['modes']['active_support']['diagnostics'])
        if name == 'gapped_exact_cap':
            demand(name + '/baseline_capped', raw['status'] == 'unknown' and raw['resource_capped'])
            demand(name + '/candidate_exact_cap', active['status'] == 'refuted' and not active['resource_capped'])
        if name == 'zero_row_cap':
            demand(name + '/both_capped', raw['resource_capped'] and active['resource_capped'])
        if name == 'all_active_order':
            demand(name + '/full_result_equality', raw == active)
            mutant = ar._kernel(ar.core.BoolRing(n, p), *args, [1, 0])
            demand('mutant/reversed_order_rejected', mutant['certificate'] != expected_certs[name])
            demand('mutant/reversed_identity_valid', ar.core.check_refutation(p, n, fs, mutant['certificate']))
        if name == 'above_cap_support':
            bad, _ = ar._support(ar.core.BoolRing(n, p), [fs[0]])
            demand('mutant/omitted_above_cap_rejected', bad != case['expected_support'])
        if name == 'free_inactive_models':
            ring = ar.core.BoolRing(n, p)
            roots = [b for b in range(1 << n) if all(ring.eval(f, b) == 0 for f in fs)]
            demand(name + '/free_bits', roots == [0, 1, 4, 5])
    demand('cold/inventory', len(STATE['cold_results']) == 14)


def invalid_suite(ar):
    cases = []
    base = {'n': 2, 'p': 5, 'degree': 2, 'rows': 8, 'fs': [{0: 1}]}
    for field in ('n', 'p', 'degree', 'rows'):
        for kind, value in (('bool', True), ('float', 2.0), ('negative', -1)):
            cases.append((field + '/' + kind, {**base, field: value}))
    cases.append(('p/one', {**base, 'p': 1}))
    for name, fs in [('negative_mask', [{-1: 1}]), ('range_mask', [{4: 1}]),
                     ('bool_mask', [{True: 1}]), ('float_mask', [{1.0: 1}]),
                     ('string_mask', [{'1': 1}]), ('alias_keys', [{1: 1, '1': 1}]),
                     ('bool_coefficient', [{1: True}]), ('float_coefficient', [{1: 1.0}]),
                     ('nonmapping', [[]]), ('nonsequence', {0: 1}),
                     ('late_malformed', [{0: 1}, {'1': 1}])]:
        cases.append((name, {**base, 'fs': fs}))
    for mode in CONTRACT['native_modes']:
        for name, case in cases:
            try:
                ar.checked_refute(mode, ar.core.BoolRing(case['n'], case['p']), case['fs'], case['degree'], case['rows'])
            except (TypeError, ValueError):
                rejected = True
            else:
                rejected = False
            demand('invalid/' + mode + '/' + name, rejected)
    try:
        ar.checked_refute('wrong', ar.core.BoolRing(2, 5), [], 0)
    except ValueError:
        demand('invalid/mode', True)
    else:
        demand('invalid/mode', False)


def callback_suite(ar, bridge, engine, check):
    identities = dict(vars(engine.legacy))
    instances = [bridge._private_engine(mode) for mode in ('baseline', 'active_support', 'baseline')]
    for j, (private, sidecar, guard) in enumerate(instances):
        private.legacy.refute(ar.core.BoolRing(2, 5), [{0: 1}], 0, 1)
        demand('binding/' + str(j), sidecar['calls'][0]['mode'] == sidecar['mode'])
        guard()
    demand('binding/shared_unchanged', set(identities) == set(vars(engine.legacy)) and
           all(getattr(engine.legacy, k) is v for k, v in identities.items()))
    for mode in CONTRACT['native_modes']:
        private, sidecar, guard = bridge._private_engine(mode)
        limits = CONTRACT['native_limits']
        prop = private.PrefixPropagator(ar.core.BoolRing(3, 5), [{1: 1}], 1, limits, 'model_only', [0, 1, 3])
        prop.on_assignment(-1, fixed=True); prop.on_new_level(); prop.on_assignment(2)
        prop.on_new_level(); prop.on_assignment(-3); prop.on_backtrack(1)
        demand(mode + '/backtrack_one', set(prop.assignments) == {0, 1})
        prop.on_backtrack(0)
        demand(mode + '/backtrack_fixed', prop.assignments == {0: (0, 0, True)})
        demand(mode + '/no_pending_clause', prop.has_clause() is False)
        try:
            prop._reject(0)
        except AssertionError:
            demand(mode + '/reject_without_proof', True)
        else:
            demand(mode + '/reject_without_proof', False)
        capped = private.PrefixPropagator(ar.core.BoolRing(2, 5), [{3: 1}], 2,
                                         {**limits, 'pc_calls': 0}, 'partial_prefix', [0, 1, 2])
        demand(mode + '/fallback_false_model', capped.check_model([1, 2]) is False)
        demand(mode + '/fallback_count', capped.events['pc_calls'] == 0 and capped.events['leaf_fallbacks'] == 1)
        demand(mode + '/fallback_clause', capped.has_clause() and capped.add_clause() == [-1, -2])
        guard()
    censored = {'status': 'censored', 'models': [0], 'learned': []}
    checked = engine.adapter.verify_transcript(5, 2, 0, [], [], censored)
    demand('censored/closed_cover', checked['cover_complete'] and not checked['projected_model_set_complete'])
    for name, result in check.mutation_controls().items():
        demand('mutation/' + name, result['rejected'])
    try:
        engine.adapter.verify_transcript(5, 2, 2, [], [], {'status': 'complete', 'models': [], 'learned': []})
    except ValueError:
        demand('mutation/missing_cover', True)
    else:
        demand('mutation/missing_cover', False)


def slot_inventory():
    return [(case, mode, strategy) for case in CONTRACT['fixed_native_families']
            for mode in CONTRACT['native_modes'] for strategy in CONTRACT['native_strategies']]


def native_slot(index):
    ar, bridge, engine, check = imported()
    case, mode, strategy = slot_inventory()[index]
    fs, p, n, m = polys(case), case['p'], case['n'], case['projected_bits']
    last = None
    def checkpoint(answer):
        nonlocal last
        last = copy.deepcopy(answer)
        emit({'checkpoint': answer})
    answer = bridge.solve(engine.legacy.CountedRing(n, p), fs, case['domain'], m,
                          CONTRACT['native_limits'], strategy, case['prefix_depths'], checkpoint,
                          refuter_mode=mode)
    demand('native/final_checkpoint', last == answer)
    checked = engine.adapter.verify_transcript(p, n, m, fs, case['domain'], answer, aux_bound=case['aux_bound'])
    demand('native/complete', answer['status'] == 'complete' and checked['projected_model_set_complete'])
    demand('native/projected_set', checked['projected_models'] == case['expected_models'])
    oracle_ring = ar.core.BoolRing(n, p)
    oracle = sorted({b & ((1 << m)-1) for b in range(1 << n)
                     if all(oracle_ring.eval(f, b) == 0 for f in fs)
                     and all(engine.legacy.clause_true(c, b) for c in case['domain'])})
    demand('native/independent_models', oracle == case['expected_models'])
    check.counters_check(answer, n, CONTRACT['native_limits'])
    demand('native/frozen_counters', True)
    calls = answer[bridge.SIDECAR]['calls']
    demand('native/setup_call_count', len(calls) == len(answer['attempts']))
    for i, (call, attempt) in enumerate(zip(calls, answer['attempts'])):
        assignments = {j: (attempt['prefix'] >> j) & 1 for j in range(attempt['depth'])}
        residuals = [oracle_ring.restrict(f, assignments) for f in fs]
        demand('native/call_index/' + str(i), call['call_index'] == i)
        expected_diagnostics(call, mode, p, residuals, 'native/call/' + str(i))
    if case['id'] == 'positive' and strategy != 'model_only':
        demand('native/partial_conflict', any(x['trigger'] == 'partial' and x['depth'] == 1 and
               x['prefix'] == 0 and x['assigned_count'] < n for x in answer['learned']))
    if case['id'] == 'negative':
        demand('native/no_false_prefix', all(x['depth'] == n for x in answer['learned']))
    if case['id'] == 'empty':
        demand('native/empty_clause', any(x['clause'] == [] for x in answer['learned']))
    emit({'native_result': {'index': index, 'case': case['id'], 'mode': mode, 'strategy': strategy,
                           'native_solver_instances': 1, 'answer': answer, 'checked': checked,
                           'assertions': STATE['assertions']}})


def software_suite():
    try:
        ar, bridge, engine, check = imported()
        cold_suite(ar, engine)
        invalid_suite(ar)
        callback_suite(ar, bridge, engine, check)
        for index, (case, mode, strategy) in enumerate(slot_inventory()):
            argv = [sys.executable, '-B', str(Path(__file__).resolve()), '--native-slot', str(index)]
            row = {'index': index, 'case': case['id'], 'mode': mode, 'strategy': strategy,
                   'argv': argv, 'started_at': stamp(), 'native_instance_upper_bound': 1}
            STATE['native_slots'].append(row)
            try:
                v = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, timeout=5,
                                   env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}, preexec_fn=memory_limit)
                row.update(returncode=v.returncode, stdout=v.stdout, stderr=v.stderr)
            except subprocess.TimeoutExpired as error:
                text = lambda v: v.decode(errors='replace') if isinstance(v, bytes) else (v or '')
                row.update(returncode=None, timeout=True, stdout=text(error.stdout), stderr=text(error.stderr))
            row['ended_at'] = stamp()
            emit({'native_slot_record': row})
            demand('slot/' + str(index) + '/process', row['returncode'] == 0)
            results = [json.loads(line)['native_result'] for line in row['stdout'].splitlines()
                       if line.startswith('{') and 'native_result' in json.loads(line)]
            demand('slot/' + str(index) + '/result', len(results) == 1)
            row['result'] = results[0]
        demand('native/inventory', len(STATE['native_slots']) == 24)
        STATE['passed'] = True
    except Exception:
        STATE.update(passed=False, error=traceback.format_exc())
    emit({'suite_result': STATE})
    return 0 if STATE['passed'] else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipt', type=Path)
    parser.add_argument('--suite', action='store_true')
    parser.add_argument('--native-slot', type=int)
    args = parser.parse_args()
    if args.native_slot is not None:
        native_slot(args.native_slot)
        return 0
    if args.suite:
        return software_suite()
    if args.receipt is None:
        parser.error('--receipt required')
    expected_path = HERE / 'producer-results.json'
    if args.receipt.resolve() != expected_path:
        raise ValueError('receipt outside declared producer path')
    record = json.loads(expected_path.read_text()) if expected_path.exists() else {
        'schema': 'prime-active-support-software-results/v1', 'attempts': [], 'scientific_runs': 0}
    if len(record['attempts']) >= 4 or any('ended_at' not in a for a in record['attempts']):
        raise ValueError('attempt budget reached or unfinished prior invocation requires reconciliation')
    expected_frozen = {x['path']: x['sha256'] for x in SOURCES}
    attempt = {'started_at': stamp(), 'cwd': str(ROOT), 'parent_argv': [sys.executable, *sys.argv],
               'argv': [sys.executable, '-B', str(Path(__file__).resolve()), '--suite'],
               'environment': {'python': sys.version, 'executable': sys.executable, 'PYTHONDONTWRITEBYTECODE': '1'},
               'source_before': {str(p.relative_to(ROOT)): {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                                                           'text': p.read_text()} for p in NEW},
               'frozen_before': frozen_hashes(), 'frozen_expected': expected_frozen}
    record['attempts'].append(attempt)
    write_json(expected_path, record)
    try:
        if attempt['frozen_before'] != expected_frozen:
            raise ValueError('frozen dependency mismatch before software suite')
        v = subprocess.run(attempt['argv'], cwd=ROOT, text=True, capture_output=True, timeout=180,
                           env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}, preexec_fn=memory_limit)
        attempt.update(returncode=v.returncode, stdout=v.stdout, stderr=v.stderr)
    except subprocess.TimeoutExpired as error:
        text = lambda v: v.decode(errors='replace') if isinstance(v, bytes) else (v or '')
        attempt.update(returncode=None, timeout=True, stdout=text(error.stdout), stderr=text(error.stderr))
    except Exception:
        attempt.update(returncode=None, stdout='', stderr=traceback.format_exc())
    attempt['ended_at'] = stamp()
    attempt['source_after'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in NEW}
    attempt['frozen_after'] = frozen_hashes()
    summaries = [json.loads(line)['suite_result'] for line in attempt['stdout'].splitlines()
                 if line.startswith('{') and 'suite_result' in json.loads(line)]
    attempt['summary'] = summaries[-1] if summaries else None
    attempt['valid'] = (attempt['returncode'] == 0 and bool(attempt['summary']) and attempt['summary']['passed']
                        and attempt['frozen_after'] == expected_frozen
                        and all(attempt['source_after'][p] == data['sha256'] for p, data in attempt['source_before'].items()))
    record['valid'] = attempt['valid']
    write_json(expected_path, record)
    emit({'receipt': str(expected_path), 'attempt': len(record['attempts']), 'valid': record['valid'],
          'returncode': attempt['returncode'], 'native_slots': len((attempt['summary'] or {}).get('native_slots', [])),
          'error': (attempt['summary'] or {}).get('error'), 'stderr': attempt['stderr']})
    return 0 if record['valid'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
