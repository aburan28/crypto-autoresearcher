"""Administrative software controls; no fixed scientific case is executed."""
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
    for name in ('common', 'prepare', 'analyze', 'supervise'):
        spec = importlib.util.spec_from_file_location(name, HERE/(name+'.py'))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        monkeypatch.setitem(sys.modules,name,module)
        result[name] = module
    return result


def test_stopped_panel_exports_unknown_instead_of_empty(modules, tmp_path, monkeypatch):
    common, prepare, analyze = (modules[k] for k in ('common','prepare','analyze'))
    protocol = prepare.make_protocol(common.git('rev-parse','HEAD'))
    protocol['protocol_id'] = 'C1-administrative-software-control'
    (tmp_path/'analyze.py').write_bytes((HERE/'analyze.py').read_bytes())
    path = tmp_path/'protocol.json'
    path.write_text(json.dumps(protocol))
    prepare.protocol_tools().freeze(path,common.git('rev-parse','HEAD'),True)
    run = tmp_path/'software-stopped'
    run.mkdir()
    execution = dict(returncode=-15,source_unchanged_after=True,timeout=True,
        observed_git_head=common.git('rev-parse','HEAD'),source_commit=common.git('rev-parse','HEAD'),
        diagnostic_wall_seconds=0,cpu_user_seconds=0,cpu_sys_seconds=0,max_rss_bytes=0,
        started_at='2026-10-29T00:00:00Z',finished_at='2026-10-29T00:00:00Z',owner='software-control')
    host = dict(cpu_model='software fixture',logical_cpus=1,memory_bytes=1,kernel='software fixture',
                hypervisor=None,isolation_tier_max=None,executable_sha256=common.digest(Path(sys.executable).resolve()),git_dirty=True)
    (run/'execution.json').write_text(json.dumps(execution))
    (run/'host.json').write_text(json.dumps(host))
    monkeypatch.setattr(sys,'argv',['analyze.py','--run',str(run),'--protocol',str(path)])
    analyze.main()
    analysis = json.loads((run/'analysis.json').read_text())
    exported = json.loads((run/'export.json').read_text())
    assert analysis['metrics']['unknown_cases'] == 7
    assert not analysis['panel_complete']
    assert all(row['symmetric_states'] is None for row in analysis['cases'])
    assert exported['flow']['completed'] == 0 and exported['flow']['not_completed'] == 2
    assert exported['backend_record']['physical_executions'] == 1
    reference = exported['runs'][1]['measurements']
    assert reference['wall_seconds'] is None and reference['counters'] == {}


def test_missing_authorization_refuses_before_source_or_output(modules, tmp_path, monkeypatch):
    module = modules['supervise']
    release = tmp_path/'release.json'
    release.write_text(json.dumps(dict(owner='software-control',parameters=modules['common'].PARAMETERS,
                                      execution_authorized=False)))
    out = tmp_path/'must-not-exist'
    monkeypatch.setattr(module,'bindings',lambda *a: pytest.fail('source or launch path was reached'))
    monkeypatch.setattr(sys,'argv',['supervise.py','--owner','software-control','--release',str(release),
                                  '--protocol',str(tmp_path/'absent.json'),'--out',str(out)])
    with pytest.raises(ValueError,match='release is absent'):
        module.main()
    assert not out.exists()
