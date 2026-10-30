#!/usr/bin/env python3
"""Verify only after authenticated transport termination; retain partial exports."""
from pathlib import Path
import argparse
import importlib.util
import json
import sys
import os
import math
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import controller as c
import driver
analysis=c.module(Path(__file__).with_name('analysis.py'),'_controlled_analysis')


def authenticate_inputs(out, repo, record, worker_plan, fixture_law=None):
    """Authenticate invocation independently of the worker's matching assertions.

    The explicit fixture seam has no source/VM qualification and is unavailable
    to the ordinary production entry point.
    """
    config=c.read(out/'config.json')
    if fixture_law=='disclosed-F11-F23-paired-v2':
        c.need(config.get('fixture_only') is True and config.get('fixture_id')==fixture_law,'explicit authenticated tiny law')
        expected,invocation,static,_=c.fixture_plan(repo,config)
        c.need(record['plan']==expected,'independent tiny source/input plan differs')
        for role,binding in config['inputs'].items():c.need(c.sha_file(out/(role+'.json'))==binding['sha256'],'fixture copied binding: '+role)
        pins={'protocol_sha256':config['inputs']['protocol']['sha256'],'source_fingerprint':expected['source_fingerprint']}
        inputs={'workload_law':fixture_law,'max_jsonl_line_bytes':record['plan']['limits']['max_jsonl_line_bytes']}
    elif fixture_law is not None:
        raise ValueError('unsupported fixture capability')
    else:
        expected, invocation, static, _=c.make_plan(repo,config)
        c.need(expected==record['plan'], 'controller plan differs from independent invocation')
        c.need(worker_plan.get('provenance',{}).get('protocol_sha256')==invocation['inputs']['protocol']['sha256'] and worker_plan.get('provenance',{}).get('source_fingerprint')==expected['source_fingerprint'], 'worker provenance differs from independent invocation')
        for role,binding in invocation['inputs'].items():
            copied=out/(role+'.json')
            c.need(c.sha_file(copied)==binding['sha256'], 'copied input hash mismatch: '+role)
            c.need(c.read(copied)==static[role], 'copied input semantics differ: '+role)
        wm,_=c.source_payload(repo,out/'worker_manifest.json','worker')
        hm,hosts=c.source_payload(repo,out/'host_manifest.json','host')
        fingerprint=c.sha_bytes(c.canonical({'worker':wm,'host':hm}))
        c.need(fingerprint==expected['source_fingerprint'], 'copied source fingerprint mismatch')
        # Every module already executing on the host must be in the exact map.
        executing=[Path(__file__),Path(c.__file__),Path(driver.__file__),Path(analysis.__file__),
                   c.safe(repo,c.PREFIX+'/host/verify.py'),c.safe(repo,c.PREFIX+'/host/reference.py'),
                   Path(__file__).with_name('analysis.py')]
        for path in executing:
            relative=path.resolve().relative_to(Path(repo).resolve()).as_posix()
            c.need(relative in hosts and c.sha_file(path)==hm['files'][relative], 'executing host source not bound: '+relative)
        pins={'protocol_sha256':invocation['inputs']['protocol']['sha256'],'source_fingerprint':fingerprint}
        inputs={'workload_law':'production/v1','prior_exclusions':static['prior_exclusions'],
                'max_jsonl_line_bytes':expected['limits']['max_jsonl_line_bytes']}
    for key,value in pins.items():
        c.need(worker_plan.get('provenance',{}).get(key)==value, 'worker provenance differs from invocation: '+key)
    return inputs


def run(out,destination,repo,verifier=None,interface=None,inner_transport=False,fixture_law=None):
    supervisor=Path(out)
    out=supervisor/'modal' if (supervisor/'modal').is_dir() else supervisor
    destination=Path(destination)
    destination.mkdir(parents=True,exist_ok=False)
    receipt=out/'controller-receipt.json'
    record={'status':'failed','files':[],'engine_execs':0,'plan':{'limits':{'max_jsonl_line_bytes':64<<20}},'controller_record_missing':True}
    export={'schema':c.SCHEMA+'postrun-result/v1','status':'incomplete','observed_only':True,
            'scientific_validity':'not_assessed','wall_valid':False,'counter_replay_qualified':False,
            'automatic_retry':False,'artifacts':[],'errors':[]}
    try:
        driver.check(supervisor,allow_inner=inner_transport)
        record=c.read(receipt)
        c.need(record['status']=='complete','operational failure; no host oracle work allowed')
        evidence=c.custody_for(out/'collected',record)
        plan=c.read(out/'collected/host-plan.json')
        c.need(fixture_law is None or fixture_law=='disclosed-F11-F23-paired-v2','explicit fixed capability only')
        authenticated=authenticate_inputs(out,repo,record,plan,fixture_law)
        public_path=out/'collected/public-cohort.json'
        entry=next((e for e in record['files'] if e['path']=='public-cohort.json'),None)
        c.need(entry is not None and c.sha_file(public_path)==entry['sha256'],'sealed public cohort missing')
        data=public_path.read_bytes()
        c.need(c.sha_bytes(data)==plan['provenance']['cohort_sha256'],'cohort provenance mismatch')
        plan['public_cohort_bytes_hex']=data.hex()
        interface=interface or c.read(out/'engine_interface.json')
        # Host module import is deliberately after custody gate and termination ACK.
        if verifier is None:
            manifest=c.read(out/'host_manifest.json')
            path=c.safe(repo,c.PREFIX+'/host/verify.py')
            c.need(c.sha_file(path)==manifest['files'][c.PREFIX+'/host/verify.py'],'host verifier source mismatch')
            host=c.module(path,'verify')
            verifier=host.verify_bundle
            reference=c.module(c.safe(repo,c.PREFIX+'/host/reference.py'),'reference')

        with (destination/'host-cells.jsonl').open('x') as stream:
            def emit(row):
                stream.write(json.dumps(row,sort_keys=True,allow_nan=False)+'\n'); stream.flush()
            checked=verifier(out/'collected/raw',evidence,plan,interface,emit=emit,authenticated_inputs=authenticated)
        c.write(destination/'verification.json',checked)
        if 'host' in locals():
            if fixture_law=='disclosed-F11-F23-paired-v2':
                run_fixed_references(host,reference,out/'collected/raw',evidence,c.read(public_path),destination)
            else:
                master=os.urandom(32)
                c.write(destination/'host-seed-event.json',{'master_hex':master.hex(),'bytes':32,'phase':'after_authenticated_frozen_workload_verification_collection_seal_quiescence_termination_ack','model':'domain-separated SHA256 null and uniform streams from one fresh host master'})
                run_references(host,reference,out/'collected/raw',evidence,plan,c.read(public_path),master,destination,record['plan']['limits']['max_jsonl_line_bytes'])
        registry={'fixture_only':record.get('fixture_only',False),'physical_sessions':[{'id':record.get('supervisor_identity',{}).get('run_id'),'kind':'pipeline_session','postrun_pid':os.getpid(),'actual_vms':record.get('vm_creates',0)}],'worker_calls':[{'kind':'in_process_mock_worker' if record.get('fixture_only') else 'candidate_VM','calls':record['engine_execs'],'parent':record.get('supervisor_identity',{}).get('run_id')}],'host_reference_kind':'actual paid function calls; not subprocesses or native matched baseline'}
        c.write(destination/'physical-registry.json',registry)
        analytical=[]
        for cell in analysis.rows(out/'collected/raw/decoder-cells.jsonl',record['plan']['limits']['max_jsonl_line_bytes']):
            cid=cell['trace_id'].split('/')[0];order=next(x['model']['r'] for x in c.read(public_path)['curves'] if x['curve_id']==cid)
            analytical.append({'cell_id':cell['cell_id'],'kind':'analytical_conditional_uniform','M':cell['M'],'exact_fraction':[min(cell['M'],order-1),order-1],'physical_invocations':0})
        c.write(destination/'analytical-reference.json',{'rows':analytical,'kind':'analytical_artifact_not_protocol_arm'})
        summary=analysis.summarize(out/'collected/raw',record['plan']['limits']['max_jsonl_line_bytes'])
        c.write(destination/'analysis.json',summary)
        export['status']='complete'
    except Exception as error:
        export['errors'].append({'type':type(error).__name__,'message':str(error)})
        # Available candidate counts retain operational/partial/zero/undefined states.
        raw=out/'collected/raw'
        try:
            summary=analysis.summarize(raw,record['plan']['limits']['max_jsonl_line_bytes'])
            c.write(destination/'partial-analysis.json',summary)
        except Exception as partial:
            export['errors'].append({'partial_analysis':type(partial).__name__,'message':str(partial)})
    for p in sorted(destination.iterdir()):
        if p.is_file(): export['artifacts'].append({'path':p.name,'sha256':c.sha_file(p),'bytes':p.stat().st_size})
    export['raw_transport']={'receipt_sha256':c.sha_file(receipt) if receipt.is_file() else None, 'files':record['files'], 'status':record['status'],
                             'integrity_scope':'inner_transport_only' if inner_transport else 'complete_supervisor_envelope'}
    ep=c.module(Path(repo)/'tools/experiment_protocol.py','_controlled_unified_export')
    try:
        bundle,findings=make_export(ep,out,destination,record,export,supervisor if not inner_transport else None)
        c.write(destination/'export.json',bundle)
        validation={'findings':findings,'schema_compliant':not ep.schema_errors(bundle,'experiment.export/v1'),'protocol_qualified':not findings}
    except (OSError,KeyError,ValueError) as error:
        findings=['unified export unavailable without required protocol/input bytes: '+str(error)]
        validation={'findings':findings,'schema_compliant':False,'protocol_qualified':False}
    c.write(destination/'export.validation.json',validation)
    export['export_findings']=findings
    c.write(destination/'postrun-result.json',export)
    # Rendering belongs to a separate descriptive run-report task, not source checks.

    return export


def run_references(verify,reference,raw,evidence,plan,public,master,destination,max_line):
    """Host-only observed banks; packed masks never expand to 1023*r tables."""
    from collections import Counter,defaultdict
    raw=Path(raw);destination=Path(destination)
    seal=verify.open_sealed(raw,evidence)
    trace_meta={}
    for trace in analysis.rows(raw/'traces.jsonl',max_line):
        trace_meta[trace['trace_id']]={'curve_id':trace['curve_id'],'target':trace['target'],'target_id':trace['target_id']}
        c.need(len(trace_meta)<=36864,'trace metadata resource cap')
    # Bounded byte-offset index; cells remain streamed and retained exactly.
    offsets=defaultdict(list)
    with (raw/'decoder-cells.jsonl').open('rb') as f:
        while True:
            start=f.tell();line=f.readline(max_line+1)
            if not line:break
            c.need(len(line)<=max_line and line.endswith(b'\n'),'cell line resource bound/partial')
            cell=json.loads(line,object_pairs_hook=c.unique,parse_constant=analysis.nonfinite,parse_float=analysis.finite_float)
            curve=trace_meta[cell['trace_id']]['curve_id'];offsets[curve].append((start,len(line)))
            c.need(sum(map(len,offsets.values()))<=73728,'cell offset index resource cap')
    total=sum(curve['model']['r'] for curve in public['curves'])
    c.need(total<=plan.get('max_total_orbit_points',1196032),'total independent orbit resource cap')
    def seed(namespace):return bytes.fromhex(c.sha_bytes(master+namespace.encode()))
    refs=[];calibration=[]
    for curve in public['curves']:
        ident=curve['curve_id'];match=analysis.SLOT.fullmatch(ident)
        stage=match[1] if match else 'disclosed_fixture'
        oracle=verify.Oracle(seal,curve['model'],curve['base'])
        oracle_setup_counts=dict(oracle.group.counts)
        r=curve['model']['r'];bank=[];starts=[];arms=defaultdict(Counter);hist=defaultdict(Counter)
        # All eight retained calibration arms; duplicate draws retained.
        for single in analysis.rows(raw/'single-points.jsonl',max_line):
            if single['curve_id']!=ident:continue
            scalar=oracle.logs[tuple(single['point'])]
            setup_arm=single['arm_id'];a=int(setup_arm.rsplit('.a',1)[1]);s=scalar*pow(a,-1,r)%r
            truth=int(s>r//2);bit=single['answer']['bit'];state='undefined' if bit is None else ('correct' if bit==truth else 'wrong')
            arms[setup_arm][state]+=1;arms[setup_arm]['n']+=1
            arms[setup_arm]['score_sum']+=(0 if bit is None else (1 if bit==truth else -1))
            if setup_arm=='circuit2.a1':bank.append(scalar)
        for trace in analysis.rows(raw/'traces.jsonl',max_line):
            if trace['curve_id']!=ident or trace['incremental'] is not None:continue
            attempt=trace['original'];arm=trace['arm_id']
            if attempt is None:hist[arm]['missing_attempt']+=1;continue
            a=trace['base_multiplier'];errors=erasures=0
            for query in attempt['predicate_trace']:
                scalar=oracle.logs[tuple(query['target'])]*pow(a,-1,r)%r
                bit=query['answer']['bit']
                if bit is None:erasures+=1
                elif bit!=int(scalar>r//2):errors+=1
            hist[arm][str(errors)+','+str(erasures)]+=1
            if arm=='circuit2.a1' and attempt['predicate_trace']:starts.append(oracle.logs[tuple(attempt['predicate_trace'][0]['target'])])
        calibration.append({'curve_id':ident,'stage':stage,'arms':{k:{**dict(v),'correlation':{'numerator':v['score_sum'],'denominator':v['n']}} for k,v in arms.items()},
            'error_erasure_histograms':{k:dict(v) for k,v in hist.items()},
            'score_definition':'+1 defined correct, -1 defined wrong, 0 undefined; unconditioned denominator includes every retained draw',
            'precision_rule':{'m_required':1800,'epsilon':0.1,'K':192,'family_bound':384*math.exp(-1800*0.1**2/2),'assumption':'independent uniform with-replacement draws on fixed curves; not curve-population uncertainty'}})
        target_results=[]
        if stage in ['confirmation-A','confirmation-B'] or stage=='disclosed_fixture':
            bsgs=reference.BSGS(seal,oracle.group,oracle.base)
            for target in curve['targets']:
                target_results.append({'target_id':target['target_id'],'point':target['point'],'bsgs':bsgs.solve(tuple(target['point']))})
        null_path=None
        if stage in ['discovery','validation']:
            mask={point:oracle.evaluate(point,-2,-1,1)['bit'] is not None for point in oracle.points}
            null=reference.mask_reference(seal,oracle,mask,seed('null/'+ident),arm_id='circuit2.a1')
            observed={'score_sum':arms['circuit2.a1']['score_sum'],'q0_successes':hist['circuit2.a1']['0,0']}
            stats=reference.retained_bank_statistics(seal,oracle,null,bank,starts,observed=observed) if null.get('status') in ['complete','degenerate'] else None
            null_path='null-'+ident+'.json'
            c.write(destination/null_path,{'mask_reference':null,'retained_bank_statistics':stats,'bank_n':len(bank),'start_n':len(starts),'descriptive_only':True})
        uniform_path='uniform-'+ident+'.jsonl'
        with (destination/uniform_path).open('x') as target,(raw/'decoder-cells.jsonl').open('rb') as source:
            for offset,length in offsets[ident]:
                source.seek(offset);cell=json.loads(source.read(length),object_pairs_hook=c.unique,parse_constant=analysis.nonfinite,parse_float=analysis.finite_float)
                meta=trace_meta[cell['trace_id']]
                uniform=reference.uniform_list(seal,oracle.group,oracle.base,tuple(meta['target']),cell['M'],seed('uniform/'+cell['cell_id']))
                target.write(json.dumps({'trace_id':cell['trace_id'],'cell_id':cell['cell_id'],'M':cell['M'],'uniform':uniform},sort_keys=True,allow_nan=False)+'\n');target.flush()
        refs.append({'curve_id':ident,'stage':stage,'orbit_points':len(oracle.points),'bsgs_targets':target_results,
            'null_file':null_path,'uniform_file':uniform_path,'independent_oracle_setup_counts':oracle_setup_counts,'independent_host_backend_counts':dict(oracle.group.counts),
            'counter_scope':'host backend separate from worker; no independent worker counter replay; all-r setup and references are host-only paid instrumentation'})
    c.write(destination/'calibration.json',{'curves':calibration,'descriptive_only':True,'null_primary_only':True})
    c.write(destination/'references.json',{'curves':refs,'wall_valid':False,'counter_replay_qualified':False})


def entry(path,base,kind='raw'):
    path=Path(path)
    return {'path':os.path.relpath(path,base),'sha256':c.sha_file(path),'bytes':path.stat().st_size,'kind':kind}


def method_observations(out,max_line):
    """Read only retained paired confirmation work, with bounded strict JSONL.

    The independently authenticated host plan identifies paired traces. Its
    planned cardinality is only a completeness check, never an observed count.
    Calibration traces have no paired ID and cannot enter either method total.
    """
    from collections import Counter
    raw=out/'collected/raw';plan=c.read(out/'collected/host-plan.json')
    expected=plan.get('paired_trace_ids',[])
    c.need(len(expected)==len(set(expected)) and len(expected)<=24576,'paired trace ID resource/uniqueness bound')
    wanted=set(expected);seen=set();issues=[];observations={}
    try:
        for trace in analysis.rows(raw/'traces.jsonl',max_line):
            ident=trace['trace_id']
            c.need(ident not in seen,'duplicate trace ID');seen.add(ident)
            c.need(len(seen)<=36864,'trace metadata resource cap')
            if ident not in wanted:
                c.need(trace.get('incremental') is None,'unplanned paired confirmation trace')
                continue
            for method in ('original','incremental'):
                attempt=trace.get(method)
                if attempt is None or not attempt.get('predicate_trace'):
                    issues.append(ident+': missing/unexecuted '+method);continue
                item=observations.setdefault(method,{'counted':Counter(),'counters':Counter(),'outcomes':Counter(),'targets':set(),'recovered':set(),'trace_ids':[],'complete':True})
                queries=attempt['predicate_trace'];n=len(queries)
                complete=(type(attempt['L']) is int and n==attempt['L'] and attempt['predicate_evaluations']==n
                          and [q['index'] for q in queries]==list(range(n)))
                if not complete:issues.append(ident+': partial '+method)
                item['complete'] &= complete
                item['trace_ids'].append(ident);item['counted']['retained_attempts']+=1
                item['counted']['retained_predicate_queries']+=n
                target=(trace['curve_id'],trace['target_id']);item['targets'].add(target)
                status=attempt['status'];item['outcomes'][status]+=1
                recovered=(status=='RECOVERED' and type(attempt.get('scalar')) is int
                           and attempt.get('scalar_prime') is not None
                           and attempt.get('public_checks')=={'transformed':True,'original':True})
                c.need(status!='RECOVERED' or recovered,'inconsistent strict recovery')
                if recovered:item['counted']['strict_recovered_events']+=1;item['recovered'].add(target)
                for family,vector in attempt['counts'].items():
                    c.need(isinstance(vector,dict),'counter family must be an object')
                    for primitive,value in vector.items():
                        c.need(type(value) is int and value>=0,'nonnegative integer primitive counter required')
                        item['counters'][family+'/'+primitive]+=value
        missing=wanted-seen
        if missing:issues.append('missing paired traces: '+str(len(missing)))
    except (OSError,KeyError,ValueError,TypeError) as error:
        issues.append('paired observation parse failure: '+str(error))
    for method,item in observations.items():
        item['complete'] &= set(item['trace_ids'])==wanted
        item['counted']['strict_recovered_events']+=0
        item['counted']['unique_targets_retained']=len(item.pop('targets'))
        item['counted']['unique_targets_recovered']=len(item.pop('recovered'))
        for field in ('counted','counters','outcomes'):item[field]=dict(item[field])
    return observations,issues


def run_fixed_references(verify,reference,raw,evidence,public,destination):
    """Actual unchanged BSGS function work, separately paid and typed, no bank draw."""
    seal=verify.open_sealed(raw,evidence);rows=[]
    for curve in public['curves']:
        oracle=verify.Oracle(seal,curve['model'],curve['base'])
        bsgs=reference.BSGS(seal,oracle.group,oracle.base)
        for target in curve['targets']:
            answer=bsgs.solve(tuple(target['point']))
            rows.append({'curve_id':curve['curve_id'],'target_id':target['target_id'],'answer':answer,'kind':'actual_host_BSGS_function_call','parent_invocation':'fixture-session','native_matched_backend_qualified':False,'full_cost_qualified':False})
    c.write(destination/'host-references.json',{'fixture_only':True,'rows':rows,'entropy_draws':0,'separately_paid':True,'wall_valid':False})


def make_export(ep,out,destination,record,result,supervisor=None):
    """One prospectively declared physical-session row; panels are linked data.

    Actual original/incremental methods and shared lists stay in analysis/raw;
    conditional-uniform is analytical, never a fictitious executed arm.
    """
    protocol=c.read(out/'protocol.json')
    bundle=ep.export_skeleton(protocol,os.path.relpath(out/'protocol.json',destination),'local' if record.get('fixture_only') else 'modal',protocol['protocol_id']+'.controlled-v2')
    source_commit=record['plan'].get('instrument_execution_commit')
    if not record.get('fixture_only'):source_commit=record.get('launch_context',{}).get('commit')
    bundle['source']={'repo':protocol['repository'],'commit':source_commit,'dirty':None}
    for arm in bundle['arms']:arm['commit']=source_commit
    identity=record.get('supervisor_identity',{})
    c.need(identity.get('run_id') and identity.get('experiment_id')==protocol['protocol_id'],'actual parent identity')
    extension=protocol['extensions']['controlled_followup_v2']
    c.need(extension['export_unit']=='physical_pipeline_session' and extension['analytical_reference_is_arm'] is False,'truthful execution grouping required')
    valid=result['status']=='complete' and record['status']=='complete'
    files=[entry(p,destination,'raw') for p in sorted((out/'collected').rglob('*')) if p.is_file()]
    files.extend(entry(p,destination,'receipt') for p in sorted(out.glob('*.json')))
    outputs=[entry(p,destination,'analysis') for p in sorted(destination.iterdir()) if p.is_file()]
    files.extend(outputs)
    row=ep.run_row(run_id=identity['run_id'],arm=extension['physical_arm'],instance_id=extension['physical_instance'],replicate=0,seed='fixed00_no_entropy' if record.get('fixture_only') else None,status='succeeded' if valid else 'infra_error',measurements={'counted':{'candidate_worker_invocations':record.get('engine_execs',0),'actual_vms':record.get('vm_creates',0)},'counters':{},'wall_valid':False},verification={'status':'no_claim' if valid else 'error','verifier':'host verify_bundle; structural work only'},exclusion={'excluded':False,'rule':None},artifacts=files,worker=None,backend_ref=identity['run_id'])
    bundle['runs']=[row];bundle['flow']=ep.compute_flow(bundle['runs']);bundle['files']=files
    script=Path(__file__).with_name('analysis.py')
    bundle['analysis']={'script':entry(script,destination,'analysis'),'outputs':outputs,'blinded':False,'blinding_key_sha256':None,'unmasked_at':None}
    bundle['host']['path']=os.path.relpath(out/'controller-receipt.json',destination);bundle['host']['sha256']=c.sha_file(out/'controller-receipt.json')
    bundle['notes']=[{'kind':'observation','by':'controlled-followup-v2','text':'One physical pipeline session, with actual worker/VM/functions listed separately in physical-registry.json. Original/incremental methods, six shared cells, per-curve panels and analytical matched-M reference are linked observations, not cloned physical rows. Source context is not execution commit; unpublished outside fixture source has execution commit null. Separately paid host BSGS is not a qualified matched-backend baseline; fullcost/native counters/RSS/clocks remain unqualified.'}]
    bundle['backend_record']={'postrun':result,'source_context_revision':record['plan'].get('source_context_revision'),'instrument_execution_commit':source_commit,'historical_records_unchanged':True}
    findings=ep.schema_errors(bundle,'experiment.export/v1')
    if not findings:findings=ep.lint_export(bundle,protocol,destination,True)
    return bundle,findings

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--destination',type=Path,required=True);p.add_argument('--repo-root',type=Path,required=True)
    a=p.parse_args(); result=run(a.out,a.destination,a.repo_root)
    print(json.dumps({'status':result['status'],'errors':result['errors'],'scientific_validity':'not_assessed'}))
    return 0 if result['status']=='complete' and not result.get('export_findings') else 1


if __name__=='__main__':raise SystemExit(main())
