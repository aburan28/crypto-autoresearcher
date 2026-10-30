"""Administrative software fixtures; never run a A1/P256 descriptor or native CLI."""
import gzip
import importlib.util
import json
from pathlib import Path
import sys
import pytest

HERE = Path(__file__).resolve().parent


@pytest.fixture
def modules(monkeypatch):
    monkeypatch.syspath_prepend(str(HERE))
    result = {}
    for name in ('common','prepare','analyze','supervise'):
        spec = importlib.util.spec_from_file_location(name,HERE/(name+'.py'))
        module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        monkeypatch.setitem(sys.modules,name,module)
        result[name] = module
    return result


def fixture_run(modules,tmp_path,monkeypatch):
    common,prepare,analyze = (modules[k] for k in ('common','prepare','analyze'))
    head = common.git('rev-parse','HEAD')
    protocol = prepare.make_protocol(head)
    protocol['protocol_id'] = 'A1-administrative-software-control'
    (tmp_path/'analyze.py').write_bytes((HERE/'analyze.py').read_bytes())
    path = tmp_path/'protocol.json';path.write_text(json.dumps(protocol))
    prepare.protocol_tools().freeze(path,head,True)
    run = tmp_path/'software-only';run.mkdir()
    execution = dict(returncode=-15,source_unchanged_after=True,timeout=True,exception=None,
        observed_git_head=head,source_commit=head,diagnostic_wall_seconds=3,
        cpu_user_seconds=1,cpu_sys_seconds=1,max_rss_bytes=1,
        started_at='2026-10-29T00:00:00Z',finished_at='2026-10-29T00:00:03Z',owner='software-control')
    host = dict(cpu_model='software fixture',logical_cpus=1,memory_bytes=1,kernel='software fixture',
                hypervisor=None,isolation_tier_max=None,executable_sha256=common.digest(Path(sys.executable).resolve()),git_dirty=True)
    (run/'execution.json').write_text(json.dumps(execution));(run/'host.json').write_text(json.dumps(host))
    monkeypatch.setattr(sys,'argv',['analyze.py','--run',str(run),'--protocol',str(path)])
    return run,execution


def test_stopped_panel_preserves_six_unknown_cells(modules,tmp_path,monkeypatch):
    run,_ = fixture_run(modules,tmp_path,monkeypatch)
    modules['analyze'].main()
    analysis = json.loads((run/'analysis.json').read_text());export = json.loads((run/'export.json').read_text())
    assert analysis['unknown_cells'] == 6 and not analysis['panel_complete']
    assert all(c['delta'] is None and c['accepted_witnesses'] is None for c in analysis['cells'])
    assert export['flow']['completed'] == 0 and export['flow']['not_completed'] == 6
    assert export['backend_record']['physical_executions'] == 1
    assert all(r['measurements']['wall_seconds'] is None for r in export['runs'])
    assert export['backend_record']['shared_diagnostic_resources']['diagnostic_wall_seconds'] == 3


def test_missing_authorization_refuses_before_source_or_output(modules,tmp_path,monkeypatch):
    module=modules['supervise'];release=tmp_path/'release.json'
    release.write_text(json.dumps(dict(owner='software-control',parameters=modules['common'].PARAMETERS,execution_authorized=False)))
    out=tmp_path/'must-not-exist'
    monkeypatch.setattr(module,'bindings',lambda *a:pytest.fail('source or launch path reached'))
    monkeypatch.setattr(sys,'argv',['supervise.py','--owner','software-control','--release',str(release),'--protocol',str(tmp_path/'absent.json'),'--out',str(out)])
    with pytest.raises(ValueError,match='release is absent'):module.main()
    assert not out.exists()




def small_carried_arm():
    return dict(B=[[1],[2]],U=[[1],[1]],rhs=[3,4],preprocessing_quality=dict(rank=0,columns=1,nullity=1),
        stacked_rank=2,outside_rank=1,rank_gain=1,base_rank_after=1,
        cancellation=dict(base_rank_before=0,base_rank_after=1,outside_rank=1,rank_gain=1,
            cancellations=[dict(coefficients=[4],rhs=4,partial_row_weights=[1,4])]))


def test_carried_weights_cancel_outside_and_reproduce_equation(modules):
    arm=small_carried_arm();assert modules['analyze'].check_cancellations(arm,5)==1
    arm['cancellation']['cancellations'][0]['partial_row_weights']=[1,0]
    with pytest.raises(ValueError,match='do not cancel outside'):modules['analyze'].check_cancellations(arm,5)


def test_extra_unknown_rank_is_subtracted_and_false_equation_rejected(modules):
    arm=small_carried_arm();arm['stacked_rank']=3
    with pytest.raises(ValueError,match='Delta rank identity'):modules['analyze'].check_cancellations(arm,5)
    arm=small_carried_arm();arm['cancellation']['cancellations'][0]['coefficients']=[3]
    with pytest.raises(ValueError,match='false carried cancellation'):modules['analyze'].check_cancellations(arm,5)


def test_signed_public_known_outside_projection(modules):
    result=dict(projection=dict(U=1,native_to_projected=[['known',2],['unknown',0,-1]]),
                outside_projection=dict(native_to_projected=[['known',1],['unknown',0]]))
    row=dict(source_scalar=4,coefficients=[1,2],outside_coefficients=[3,4])
    assert modules['analyze'].project_partial_metadata(row,result,2,5)==([3],[4],4)


def test_gzip_duplicate_encodings_refused(modules,tmp_path):
    path=tmp_path/'software.json'
    with gzip.open(str(path)+'.gz','wt') as stream:json.dump({'software_control':True},stream)
    assert modules['analyze'].load(path)=={'software_control':True}
    path.write_text('{}')
    with pytest.raises(ValueError,match='ambiguous retained encodings'):modules['analyze'].load(path)


def test_three_nested_arm_records_charge_one_shared_stream(modules,tmp_path,monkeypatch):
    run,execution=fixture_run(modules,tmp_path,monkeypatch);common=modules['common'];raw=run/'raw';raw.mkdir()
    data=json.loads(common.INPUTS.read_text());cell=data['cells'][0];f=cell['fixture']
    # Only administrative synthetic plumbing: no actual pool points, recipe,
    # curve/field memberships, branch collection or dense rank solver executed.
    monkeypatch.setattr(modules['analyze'],'check_pool_metadata',lambda *args:None)
    arms=[];checks=[]
    for name,prefix in zip(common.ARMS,(0,16,32)):
        quality=dict(rows=97,rank=13,columns=15,nullity=2)
        cancellation=dict(base_rank_before=13,base_rank_after=13,outside_rank=0,rank_gain=0,cancellations=[])
        arm=dict(arm=name,pool_prefix=prefix,row_indices=[],B=[],U=[],rhs=[],preprocessing_quality=quality,
            new_quality=dict(rows=0,unique_affine_equations=0),stacked_rank=13,outside_rank=0,rank_gain=0,
            base_rank_after=13,direct_base_rank=13,direct_base_gain=0,cross_row_cancellation_gain=0,complete=True,cancellation=cancellation,
            old_kernel=[[0]*15,[0]*15],cancelled_old_kernel_syndromes=[],nonzero_old_kernel_syndromes=0)
        arms.append(arm);checks.append(dict(arm=name,rank_gain=0,outside_rank=0,stacked_rank=13,base_rank_after=13,direct_base_rank=13,direct_base_gain=0,cross_row_cancellation_gain=0,cancellations_verified=0))
    value=dict(schema='prym-residual-partials/v1',curve_uid=f['uid'],complete=True,source_order=cell['source_order'],
        attempts=common.expected_attempts(cell),inputs_sha256=common.digest(common.INPUTS),rows=[],arms=arms,
        pool={'software_control':True},projection=dict(U=15),outside_projection=dict(native_to_projected=[['unknown',j] for j in range(32)]),operation_vector={'software_counter':7})
    with gzip.open(raw/(cell['id']+'.json.gz'),'wt') as stream:json.dump(value,stream)
    (raw/(cell['id']+'.verification.json')).write_text(json.dumps(dict(checked=True,complete_branch_replay=True,pool_recipe_checked=True,
        attempts_replayed=value['attempts'],rows_verified=0,arms=checks)))
    modules['analyze'].main();analysis=json.loads((run/'analysis.json').read_text());export=json.loads((run/'export.json').read_text())
    assert analysis['unknown_cells']==3 and analysis['physical_collection_attempts_observed']==2293760
    assert analysis['physical_replay_attempts_observed']==2293760
    assert len(export['runs'])==6 and export['backend_record']['physical_executions']==1
    assert export['runs'][0]['measurements']['counters']=={'software_counter':7}
    assert all(r['measurements']['counters']=={} for r in export['runs'] if r['arm']!='smooth')


def test_collected_snapshot_survives_failed_elimination_with_unknown_gains(modules,tmp_path,monkeypatch):
    run,_=fixture_run(modules,tmp_path,monkeypatch);common=modules['common'];raw=run/'raw';raw.mkdir()
    data=json.loads(common.INPUTS.read_text());cell=data['cells'][0];f=cell['fixture']
    monkeypatch.setattr(modules['analyze'],'check_pool_metadata',lambda *args:None)
    # Synthetic administrative snapshot with no E-point/pool generation.
    value=dict(schema='prym-residual-partials/v1',curve_uid=f['uid'],complete=True,source_order=cell['source_order'],
        attempts=common.expected_attempts(cell),inputs_sha256=common.digest(common.INPUTS),rows=[],arms=[],pool={'software_control':True},operation_vector={'software_counter':7})
    with gzip.open(raw/(cell['id']+'.collection.json.gz'),'wt') as stream:json.dump(value,stream)
    modules['analyze'].main();analysis=json.loads((run/'analysis.json').read_text());export=json.loads((run/'export.json').read_text())
    assert analysis['unknown_cells']==6 and analysis['physical_collection_attempts_observed']==2293760
    assert all(c['delta'] is None for c in analysis['cells'])
    assert export['runs'][0]['measurements']['counters']=={'software_counter':7}
    assert all(r['measurements']['counters']=={} for r in export['runs'] if r['arm']!='smooth')
