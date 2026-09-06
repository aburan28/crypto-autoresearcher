"""Four write-once receipt groups, native stop retained; Python standard library only."""
import argparse,datetime,hashlib,json,os,pathlib,platform,resource,signal,subprocess,sys,time
sys.dont_write_bytecode=True
from checker import check
P=pathlib.Path(__file__).resolve().parent
IDS=['RUN-PFDR-20260906-eb1a30','RUN-PFDR-20260906-853e51','RUN-PFDR-20260906-8c21de','RUN-PFDR-20260906-9cd715']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,obj):
    with p.open('x') as f:f.write(json.dumps(obj,indent=2)+'\n' if not isinstance(obj,str) else obj)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--group',type=int,choices=range(1,5),required=True);parser.add_argument('--setup-wall-seconds',type=float,default=0);args=parser.parse_args()
    g=args.group;start=now();t=time.monotonic();cpu=time.process_time();rid=IDS[g-1]
    budget=900-args.setup_wall_seconds
    if budget<=0:raise RuntimeError('setup exhausted group budget')
    signal.alarm(max(1,int(budget)));resource.setrlimit(resource.RLIMIT_CPU,(max(1,int(budget)),max(1,int(budget))))
    resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3))
    d=P/'runs'/rid;d.mkdir(parents=True,exist_ok=False)
    frozen=json.loads((P/'implementation.md').read_text().split('```json\n')[1].split('\n```')[0])
    for name,digest in frozen['sha256'].items():assert sha(P/name)==digest, name
    inputs=json.loads((P/'inputs.json').read_text());fs=[f for f in inputs['fixtures'] if f['group']==g]
    command=' '.join(sys.argv);git=lambda *a:subprocess.check_output(['git',*a],text=True).strip()
    env=dict(python=sys.version,executable=sys.executable,platform=platform.platform(),architecture=platform.machine(),dependencies={'python_standard_library':platform.python_version()},cwd=os.getcwd(),seed=0,threads=1)
    raw=dict(group=g,run_id=rid,fixtures=[],incorrectly_accepted_claims=0,native_measurements=0)
    cert=dict(native_matrices=[],native_certificates=[],missing_native_reason=inputs['native_stop_reason'])
    for f in fs:
        r=dict(id=f['id'],fixture_sha256=f['fixture_sha256'],accepted=False)
        if g==1:r.update(status='unmeasured',reason=inputs['native_stop_reason'],d_ff=None,d_lf=None,sd_bounds=None)
        elif g==2:r.update(status='incompatible',reason='Boolean quotient signature differs from ordinary ring; no interface proof; ordinary certificate reuse rejected.')
        elif g==3:r.update(status='inconclusive',reason='No certified native witness; control predictions cannot be substituted.',certified_witness=None)
        elif f['id']=='uniform-gap':
            r.update(status='rejected_inference',reason='A finite table cannot refute existence of an unspecified uniform constant; no asymptotic conclusion.')
            cert['quantifier']=dict(finite_certificate_implies_no_uniform_constant=False,finite_table_would_only_bound_supplied_constants=True,argument='For any finite set of certified finite gaps, its maximum is a constant bounding that finite set. Disproving a constant valid for all systems requires every candidate constant to have a certified counterexample; the finite set alone cannot supply this.')
        else:
            p=f['field'];x=f['target_x'];a,b=f['curve'];rhs=(x**3+a*x+b)%p
            residues=[[y,y*y%p] for y in range(p)];roots=[y for y,s in residues if s==rhs]
            r.update(status='admissible' if roots else 'inadmissible',admissible=bool(roots),rational_y=roots,reason='Exact enumeration of the declared rational-target fiber.')
            cert['domain']=dict(field=p,x=x,rhs=rhs,y_square_residues=residues,roots=roots)
        raw['fixtures'].append(r)
    raw['checker']=check(inputs,raw,cert)
    ru=resource.getrusage(resource.RUSAGE_SELF); wall=time.monotonic()-t
    manifest={'run':dict(id=rid,experiment_id='EXP-PFDR-845d33',status='completed_valid' if g in [2,4] else 'completed_inconclusive',code=dict(commit=git('rev-parse','HEAD'),dirty=True,dirty_state=git('status','--short'),command=command,sha256=frozen['sha256'],freeze_timestamp=frozen['frozen_at']),inference=dict(requested_policy='executor-implementation',canonical_policy='executor-implementation',backend=None,provider=None,resolved_model_id=None,model_provenance='not-applicable',model_verified=False,fallback_used=False,fallback_reason=None,degraded_requirements=[],independent_session=False,note='No model in arithmetic loop; implementation authored by native Executor session, model identifier not independently probed.'),environment=env,inputs=dict(seed=0,fixture_ids=[f['id'] for f in fs],input_sha256=sha(P/'inputs.json')),timing=dict(started_at=start,finished_at=now(),wall_seconds=wall,setup_wall_seconds_charged=args.setup_wall_seconds,total_charged_wall_seconds=wall+args.setup_wall_seconds),resources=dict(cpu_seconds=time.process_time()-cpu,peak_rss_bytes=ru.ru_maxrss if sys.platform=='darwin' else ru.ru_maxrss*1024,memory_limit_bytes=8*1024**3,wall_limit_seconds=900,workers=1),result=dict(valid=g in [2,4],invalid_reason=None if g in [2,4] else 'unresolved_native_definition_interface; dependent certificates unavailable',failure_class=None if g in [2,4] else 'specification_error',metrics={'incorrectly_accepted_claims':0},certificate={'kind':'none','verified':None,'verifier':None}),protocol_deviations=[],anomalies=[inputs['native_stop_reason']] if g in [1,3] else [],scope='Eight declared toy fixtures only; no scientific claim promotion')}
    write(d/'command.txt',command+'\n');write(d/'environment.json',env);write(d/'raw-result.json',raw);write(d/'certificates.json',cert);write(d/'stdout.log',json.dumps(raw)+'\n');write(d/'stderr.log','');write(d/'manifest.yaml',manifest)
    print(json.dumps(dict(group=g,status=manifest['run']['status'],fixtures=raw['fixtures'],wall_seconds=wall,checker=raw['checker'])))
if __name__=='__main__':main()
