"""Administrative software fixtures; never run a A2/P256 descriptor or native CLI."""
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
    protocol['protocol_id'] = 'A2-administrative-software-control'
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


def test_stopped_panel_preserves_four_unknown_cells(modules,tmp_path,monkeypatch):
    run,_ = fixture_run(modules,tmp_path,monkeypatch)
    modules['analyze'].main()
    analysis = json.loads((run/'analysis.json').read_text());export = json.loads((run/'export.json').read_text())
    assert analysis['unknown_cells'] == 4 and not analysis['panel_complete']
    assert all(c['rank_gain'] is None and c['accepted_witnesses'] is None for c in analysis['cells'])
    assert export['flow']['completed'] == 0 and export['flow']['not_completed'] == 4
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




def synthetic_norm_row():
    # Metadata fixture, not a curve witness or native relation.
    fixture=dict(p=101,r=97,factor_base=[{'point':[1,10]},{'point':[4,20]},{'point':[9,30]}])
    row=dict(residual_roots=[4,97],v_coefficients=[0,1],residual_E_images=[[16,4],[16,97]],
             norm_completed=True,base_labels=[[0,1,0],[1,1,0],[2,1,0]],coefficients=[1,1,1])
    return fixture,row


def test_norm_metadata_requires_true_E_pair_and_base_only_coefficients(modules):
    fixture,row=synthetic_norm_row();modules['analyze'].check_residual_metadata(row,fixture)
    row['coefficients']=[2,1,1]
    with pytest.raises(ValueError,match='base-only residual coefficient'):modules['analyze'].check_residual_metadata(row,fixture)
    fixture,row=synthetic_norm_row();row.update(v_coefficients=[1],residual_E_images=[[16,1],[16,1]])
    with pytest.raises(ValueError,match='noncancelling residual pair'):modules['analyze'].check_residual_metadata(row,fixture)


def test_false_completion_label_and_outside_column_rejected(modules):
    fixture,row=synthetic_norm_row();row['norm_completed']=False
    with pytest.raises(ValueError,match='false norm-completion label'):modules['analyze'].check_residual_metadata(row,fixture)
    fixture,row=synthetic_norm_row();row['outside_coefficients']=[]
    with pytest.raises(ValueError,match='outside unknowns'):modules['analyze'].check_residual_metadata(row,fixture)


def test_gzip_duplicate_encodings_refused(modules,tmp_path):
    path=tmp_path/'software.json'
    with gzip.open(str(path)+'.gz','wt') as stream:json.dump({'software_control':True},stream)
    assert modules['analyze'].load(path)=={'software_control':True}
    path.write_text('{}')
    with pytest.raises(ValueError,match='ambiguous retained encodings'):modules['analyze'].load(path)


def test_completed_collection_snapshot_preserves_cost_with_unknown_arm_ranks(modules,tmp_path,monkeypatch):
    run,_=fixture_run(modules,tmp_path,monkeypatch);common=modules['common'];raw=run/'raw';raw.mkdir()
    cell=json.loads(common.INPUTS.read_text())['cells'][0];f=cell['fixture']
    value=dict(schema='prym-norm-completion/v1',curve_uid=f['uid'],source_order=cell['source_order'],complete=True,
        attempts=common.expected_attempts(cell),inputs_sha256=common.digest(common.INPUTS),rows=[],arms=[],operation_vector={'software_counter':7})
    with gzip.open(raw/(cell['id']+'.collection.json.gz'),'wt') as stream:json.dump(value,stream)
    modules['analyze'].main();analysis=json.loads((run/'analysis.json').read_text());export=json.loads((run/'export.json').read_text())
    assert analysis['unknown_cells']==4 and analysis['physical_collection_attempts_observed']==2293760
    assert all(c['rank_gain'] is None for c in analysis['cells'])
    assert export['runs'][0]['measurements']['counters']=={'software_counter':7}
    assert all(r['measurements']['counters']=={} for r in export['runs'] if r['arm']!='smooth')


def test_synthetic_checked_arms_share_one_stream(modules,tmp_path,monkeypatch):
    run,_=fixture_run(modules,tmp_path,monkeypatch);common=modules['common'];raw=run/'raw';raw.mkdir()
    cell=json.loads(common.INPUTS.read_text())['cells'][0];f=cell['fixture'];arms=[];checks=[]
    # Empty synthetic records exercise export accounting; no actual pool/point/
    # native geometry/rank oracle is evaluated. Check_arm is isolated separately
    # from these injected administrative summaries.
    monkeypatch.setattr(modules['analyze'],'check_arm_metadata',lambda *args:dict(accepted_witnesses=0,norm_completed_witnesses=0,
        distinct_equations=0,new_rank=0,combined_rank=13,rank_gain=0,base_nullity_after=2,nonzero_old_kernel_syndromes=0))
    for name in common.ARMS:
        arms.append(dict(arm=name,preprocessing_quality=dict(rank=13)))
        checks.append(dict(arm=name,rank_gain=0,combined_rank=13,base_rank=13,norm_completed_witnesses=0))
    value=dict(schema='prym-norm-completion/v1',curve_uid=f['uid'],source_order=cell['source_order'],complete=True,
        attempts=common.expected_attempts(cell),inputs_sha256=common.digest(common.INPUTS),rows=[],arms=arms,projection={'software_control':True},operation_vector={'software_counter':7})
    with gzip.open(raw/(cell['id']+'.json.gz'),'wt') as stream:json.dump(value,stream)
    (raw/(cell['id']+'.verification.json')).write_text(json.dumps(dict(checked=True,complete_branch_replay=True,attempts_replayed=value['attempts'],rows_verified=0,arms=checks)))
    modules['analyze'].main();analysis=json.loads((run/'analysis.json').read_text());export=json.loads((run/'export.json').read_text())
    assert analysis['unknown_cells']==2 and analysis['physical_collection_attempts_observed']==2293760
    assert analysis['physical_replay_attempts_observed']==2293760 and len(export['runs'])==4
    assert export['backend_record']['physical_executions']==1
    assert all(r['measurements']['counters']=={} for r in export['runs'] if r['arm']=='norm_completed')


def test_same_column_rank_and_old_kernel_metadata_rechecked(modules):
    base=dict(source_scalar=2,coefficients=[1]);row=dict(source_scalar=2,coefficients=[1],norm_completed=False)
    definition=dict(preprocessing_rows=[base]);projection=dict(U=1,native_to_projected=[['unknown',0,1]])
    arm=dict(arm='norm_completed',row_indices=[0],complete=True,preprocessing_quality=dict(rows=1,columns=1,rank=1,nullity=0),
        new_quality=dict(rows=1,columns=1,rank=1,nullity=0,unique_affine_equations=1),combined_quality=dict(rows=2,columns=1,rank=1,nullity=0),
        rank_gain=0,old_kernel=[],kernel=[],old_kernel_syndromes=[[]],nonzero_old_kernel_syndromes=0,norm_completed_witnesses=0)
    assert modules['analyze'].check_arm_metadata(arm,[row],definition,projection,5)['rank_gain']==0
    arm['old_kernel_syndromes']=[[1]]
    with pytest.raises(ValueError,match='old-kernel row products'):modules['analyze'].check_arm_metadata(arm,[row],definition,projection,5)
    arm['old_kernel_syndromes']=[[]];arm['combined_quality']['columns']=2
    with pytest.raises(ValueError,match='same-column rank'):modules['analyze'].check_arm_metadata(arm,[row],definition,projection,5)
