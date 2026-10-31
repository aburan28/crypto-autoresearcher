"""Administrative software fixtures; never run a A3/P256 descriptor or native CLI."""
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
    protocol['protocol_id'] = 'A3-administrative-software-control'
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






def test_phase_counter_conservation_and_overlap_refusal(modules):
    phase=lambda name,c:dict(phase=name,status='complete',wall_valid=False,cpu_seconds=0,wall_seconds=0,counters=c)
    value=dict(collection_phases=[phase('setup',{'Fp.add':2})],collection_counters={'Fp.add':2},
        analysis=dict(analysis_phases=[phase('elimination',{'Fr.mul':1})],total_counters={'Fp.add':2,'Fr.mul':1}))
    assert modules['analyze'].check_phase_accounting(value)[1]=={'Fp.add':2,'Fr.mul':1}
    value['analysis']['analysis_phases'][0]['phase']='setup'
    with pytest.raises(ValueError,match='overlapping inner phase'):modules['analyze'].check_phase_accounting(value)
    value['analysis']['analysis_phases'][0]['phase']='elimination';value['analysis']['total_counters']['Fr.mul']=2
    with pytest.raises(ValueError,match='total counter conservation'):modules['analyze'].check_phase_accounting(value)


def software_direct(scalar=1,triple=None):
    triple=[0,1,2] if triple is None else triple;signs=[1,-1,1];coefficients=[0]*16
    for j,sign in zip(triple,signs):coefficients[j]=sign%97
    return dict(schema='direct-three-sum-row/v1',curve_uid='software',source_scalar=scalar,triple=triple,signs=signs,coefficients=coefficients)


def test_distinct_signed_descriptor_coefficients(modules):
    cell=dict(fixture=dict(uid='software',r=97),source_order=[1]);row=software_direct()
    modules['analyze'].check_row_metadata(dict(rows=[row]),cell)
    row['coefficients'][0]=0
    with pytest.raises(ValueError,match='coefficient identity'):modules['analyze'].check_row_metadata(dict(rows=[row]),cell)


def test_archived_norm_is_subset_not_equal_direct_set(modules):
    direct=software_direct();extra=software_direct(triple=[0,1,3])
    archived=dict(source_scalar=1,base_labels=[[0,1,0],[1,-1,1],[2,1,0]],coefficients=direct['coefficients'],norm_completed=True,residual_E_images=[[4,3],[4,98]])
    cell=dict(fixture=dict(p=101),archived_norm_rows=[archived,archived])
    result=modules['analyze'].archived_subset(cell,[direct,extra])
    assert result==dict(witnesses=2,distinct_direct_descriptors=1,direct_row_indices=[0,0])
    archived['norm_completed']=False
    with pytest.raises(ValueError,match='archived norm-only'):modules['analyze'].archived_subset(cell,[direct,extra])


def test_gzip_ambiguity_and_unanalyzed_snapshot_accounting(modules,tmp_path,monkeypatch):
    run,_=fixture_run(modules,tmp_path,monkeypatch);common=modules['common'];raw=run/'raw';raw.mkdir()
    cell=json.loads(common.INPUTS.read_text())['cells'][0];arms=[]
    # Pure administrative synthetic records, no native E operations/table/source
    # construction. Placeholder pair payload is never certified as a real table.
    monkeypatch.setattr(modules['analyze'],'archived_subset',lambda *args:{'software_control':True})
    for name in common.ARMS:
        count=common.expected_attempts(cell,name);counters={'software_'+name:count}
        arms.append(dict(schema='direct-three-sum/v1',curve_uid=cell['fixture']['uid'],arm=name,source_order=cell['source_order'],complete=True,
            attempts=count,rows=[],pair_entries=[dict(indices=[],signs=[],point=None) for _ in range(common.expected_pairs(cell))] if name=='pair_table' else [],projection=dict(U=15),
            collection_phases=[dict(phase='software',status='complete',wall_valid=False,wall_seconds=0,cpu_seconds=0,counters=counters)],collection_counters=counters,analysis=None))
    events=[]
    for value in arms:
        blocks=[]
        for i,scalar in enumerate(cell['source_order']):
            block=dict(scalar=scalar,attempts=(i+1)*(4480 if value['arm']=='enumeration' else 32),branch_sha256='0'*64)
            block['statuses' if value['arm']=='enumeration' else 'queries']='.'*4480 if value['arm']=='enumeration' else [{'software_control':True}]*32
            blocks.append(block);events.append(dict(kind='source_complete',arm=value['arm'],**block))
        value['status_blocks']=blocks
        events.extend(dict(kind='pair_entry',arm=value['arm'],index=i,**pair) for i,pair in enumerate(value['pair_entries']))
    (raw/(cell['id']+'.events.jsonl')).write_text(''.join(json.dumps(e)+'\n' for e in events))
    aggregate=dict(schema='direct-three-sum-cell/v1',cell_id=cell['id'],curve_uid=cell['fixture']['uid'],complete=True,inputs_sha256=common.digest(common.INPUTS),arms=arms)
    path=raw/(cell['id']+'.collection.json')
    with gzip.open(str(path)+'.gz','wt') as stream:json.dump(aggregate,stream)
    modules['analyze'].main();a=json.loads((run/'analysis.json').read_text());e=json.loads((run/'export.json').read_text())
    assert a['unknown_cells']==2 and [r['attempts'] for r in a['cells'][:2]]==[286720,2048]
    assert all(r['rank_gain'] is None for r in a['cells']) and e['backend_record']['physical_executions']==1
    (raw/(cell['id']+'.events.jsonl')).unlink()
    with pytest.raises(ValueError,match='complete source journal differs'):modules['analyze'].main()
    path.write_text('{}')
    with pytest.raises(ValueError,match='ambiguous retained encodings'):modules['analyze'].load(path)


def test_old_kernel_and_same_columns_rechecked(modules):
    width=15;unit=lambda i:[int(j==i) for j in range(width)];row=dict(source_scalar=3,coefficients=unit(0))
    projection=dict(U=width,native_to_projected=[['unknown',j,1] for j in range(width)])
    a=dict(rows=1,distinct_equations=1,normalized_equations=[unit(0)+[3]],preprocessing=dict(rank=0,columns=width,nullity=width),
        new=dict(rank=1,columns=width,nullity=width-1),combined=dict(rank=1,columns=width,nullity=width-1),rank_gain=1,
        old_kernel=[unit(j) for j in range(width)],kernel=[unit(j) for j in range(1,width)],old_kernel_syndromes=[unit(0)],nonzero_old_kernel_syndromes=1)
    value=dict(analysis=a,projection=projection,rows=[row]);cell=dict(fixture=dict(r=97),preprocessing_rows=[])
    assert modules['analyze'].check_analysis(value,cell)['rank_gain']==1
    a['old_kernel_syndromes']=[[0]*width]
    with pytest.raises(ValueError,match='old kernel row products'):modules['analyze'].check_analysis(value,cell)
