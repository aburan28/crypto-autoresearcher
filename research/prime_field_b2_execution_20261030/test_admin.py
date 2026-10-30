"""Administrative software fixtures; never run a B2/P256 descriptor or native CLI."""
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
    protocol['protocol_id'] = 'B2-administrative-software-control'
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


def test_stopped_panel_preserves_ten_unknown_cells(modules,tmp_path,monkeypatch):
    run,_ = fixture_run(modules,tmp_path,monkeypatch)
    modules['analyze'].main()
    analysis = json.loads((run/'analysis.json').read_text());export = json.loads((run/'export.json').read_text())
    assert analysis['unknown_cells'] == 10 and not analysis['panel_complete']
    assert all(c['new_rank'] is None and c['witnesses'] is None and c['verification_attempts'] is None for c in analysis['cells'])
    assert export['flow']['completed'] == 0 and export['flow']['not_completed'] == 10
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


def write_synthetic_result(modules,run,wrong=False):
    common=modules['common'];definition=json.loads(common.INPUTS.read_text())['cells'][0];f=definition['fixture']
    raw=run/'raw';raw.mkdir()
    row=dict(source_scalar=1,coefficients=[1],constraints=[[0,1],[1,1],[2,1],[3,1]])
    value=dict(schema='prym-shifted-subset/v1',cell_id=definition['id'],arm='baseline',curve_uid=f['uid'],cover_shift=0,
        active_atoms=definition['active_atoms'],source_order=definition['source_order'],attempts=common.expected_attempts(definition),
        complete=True,inputs_sha256=common.digest(common.INPUTS),projection=dict(U=1,native_to_projected=[['unknown',0,1]]),
        rows=[row],new_quality=dict(rows=1,unique_affine_equations=1,rank=1,columns=1,nullity=0),
        combined_quality=dict(rows=1,rank=1,columns=1,nullity=0),preprocessing_quality=dict(rows=0,rank=0,columns=1,nullity=1),
        old_kernel=[[1]],old_kernel_syndromes=[[0 if wrong else 1]],operation_vector={'software_counter':1},branch_sha256='0'*64)
    path=raw/(definition['id']+'-baseline.json.gz')
    with gzip.open(path,'wt') as stream:json.dump(value,stream)
    return raw,value,definition


def test_gzip_collected_result_is_unverified_and_other_cells_unknown(modules,tmp_path,monkeypatch):
    run,_=fixture_run(modules,tmp_path,monkeypatch);write_synthetic_result(modules,run)
    modules['analyze'].main();analysis=json.loads((run/'analysis.json').read_text());export=json.loads((run/'export.json').read_text())
    assert analysis['unknown_cells']==9 and not analysis['panel_complete']
    cell=analysis['cells'][0]
    assert cell['rank_gain']==1 and cell['nonzero_old_kernel_syndromes']==1
    assert cell['verification_attempts'] is None and cell['source_zero_witnesses'] is None
    assert export['backend_record']['physical_executions']==1 and len(export['runs'])==10


def test_false_old_kernel_syndrome_is_rejected_without_collection(modules,tmp_path,monkeypatch):
    run,_=fixture_run(modules,tmp_path,monkeypatch);write_synthetic_result(modules,run,wrong=True)
    with pytest.raises(ValueError,match='old-kernel syndromes differ'):modules['analyze'].main()
    assert not (run/'export.json').exists()
