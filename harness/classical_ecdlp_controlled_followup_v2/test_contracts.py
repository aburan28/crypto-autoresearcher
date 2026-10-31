#!/usr/bin/env python3
"""Fixed disclosed tiny solver/BSGS contract controls; no scientific launcher."""
import argparse,base64,copy,enum,gzip,hashlib,io,json,os,shutil,subprocess,sys,types,unittest
from datetime import datetime,timezone
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import controller as c
import driver
import worker_runtime as worker

ARGS=None
EVENTS=[]

def now():return datetime.now(timezone.utc).isoformat()
def snapshot():
    files={}
    for p in sorted(HERE.rglob('*')):
        if p.is_file() and p.suffix in ('.py','.json') and p.name!='delivery.json':
            b=p.read_bytes();files[p.relative_to(HERE).as_posix()]={'sha256':c.sha_bytes(b),'bytes':len(b),'base64':base64.b64encode(b).decode()}
    for rel in ('tools/experiment_execution.py','tools/experiment_protocol.py','schemas/experiment-export.v1.json','schemas/experiment-protocol.v1.json'):
        b=(Path(ARGS.canonical_repo)/rel).read_bytes();files[rel]={'sha256':c.sha_bytes(b),'bytes':len(b),'base64':base64.b64encode(b).decode()}
    return {'captured_at':now(),'files':files}

def command(argv,cwd):
    before=snapshot();start=now();p=subprocess.run(argv,cwd=cwd,capture_output=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
    event={'argv':argv,'cwd':str(cwd),'started_at':start,'finished_at':now(),'returncode':p.returncode,'stdout':p.stdout.decode(),'stderr':p.stderr.decode(),'source_before':before,'source_after':snapshot()};EVENTS.append(event);return event

class FileType(enum.Enum):
    FILE='file';DIRECTORY='directory'
class MockFilesystem:
    def __init__(self,sandbox):self.sb=sandbox
    def blob(self,path):return b'{}' if path.startswith('/opt/study/') else self.sb.files[path.removeprefix('/work/result/')]
    def stat(self,path):
        directory=path in ('/','/opt','/opt/study','/work','/work/result','/work/result/raw')
        return types.SimpleNamespace(type=FileType.DIRECTORY if directory else FileType.FILE,size=0 if directory else len(self.blob(path)),symlink_target=None)
    def read_bytes(self,path):return self.blob(path)
    def write_bytes(self,data,path):self.sb.stage[path]=data
    def copy_to_local(self,path,local):Path(local).write_bytes(self.blob(path))
class MockSandbox:
    object_id='sb-MOCK-DISCLOSED-TINY-NO-VM'
    def __init__(self,root,engine_rc=0):self.root=root;self.stage={};self.files={};self.filesystem=MockFilesystem(self);self.engine_rc=engine_rc;self.calls=0
    def exec(self,*argv,**kw):
        if argv[0]=='mkdir':return types.SimpleNamespace(wait=lambda:0)
        self.calls+=1;request=json.loads(self.stage['/work/stage/request.json']);result=worker.run(request,self.root/'result/raw')
        (self.root/'result/worker.stdout').write_bytes(c.canonical(result)+b'\n');(self.root/'result/worker.stderr').write_bytes(b'')
        self.files={p.relative_to(self.root/'result').as_posix():p.read_bytes() for p in sorted((self.root/'result').rglob('*')) if p.is_file()}
        seal={'engine_returncode':self.engine_rc,'uid1000_quiescent':True,'files':[{'path':n,'size':len(b),'sha256':c.sha_bytes(b)} for n,b in self.files.items()]}
        return types.SimpleNamespace(wait=lambda:0,stdout=io.StringIO(json.dumps(seal)),stderr=io.StringIO(''))
    def terminate(self,wait):
        if wait is not True:raise ValueError('mock ACK requires wait')
        return -15

def sdk(sb):
    return types.SimpleNamespace(fixture_only=True,__version__='1.6.2',App=types.SimpleNamespace(lookup=lambda *a,**k:types.SimpleNamespace(app_id=c.APP_ID)),Image=types.SimpleNamespace(from_id=lambda *a:object()),Sandbox=types.SimpleNamespace(create=lambda *a,**k:sb))

def fixture_protocol(ep,root):
    # Reuse schema-valid structural scaffolding only; replace all study semantics.
    p=c.read(Path(ARGS.canonical_repo)/'experiments/EXP-ECDLP-787704/protocol.json')
    p['protocol_id']='EXP-FIXTURE-52e442';p['created']='2026-10-30';p['repository']='other';p['question']='Synthetic fixed tiny type fixture, not scientific approval or fresh-population experiment.'
    p['claims']=[{'class':'out_of_scope','decided_by':[],'id':'no-science','text':'Typed pipeline/source/metadata controls only; no empirical attack or family claim.'}]
    arm=copy.deepcopy(p['arms'][0]);arm.update(id='pipeline',description='One physical tiny pipeline session; child function work in registry.',parameters={'fixture_only':True});arm['instrument'].update(commit=None,binary_sha256=None,build=[],repo='unpublished-outside-source',env={},flags={'fixture_only':'true'});p['arms']=[arm]
    p['controls']={k:{'present':False,'not_applicable_reason':'One physical synthetic type-fixture row; positive/negative assertions executed by source-bound unit suite, not fictitious research arms.',**({'comparison':None} if k=='aa' else {'arm':None,'expected_detection':None} if k=='positive' else {'arm':None,'null_population':None})} for k in ('aa','positive','negative')}
    p['variable_ledger']={'independent':[],'factors':[{'name':'fixed_fixture','treatment':'fixed','how':'Disclosed public fixtures only.'}],'comparisons':[{'id':'typed-contract','arms':['pipeline'],'design':'absolute','differs_in':[],'threshold':'Complete literal fixed fixture and honest metadata.'}],'crosses_map':True,'aa_not_applicable':'No timing/scientific inference in a synthetic contract fixture.'}
    p['randomization']={'arm_order':'fixed','arm_order_reason':'One actual session, deterministic fixtures.','blinding':{'analysis_labels_masked':False,'how':'Fixed disclosed public unit fixture only.','unmasked_at':None},'instance_sampling':{'independent_of_arm':True,'rule':'Fixed F11/F23 public targets, no sampling.'},'seed_derivation':{'method':'harness_drawn','note':'fixed00_no_entropy; no entropy or new targets.'}}
    p['sample_size']['instances']=1;p['sample_size']['replicates']=1;p['sample_size']['warmups']=0;p['sample_size']['power'].update(note='Synthetic exact type fixture; no statistical power claim.');p['sample_size']['preflight_runtime'].update(estimated_total_seconds=1,measured_on='Synthetic metadata constant for fixed format validation only; not an observed runtime or scientific budget.')
    p['metrics']={'primary':[{'id':'candidate_worker_invocations','name':'Actual candidate worker calls','unit':'calls','kind':'counted','definition':'One actual mock-transport worker function call; zero actual VMs.','source':'controller-receipt.json','aggregation':'per_row','uncertainty':'none_exact'}],'secondary':[]}
    p['measurement'].update(counters=['Actual emitted old solver/host vectors, no native-cost qualification.'],record=['Full source/input bytes before/after every fixed control'],clock='none',isolation_required='none')
    p['execution'].update(queue='synthetic-fixture-only',placement={'fixture_only':True,'actual_vms':0},timeout_seconds=120)
    p['stopping_rules']=[{'rule':'Exactly the disclosed tiny fixture, no scientific run or hidden retry.','kind':'fixed_n','preregistered':True}]
    p['decision_rule'].update(comparison_ids=['typed-contract'],statistic='Typed contract only',effect_size_measure='Not applicable to synthetic fixture',interval='No scientific inference',threshold='Exact structural preservation',text='A unit-test pass is not scientific approval or source readiness.')
    p['analysis_plan']={'blinded':False,'frozen_before_data':True,'inputs':['raw tiny bundle'],'outputs':['analysis.json','export.json'],'script':{'path':str(HERE/'postrun/analysis.py'),'sha256':c.sha_file(HERE/'postrun/analysis.py')}}
    p['inadmissible']=['Presenting synthetic metadata as scientific admission','Claiming unpublished source existed in an old commit','Cloned physical execution rows','Analytical reference represented as physical arm'];p['amendments']=[]
    for k in ('hypotheses','links','preflight','design_rationale','extensions'):p.pop(k,None)
    p['extensions']={'fixture_only':True,'controlled_followup_v2':{'export_unit':'physical_pipeline_session','physical_arm':'pipeline','physical_instance':'tiny-pipeline','analytical_reference_is_arm':False}}
    p['freeze']={'status':'frozen','protocol_sha256':None,'commit':None,'frozen_at':now(),'filed_before_affected_data':True};p['freeze']['protocol_sha256']=ep.protocol_hash(p)
    return p

def setup_case(root,ep,engine_rc=0):
    root.mkdir();repo=Path(ARGS.repo_root);inputsdir=root/'inputs';inputsdir.mkdir()
    protocol=fixture_protocol(ep,root);c.write(inputsdir/'protocol.json',protocol)
    interface=c.read(HERE/'engine-interface.json')
    data={'protocol':protocol,'engine_plan':{'expected':{'setups':2,'singles':2,'traces':28,'intents':28,'cells':168},'sampler':{},'engine_interface_canonical_sha256':c.sha_bytes(c.canonical(interface)),'max_total_orbit_points':30},'image_receipt':{'app_name':'FIXED-MOCK-NO-VM','environment_name':'fixture',**{k:c.sha_bytes(b'{}') for k in ('build_info_sha256','adapter_manifest_sha256','build_provenance_sha256')}},'prior_exclusions':{'excluded_p_j':[]}}
    for role in ('engine_plan','image_receipt','prior_exclusions'):c.write(inputsdir/(role+'.json'),data[role])
    binding={role:{'path':str((inputsdir/(role+'.json')).relative_to(repo)),'sha256':c.sha_file(inputsdir/(role+'.json'))} for role in data}
    for role,name in [('worker_manifest','worker-source-manifest.json'),('host_manifest','host-source-manifest.json'),('engine_interface','engine-interface.json'),('host_interface','host/verifier-interface.json')]:binding[role]={'path':str((HERE/name).relative_to(repo)),'sha256':c.sha_file(HERE/name)}
    out=root/'native';out.mkdir();argv=list(sys.orig_argv);checker=argv
    trial={'id':'tiny-fixture','run_id':'RUN-FIXTURE-52e442','parameters':{'fixture_only':True}}
    native_plan={'experiment_id':protocol['protocol_id'],'task_id':'TASK-20261030-52e442','approved_by':None}
    source_map={n:v['sha256'] for n,v in snapshot()['files'].items()};context={'commit':'synthetic-format-context-no-Git-source-claim'}
    environment={'python':sys.version,'platform':sys.platform,'commit':context['commit'],'source_sha256':source_map,'specification_sha256':c.sha_file(inputsdir/'protocol.json'),'runtime_lock':None,'runtime_lock_sha256':None}
    planpath=root/'native-plan.json';c.write(planpath,native_plan);ph=c.sha_file(planpath);start=now()
    launch={'argv':argv,'check_argv':checker,'started_at':start,'trial_id':trial['id'],'run_id':trial['run_id'],'authority':context,'plan_sha256':ph,'task_id':native_plan['task_id']}
    c.write(out/'launch.json',launch);c.write(out/'environment.json',environment);(out/'command.txt').write_text(json.dumps(argv)+'\n');(out/'stdout.log').write_bytes(b'');(out/'stderr.log').write_bytes(b'')
    config={'schema':c.SCHEMA+'transport-config/v1','fixture_only':True,'fixture_id':'disclosed-F11-F23-paired-v2','inputs':binding,'limits':{'max_total_bytes':1<<27,'max_file_bytes':1<<26,'max_jsonl_line_bytes':1<<20,'command_seconds':30,'sandbox_seconds':120},'seed_rules':{'fixture_only':'fixed00_no_entropy'},'trial_plan':str(planpath.relative_to(repo)),'trial_parameters':trial['parameters'],'approved_by':None,'task_id':native_plan['task_id']}
    sb=MockSandbox(root/'mock-worker',engine_rc);before=snapshot()
    raw=driver.run(repo,config,out,sdk=sdk(sb),experiment_id=protocol['protocol_id'],run_id=trial['run_id']);finish=now()
    EVENTS.append({'kind':'actual_tiny_solver_mock_pipeline','started_at':start,'finished_at':finish,'source_before':before,'source_after':snapshot(),'engine_rc_fixture':engine_rc,'actual_mock_worker_calls':sb.calls,'actual_vms':0,'raw_status':raw['operational_status']})
    return dict(root=root,repo=repo,out=out,config=config,protocol=protocol,protocol_path=inputsdir/'protocol.json',native_plan=native_plan,planpath=planpath,plan_hash=ph,trial=trial,authority=context,argv=argv,checker=checker,start=start,finish=finish,raw=raw)

class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(ARGS.control_root);cls.root.mkdir(parents=True,exist_ok=False)
        sys.path.insert(0,str(Path(ARGS.canonical_repo)/'tools'));sys.path.insert(0,ARGS.canonical_repo)
        import experiment_protocol,experiment_execution
        cls.ep=experiment_protocol;cls.native=experiment_execution
        cls.case=setup_case(cls.root/'complete',cls.ep)
        cls.post=c.module(HERE/'postrun/run_postrun.py','controlled_v2_postrun')
        cls.postout=cls.case['root']/'postrun'
        cls.result=cls.post.run(cls.case['out'],cls.postout,cls.case['repo'],fixture_law='disclosed-F11-F23-paired-v2')

    def test_01_math_identity_and_actual_pipeline_coverage(self):
        inventory=c.read(Path(ARGS.canonical_repo)/'coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-f7bbdf/next-source-repair-4a31b3/frozen-source-inputs.json')
        for old,digest in inventory['immutable_math_copy_sha256'].items():
            rel=Path(old).relative_to('harness/classical_ecdlp_controlled_followup');self.assertEqual(c.sha_file(HERE/rel),digest)
        self.assertEqual(self.case['raw']['operational_status'],'completed',self.case['raw'].get('driver_error'))
        self.assertEqual(self.result['status'],'complete',self.result)
        checked=c.read(self.postout/'verification.json');self.assertEqual(checked['observed'],{'setups':2,'singles':2,'traces':28,'intents':28,'cells':168})
        refs=c.read(self.postout/'host-references.json');self.assertEqual(len(refs['rows']),2)
        for q in refs['rows']:self.assertEqual(q['answer']['scalar'],7);self.assertEqual(q['answer']['status'],'success')
        analytical=c.read(self.postout/'analytical-reference.json');self.assertEqual(len(analytical['rows']),168);self.assertTrue(all(x['physical_invocations']==0 for x in analytical['rows']))
        registry=c.read(self.postout/'physical-registry.json');self.assertEqual(len(registry['physical_sessions']),1);self.assertEqual(registry['physical_sessions'][0]['actual_vms'],0)
        rows=list(self.post.analysis.rows(self.case['out']/'modal/collected/raw/decoder-cells.jsonl',1<<20));self.assertEqual(len(rows),168)
        EVENTS.append({'kind':'actual_tiny_outcome_coverage','status_counts':dict(__import__('collections').Counter(q['status'] for q in rows)),'zero_candidate_checks':sum(q['zero_candidate_checks'] for q in rows),'M0':sum(q['M']==0 for q in rows),'caps':sum(q['capped'] for q in rows),'undefined':sum(q['status']=='UNDEFINED' for q in rows),'scope':'Fixed disclosed F11/F23 only; not empirical population science.'})

    def test_02_native_complete_json_unchanged(self):
        q=self.case;manifest=q['out']/'manifest.yaml';before=manifest.read_bytes()
        result=self.native.complete_manifest(q['out'],q['native_plan'],str(q['planpath'].relative_to(q['repo'])),q['plan_hash'],q['trial'],q['authority'],q['argv'],q['checker'],q['start'],q['finish'])
        self.assertEqual(result['action'],'unchanged');self.assertEqual(manifest.read_bytes(),before);self.assertEqual(driver.check(q['out'])['operational_status'],'complete')
        EVENTS.append({'kind':'native_complete_manifest','result':result,'manifest_sha256':c.sha_file(manifest),'manifest_bytes_preserved':True})
        body=c.read(manifest)
        for name,mutate in [('commit',lambda x:x['run']['code'].update(commit='0'*40)),('command',lambda x:x['run']['code'].update(command=['false'])),('source',lambda x:x['run']['environment']['source_sha256'].__setitem__(next(iter(x['run']['environment']['source_sha256'])),'0'*64)),('primitive',lambda x:x['run'].update(attack_claimed=0)),('clock',lambda x:x['run']['timing'].update(started_at='2000-01-01T00:00:00+00:00'))]:
            bad=copy.deepcopy(body);mutate(bad);manifest.write_text(json.dumps(bad))
            with self.assertRaises(self.native.EnvelopeRefused):self.native.complete_manifest(q['out'],q['native_plan'],str(q['planpath'].relative_to(q['repo'])),q['plan_hash'],q['trial'],q['authority'],q['argv'],q['checker'],q['start'],q['finish'])
        manifest.write_bytes(before)

    def test_03_strict_json_and_missing_partial_rows(self):
        for name,text in [('duplicate','{"x":0,"x":1}'),('yaml','x: 0\n'),('nan','{"x":NaN}'),('float','{"x":1e999}'),('missing','{')]:
            p=self.root/(name+'.json');p.write_text(text)
            with self.assertRaises(ValueError):c.read(p)
        partial=self.root/'partial.jsonl';partial.write_text('{"x":0}')
        with self.assertRaises(ValueError):list(self.post.analysis.rows(partial,1024))
        raw=self.case['out']/'raw-result.json';original=raw.read_bytes();q=c.read(raw);q['operational_status']='failed';raw.write_text(json.dumps(q))
        with self.assertRaises(ValueError):driver.check(self.case['out'])
        raw.write_bytes(original)

    def test_04_genuine_failure_preserved_false_success_refused(self):
        case=setup_case(self.root/'failed',self.ep,engine_rc=1)
        self.assertEqual(case['raw']['operational_status'],'failed');self.assertEqual(driver.check(case['out'])['operational_status'],'failed')
        result=self.post.run(case['out'],case['root']/'postrun',case['repo'],fixture_law='disclosed-F11-F23-paired-v2')
        self.assertEqual(result['status'],'incomplete');bundle=c.read(case['root']/'postrun/export.json');self.assertEqual(bundle['runs'][0]['status'],'infra_error');self.assertEqual(bundle['flow']['not_completed'],1)
        raw=case['out']/'raw-result.json';manifest=case['out']/'manifest.yaml';r=c.read(raw);m=c.read(manifest);r['operational_status']='completed';m['run']['status']='completed';raw.write_text(json.dumps(r));manifest.write_text(json.dumps(m))
        with self.assertRaises(ValueError):driver.check(case['out'])
        EVENTS.append({'kind':'simulated_nonzero_worker_exit_preserved','observed_model_exit':1,'status':'failed','export_status':'infra_error','false_success_refused':True,'actual_vm':False})

    def test_05_synthetic_erasure_zero_boundary_controls(self):
        # Fixed response erasures are explicitly synthetic unit inputs, not
        # fabricated physical predicate observations or scientific result rows.
        import engine
        host=sys.modules['verify'];raw=self.case['out']/'modal/collected/raw';evidence=c.read(self.case['out']/'modal/custody.json');seal=host.open_sealed(raw,evidence)
        trace=next(self.post.analysis.rows(raw/'traces.jsonl',1<<20));model={'p':11,'a':1,'b':6,'r':13};base=(2,7);from constructor import prepare
        prepared=prepare(model,base,engine.arm_specs()[4]);oracle=host.Oracle(seal,model,[2,7]);seen=__import__('collections').Counter()
        for e in (0,1,2,3):
            attempt=copy.deepcopy(trace['original'])
            for i in range(e):attempt['predicate_trace'][i]['answer'].update(status='UNDEFINED',bit=None,reason='SYNTHETIC_FIXED_ERASURE')
            if e:attempt['status']='UNDEFINED'
            bits=[q['answer']['bit'] for q in attempt['predicate_trace']]
            for t,cap in engine.CELL_SPECS:
                cell=engine.decode_cell(prepared,base,tuple(trace['target']),1,trace['target_multiplier'],attempt,t,cap)
                cell.update(cell_id=trace['trace_id']+f'/t{t}.e{cap}',trace_id=trace['trace_id'])
                host.check_engine_cell(oracle,trace,bits,cell);seen[cell['status']]+=1
                actual_erasures=bits.count(None)
                self.assertEqual(cell['capped'],actual_erasures>cap);self.assertEqual(cell['word_count'],0 if actual_erasures>cap else (1<<actual_erasures)*sum(__import__('math').comb(len(bits)-actual_erasures,k) for k in range(min(t,len(bits)-actual_erasures)+1)))
        self.assertGreater(seen['UNDEFINED'],0);self.assertGreater(seen['CAPPED_ERASURES'],0)
        EVENTS.append({'kind':'synthetic_decoder_boundary_only','predicate_observation':False,'status_counts':dict(seen),'missing_data_zero_filled':False})

    def test_06_unified_export_positive_and_historical_seven_controls(self):
        bundle=c.read(self.postout/'export.json');protocol=self.case['protocol'];self.assertEqual(len(bundle['runs']),1);self.assertEqual(len(bundle['arms']),1);self.assertIsNone(bundle['source']['commit']);self.assertIsNone(bundle['arms'][0]['commit'])
        self.assertEqual(self.ep.schema_errors(protocol,'experiment.protocol/v1'),[]);self.assertEqual(self.ep.lint_protocol(protocol),[])
        argv=[sys.executable,'-B',str(Path(ARGS.canonical_repo)/'tools/experiment_protocol.py'),'check-export',str(self.postout/'export.json'),'--protocol',str(self.case['protocol_path']),'--verify-files']
        event=command(argv,Path(ARGS.repo_root));self.assertEqual(event['returncode'],0,event['stdout']+event['stderr'])
        cases=[('commit','protocol',lambda p:p['arms'][0]['instrument'].update(commit='1'*40),'commit'),('missing_reference','protocol',lambda p:p['arms'].append({**copy.deepcopy(p['arms'][0]),'id':'conditional-uniform','role':'reference'}),'arms with no run'),('row96','protocol',lambda p:(p['arms'].append({**copy.deepcopy(p['arms'][0]),'id':'conditional-uniform','role':'reference'}),p['sample_size'].update(instances=48)),'plans 96'),('candidate_instances','protocol',lambda p:p['sample_size'].update(instances=48),'arm pipeline: measured 1 instances, expected 48'),('reference_instances','protocol',lambda p:(p['arms'].append({**copy.deepcopy(p['arms'][0]),'id':'conditional-uniform','role':'reference'}),p['sample_size'].update(instances=48)),'arm conditional-uniform: measured 0 instances, expected 48'),('different_instances','both',None,'instance identities differ'),('analysis_omission','export',lambda p:p['analysis'].update(script=None),'analysis.script.sha256')]
        for name,kind,mutation,needle in cases:
            pp=copy.deepcopy(protocol);ee=copy.deepcopy(bundle)
            if kind=='protocol':mutation(pp)
            elif kind=='export':mutation(ee)
            else:
                pp['arms'].append({**copy.deepcopy(pp['arms'][0]),'id':'other','role':'reference'});ee['arms'].append({**copy.deepcopy(ee['arms'][0]),'id':'other','role':'reference'});ee['runs'].append({**copy.deepcopy(ee['runs'][0]),'run_id':'SYNTHETIC-CLONE-REJECT','arm':'other','instance_id':'different'});ee['flow']=self.ep.compute_flow(ee['runs'])
            pp['freeze']['protocol_sha256']=self.ep.protocol_hash(pp);ee['protocol']['sha256']=pp['freeze']['protocol_sha256']
            pro=self.case['root']/('negative-'+name+'.protocol.json');ex=self.postout/('negative-'+name+'.json');c.write(pro,pp);c.write(ex,ee)
            ev=command([sys.executable,'-B',str(Path(ARGS.canonical_repo)/'tools/experiment_protocol.py'),'check-export',str(ex),'--protocol',str(pro),'--verify-files'],Path(ARGS.repo_root));self.assertEqual(ev['returncode'],1);self.assertIn(needle,ev['stdout']+ev['stderr'])

    def test_07_pending_publication_not_readiness(self):
        self.assertIsNone(c.read(HERE/'worker-source-manifest.json')['source_revision']);self.assertIsNone(c.read(HERE/'host-source-manifest.json')['source_revision'])
        with self.assertRaises(ValueError):c.source_payload(Path(ARGS.repo_root),HERE/'worker-source-manifest.json','worker')
        self.assertEqual(c.read(self.postout/'analysis.json')['coverage']['retained_decoder_cells'],168)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo-root',required=True);p.add_argument('--canonical-repo',required=True);p.add_argument('--control-root',required=True);ARGS,remaining=p.parse_known_args()
    # Full source capture happens before any fixture/protocol data is consumed.
    before=snapshot();started=now()
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contracts))
    record={'schema':'controlled-followup-v2.unit-controls/v1','argv':sys.orig_argv,'started_at':started,'finished_at':now(),'source_before':before,'source_after':snapshot(),'returncode':0 if result.wasSuccessful() else 1,'events':EVENTS,'scientific_invocations':0,'math_population':'Only disclosed F11/r13 and F23/r17 fixed unit fixtures; no new curves/targets/entropy.'}
    Path(ARGS.control_root).mkdir(parents=True,exist_ok=True);c.write(Path(ARGS.control_root)/'checks.json',record)
    raise SystemExit(record['returncode'])
