"""Marked p101 controls; no actual larger-field curve or target is generated."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import pytest

ROOT=Path(__file__).resolve().parents[1];HERE=ROOT/'research/prime_field_a4_execution_20261030'
OLD=ROOT/'research/prym_experiment_design_20261019/implementation'


@pytest.fixture(scope='module')
def prepared():
    patch=pytest.MonkeyPatch();patch.syspath_prepend(str(OLD));patch.syspath_prepend(str(HERE));modules={}
    for name,path in [('arithmetic',OLD),('independent',OLD),('relations',OLD),('fixtures',OLD),('check',HERE),('core',HERE)]:
        spec=importlib.util.spec_from_file_location(name,path/(name+'.py'));module=importlib.util.module_from_spec(spec)
        patch.setitem(sys.modules,name,module);spec.loader.exec_module(module);modules[name]=module
    rules=json.loads((HERE/'inputs.json').read_text());rules.update(fields=[dict(p=101,base_size=8)],curves_per_field=1,sources=8,targets=4,prefixes=[0,2,8],software_control=True)
    events=[];generated=modules['core'].generate(rules,events.append);modules['check'].check_generation(rules,generated)
    cell=generated['cells'][0];cell['fixture']['software_control']=True
    value,meter=modules['core'].collect(cell,rules,events.append)
    for count in rules['prefixes']: value['prefixes'].append(modules['core'].prefix_analysis(cell,rules,value,meter,count))
    value['total_counters']=meter.counters()
    yield modules,rules,generated,cell,value
    patch.undo()


def test_complete_holdout_draw_collection_and_target_certificates(prepared):
    modules,rules,generated,cell,value=prepared;verification=modules['check'].check(cell,rules,value)
    assert verification['checked'] and verification['signed_triples_enumerated']==56*8
    assert verification['source_queries_checked']==8*16 and verification['target_queries_checked']==4*16
    assert verification['source_rows_verified']>0
    assert len(verification['prefixes'])==3
    assert any(p['joint_targets']>0 for p in verification['prefixes'])
    assert len(value['target_generation']['targets'])==4


def test_selection_and_draw_corruptions(prepared):
    modules,rules,generated,cell,value=prepared
    bad=deepcopy(generated);bad['search_trace'][0]['b']+=1
    with pytest.raises(ValueError): modules['check'].check_generation(rules,bad)
    bad=deepcopy(value);bad['target_generation']['targets'][0]['point'][0]+=1
    with pytest.raises(ValueError,match='target draw'): modules['check'].check(cell,rules,bad)


def test_recovery_query_rank_and_counter_corruptions(prepared):
    modules,rules,generated,cell,value=prepared
    mutations=[lambda v:v['status_blocks'][0]['queries'][0]['bucket'].append(999),
               lambda v:v['target_collection']['rows'].pop(),
               lambda v:v['prefixes'][0]['base'].update(rank=1),
               lambda v:v['prefixes'][-1]['joint_recoveries'][0]['syndrome'].append(1),
               lambda v:v['total_counters'].__setitem__('target_queries',0)]
    for mutate in mutations:
        bad=deepcopy(value);mutate(bad)
        with pytest.raises(ValueError): modules['check'].check(cell,rules,bad)


def test_metered_certificate_system_identifies_without_full_rank(prepared):
    modules,_,_,cell,_=prepared;m=modules['core'];meter=m.direct.Meter(cell['fixture']);system=m.CertifiedSystem(3,meter)
    system.add([1,2,0],5);kernel=system.kernel();identified=system.identify([2,4,0],kernel)
    assert identified['identifiable'] and identified['value']==10 and identified['row_weights']==[2]
    assert len(kernel)==2 and not system.identify([0,0,1],kernel)['identifiable']
    modules['check'].check_identified(dict(identified,scalar=10),[2,4,0],system.rows,system.rhs,kernel,cell['fixture']['r'])
    bad=deepcopy(identified);bad['row_weights'][0]+=1
    with pytest.raises(ValueError,match='row-weight'): modules['check'].check_identified(dict(bad,scalar=10),[2,4,0],system.rows,system.rhs,kernel,cell['fixture']['r'])


def test_native_generation_and_collection_cannot_bypass_admission(prepared):
    modules,rules,generated,cell,value=prepared;bad=deepcopy(rules);bad.pop('software_control')
    with pytest.raises(ValueError,match='admission'): modules['core'].generate(bad,lambda e:pytest.fail('ran'))
    native=deepcopy(cell);native['fixture'].pop('software_control')
    with pytest.raises(ValueError,match='admission'): modules['core'].collect(native,rules,lambda e:pytest.fail('ran'))
