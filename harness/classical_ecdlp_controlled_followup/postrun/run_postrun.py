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
    if fixture_law is not None:
        c.need(fixture_law=='fixed-F11-calibration/v1', 'unknown fixed fixture law')
        c.need(config.get('seed_rules')=={'fixture_only':'fixed00_no_entropy'}, 'fixture invocation declaration')
        c.need(c.read(out/'protocol.json')['protocol_id']=='TEST-F11', 'fixture protocol identity')
        pins={'protocol_sha256':'00'*32, 'source_fingerprint':'00'*32}
        c.need(record['plan']['source_fingerprint']==pins['source_fingerprint'], 'independent fixture source pin')
        c.need(config['inputs']['protocol']['sha256']==pins['protocol_sha256'], 'independent fixture protocol pin')
        inputs={'workload_law':fixture_law,'max_jsonl_line_bytes':record['plan']['limits']['max_jsonl_line_bytes']}
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
                   Path(__file__).with_name('render_report.py')]
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
        c.need(fixture_law is None or verifier is not None, 'fixed fixture requires explicit injected verifier')
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
            master=os.urandom(32)
            c.write(destination/'host-seed-event.json',{'master_hex':master.hex(),'bytes':32,'phase':'after_authenticated_frozen_workload_verification_collection_seal_quiescence_termination_ack','model':'domain-separated SHA256 null and uniform streams from one fresh host master'})
            run_references(host,reference,out/'collected/raw',evidence,plan,c.read(public_path),master,destination,record['plan']['limits']['max_jsonl_line_bytes'])
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
    # Export seals raw and analysis only. Reports consume its completed findings;
    # neither report nor export attempts to hash its own bytes.
    renderer=c.module(Path(__file__).with_name('render_report.py'),'_controlled_render')
    renderer.render(destination)
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


def make_export(ep,out,destination,record,result,supervisor=None):
    protocol=c.read(out/'protocol.json')
    bundle=ep.export_skeleton(protocol,os.path.relpath(out/'protocol.json',destination),'modal',protocol['protocol_id']+'.controlled-export')
    bundle['producer']={'runtime':'codex_cli','model':None,'session':None,'role':'executor'}
    bundle['source']={'repo':protocol['repository'],'commit':record['plan'].get('source_revisions',{}).get('host'),'dirty':None}
    receipt=out/'controller-receipt.json' if (out/'controller-receipt.json').is_file() else out/'controller-error.json'
    bundle['host']['path']=os.path.relpath(receipt,destination) if receipt.is_file() else None
    bundle['host']['sha256']=c.sha_file(receipt) if receipt.is_file() else None
    arm=protocol['extensions']['controlled_followup']['export_arm']
    c.need(arm in {a['id'] for a in protocol['arms']},'composite export arm absent from protocol')
    actual=record.get('engine_execs',0)>0
    if actual:
        summary_path=destination/('analysis.json' if (destination/'analysis.json').exists() else 'partial-analysis.json')
        summary=c.read(summary_path) if summary_path.exists() else {}
        rows=summary.get('per_curve_six_cell',[])
        identity=record.get('supervisor_identity',{})
        c.need(identity.get('experiment_id')==protocol['protocol_id'] and str(identity.get('run_id','')).startswith('RUN-'),'allocated supervisor identity required for export')
        bundle['runs']=[ep.run_row(run_id=identity['run_id'],arm=arm,instance_id='candidate-vm',replicate=0,seed=None,
            status='succeeded' if record['status']=='complete' else 'infra_error',attempts=1,resumed=0,
            measurements={'counted':{'retained_decoder_cells':sum(r['attempts'] for r in rows),'retained_success_events':sum(r['successes'] for r in rows)},
                'counters':{'per_curve_six_cell_json':json.dumps(rows,sort_keys=True),'counter_replay_qualified':'false','unmetered':'native RSS,interpreter allocations,I/O,integer internals'},'wall_valid':False},
            verification={'status':'verified' if result['status']=='complete' else 'error','verifier':'source-bound independent host verify_bundle' if result['status']=='complete' else None},
            exclusion={'excluded':result['status']!='complete','rule':'operationally incomplete or independent verification failed' if result['status']!='complete' else None},worker=record.get('sandbox_id'))]
    bundle['flow']=ep.compute_flow(bundle['runs'])
    # The complete heterogeneous schedule remains data, never padded rows.
    files=[entry(p,destination,'raw') for p in sorted((out/'collected').rglob('*')) if p.is_file()] if (out/'collected').exists() else []
    files.extend(entry(p,destination,'receipt') for p in sorted(out.glob('*.json')))
    outputs=[entry(p,destination,'report' if p.suffix in {'.pdf','.svg','.md'} else 'analysis') for p in sorted(destination.iterdir()) if p.is_file()]
    if supervisor is not None:
        files.extend(entry(supervisor/name,destination,'receipt') for name in ['manifest.yaml','raw-result.json','modal-evidence.tar.gz','modal-evidence-manifest.json'])
    files.extend(outputs);bundle['files']=files
    bundle['analysis']={'script':entry(Path(__file__).with_name('analysis.py'),destination,'analysis'),'outputs':outputs,'blinded':False,'blinding_key_sha256':None,'unmasked_at':None}
    bundle['notes']=[{'kind':'observation','by':'controlled postrun','text':'One actual composite supervisor execution row; raw calibration/confirmation schedules and shared six-cell outcomes retained. No padded observations. Wall clocks and counter replay unqualified; no scientific conclusion.'}]
    bundle['backend_record']=result
    findings=ep.schema_errors(bundle,'experiment.export/v1') or ep.lint_export(bundle,protocol,destination,True)
    return bundle,findings


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--destination',type=Path,required=True);p.add_argument('--repo-root',type=Path,required=True)
    a=p.parse_args(); result=run(a.out,a.destination,a.repo_root)
    print(json.dumps({'status':result['status'],'errors':result['errors'],'scientific_validity':'not_assessed'}))
    return 0 if result['status']=='complete' and not result.get('export_findings') else 1


if __name__=='__main__':raise SystemExit(main())
