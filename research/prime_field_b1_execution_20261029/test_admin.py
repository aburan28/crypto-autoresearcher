"""Administrative software fixtures; never run a B1/P256 descriptor or native CLI."""
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
    protocol['protocol_id'] = 'B1-administrative-software-control'
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
    assert all(c['rank'] is None and c['witnesses'] is None and c['verification_attempts'] is None for c in analysis['cells'])
    assert export['flow']['completed'] == 0 and export['flow']['not_completed'] == 4
    assert export['backend_record']['physical_executions'] == 1
    assert all(r['measurements']['wall_seconds'] is None for r in export['runs'])
    assert export['backend_record']['shared_diagnostic_resources']['diagnostic_wall_seconds'] == 3


def test_small_synthetic_gzip_records_separate_collection_and_replay(modules,tmp_path,monkeypatch):
    run,execution = fixture_run(modules,tmp_path,monkeypatch)
    common=modules['common'];raw=run/'raw';raw.mkdir()
    # Synthetic records exercise administrative plumbing only. No mathematical
    # collector/checker is imported; this is not native B1 evidence.
    for f in json.loads(common.INPUTS.read_text())['fixtures']:
        for arm in common.PARAMETERS['arms']:
            stem=f['uid']+'-'+arm
            quality=dict(rows=0,unique_affine_equations=0,duplicate_equations=0,rank=0,columns=1,nullity=1)
            value=dict(curve_uid=f['uid'],source_order=f['width_binding']['source_order'],
                include_zero=arm=='completed_zero',complete=True,attempts=common.ATTEMPTS_PER_CELL,
                inputs_sha256=common.digest(common.INPUTS),projection=dict(U=1,native_to_projected=[]),
                rows=[],quality=quality,operation_vector={'software_counter':2},branch_sha256='0'*64,
                old_kernel_syndromes=[],kernel=[[1]])
            with gzip.open(raw/(stem+'.json.gz'),'wt') as stream:json.dump(value,stream)
            # First arm has no verification: collection survives without replay.
            if arm=='completed_zero':
                with gzip.open(raw/(stem+'.verification.json.gz'),'wt') as stream:
                    json.dump(dict(checked=True,source_statuses_checked=True,attempts_replayed=common.ATTEMPTS_PER_CELL,**quality),stream)
    execution.update(returncode=0,timeout=False)
    (run/'execution.json').write_text(json.dumps(execution))
    modules['analyze'].main()
    analysis=json.loads((run/'analysis.json').read_text());export=json.loads((run/'export.json').read_text())
    assert not analysis['panel_complete'] and analysis['unknown_cells']==0
    assert analysis['collection_attempts_observed']==9175040
    assert analysis['verification_attempts_observed']==4587520
    assert [c['status'] for c in analysis['cells']]==['collected_unverified','verified']*2
    assert all(c['source_zero_witnesses'] is None for c in analysis['cells'])
    assert export['flow']['completed']==2
    assert any(f['path'].endswith('.verification.json.gz') for f in export['files'])


def test_missing_authorization_refuses_before_source_or_output(modules,tmp_path,monkeypatch):
    module=modules['supervise'];release=tmp_path/'release.json'
    release.write_text(json.dumps(dict(owner='software-control',parameters=modules['common'].PARAMETERS,execution_authorized=False)))
    out=tmp_path/'must-not-exist'
    monkeypatch.setattr(module,'bindings',lambda *a:pytest.fail('source or launch path reached'))
    monkeypatch.setattr(sys,'argv',['supervise.py','--owner','software-control','--release',str(release),'--protocol',str(tmp_path/'absent.json'),'--out',str(out)])
    with pytest.raises(ValueError,match='release is absent'):module.main()
    assert not out.exists()


def test_false_old_kernel_syndrome_is_rejected_without_collection(modules,tmp_path,monkeypatch):
    run,_ = fixture_run(modules,tmp_path,monkeypatch)
    common=modules['common'];raw=run/'raw';raw.mkdir()
    f=json.loads(common.INPUTS.read_text())['fixtures'][0]
    projection=dict(U=1,native_to_projected=[['unknown',0,1]])
    for arm in common.PARAMETERS['arms']:
        new=arm=='completed_zero';rows=[dict(source_scalar=1,coefficients=[1])] if new else []
        value=dict(curve_uid=f['uid'],source_order=f['width_binding']['source_order'],include_zero=new,
            complete=True,attempts=common.ATTEMPTS_PER_CELL,inputs_sha256=common.digest(common.INPUTS),
            projection=projection,rows=rows,kernel=[] if new else [[1]],operation_vector={},branch_sha256='0'*64,
            quality=dict(rows=len(rows),unique_affine_equations=len(rows),duplicate_equations=0,
                         rank=int(new),columns=1,nullity=int(not new)),old_kernel_syndromes=[[0]] if new else [])
        (raw/(f['uid']+'-'+arm+'.json')).write_text(json.dumps(value))
    with pytest.raises(ValueError,match='old-kernel syndromes differ'):
        modules['analyze'].main()
    assert not (run/'export.json').exists()
