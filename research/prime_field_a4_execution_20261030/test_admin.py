"""Synthetic administrative controls only; no curve/target generation or point sums."""
import gzip
import importlib.util
import json
from pathlib import Path
import sys
import pytest
HERE=Path(__file__).resolve().parent

@pytest.fixture
def modules(monkeypatch):
    monkeypatch.syspath_prepend(str(HERE));out={}
    for name in ('common','prepare','analyze','supervise'):
        spec=importlib.util.spec_from_file_location(name,HERE/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);monkeypatch.setitem(sys.modules,name,m);out[name]=m
    return out


def setup_run(modules,tmp_path,monkeypatch):
    c,p,a=(modules[n] for n in ('common','prepare','analyze'));head=c.git('rev-parse','HEAD');protocol=p.make_protocol(head);protocol['protocol_id']='A4-administrative-software-control'
    (tmp_path/'analyze.py').write_bytes((HERE/'analyze.py').read_bytes());path=tmp_path/'protocol.json';path.write_text(json.dumps(protocol));p.protocol_tools().freeze(path,head,True)
    run=tmp_path/'software-only';run.mkdir();execution=dict(returncode=-15,source_unchanged_after=True,timeout=True,exception=None,observed_git_head=head,source_commit=head,diagnostic_wall_seconds=3,cpu_user_seconds=1,cpu_sys_seconds=1,max_rss_bytes=1,started_at='2026-10-30T00:00:00Z',finished_at='2026-10-30T00:00:03Z',owner='software-control')
    host=dict(cpu_model='software fixture',logical_cpus=1,memory_bytes=1,kernel='software fixture',hypervisor=None,isolation_tier_max=None,executable_sha256=c.digest(Path(sys.executable).resolve()),git_dirty=True)
    (run/'execution.json').write_text(json.dumps(execution));(run/'host.json').write_text(json.dumps(host));monkeypatch.setattr(sys,'argv',['analyze','--run',str(run),'--protocol',str(path)]);return run


def test_stopped_rules_only_panel_twelve_unknown(modules,tmp_path,monkeypatch):
    run=setup_run(modules,tmp_path,monkeypatch);modules['analyze'].main();a=json.loads((run/'analysis.json').read_text());e=json.loads((run/'export.json').read_text())
    assert a['unknown_cells']==12 and not a['panel_complete'] and all(c['base_rank'] is None for c in a['cells'])
    assert e['flow']['not_completed']==12 and e['backend_record']['physical_executions']==1 and all(not r['measurements']['counters'] for r in e['runs'])


def test_no_authorization_before_bindings_or_generation(modules,tmp_path,monkeypatch):
    m=modules['supervise'];release=tmp_path/'release.json';release.write_text(json.dumps(dict(owner='software',parameters=modules['common'].PARAMETERS,execution_authorized=False)));out=tmp_path/'absent'
    monkeypatch.setattr(m,'bindings',lambda *a:pytest.fail('source/generation path reached'));monkeypatch.setattr(sys,'argv',['supervise','--owner','software','--release',str(release),'--protocol',str(out),'--out',str(out)])
    with pytest.raises(ValueError,match='release is absent'):m.main()
    assert not out.exists()


def test_rules_work_counts_without_generated_fixtures(modules):
    c=modules['common'];rules=json.loads(c.INPUTS.read_text());work=[c.expected_work(s,rules) for s in c.specifications(rules)]
    assert {k:sum(w[k] for w in work) for k in work[0]}==dict(source_queries=12288,target_queries=1536,pair_entries=4928,oracle_signed_triples=88320)
    assert 'cells' not in rules


def test_certificate_kernel_and_weights_corruptions(modules):
    a=modules['analyze'];record=dict(identifiable=True,value=7,row_weights=[1],syndrome=[],scalar=7)
    a.certificate(record,[1],[[1]],[7],[],101);record['row_weights']=[2]
    with pytest.raises(ValueError,match='row-weight'):a.certificate(record,[1],[[1]],[7],[],101)
    record=dict(identifiable=True,value=7,row_weights=[1],syndrome=[0],scalar=7)
    with pytest.raises(ValueError,match='kernel identifiability'):a.certificate(record,[1],[[1]],[7],[[1]],101)


def test_phase_conservation_units_and_duplicate_refusal(modules):
    p=dict(phase='source',status='complete',wall_valid=False,cpu_seconds=0,wall_seconds=0,counters={'Fp.mul':2,'group_add':1});a=modules['analyze']
    assert a.phase_sum([p])=={'Fp.mul':2,'group_add':1}
    with pytest.raises(ValueError,match='duplicate'):a.phase_sum([p,p])


def test_gzip_collection_fallback_and_missing_journal(modules,tmp_path,monkeypatch):
    run=setup_run(modules,tmp_path,monkeypatch);raw=run/'raw';raw.mkdir();c=modules['common'];rules=json.loads(c.INPUTS.read_text());specs=c.specifications(rules)
    cells=[dict(id=s['id'],fixture=dict(uid=s['id'],r=101,p=s['p']),source_order=list(range(1,65))) for s in specs]
    generated=dict(schema='holdout-generated-fixtures/v1',complete=True,inputs_sha256=c.digest(c.INPUTS),cells=cells,search_trace=[],generation_diagnostics=dict(wall_valid=False))
    (raw/'generated.json').write_text(json.dumps(generated));(raw/'generation.events.jsonl').write_text(''.join(json.dumps(dict(kind='curve_selected',cell=x))+'\n' for x in cells))
    work=c.expected_work(specs[0],rules);source=[dict(scalar=s,queries=[],attempts=s*32,branch_sha256='software') for s in range(1,65)];target=[dict(target_index=i,queries=[],attempts=(i+1)*32) for i in range(8)]
    pairs=[dict(indices=[],signs=[],point=None) for _ in range(work['pair_entries'])]
    phase=dict(phase='software',status='complete',wall_valid=False,cpu_seconds=0,wall_seconds=0,counters={'Fp.mul':2})
    value=dict(schema='direct-three-sum/v1',cell_id=specs[0]['id'],curve_uid=specs[0]['id'],arm='pair_table',inputs_sha256=c.digest(c.INPUTS),complete=True,source_order=cells[0]['source_order'],attempts=work['source_queries'],rows=[],status_blocks=source,pair_entries=pairs,target_generation=dict(targets=[],search_trace=[]),target_collection=dict(rows=[],status_blocks=target,attempts=work['target_queries']),prefixes=[],holdout_collection_phases=[phase],holdout_collection_counters={'Fp.mul':2})
    with gzip.open(raw/(specs[0]['id']+'.collection.json.gz'),'wt') as f:json.dump(value,f)
    with pytest.raises(ValueError,match='complete source journal'):modules['analyze'].main()
    events=[dict(kind='source_complete',arm='pair_table',**v) for v in source]+[dict(kind='pair_entry',arm='pair_table',index=i,**v) for i,v in enumerate(pairs)]+[dict(kind='target_complete',**v) for v in target]
    (raw/(specs[0]['id']+'.events.jsonl')).write_text(''.join(json.dumps(e)+'\n' for e in events));modules['analyze'].main();a=json.loads((run/'analysis.json').read_text());e=json.loads((run/'export.json').read_text())
    assert [v['status'] for v in a['cells'][:3]]==['collected_unanalyzed']*3 and all(v['base_rank']is None for v in a['cells'])
    assert [v['measurements']['counters'] for v in e['runs'][:3]]==[{'Fp.mul':2},{},{}]
    assert sum(v['measurements']['counters'].get('Fp.mul',0) for v in e['runs'])==2
    with (raw/(specs[0]['id']+'.collection.json')).open('w') as f:json.dump(value,f)
    with pytest.raises(ValueError,match='ambiguous'):modules['analyze'].load(raw/(specs[0]['id']+'.collection.json'))


def test_prefix_recovery_and_false_syndrome_metadata(modules):
    """One formal unknown/target, no curve arithmetic or generated native fixture."""
    a=modules['analyze'];r=101;cell=dict(fixture=dict(r=r),source_order=[1]);rules=dict(targets=1)
    row=dict(coefficients=[1],source_scalar=1);natural=dict(coefficients=[1],source_scalar=0,target_index=0)
    result=dict(rows=[row],projection=dict(U=1,native_to_projected=[['unknown',0,1]]),target_collection=dict(rows=[natural]),collision_diagnostics=[dict(bounded_multiple_matches=[])])
    record=dict(prefix=16,source_row_indices=[0],base=dict(rows=1,columns=1,rank=1,nullity=0,kernel=[]),distinct_equations=1,singles=[dict(target_row_index=0,target_index=0,offset=0,identifiable=True,value=1,row_weights=[1],syndrome=[],scalar=1)],joint=dict(rows=2,columns=2,rank=2,nullity=0,kernel=[]),joint_recoveries=[dict(target_index=0,identifiable=True,value=1,row_weights=[1,100],syndrome=[],scalar=1)],outside_target_rank=1,base_rank_after_target_cancellation=1,target_base_rank_gain=0,single_identified_targets=[0],joint_identified_targets=[0])
    m=a.prefix_metrics(cell,rules,result,record)
    assert m['joint_targets']==1 and m['joint_base_nullity']==0 and m['early_joint_targets']==0
    record['singles'][0]['row_weights']=[2]
    with pytest.raises(ValueError,match='row-weight'):a.prefix_metrics(cell,rules,result,record)
