"""Administrative software fixtures; never run a retained cover/B1/P256 descriptor or native CLI."""
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
    protocol['protocol_id'] = 'cover-administrative-software-control'
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


def test_stopped_panel_preserves_unknown_cells(modules,tmp_path,monkeypatch):
    run,_ = fixture_run(modules,tmp_path,monkeypatch)
    modules['analyze'].main()
    analysis = json.loads((run/'analysis.json').read_text());export = json.loads((run/'export.json').read_text())
    assert analysis['unknown_cells'] == 2 and not analysis['panel_complete']
    assert all(c['frames'] is None and c['eligible_frames'] is None for c in analysis['cells'])
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


def test_gzip_reading_preserves_unknown_and_refuses_duplicate_encodings(modules,tmp_path):
    analyze=modules['analyze'];path=tmp_path/'software.json'
    assert analyze.load(path) is None
    with gzip.open(str(path)+'.gz','wt') as stream:json.dump({'software_control':True},stream)
    assert analyze.load(path)=={'software_control':True}
    path.write_text('{}')
    with pytest.raises(ValueError,match='ambiguous'):analyze.load(path)


def test_synthetic_complete_export_shares_counts_without_reference_cost(modules,tmp_path,monkeypatch):
    run,execution=fixture_run(modules,tmp_path,monkeypatch);common=modules['common'];raw=run/'raw';raw.mkdir()
    # Administrative synthetic traces only: no native helper, source arithmetic,
    # membership operation or oracle is invoked, and these are not observations.
    cells=[];checks=[]
    for f in json.loads(common.INPUTS.read_text())['fixtures']:
        rows=[dict(h=h,c4=0,c2=0,c0=0,singular=True,eligible=False,base_square_mask='0'*16,
                   base_zero_mask='0'*16,source_square_mask='0'*64,source_zero_mask='0'*64) for h in range(4099)]
        cells.append(dict(fixture_uid=f['uid'],curve_uid=f['ec1']['curve_uid'],
                          **{k:f[k] for k in ('p','a','b','r')},source_order=f['width_binding']['source_order'],
                          rows=rows,eligible_h=[],counters={'software_counter':1}))
        checks.append(dict(fixture_uid=f['uid'],frames_checked=4099,source_points_checked=64,checked=True))
    with gzip.open(raw/'survey.json.gz','wt') as stream:
        json.dump(dict(schema='prime-field-shifted-cover-survey/v1',complete=True,inputs_sha256=common.digest(common.INPUTS),cells=cells),stream)
    (raw/'verification.json').write_text(json.dumps(dict(checked=True,frames_checked=8198,source_points_checked=128,cells=checks)))
    execution.update(returncode=0,timeout=False);(run/'execution.json').write_text(json.dumps(execution))
    modules['analyze'].main();analysis=json.loads((run/'analysis.json').read_text());export=json.loads((run/'export.json').read_text())
    assert analysis['panel_complete'] and [c['frames'] for c in analysis['cells']]==[4099,4099]
    assert len(export['runs'])==4 and export['backend_record']['physical_executions']==1
    assert all(r['measurements']['counters']=={} for r in export['runs'] if r['arm']=='roots_set_oracle')
    assert all(r['measurements']['counted']['eligible_frames']==0 for r in export['runs'])
