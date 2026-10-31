#!/usr/bin/env python3
"""Strict JSON local exact-density diagnostic; scientific execution needs admission.

fixtures is restricted to immutable public F23/r17 and abstract Z17/Z29.
census and regression require the real supervisor launch plus approved trial.
All full-orbit/label computations are paid diagnostic preparation, never attacks.
"""
import argparse
import base64
from collections import Counter
from datetime import datetime, timezone
import hashlib
import gzip
import json
import os
from pathlib import Path
import platform
import resource
import signal
import subprocess
import sys
import time

from predicate import Group, Prepared, PRIMARY, CELLS, attempt, literal_decode

HERE=Path(__file__).resolve().parent
RUNTIME_REPO=HERE.parents[1]
RUNTIME_SOURCES=('tools/artifact_store.py',)
BATCH='coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-f7bbdf/'
INVENTORY=BATCH+'git-payload-bindings-bootstrap.json'
PUBLIC='experiments/EXP-ECDLP-080f41/runs/RUN-ECDLP-939237/modal/collected/public-cohort.json'
RAW=str(Path(PUBLIC).parent/'raw')
SOURCES=('driver.py','predicate.py','census.cpp','check.py','test_exact_density.py','interface.json','source-manifest.json')
MEMBERS=('summary.json.gz','states.jsonl.gz','preparations.jsonl.gz','inputs.json','payload-verification.json','provenance.before.json.gz','provenance.after.json.gz','process.json.gz','census.bin','compiler.stdout.log','compiler.stderr.log','census.stdout.log','census.stderr.log','regression.json.gz','controls.json','partial.json')
STATUSES=('RECOVERED','UNDEFINED','EMPTY_INTERVAL','REJECTED_FINAL_VERIFICATION','CAPPED_ERASURES')
FIXTURE=dict(curve_id='public-F23-r17',model=dict(p=23,a=11,b=5,r=17),base=[5,22],targets=[])
FLAGS=['-std=c++17','-O3','-DNDEBUG','-Wall','-Wextra','-Werror']

def now(): return datetime.now(timezone.utc).isoformat()
def canon(v): return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def dump(path,v):
    path=Path(path);data=(canon(v)+'\n').encode()
    with path.open('xb') as f:
        if path.name.endswith('.gz'):
            with gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0) as z:z.write(data)
        else:f.write(data)
def open_binary(path):
    path=Path(path)
    if path.is_file():
        if any(Path(str(path)+suffix).is_file() for suffix in ('.gz','.blob.json','.gz.blob.json')):raise ValueError('ambiguous stored forms: '+str(path))
        return path.open('rb')
    import importlib.util
    spec=importlib.util.spec_from_file_location('exact_density_artifact_store',RUNTIME_REPO/'tools/artifact_store.py')
    module=__import__('sys').modules.get(spec.name)
    if module is None:
        module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    return module.open_artifact(path)
def open_logical(path):
    stream=open_binary(path)
    if not str(path).endswith('.gz'):return stream
    decoded=gzip.GzipFile(fileobj=stream,mode='rb');original_close=decoded.close
    def close():
        try:original_close()
        finally:stream.close()
    decoded.close=close
    return decoded
def digest_size(path):
    h=hashlib.sha256();n=0
    with open_binary(path) as f:
        while chunk:=f.read(1024*1024): h.update(chunk);n+=len(chunk)
    return h.hexdigest(),n
def sha(path): return digest_size(path)[0]
def reject_constant(v): raise ValueError('nonfinite JSON constant: '+v)
def unique(pairs):
    out={}
    for k,v in pairs:
        if k in out: raise ValueError('duplicate JSON key: '+k)
        out[k]=v
    return out
def strict(path):
    with open_logical(path) as f: return json.loads(f.read().decode('utf-8'),object_pairs_hook=unique,parse_constant=reject_constant)
def snapshot(binary=None):
    files={}
    for name in SOURCES:
        p=HERE/name; data=p.read_bytes()
        files[name]=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),base64=base64.b64encode(data).decode())
    for name in RUNTIME_SOURCES:
        data=(RUNTIME_REPO/name).read_bytes()
        files[name]=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),base64=base64.b64encode(data).decode())
    if binary is not None and Path(binary).is_file():
        data=Path(binary).read_bytes(); files['census.bin']=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),base64=base64.b64encode(data).decode())
    return dict(captured_at=now(),files=files)
def same_sources(before,after):
    return {k:v['sha256'] for k,v in before['files'].items()}=={k:v['sha256'] for k,v in after['files'].items()}

def verify_payloads(root,required):
    inventory=strict(root/INVENTORY)
    by={x['path']:x for x in inventory['payload_files']}
    verified=[]
    # Verify committed metadata independently of hydrated full-member bytes.
    for x in inventory['storage_metadata_files']:
        p=root/x['path']
        if p.stat().st_size!=x['bytes'] or sha(p)!=x['sha256']: raise ValueError('storage metadata mismatch: '+x['path'])
        verified.append(dict(path=x['path'],bytes=x['bytes'],sha256=x['sha256'],kind='storage_metadata'))
    for rel in required:
        x=by[rel]; p=root/rel
        if p.stat().st_size!=x['payload_bytes'] or sha(p)!=x['payload_sha256']: raise ValueError('full payload mismatch: '+rel)
        verified.append(dict(path=rel,bytes=x['payload_bytes'],sha256=x['payload_sha256'],kind=x['representation']))
    return dict(inventory=INVENTORY,inventory_sha256=sha(root/INVENTORY),verified=verified)

def admitted(args,out):
    if not args.trial_plan or not args.trial_id: raise ValueError('scientific invocation requires admitted trial plan and trial id')
    root=Path(args.repo).resolve(); plan_path=Path(args.trial_plan).resolve(); plan=strict(plan_path)
    launch=strict(out/'launch.json'); env=strict(out/'environment.json')
    trial=next(t for t in plan['trials'] if t['id']==args.trial_id)
    if args.mode=='fixtures':
        if plan.get('fixture_only') is not True: raise ValueError('format fixture context required')
    elif plan.get('frozen') is not True or not plan.get('approved_by') or plan.get('candidate_only') is True: raise ValueError('unapproved plan')
    if launch['plan_sha256']!=sha(plan_path) or launch['trial_id']!=args.trial_id or launch['run_id']!=trial['run_id']: raise ValueError('launch/plan mismatch')
    actual=sys.orig_argv
    executable=__import__('shutil').which(launch['argv'][0])
    if not executable or not os.path.samefile(executable,sys.executable) or launch['argv'][1:]!=actual[1:]: raise ValueError('actual argv/launch mismatch')
    if launch['authority'].get('commit')!=env.get('commit'): raise ValueError('launch authority mismatch')
    for rel in RUNTIME_SOURCES:
        if plan['source_sha256'].get(rel)!=sha(root/rel): raise ValueError('plan runtime source mismatch: '+rel)
    for name in SOURCES:
        rel='harness/classical_ecdlp_exact_density/'+name
        if plan['source_sha256'].get(rel)!=sha(HERE/name): raise ValueError('plan source mismatch: '+name)
    if args.mode not in trial.get('parameters',{}).get('modes',[args.mode]): raise ValueError('mode mismatch')
    return plan,trial,launch,env

def invoke(argv,stdin,stdout,stderr,processes,binary=None):
    before=snapshot(binary); started=now(); start=time.monotonic()
    event=dict(argv=argv,cwd=str(Path.cwd()),started_at=started,source_before=before,
        stdin_sha256=hashlib.sha256(stdin).hexdigest(),stdin_base64=base64.b64encode(stdin).decode(),
        environment={k:os.environ[k] for k in ('LANG','LC_ALL','PATH') if k in os.environ},
        compiler_flags=FLAGS,wall_valid=False,rss_bytes=None,native_primitive_costs=None)
    compressed=str(stdout).endswith('.gz')
    event['stdout_path']=Path(stdout).name;event['stderr_path']=Path(stderr).name
    event['stdout_stored_start']=Path(stdout).stat().st_size
    stdout_hash=hashlib.sha256();stdout_bytes=stdout_lines=0
    with Path(stdout).open('ab') as so,Path(stderr).open('ab') as se:
        p=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE if compressed else so,stderr=se)
        event['pid']=p.pid
        try:
            if compressed:
                with gzip.GzipFile(filename='',mode='wb',fileobj=so,mtime=0) as target:
                    p.stdin.write(stdin);p.stdin.close()
                    while chunk:=p.stdout.read(65536):
                        target.write(chunk);stdout_hash.update(chunk);stdout_bytes+=len(chunk);stdout_lines+=chunk.count(b'\n')
                    p.stdout.close();p.wait()
            else:p.communicate(stdin)
        finally:
            if p.poll() is None:p.terminate();p.wait()
            event.update(returncode=p.returncode,signal=-p.returncode if p.returncode<0 else None,finished_at=now(),elapsed_seconds=time.monotonic()-start,source_after=snapshot(binary))
            if compressed:event.update(stdout_sha256=stdout_hash.hexdigest(),stdout_bytes=stdout_bytes,stdout_lines=stdout_lines)
            so.flush()
            event['stdout_stored_end']=Path(stdout).stat().st_size
            event['sources_unchanged']=same_sources(before,event['source_after']);processes.append(event)
    if p.returncode or not event['sources_unchanged']: raise ValueError('process failed/source changed: '+str(argv))


def prepare_curve(curve,oracle='predicate',erased=()):
    model=curve['model']; g=Group(model); r=g.r; P=tuple(curve['base'])
    if not g.member(P) or g.mul(r,P) is not None: raise ValueError('invalid public base/order')
    from math import isqrt
    for n in (g.p,r):
        for d in range(2,isqrt(n)+1):
            g.counts['public_primality_trial_divisions']+=1
            if n%d==0: raise ValueError('nonprime public parameter')
    if (4*g.a**3+27*g.b**2)%g.p==0: raise ValueError('singular curve')
    prep=Prepared(model,P,PRIMARY)
    orbit=[None]; seen={None}; current=P; oh=hashlib.sha256(); ah=hashlib.sha256(); labels=[]; reasons=Counter()
    for s in range(r):
        R=None if s==0 else current
        if s:
            if R is None or R in seen or not g.member(R): raise ValueError('orbit identity/order/equation failed')
            seen.add(R); orbit.append(R); current=g.add(current,P)
        oh.update((canon([s,R])+'\n').encode())
        ans=prep.evaluate(R)
        ah.update((canon([s,ans])+'\n').encode()); reasons[str(ans['reason'])]+=1
        labels.append(-1 if ans['status']!='BIT' else ans['bit'])
    if current is not None or len(seen)!=r: raise ValueError('incomplete orbit')
    if oracle!='predicate':
        if oracle not in ('true_half','negated_half','undefined'): raise ValueError('unfrozen fixture oracle')
        labels=[-1 if oracle=='undefined' else 0 if s==0 else int(s>r//2)^(oracle=='negated_half') for s in range(r)]
    # Position erasures belong to each trace and cannot be a global scalar label;
    # those fixture controls are checked by literal_decode, not this native table.
    if erased: raise ValueError('position erasures require literal fixture control')
    record=dict(curve_id=curve['curve_id'],model=model,base=curve['base'],arm=PRIMARY,oracle=oracle,
        setup_reason=prep.reason,setup_fields={k:getattr(prep,k) for k in ('inverse_r','z_base','c','anchor','inverse_anchor','root_factor')},
        orbit_sha256=oh.hexdigest(),predicate_answers_sha256=ah.hexdigest(),predicate_reason_histogram=dict(reasons),
        labels=''.join('u' if b<0 else str(b) for b in labels),orbit_points=r,identity_count=1,
        work=dict(orbit_group=dict(g.counts),predicate_group=dict(prep.g.counts),stored_points_peak=r,stored_labels=r),
        public_check_certificate='Certified canonical distinct [s]P orbit of order r; a=b=1, G=P,Q=R=[s]P. Each legal k evaluates transformed (orbit[k]==orbit[s]) AND original (orbit[k]==orbit[s]) separately. Zero/failure counts retained. Diagnostic only; no attack or old primitive counters.')
    return labels,record


def summary_rows(curves,states):
    summaries=[]
    for curve,records in zip(curves,states):
        r=curve['model']['r']; den=r-1
        for j,(t,ec) in enumerate(CELLS):
            totals=Counter(); hist={k:Counter() for k in ('status','erasures','M','zero','hamming','capped','word_count')}
            for row in records:
                s,V,mask,e,hd,cells=row; c=cells[j]
                for name,n in zip(('words','legal','empty','zero_checks','sumM','successes','transformed_true','transformed_false','original_true','original_false','weight0','weight1','weight2'),c[1:]): totals[name]+=n
                for name,val in (('status',STATUSES[c[0]]),('erasures',e),('M',c[5]),('zero',c[4]),('hamming',hd),('capped',e>ec),('word_count',c[1])): hist[name][str(val)]+=1
            summaries.append(dict(curve_id=curve['curve_id'],arm_id=PRIMARY['id'],radius=t,erasure_cap=ec,states=den,q=[totals['successes'],den],uniform_reference=[totals['sumM'],den*den],totals=dict(totals),histograms={k:dict(v) for k,v in hist.items()}))
    return summaries


def fixed_controls():
    counts=Counter(); examples=[]
    for r in (17,29):
        L=r.bit_length()+1
        for s in range(1,r):
            true=[int((s*(1<<i)%r)>r//2) for i in range(L)]
            for neg in (False,True):
                for erase in ((),(0,),(0,1),(0,1,2)):
                    bits=[None if i in erase else b^neg for i,b in enumerate(true)]
                    for t,ec in CELLS:
                        strict_status='UNDEFINED' if erase else 'RECOVERED' if not neg else 'EMPTY_INTERVAL' if not __import__('predicate').interval(r,L,sum(b<<(L-1-i) for i,b in enumerate(bits)))[1] else 'REJECTED_FINAL_VERIFICATION'
                        d=literal_decode(bits,r,t,ec,checks=lambda k,x:(k==s,x==s),strict_status=strict_status)
                        cap=len(erase)>ec
                        assert d['capped']==cap and (not cap or d['M']==d['word_count']==0)
                        if not neg and not cap: assert s in d['recovered_scalars']
                        if neg: assert not d['recovered_scalars']
                        assert 0 not in d['distinct_nonzero_candidates']
                        assert d['zero_candidate_checks']==sum(w['legal'] and w['candidate_scalar']==0 for w in d['words'])
                        counts['cells']+=1; counts['words']+=d['word_count']; counts['zero_checks']+=d['zero_candidate_checks']
                        if len(examples)<4: examples.append(dict(r=r,s=s,negated=neg,erased=list(erase),cell=[t,ec],M=d['M']))
            bits=[None]*L
            for t,ec in CELLS:
                d=literal_decode(bits,r,t,ec,strict_status='UNDEFINED')
                assert d['word_count']==d['M']==0
                counts['undefined_cells']+=1
    g=Group(FIXTURE['model']); P=tuple(FIXTURE['base']); assert g.member(P) and g.mul(17,P) is None
    assert len({g.mul(s,P) for s in range(17)})==17
    return dict(status='complete',scope='fixed public F23/r17 and abstract Z17/Z29 only',counts=dict(counts),examples=examples)


def regression(root):
    """Deferred full retained replay, fresh public equations; never imports old code.

    Streaming old rows and seeking trace offsets keeps only one trace/cell list.
    Every original/incremental noncounter field and every retained word is checked.
    """
    counts=Counter(); setups={}; intent_offsets={}; trace_offsets={}
    def rows(name):
        with (root/RAW/name).open() as f:
            for line in f: yield json.loads(line,object_pairs_hook=unique,parse_constant=reject_constant)
    def clean(v):
        if isinstance(v,dict): return {k:clean(x) for k,x in v.items() if k not in ('counts','counters')}
        if isinstance(v,list): return [clean(x) for x in v]
        return v
    for q in rows('setups.jsonl'):
        key=(q['curve_id'],q['arm_id'])
        if key in setups: raise ValueError('duplicate setup')
        p=Prepared(q['model'],q['prepared_base'],q['arm']); base=tuple(q['base'])
        if p.g.mul(q['arm']['base_multiplier'],base)!=p.base or p.reason!=q['setup_reason']: raise ValueError('setup mismatch: '+str(key))
        setups[key]=(p,base); counts['setups']+=1
    for q in rows('single-points.jsonl'):
        p,_=setups[q['curve_id'],q['arm_id']]
        if p.evaluate(q['point'])!=q['answer']: raise ValueError('single mismatch: '+q['single_id'])
        counts['singles']+=1
    with (root/RAW/'attempt-intents.jsonl').open('rb') as f:
        while True:
            offset=f.tell(); line=f.readline()
            if not line: break
            q=json.loads(line); key=q['trace_id']
            if key in intent_offsets: raise ValueError('duplicate intent')
            intent_offsets[key]=offset; counts['intents']+=1
    with (root/RAW/'attempt-intents.jsonl').open('rb') as intents, (root/RAW/'traces.jsonl').open('rb') as f:
        while True:
            offset=f.tell(); line=f.readline()
            if not line: break
            q=json.loads(line); key=q['trace_id']
            if key in trace_offsets: raise ValueError('duplicate trace')
            trace_offsets[key]=offset; intents.seek(intent_offsets[key]); intent=json.loads(intents.readline())
            p,base=setups[q['curve_id'],q['arm_id']]
            a=q['base_multiplier']; b=q['target_multiplier']
            target=tuple(intent['target']); got=attempt(p,base,target,a,b)
            if got!=clean(q['original']): raise ValueError('trace mismatch: '+key)
            if q['incremental'] is not None:
                if got!=clean(q['incremental']) or q['equal'] is not True: raise ValueError('incremental mismatch: '+key)
                # Check recurrence independently at each retained adjacent query.
                trace=got['predicate_trace']
                if not p.reason and p.arm['kind']!='wrong_root':
                    for left,right in zip(trace,trace[1:]):
                        U=None if left['target'] is None else tuple(left['target']); V,m=p.g.addline(U,U)
                        if V!=(None if right['target'] is None else tuple(right['target'])): raise ValueError('doubling index')
                        if right['answer']['z']!=(2*left['answer']['z']+m)%p.g.p: raise ValueError('incremental z')
                counts['incremental_traces']+=1
            counts['physical_traces']+=1
    with (root/RAW/'traces.jsonl').open('rb') as traces,(root/RAW/'attempt-intents.jsonl').open('rb') as intents:
        for q in rows('decoder-cells.jsonl'):
            key=q['trace_id']; traces.seek(trace_offsets[key]); tr=json.loads(traces.readline()); intents.seek(intent_offsets[key]); intent=json.loads(intents.readline())
            p,base=setups[tr['curve_id'],tr['arm_id']]; target=tuple(intent['target']); a=tr['base_multiplier']; b=tr['target_multiplier']; R=p.g.mul(b,target)
            bits=[x['answer']['bit'] if x['answer']['status']=='BIT' else None for x in tr['original']['predicate_trace']]
            def checks(k,x):
                tc=p.g.mul(k,p.base)==R; oc=p.g.mul(x,base)==target
                return tc,oc
            got=literal_decode(bits,p.g.r,q['radius'],q['erasure_cap'],a,b,checks,tr['original']['status'])
            for k,v in got.items():
                if v!=q[k]: raise ValueError('cell/word mismatch: '+q['cell_id']+'/'+k)
            counts['cells']+=1; counts['words']+=len(got['words'])
    expected=dict(setups=216,singles=345600,intents=36864,physical_traces=36864,incremental_traces=12288,cells=73728,words=3068802)
    if any(counts[k]!=v for k,v in expected.items()) or len(trace_offsets)!=len(intent_offsets): raise ValueError('retained regression coverage mismatch')
    return dict(status='complete',counts=dict(counts),expected=expected,diagnostic_work='Fresh public affine/Miller/list/conversion/both equations; full cost paid; old counters not replayed',work={f'{c}/{a}':dict(p.g.counts) for (c,a),(p,_) in setups.items()})

def standard_export(out,backend,mode,plan,trial,launch,inputs):
    """Unified export schema; backend_record holds exact density sealing details.

    Fixture protocol bindings describe actual fixed inputs only and explicitly
    confer no frozen scientific-protocol or approval status.
    """
    complete=backend['status']=='complete'
    commit=launch['authority'].get('commit') if launch else None
    if not isinstance(commit,str) or len(commit)!=40:commit=None
    protocol=inputs.get('protocol') if inputs else None
    if not protocol:
        context='inputs.json' if (out/'inputs.json').is_file() else 'provenance.before.json.gz'
        protocol=dict(path=context,sha256=sha(out/context),protocol_id='fixed-public-unit-context' if mode=='fixtures' else 'unavailable-frozen-protocol',version=1)
    arm=trial.get('parameters',{}).get('export_arm',PRIMARY['id']) if trial else PRIMARY['id']
    files=[dict(path=n,sha256=b['sha256'],bytes=b['bytes'],kind='raw') for n,b in sorted(backend['members'].items())]
    process=strict(out/'process.json.gz');started=process['started_at'];finished=process['finished_at']
    counted=dict(completed_curves=inputs.get('expected_curves',0) if complete and inputs else 0)
    if complete and (out/'summary.json.gz').is_file():
        summary=strict(out/'summary.json.gz');counted.update(summary['diagnostic_work']);counted['completed_curves']=len(summary['curves'])
    run_id=trial['run_id'] if trial else 'fixed-public-unit-controls'
    row=dict(run_id=run_id,arm=arm,instance_id=mode,seed=None,replicate=0,warmup=False,status='succeeded' if complete else 'infra_error',outcome_class='completed' if complete else 'not_completed',attempts=1,resumed=0,checkpoint=dict(policy='none',generations_written=0,restored_from_generation=None),measurements=dict(counted=counted,wall_seconds=None,wall_valid=False,cpu_user_seconds=None,cpu_sys_seconds=None,max_rss_bytes=None,counters={}),isolation=dict(tier=None,contended=None,blockers=['No qualified isolated clock or machine-cost claim.']),verification=dict(status='not_run',verifier=None),exclusion=dict(excluded=False,rule=None),artifacts=files,started_at=started,finished_at=finished,worker=None)
    return dict(schema='experiment.export/v1',export_id=run_id+'.export',created=now(),protocol=protocol,producer=dict(runtime=None,model=None,session=None,role='executor'),source=dict(repo=str(RUNTIME_REPO),commit=commit,dirty=None),backend='local',host=dict(path='process.json.gz',sha256=sha(out/'process.json.gz'),class_id=None,summary=dict(cpu_model=None,logical_cpus=os.cpu_count(),memory_bytes=None,kernel=platform.release(),hypervisor=None,isolation_tier_max=None)),arms=[dict(id=arm,role='candidate',binary_sha256=sha(out/'census.bin') if (out/'census.bin').is_file() else None,commit=commit)],runs=[row],flow=dict(planned=1,attempted=1,completed=int(complete),not_completed=int(not complete),interrupted=0,resumed=0,excluded=[]),files=files,analysis=dict(script=None,blinded=False,blinding_key_sha256=None,outputs=[],unmasked_at=None),notes=[dict(kind='observation',text='Producer diagnostic export; scientific validity not assessed. Fixed unit contexts are not scientific protocol approval. Missing coverage never receives q=0; clocks, attack cost and independent validation remain unqualified.',by='executor')],reviews_dir='reviews',backend_record=backend)

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=('fixtures','census','regression','check','export'))
    parser.add_argument('--out',required=True)
    parser.add_argument('--repo',default=str(HERE.parents[1]))
    parser.add_argument('--trial-plan'); parser.add_argument('--trial-id')
    args=parser.parse_args(argv); out=Path(args.out).resolve()
    global RUNTIME_REPO
    RUNTIME_REPO=Path(args.repo).resolve()
    if args.mode in ('check','export'):
        from check import validate
        report=validate(out,Path(args.repo).resolve())
        print(canon(report)); return 0
    out.mkdir(parents=True,exist_ok=True)
    if any((out/name).exists() for name in (*MEMBERS,'raw-result.json','manifest.yaml','export.json')): raise ValueError('write-once output already exists')
    processes=[]; started=now(); before=snapshot(); plan=trial=launch=env=None;inputs={}
    dump(out/'provenance.before.json.gz',before)
    # Logs preserve every original child stdout/stderr; empty success stderr is allowed.
    for name in ('compiler.stdout.log','compiler.stderr.log','census.stdout.log','census.stderr.log','states.jsonl.gz','preparations.jsonl.gz'):
        with (out/name).open('xb') as f:
            if name.endswith('.gz'):
                with gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0):pass
    partial=dict(status='incomplete',mode=args.mode,completed_curves=0,missing_data='No density is assigned to incomplete work.')
    success=False
    try:
        manifest=strict(HERE/'source-manifest.json')
        for name,entry in manifest['sources'].items():
            if sha(HERE/name)!=entry['sha256'] or (HERE/name).stat().st_size!=entry['bytes']: raise ValueError('source manifest mismatch: '+name)
        for rel,entry in manifest['runtime_sources'].items():
            if digest_size(RUNTIME_REPO/rel)!=(entry['sha256'],entry['bytes']): raise ValueError('runtime reader source mismatch: '+rel)
        if args.mode!='fixtures' or args.trial_plan: plan,trial,launch,env=admitted(args,out)
        root=Path(args.repo).resolve()
        if args.mode=='fixtures':
            inputs=dict(mode='fixtures',fixed_public=FIXTURE,abstract_orders=[17,29],oracle_variants=['predicate','true_half','negated_half','undefined'])
            payload=dict(status='not_applicable_fixed_public_fixture',verified=[])
            curves=[FIXTURE|dict(curve_id=FIXTURE['curve_id']+'/'+oracle,oracle=oracle) for oracle in inputs['oracle_variants']]
        else:
            required=[PUBLIC,RAW+'/setups.jsonl']
            if args.mode=='regression': required += [RAW+'/'+n for n in ('single-points.jsonl','traces.jsonl','attempt-intents.jsonl','decoder-cells.jsonl')]
            # Verify all pinned semantic source bytes before any scientific read.
            required += list(manifest['semantic_sources'])
            payload=verify_payloads(root,required)
            public=strict(root/PUBLIC); curves=public['curves']
            if len(curves)!=48 or sum(c['model']['r']-1 for c in curves)!=821638 or max(c['model']['r'] for c in curves)!=61717: raise ValueError('frozen population metadata mismatch')
            setup_map={}
            with (root/RAW/'setups.jsonl').open() as f:
                for line in f:
                    q=json.loads(line)
                    if q['arm_id']==PRIMARY['id']:
                        if q['curve_id'] in setup_map: raise ValueError('duplicate primary setup')
                        setup_map[q['curve_id']]=q
            for c in curves:
                q=setup_map[c['curve_id']]
                if q['model']!=c['model'] or q['base']!=c['base'] or q['prepared_base']!=c['base'] or q['arm']!=PRIMARY: raise ValueError('primary setup/base mismatch')
            if len(setup_map)!=48: raise ValueError('extra/missing primary setup')
            protocol_path=plan['exact_density']['protocol']
            protocol_document=strict(root/protocol_path)
            protocol_digest=hashlib.sha256(json.dumps({k:v for k,v in protocol_document.items() if k!='freeze'},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
            if protocol_document.get('schema')!='experiment.protocol/v1' or protocol_document['freeze']['status']!='frozen' or protocol_document['freeze']['protocol_sha256']!=protocol_digest or protocol_document['freeze']['filed_before_affected_data'] is not True:raise ValueError('frozen protocol binding mismatch')
            protocol_binding=dict(path=protocol_path,sha256=protocol_digest,protocol_id=protocol_document['protocol_id'],version=protocol_document['version'])
            inputs=dict(protocol=protocol_binding,protocol_file_sha256=sha(root/protocol_path),expected_curves=48,mode=args.mode,original_public=PUBLIC,curves=[dict(curve_id=c['curve_id'],model=c['model'],base=c['base']) for c in curves],expected_nonzero_states=821638,primary_arm=PRIMARY,trial_plan=str(Path(args.trial_plan).resolve().relative_to(root)),trial_plan_sha256=sha(Path(args.trial_plan)),trial_id=args.trial_id)
        if launch:
            inputs.update(trial_plan=str(Path(args.trial_plan).resolve().relative_to(root)),trial_plan_sha256=sha(Path(args.trial_plan)),trial_id=args.trial_id)
        dump(out/'inputs.json',inputs); dump(out/'payload-verification.json',payload)
        version=subprocess.run(['g++','--version'],capture_output=True,check=False)
        if version.returncode: raise ValueError('compiler version failed')
        # Actual version stdout/stderr and exact flags recorded with compiler invocation.
        compiler=dict(argv=['g++','--version'],returncode=version.returncode,stdout_base64=base64.b64encode(version.stdout).decode(),stderr_base64=base64.b64encode(version.stderr).decode(),executable=__import__('shutil').which('g++'))
        compiler['executable_sha256']=sha(Path(compiler['executable']))
        compiler['executable_bytes']=Path(compiler['executable']).stat().st_size
        invoke([compiler['executable'],*FLAGS,str(HERE/'census.cpp'),'-o',str(out/'census.bin')],b'',out/'compiler.stdout.log',out/'compiler.stderr.log',processes)
        summaries=[]; curve_hashes=[]
        controls=fixed_controls() if args.mode=='fixtures' else dict(status='not_run',reason='Fixed controls are a separate frozen fixture trial.')
        reg=regression(root) if args.mode=='regression' else dict(status='not_run',reason='Deferred to separately admitted retained-regression trial.')
        if args.mode!='regression':
            for ci,curve in enumerate(curves):
                labels,prep=prepare_curve(curve,curve.get('oracle','predicate'))
                prep['curve_index']=ci
                with (out/'preparations.jsonl.gz').open('ab') as f:
                    with gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0) as z:z.write((canon(prep)+'\n').encode())
                r=curve['model']['r']; L=r.bit_length()+1
                data=(f'{r} {L} {ci}\n'+' '.join(map(str,labels))+'\n').encode()
                offset=(out/'states.jsonl.gz').stat().st_size
                invoke([str(out/'census.bin')],data,out/'states.jsonl.gz',out/'census.stderr.log',processes,out/'census.bin')
                records=[];h=hashlib.sha256()
                with (out/'states.jsonl.gz').open('rb') as stored:
                    stored.seek(offset)
                    with gzip.GzipFile(fileobj=stored,mode='rb') as native:
                        for expected_s,line in enumerate(native,1):
                            row=json.loads(line)
                            if len(row)!=7 or row[:2]!=[ci,expected_s]:raise ValueError('partial/native scalar or curve order')
                            if line!=(canon(row)+'\n').encode() or len(line)>512:raise ValueError('native canonical representation bound')
                            h.update(line);records.append(row[1:])
                event=processes[-1]
                with (out/'census.stdout.log').open('a') as f:f.write(canon(dict(curve_index=ci,curve_id=curve['curve_id'],artifact='states.jsonl.gz',compressed_start=offset,compressed_end=event['stdout_stored_end'],uncompressed_bytes=event['stdout_bytes'],lines=event['stdout_lines'],sha256=event['stdout_sha256']))+'\n')
                if len(records)!=r-1: raise ValueError('partial curve stream')
                summaries.extend(summary_rows([curve],[records]))
                curve_hashes.append(dict(curve_id=curve['curve_id'],curve_index=ci,states=r-1,sha256=h.hexdigest()))
                partial['completed_curves']+=1
        dump(out/'summary.json.gz',dict(status='complete',mode=args.mode,rows=summaries,curves=curve_hashes,wall_valid=False,attack_claimed=False,unknown_costs=['native primitive weights','attack end-to-end cost','isolated qualified clock','per-process peak RSS'],diagnostic_work=dict(word_visits=sum(x['totals'].get('words',0) for x in summaries),public_equation_certifications=sum(x['totals'].get('legal',0)*2 for x in summaries),distinct_nonzero_reference_additions=sum(x['totals'].get('sumM',0) for x in summaries),serialization_states=sum(x['states'] for x in curve_hashes))))
        dump(out/'controls.json',controls); dump(out/'regression.json.gz',reg)
        partial.update(status='complete',missing_data=None)
        success=True
    except BaseException as error:
        partial.update(error_type=type(error).__name__,error=str(error),scientific_validity='not_assessed')
        raise
    finally:
        after=snapshot(out/'census.bin')
        dump(out/'provenance.after.json.gz',after)
        source_unchanged=all(before['files'][n]['sha256']==after['files'][n]['sha256'] for n in (*SOURCES,*RUNTIME_SOURCES))
        if not source_unchanged: partial.update(status='incomplete',error='source changed');success=False
        dump(out/'partial.json',partial)
        dump(out/'process.json.gz',dict(schema='exact-density.process/v1',pid=os.getpid(),argv=sys.orig_argv,started_at=started,finished_at=now(),returncode=None,termination='pending_outer_supervisor_exit',computation_status='complete' if success else 'incomplete',python=sys.version,python_executable=sys.executable,python_executable_sha256=sha(Path(sys.executable)),platform=platform.platform(),compiler=locals().get('compiler'),children=processes,source_unchanged=source_unchanged,resource_observation=dict(driver_ru_maxrss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,children_ru_maxrss=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,units='KiB on Linux; bytes on macOS; process lifetime maximum, not summed RSS',qualified_wall=False),unknown_machine_costs=['old native primitive counters','per-child RSS','clock isolation']))
        if not success:
            present={n:dict(bytes=(out/n).stat().st_size,sha256=sha(out/n)) for n in MEMBERS if (out/n).is_file()}
            dump(out/'export.json',standard_export(out,dict(schema='exact-density.export-seal/v1',status='incomplete',members=present,missing=[n for n in MEMBERS if n not in present],scientific_validity='not_assessed',attack_claimed=False),args.mode,plan,trial,launch,inputs))
            dump(out/'raw-result.json',dict(schema='classical.ecdlp.exact-density.result/v1',status='incomplete',mode=args.mode,attack_claimed=False,export_sha256=sha(out/'export.json'),metrics={'complete':False},missing_data='No q or uniform-reference value assigned to incomplete coverage; see partial.json.',scientific_validity='not_assessed'))
    if not success: return 2
    members={name:dict(bytes=(out/name).stat().st_size,sha256=sha(out/name)) for name in MEMBERS}
    dump(out/'export.json',standard_export(out,dict(schema='exact-density.export-seal/v1',status='complete',kind='exact-density-diagnostic',members=members,source_sha256={**{n:sha(HERE/n) for n in SOURCES},**{n:sha(RUNTIME_REPO/n) for n in RUNTIME_SOURCES}},attack_claimed=False),args.mode,plan,trial,launch,inputs))
    dump(out/'raw-result.json',dict(schema='classical.ecdlp.exact-density.result/v1',status='complete',mode=args.mode,attack_claimed=False,export_sha256=sha(out/'export.json'),summary_sha256=sha(out/'summary.json.gz'),scientific_validity='not_assessed',metrics={'complete':True}))
    if launch:
        body=dict(id=trial['run_id'],experiment_id=plan['experiment_id'],task_id=plan['task_id'],trial_id=trial['id'],approved_by=plan['approved_by'],status='completed',code=dict(commit=launch['authority']['commit'],command=launch['argv'],check_command=launch['check_argv'],command_file='command.txt'),environment={'file':'environment.json',**env},inputs=dict(trial_plan=inputs['trial_plan'],plan_sha256=inputs['trial_plan_sha256'],trial_id=trial['id'],**{k:trial[k] for k in ('parameters','seed','curve_id') if k in trial}),timing=dict(started_at=started,finished_at=now()),result=dict(raw_result='raw-result.json',certificate=dict(kind='none',verified=None)),attack_claimed=False)
    else:
        # A real unit fixture, not an allocated scientific RUN or an approval.
        body=dict(status='completed',fixture_only=True,code=dict(command=sys.orig_argv),environment=dict(python=sys.version),inputs=inputs,timing=dict(started_at=started,finished_at=now()),result=dict(raw_result='raw-result.json',certificate=dict(kind='none',verified=None)),attack_claimed=False)
    body['exact_density']=dict(export_sha256=sha(out/'export.json'),raw_result_sha256=sha(out/'raw-result.json'))
    dump(out/'manifest.yaml',{'run':body})
    from check import validate
    print(canon(validate(out,Path(args.repo).resolve())));return 0

if __name__=='__main__':
    try: sys.exit(main())
    except (ValueError,OSError,KeyError,AssertionError,StopIteration,subprocess.SubprocessError) as e:
        print('exact-density refused: '+str(e),file=sys.stderr);sys.exit(2)
