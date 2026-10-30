"""Software fixtures for the additive collectors and the complete extractor."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
F1 = ROOT/'research/p256_factor_base_parallel_20261026/tracks/f1'
STUDY = ROOT/'research/prime_field_factor_base_20261028'


@pytest.fixture
def f1(monkeypatch):
    monkeypatch.syspath_prepend(str(F1))
    # Frozen scripts use short imports; isolate them from other research tests.
    for name in ('core', 'exterior', 'reference', 'profiled'):
        spec = importlib.util.spec_from_file_location(name, F1/(name+'.py'))
        dependency = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(dependency)
        monkeypatch.setitem(sys.modules, name, dependency)
    spec = importlib.util.spec_from_file_location('prime_field_f1_driver', F1/'driver.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def toy_case(f1, depth):
    from crypto_autoresearcher.index_calculus.curve import Curve
    from reference import domain
    p, a, b = 127, 2, 5
    curve = Curve(p, a, b)
    order = 1+sum(1 if curve.rhs(x) == 0 else 2 if curve.lift_x(x) else 0 for x in range(p))
    points = [curve.lift_x(x) for x in domain(depth, 0, p)]
    points = [point for point in points if point is not None]
    target = curve.add(curve.add(points[0], points[1]), points[2])
    assert target is not None
    return dict(p=p, a=a, b=b, r=order), dict(
        id='software-depth-'+str(depth), kind='triple', depth=depth, terminal=0, target=list(target))


@pytest.mark.parametrize('depth', [2, 3, 4])
def test_f1_complete_against_finite_oracle(f1, depth):
    pytest.importorskip('flint')
    parameters, case = toy_case(f1, depth)
    result = f1.solve_case(parameters, case)
    assert f1.check_case(parameters, case, result)['checked']
    assert result['solutions']
    assert result['complete_coordinate_partitions'] == [[1, 1, 1], [2, 1], [3]]
    if depth == 4:
        assert result['operator_dimensions']['distinct'] == 560
    corrupt = deepcopy(result)
    corrupt['solutions'].pop()
    with pytest.raises(ValueError, match='signed-solution'):
        f1.check_case(parameters, case, corrupt)
    corrupt = deepcopy(result)
    corrupt['solutions'][0] = ((1, 1),)*3
    with pytest.raises(ValueError):
        f1.check_case(parameters, case, corrupt)


def test_f1_resource_and_nonseparable_guards(f1, monkeypatch):
    pytest.importorskip('flint')
    parameters, case = toy_case(f1, 3)
    monkeypatch.setattr(f1, 'solve_stratum', lambda *a: pytest.fail('allocated after guard'))
    with pytest.raises(f1.ExtractionUnknown, match='dimension'):
        f1.solve_case(parameters, case, max_dimension=2)
    from exterior import solve_stratum
    with pytest.raises(ValueError, match='Separable'):
        solve_stratum(parameters, 3, 2, tuple(case['target']), 'distinct')


def test_f1_arity_four_all_partitions(f1):
    parameters, case = toy_case(f1, 2)
    result = f1.arity_four_control(parameters, 2, 0)
    assert len(result) == 5
    assert all(record['solutions'] for record in result)


@pytest.mark.parametrize('depth', [2, 4])
def test_stage_instrumentation_preserves_frozen_arithmetic(f1, depth):
    pytest.importorskip('flint')
    from profiled import Stages
    parameters, case = toy_case(f1, depth)
    events = []
    result = f1.solve_case(parameters, case, stages=Stages(events.append))
    assert result == f1.solve_case(parameters, case)
    assert f1.check_case(parameters, case, result)['checked']
    phases = {row['phase'] for row in events}
    assert {'scalar_chain', 'relation_operator', 'kernel_elimination', 'operator_restriction',
            'character_extraction', 'cubic_factoring', 'curve_lifting',
            'subgroup_verification', 'sign_enumeration'} <= phases
    assert all(row['wall_ns'] >= 0 and row['cpu_ns'] >= 0 and row['status'] == 'complete'
               for row in events)
    assert {row['stratum'] for row in events} == {'distinct', 'twoequal', 'allequal'}


def test_stage_failure_is_retained_and_resource_guard_precedes_allocation(f1):
    from profiled import Stages
    events = []
    stages = Stages(events.append)
    def fail():
        raise RuntimeError('software failure control')
    with pytest.raises(RuntimeError):
        stages.call('failure_control', fail)
    assert events[0]['status'] == 'failed' and events[0]['error_type'] == 'RuntimeError'
    parameters, case = toy_case(f1, 4)
    with pytest.raises(f1.ExtractionUnknown, match='dimension'):
        f1.solve_case(parameters, case, max_dimension=559, stages=stages)
    assert len(events) == 1


@pytest.fixture
def prym(monkeypatch):
    monkeypatch.syspath_prepend(str(STUDY))
    monkeypatch.syspath_prepend(str(ROOT/'research/prym_experiment_design_20261019/implementation'))
    # Existing Pyrm scripts also use short imports. Restore any previous module
    # bindings when this fixture exits rather than leaking into the full suite.
    directories = {
        **{name: ROOT/'research/prym_experiment_design_20261019/implementation'
           for name in ('arithmetic', 'independent', 'relations', 'census', 'fixtures')},
        'check_inputs': ROOT/'research/prym_factor_base_width_20261025',
        'check_census': ROOT/'research/prym_rank_census_20261025',
        'collect_width': ROOT/'research/prym_factor_base_width_20261025',
        'check_prym': STUDY,
        'check_targets': STUDY,
    }
    for name, directory in directories.items():
        spec = importlib.util.spec_from_file_location(name, directory/(name+'.py'))
        dependency = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(dependency)
        monkeypatch.setitem(sys.modules, name, dependency)
    spec = importlib.util.spec_from_file_location('prime_field_prym_completion', STUDY/'prym_completion.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    from fixtures import describe
    fixture, _ = describe(101, 2, 21, 8)
    fixture['software_control'] = True
    return module, fixture


def test_zero_source_and_interpolation_admitted_without_duplicates(prym):
    module, fixture = prym
    context = module.CompletionContext(fixture)
    old = module.Context(fixture)
    # The p101 software generator has x=0. Source=1 must now lift to C.
    assert context.lift_source(1)[0] == 0
    assert old.lift_source(1) is None
    descriptor, reason = context.descriptor(1, (1, 2, 3), (0, 0, 0))
    assert descriptor is not None and reason is None
    assert descriptor['points'][0][0] == 0
    assert context.pi2(descriptor['points'][0]) is None
    assert context.descriptor(1, (0, 1, 2), (0, 0, 0))[1] == 'duplicate_interpolation_x'


def test_completed_small_stream_retains_old_rows_and_verifies_new(prym):
    module, fixture = prym
    old = module.collect(fixture, [1, 2], lambda record: None, include_zero=False)
    events = []
    new = module.collect(fixture, [1, 2], events.append)
    assert old['attempts'] == new['attempts'] == 2*56*64
    assert sum(new['statuses'].values()) == new['attempts']
    assert new['quality']['rows'] == len(new['rows'])
    assert len(new['status_blocks']) == 2
    assert all(len(block['statuses']) == 56*64 for block in new['status_blocks'])
    from collections import Counter
    retained = Counter(new['status_legend'][code] for block in new['status_blocks']
                       for code in block['statuses'])
    assert retained == new['statuses']
    assert new['quality']['rank'] >= old['quality']['rank']
    canonical = lambda row: tuple(row['coefficients'])+(row['source_scalar'],)
    assert {canonical(row) for row in old['rows']} <= {canonical(row) for row in new['rows']}
    assert any(record.get('touches_zero') for record in events)
    for row in new['rows']:
        assert module.verify_row(fixture, row)
    from check_prym import check
    assert check(fixture, [1, 2], new)['checked']
    assert check(fixture, [1, 2], old)['checked']
    for mutate in [lambda v: v['rows'].pop(), lambda v: v.update(branch_sha256='0'*64),
                   lambda v: v['quality'].update(rank=0), lambda v: v['statuses'].update(accepted=0),
                   lambda v: v['status_blocks'][0].update(statuses='+'*3584),
                   lambda v: v['status_blocks'][0].update(branch_sha256='0'*64),
                   lambda v: v['status_legend'].update(S='accepted')]:
        corrupted = deepcopy(new)
        mutate(corrupted)
        with pytest.raises(ValueError):
            check(fixture, [1, 2], corrupted)


def test_scientific_collect_has_no_unadmitted_path(prym):
    module, fixture = prym
    fixture.pop('software_control')
    with pytest.raises(ValueError, match='admission'):
        module.collect(fixture, [1], lambda record: pytest.fail('executed'))


def test_prym_phase_failure_is_journaled(prym, monkeypatch, tmp_path):
    module, fixture = prym
    monkeypatch.setitem(sys.modules, 'prym_completion', module)
    spec = importlib.util.spec_from_file_location('phase_control', STUDY/'run_prym.py')
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    def fail():
        raise RuntimeError('marked software failure')
    import json
    journal = tmp_path/'phases.jsonl'
    with pytest.raises(RuntimeError, match='marked software failure'):
        runner.phase(journal, fixture, 'software_control', 'verification', fail)
    retained = json.loads(journal.read_text())
    assert retained['status'] == 'failed' and retained['error_type'] == 'RuntimeError'
    assert retained['cpu_seconds'] >= 0 and retained['wall_seconds'] >= 0
    assert retained['wall_valid'] is False


@pytest.mark.parametrize('target_index', [0, None])
def test_target_collector_labels_and_fixed_projection(prym, monkeypatch, target_index):
    module, fixture = prym
    monkeypatch.setitem(sys.modules, 'prym_completion', module)
    spec = importlib.util.spec_from_file_location('prime_field_target_completion', STUDY/'target_completion.py')
    target_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(target_module)
    from crypto_autoresearcher.index_calculus.curve import Curve
    from crypto_autoresearcher.index_calculus.target_relations import hash_public_target
    from collect_width import project
    curve = Curve(fixture['p'], fixture['a'], fixture['b'])
    recipe = hash_public_target(curve, fixture['r'], fixture['uid'], 0)
    Q = tuple(recipe['point']) if target_index is not None else tuple(fixture['P'])
    # Different source/multiplier schedules catch accidental target anchors.
    baseline = module.collect(fixture, [1, 2], lambda row: None)
    events = []
    result = target_module.collect(fixture, [1, 2], baseline['rows'], Q, [1, 3], events.append)
    assert result['complete'] and result['attempts'] == 2*56*64
    assert sum(result['statuses'].values()) == result['attempts']
    assert result['projection'] == baseline['projection']
    assert result['rows']
    for row in result['rows']:
        assert row['source_scalar'] == 0 and row['target_coefficient'] in [1, 3]
        assert module.verify_row(fixture, row, target=Q)
        vector, offset = project(row, result['projection'], fixture['r'])
        # Direct point sum verifies the projection sign independently of logs.
        lhs = None
        for c, point in zip(vector, result['projection']['unknown_points']):
            lhs = curve.add(lhs, curve.mul(c, tuple(point)))
        assert lhs == curve.add(curve.mul(offset, tuple(fixture['P'])),
                                curve.mul(row['target_coefficient'], Q))
        corrupted = deepcopy(row)
        corrupted['target_coefficient'] = (row['target_coefficient']+1) % fixture['r']
        with pytest.raises(ValueError):
            module.verify_row(fixture, corrupted, target=Q)
    certificate = result['final_target_certificate']
    if certificate is not None:
        assert curve.mul(certificate['scalar'], tuple(fixture['P'])) == Q
    if target_index is None:
        assert certificate is not None and certificate['scalar'] == 1  # software positive only
    from check_targets import check
    assert check(fixture, [1, 2], baseline['rows'], Q, [1, 3], result)['complete_branch_replay']
    mutations = [lambda v: v['rows'].pop(), lambda v: v.update(branch_sha256='0'*64),
                 lambda v: v['statuses'].update(accepted=0),
                 lambda v: v['status_blocks'][0].update(statuses='+'*3584),
                 lambda v: v['status_blocks'][0].update(branch_sha256='0'*64),
                 lambda v: v['preprocessing'].update(rank=0),
                 lambda v: v['projection'].update(U=0),
                 lambda v: v.update(target_is_public_anchor=not v['target_is_public_anchor']),
                 lambda v: v['target_identification'].update(augmented_rank=-1)]
    if certificate is not None:
        mutations += [lambda v: v['final_target_certificate'].update(value=-1),
                      lambda v: v['final_target_certificate'].update(row_weights=[])]
        mutations += [lambda v: v['first_combined_recovery'].update(attempt=-1)]
    for mutate in mutations:
        corrupt = deepcopy(result)
        mutate(corrupt)
        with pytest.raises(ValueError):
            check(fixture, [1, 2], baseline['rows'], Q, [1, 3], corrupt)
    with pytest.raises(ValueError, match='independent of target'):
        target_module.prepare(fixture, [1, 2], result['rows'][:1])
    assert len([row for row in events if row['kind'] == 'verified_witness']) == len(result['rows'])
    fixture.pop('software_control')
    with pytest.raises(ValueError, match='admission'):
        target_module.collect(fixture, [1, 2], [], Q, [1], lambda row: pytest.fail('executed'))


def test_gate_rejects_parameters_before_any_checkpoint(tmp_path):
    import json
    from crypto_autoresearcher.index_calculus.execution_gate import admit
    protocol, release = tmp_path/'protocol.json', tmp_path/'release.json'
    protocol.write_text('{}')
    release.write_text(json.dumps(dict(parameters={'max_dimension': 1}, execution_authorized=True)))
    with pytest.raises(ValueError, match='parameters'):
        admit(tmp_path, protocol, tmp_path/'inputs.json', [], {'max_dimension': 560}, release)


def test_public_target_recipe_has_separate_complete_hash_replay(prym):
    _,fixture=prym
    from crypto_autoresearcher.index_calculus.curve import Curve
    from crypto_autoresearcher.index_calculus.target_relations import hash_public_target
    from check_targets import check_recipe
    curve=Curve(fixture['p'],fixture['a'],fixture['b'])
    identity='urn:marked-small-software-curve';domain='marked-software-target/v1';attempts=[]
    recipe=hash_public_target(curve,fixture['r'],identity,0,domain=domain,on_attempt=attempts.append)
    result=check_recipe(fixture,identity,domain,0,10000,recipe,attempts)
    assert result['hash_recipe_checked'] and result['hash_attempts_replayed']==len(attempts)
    for mutate in [lambda v:v.update(point=[0,0]),lambda v:v['selected'].update(counter=999),
                   lambda v:v.update(scalar_label_generated=True),lambda v:v.update(curve_uid='wrong')]:
        corrupted=deepcopy(recipe);mutate(corrupted)
        with pytest.raises(ValueError):check_recipe(fixture,identity,domain,0,10000,corrupted,attempts)
    with pytest.raises(ValueError):check_recipe(fixture,identity+'wrong',domain,0,10000,recipe,attempts)
    with pytest.raises(ValueError):check_recipe(fixture,identity,domain,0,10000,recipe,attempts+[attempts[-1]])
