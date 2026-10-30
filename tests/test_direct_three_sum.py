"""Small marked controls for relation equality, completeness and corrupt certificates."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import sys

import pytest

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'research/prime_field_a3_execution_20261030'
OLD=ROOT/'research/prym_experiment_design_20261019/implementation'


@pytest.fixture(scope='module')
def prepared():
    patch=pytest.MonkeyPatch();patch.syspath_prepend(str(OLD));patch.syspath_prepend(str(HERE));modules={}
    for name,path in [('arithmetic',OLD),('independent',OLD),('relations',OLD),('fixtures',OLD),('check',HERE),('core',HERE)]:
        spec=importlib.util.spec_from_file_location(name,path/(name+'.py'));module=importlib.util.module_from_spec(spec)
        patch.setitem(sys.modules,name,module);spec.loader.exec_module(module);modules[name]=module
    fixture,_=modules['fixtures'].describe(101,2,21,8);fixture['software_control']=True
    cell=dict(id='small-direct-control',fixture=fixture,source_order=[1,2,3,4],preprocessing_rows=[],archived_norm_rows=[])
    result=dict(schema='direct-three-sum-cell/v1',cell_id=cell['id'],curve_uid=fixture['uid'],complete=True,arms=[])
    for name in ('enumeration','pair_table'):
        value,meter=modules['core'].collect(cell,name,lambda e:None)
        value['analysis']=modules['core'].analyze(cell,value,meter);result['arms'].append(value)
    yield modules,cell,result
    patch.undo()


def test_complete_small_equivalence_and_infinity_query(prepared):
    modules,cell,result=prepared;verification=modules['check'].check(cell,result)
    assert verification['checked'] and verification['rows_verified']>0
    assert result['arms'][0]['rows']==result['arms'][1]['rows']
    assert verification['attempts_replayed']==4*56*8
    assert verification['pair_entries_checked']==28*4 and verification['queries_checked']==4*8*2
    assert any(q['wanted']is None for b in result['arms'][1]['status_blocks'] for q in b['queries'])
    assert all(r['analysis']['total_counters']['Fr.field_mul']>0 for r in result['arms'])


def test_complete_replay_rejects_omissions_labels_ranks_and_costs(prepared):
    modules,cell,result=prepared
    mutations=[lambda r:r['arms'][0]['rows'].pop(),
               lambda r:r['arms'][0]['status_blocks'][0].update(statuses='.'),
               lambda r:r['arms'][1]['pair_entries'][0]['point'].__setitem__(1,0),
               lambda r:r['arms'][1]['status_blocks'][0]['queries'][0]['bucket'].append(999),
               lambda r:r['arms'][1]['analysis']['combined'].update(rank=-1),
               lambda r:r['arms'][0]['analysis']['old_kernel'][0].append(1),
               lambda r:r['arms'][1]['analysis']['total_counters'].__setitem__('queries',0)]
    for mutate in mutations:
        bad=deepcopy(result);mutate(bad)
        with pytest.raises(ValueError): modules['check'].check(cell,bad)


def test_native_admission_and_size_refusals(prepared,monkeypatch):
    modules,cell,result=prepared;bad=deepcopy(cell);bad['fixture'].pop('software_control')
    with pytest.raises(ValueError,match='admission'): modules['core'].collect(bad,'enumeration',lambda e:pytest.fail('launched'))
    monkeypatch.setitem(modules['core'].PARAMETERS,'max_pair_entries',0)
    with pytest.raises(ValueError,match='pair-table size gate'): modules['core'].collect(cell,'pair_table',lambda e:None)
    monkeypatch.setitem(modules['core'].PARAMETERS,'max_retained_rows',0)
    records=[]
    with pytest.raises(ValueError,match='retained-row size gate'): modules['core'].collect(cell,'enumeration',records.append)
    assert any(e['kind']=='accepted' for e in records)


def test_archived_norm_subset_cannot_use_a_five_term_row(prepared):
    modules,cell,result=prepared;row=result['arms'][0]['rows'][0];reference=deepcopy(row)
    reference.update(norm_completed=True,base_labels=[[j,s,0 if s==1 else 1] for j,s in zip(row['triple'],row['signs'])],
                     residual_E_images=[[7,3],[7,98]])
    with_reference=deepcopy(cell);with_reference['archived_norm_rows']=[reference]
    assert modules['check'].check(with_reference,result)['archived_norm_subset']['witnesses']==1
    with_reference['archived_norm_rows'][0]['coefficients'][0]=(reference['coefficients'][0]+1)%cell['fixture']['r']
    with pytest.raises(ValueError,match='coefficient identity'): modules['check'].check(with_reference,result)
