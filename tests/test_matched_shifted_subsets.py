"""Marked small-curve controls, never a retained p4099 collector launch."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import sys

import pytest

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'research/prime_field_b2_execution_20261030'


@pytest.fixture
def modules(monkeypatch):
    old=ROOT/'research/prym_experiment_design_20261019/implementation'
    monkeypatch.syspath_prepend(str(HERE));monkeypatch.syspath_prepend(str(old))
    paths={**{name:old for name in ('arithmetic','independent','relations','fixtures')},
           **{name:ROOT/'research/prym_factor_base_width_20261025' for name in ('collect_width','check_inputs')},
           'check':HERE,'core':HERE}
    result={}
    for name,directory in paths.items():
        spec=importlib.util.spec_from_file_location(name,directory/(name+'.py'))
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        monkeypatch.setitem(sys.modules,name,module);result[name]=module
    f,_=result['fixtures'].describe(101,2,21,8);f['software_control']=True
    return result,f


def test_h0_positive_and_full_independent_replay(modules):
    m,f=modules
    cell=dict(id='marked-h0-control',fixture=f,source_order=[1,2],active_atoms=list(range(8)),shift=0,preprocessing_rows=[])
    events=[];result=m['core'].collect(cell,0,'baseline',events.append)
    assert result['rows'] and result['complete']
    assert m['check'].check(cell,0,'baseline',result)['checked']
    assert sum(result['statuses'].values())==result['attempts']==2*56*64
    assert len(result['projection']['native_to_projected'])==8
    assert len([e for e in events if e['kind']=='accepted'])==len(result['rank_progress'])
    # A valid h0 row is exactly the original principal-divisor certificate.
    for row in result['rows']:
        historical={k:v for k,v in row.items() if k not in ('cover_shift','active_atoms')}
        historical.update(schema='prym-principal-row/v1',source_locator='explicit interpolation and residual quadratic; no post-hoc kernel')
        assert m['independent'].verify_row(f,historical)
    for mutate in [lambda v:v['rows'].pop(),lambda v:v['status_blocks'][0].update(statuses='+'*3584),
                   lambda v:v['combined_quality'].update(rank=-1),lambda v:v['old_kernel_syndromes'][0].append(1),
                   lambda v:v['rank_progress'][0].update(attempt=-1)]:
        corrupt=deepcopy(result);mutate(corrupt)
        with pytest.raises(ValueError):m['check'].check(cell,0,'baseline',corrupt)


def test_nonzero_shift_same_subset_and_false_witnesses(modules):
    m,f=modules
    # Broader marked-small base gives an actual nonzero-shift positive; the
    # initial eight-atom/source prefix had no accepted witness in either oracle.
    f,_=m['fixtures'].describe(101,2,21,16);f['software_control']=True
    from crypto_autoresearcher.index_calculus.cover_frames import ShiftedCover
    frame=ShiftedCover(f['p'],f['a'],f['b'],1)
    active=[i for i,atom in enumerate(f['factor_base']) if frame.lifts(tuple(atom['point']))]
    assert len(active)>=3
    cell=dict(id='marked-shift-control',fixture=f,source_order=list(range(1,9)),active_atoms=active,shift=1,preprocessing_rows=[])
    results=[]
    for arm,h in [('baseline',0),('shifted',1)]:
        result=m['core'].collect(cell,h,arm,lambda e:None)
        assert m['check'].check(cell,h,arm,result)['checked']
        assert result['projection']['U']+len(result['projection']['public_derivations'])==16
        assert all(not row['coefficients'][j] for row in result['rows'] for j in range(16) if j not in active)
        results.append(result)
    assert results[1]['rows']  # Positive through the actual nonzero-shift path.
    row=results[1]['rows'][0]
    for mutate in [lambda v:v.update(cover_shift=0),lambda v:v['coefficients'].__setitem__(0,99),
                   lambda v:v['constraints'][0].__setitem__(1,0),lambda v:v['residual_roots'].__setitem__(0,v['residual_roots'][1])]:
        corrupt=deepcopy(row);mutate(corrupt)
        with pytest.raises(ValueError):m['check'].verify_row(f,1,active,corrupt)
    inactive=next((i for i in range(16) if i not in active),None)
    if inactive is not None:
        with pytest.raises(ValueError,match='no rational'):m['core'].ShiftedContext(f,1,sorted(active+[inactive]))


def test_native_admission_and_domain_guards(modules):
    m,f=modules
    cell=dict(id='guard',fixture=f,source_order=[1],active_atoms=list(range(8)),preprocessing_rows=[])
    f.pop('software_control')
    with pytest.raises(ValueError,match='admission'):m['core'].collect(cell,0,'baseline',lambda e:pytest.fail('ran'))
    with pytest.raises(ValueError):m['core'].ShiftedContext(f,0,[0,0,1])
    with pytest.raises(ValueError):m['core'].ShiftedContext(f,-1,[0,1,2])
