"""Marked small-curve positives and deliberate pool/row/cancellation corruptions."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import sys

import pytest

ROOT=Path(__file__).resolve().parents[1];HERE=ROOT/'research/prime_field_a2_execution_20261030'


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
    result=modules['core'].collect(cell,lambda e:None)
    result['arms']=[modules['core'].analyze_arm(cell,result,name) for name in ('smooth','norm_completed')]
    yield modules,cell,result
    patch.undo()


def test_norm_positive_and_complete_independent_replay(prepared):
    m,cell,result=prepared
    assert result['rows'] and any(row['norm_completed'] for row in result['rows'])
    assert m['check'].check(cell,result)['checked']
    assert result['arms'][1]['combined_quality']['rank']>=result['arms'][0]['combined_quality']['rank']
    assert all(len(row['coefficients'])==8 and 'outside_coefficients' not in row for row in result['rows'])


def test_norm_geometry_rank_and_inclusion_corruptions(prepared):
    m,cell,result=prepared
    for mutate in (lambda v:v['rows'][0].update(norm_completed=not v['rows'][0]['norm_completed']),
                   lambda v:v['rows'][0]['residual_E_images'][0].__setitem__(1,0),
                   lambda v:v['arms'][1].update(rank_gain=-1),lambda v:v['arms'][1]['old_kernel_syndromes'][0].append(1)):
        bad=deepcopy(result);mutate(bad)
        with pytest.raises(ValueError):m['check'].check(cell,bad)


def test_norm_admission_and_retention_gate(prepared,monkeypatch):
    m,cell,result=prepared;bad=deepcopy(cell);bad['fixture'].pop('software_control')
    with pytest.raises(ValueError,match='admission'):m['core'].collect(bad,lambda e:pytest.fail('ran'))
    monkeypatch.setitem(m['core'].PARAMETERS,'max_retained_rows',0)
    with pytest.raises(ValueError,match='size gate'):m['core'].collect(cell,lambda e:None)
