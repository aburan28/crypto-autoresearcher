"""Administrative software fixtures; never run a D1/P256 descriptor or native CLI."""
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
    protocol['protocol_id'] = 'D1-administrative-software-control'
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


def test_stopped_panel_preserves_eight_unknown_cells(modules,tmp_path,monkeypatch):
    run,_ = fixture_run(modules,tmp_path,monkeypatch)
    modules['analyze'].main()
    analysis = json.loads((run/'analysis.json').read_text());export = json.loads((run/'export.json').read_text())
    assert analysis['unknown_cases'] == 8 and not analysis['panel_complete']
    assert all(c['base_rank'] is None and c['witnesses'] is None and c['verification_attempts'] is None for c in analysis['cells'])
    assert export['flow']['completed'] == 0 and export['flow']['not_completed'] == 16
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




def test_certificate_weights_check_on_small_linear_software_fixture(modules):
    result=dict(projection=dict(U=1,native_to_projected=[['unknown',0,1]]),
                rows=[dict(source_scalar=0,coefficients=[1],target_coefficient=1)])
    base=[dict(source_scalar=2,coefficients=[1])]
    certificate=dict(identifiable=True,verified=True,value=2,scalar=2,row_weights=[1,4],base_rows=1,base_columns=1,target_rows=1)
    modules['analyze'].check_certificate(certificate,result,base,5)
    certificate['row_weights']=[1,0]
    with pytest.raises(ValueError,match='false target row-combination'):
        modules['analyze'].check_certificate(certificate,result,base,5)


def test_gzip_duplicate_encodings_refused(modules,tmp_path):
    path=tmp_path/'administrative.json'
    with gzip.open(str(path)+'.gz','wt') as stream:json.dump({'software_control':True},stream)
    assert modules['analyze'].load(path)=={'software_control':True}
    path.write_text('{}')
    with pytest.raises(ValueError,match='ambiguous raw encodings'):modules['analyze'].load(path)


def test_recipe_metadata_uses_software_domain_and_full_identity(modules):
    from hashlib import sha256
    # Pure metadata fixture: no native identity, curve arithmetic, root search,
    # subgroup test, target draw or target scalar is evaluated.
    data=dict(target_domain='administrative-software/v1',max_target_counters=10000)
    cell=dict(target_curve_uid='software-full-identity',fixture=dict(p=101,r=97))
    digest=sha256(b'administrative-software/v1|software-full-identity|3|0').hexdigest()
    point=[int(digest,16)%101,0]  # synthetic bytes, not claimed to be on a curve
    recipe=dict(curve_uid=cell['target_curve_uid'],domain=data['target_domain'],index=3,scalar_label_generated=False,
                subgroup_order=97,point=point,selected=dict(counter=0,sha256=digest,x=point[0]),rejected=[])
    value=dict(target_recipe=recipe,target=point)
    assert modules['analyze'].check_recipe_metadata(data,cell,3,value)==recipe
    recipe['curve_uid']='wrong-software-identity'
    with pytest.raises(ValueError,match='wrong frozen full-EC1 target recipe'):
        modules['analyze'].check_recipe_metadata(data,cell,3,value)


def test_synthetic_verified_record_keeps_reference_costs_empty(modules,tmp_path,monkeypatch):
    run,execution=fixture_run(modules,tmp_path,monkeypatch);common=modules['common'];raw=run/'raw';raw.mkdir()
    data=json.loads(common.INPUTS.read_text());cell=data['cells'][0];f=cell['fixture']
    # Administrative synthetic record only; recipe verification is tested above
    # on a software identity. No actual native hash recipe/target is evaluated.
    monkeypatch.setattr(modules['analyze'],'check_recipe_metadata',lambda *args:{'software_control':True})
    diagnostic=dict(identifiable=False,value=None,row_weights=None,base_rank=13,base_columns=15,base_rows=97,
                    target_rows=0,augmented_rank=13,syndrome=[0,0,1])
    value=dict(schema='prym-natural-target-completion/v1',curve_uid=f['uid'],source_order=cell['source_order'],multipliers=data['multipliers'],
        complete=True,attempts=common.expected_attempts(data,cell),stopping_rule='full census regardless of recovery',
        inputs_sha256=common.digest(common.INPUTS),target=[0,0],target_recipe={'software_control':True},
        target_identification=diagnostic,preprocessing=dict(rank=13,columns=15,nullity=2),projection=dict(U=15),rows=[],
        first_single_recovery=None,first_combined_recovery=None,final_target_certificate=None,
        target_is_signed_base_point=False,target_is_public_anchor=False,operation_vector={'software_counter':1},target_validation_group_ops=2)
    stem=f['uid']+'-target-0'
    with gzip.open(raw/(stem+'.json.gz'),'wt') as stream:json.dump(value,stream)
    (raw/(stem+'.verification.json')).write_text(json.dumps(dict(checked=True,complete_branch_replay=True,hash_recipe_checked=True,
        attempts_replayed=value['attempts'],rows_verified=0,base_rank=13,augmented_rank=13,target_identifiable=False)))
    modules['analyze'].main();analysis=json.loads((run/'analysis.json').read_text());export=json.loads((run/'export.json').read_text())
    assert analysis['unknown_cases']==7 and analysis['cells'][0]['status']=='verified'
    assert analysis['cells'][0]['identified_target']==0
    assert len(export['runs'])==16 and export['backend_record']['physical_executions']==1
    assert export['runs'][0]['measurements']['counters']['separate_curve_validation_group_ops']==2
    assert all(r['measurements']['counters']=={} for r in export['runs'] if r['arm']=='finite_replay')
