"""Marked small-curve positives and deliberate pool/row/cancellation corruptions."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import sys

import pytest

ROOT=Path(__file__).resolve().parents[1];HERE=ROOT/'research/prime_field_a1_execution_20261030'


@pytest.fixture(scope='module')
def prepared():
    patch=pytest.MonkeyPatch()
    old=ROOT/'research/prym_experiment_design_20261019/implementation'
    patch.syspath_prepend(str(old));patch.syspath_prepend(str(HERE))
    modules={}
    for name,path in [('arithmetic',old),('relations',old),('independent',old),('fixtures',old),('check',HERE),('core',HERE)]:
        spec=importlib.util.spec_from_file_location(name,path/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);patch.setitem(sys.modules,name,m);modules[name]=m
    f,_=modules['fixtures'].describe(101,2,21,8);f['software_control']=True
    cell=dict(id='marked-small-residual-control',fixture=f,source_order=[1],preprocessing_rows=[],pool_curve_uid='marked-software-full-curve-identity')
    recipe=dict(domain='prime-field-residual-pool/20261030/v1',size=32,max_counter=10000);events=[]
    pool=modules['core'].generate_pool(cell,recipe,events.append);result=modules['core'].collect(cell,pool,events.append)
    result['arms']=[modules['core'].analyze_arm(cell,result,k) for k in (0,16,32)]
    yield modules,cell,recipe,result,events
    patch.undo()


def test_positive_complete_census_and_independent_cancellation(prepared):
    m,cell,recipe,result,events=prepared
    assert result['attempts']==56*64 and result['rows']
    assert any(row['outside_indices_used'] for row in result['rows'])
    checked=m['check'].check(cell,result,recipe);assert checked['checked'] and checked['pool_recipe_checked']
    assert result['arms'][2]['outside_rank']>0
    assert all(a['rank_gain']<=result['projection']['U'] for a in result['arms'])
    assert all(a['naive_augmented_gain']-a['outside_rank']==a['rank_gain'] for a in result['arms'])
    assert len([e for e in events if e['kind']=='accepted'])==len(result['rows'])


def test_false_pool_and_witnesses_refused(prepared):
    m,cell,recipe,result,events=prepared
    for mutate in [lambda v:v['pool']['hash_attempts'][0].update(counter=999),lambda v:v['pool']['points'][0].__setitem__(1,0),
                   lambda v:v['status_blocks'][0].update(statuses='+'*3584),lambda v:v['rows'].pop()]:
        bad=deepcopy(result);mutate(bad)
        with pytest.raises(ValueError):m['check'].check(cell,bad,recipe)
    row=deepcopy(next(row for row in result['rows'] if row['outside_indices_used']));row['outside_coefficients'][row['outside_indices_used'][0]]+=1
    with pytest.raises(ValueError):m['check'].verify_row(cell,result['pool'],row)


def test_unknown_count_and_cancellation_corruptions_refused(prepared):
    m,cell,recipe,result,events=prepared
    for mutate in [lambda v:v['arms'][2].update(rank_gain=v['arms'][2]['rank_gain']+1),
                   lambda v:v['arms'][2]['cancellation']['cancellations'].pop(),
                   lambda v:v['arms'][2]['cancellation']['cancellations'][0].update(rhs=(v['arms'][2]['cancellation']['cancellations'][0]['rhs']+1)%cell['fixture']['r'])]:
        bad=deepcopy(result);mutate(bad)
        with pytest.raises(ValueError):m['check'].check_arms(cell,bad)


def test_admission_and_matrix_size_guards(prepared,monkeypatch):
    m,cell,recipe,result,events=prepared;bad=deepcopy(cell);bad['fixture'].pop('software_control')
    with pytest.raises(ValueError,match='admission'):m['core'].generate_pool(bad,recipe,lambda e:pytest.fail('ran'))
    monkeypatch.setitem(m['core'].PARAMETERS,'max_partial_rows',0)
    with pytest.raises(ValueError,match='size gate'):m['core'].collect(cell,result['pool'],lambda e:None)
