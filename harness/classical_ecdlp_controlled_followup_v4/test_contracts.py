#!/usr/bin/env python3
"""Bounded disclosed software controls; every attempt has a fresh evidence root."""
from pathlib import Path
import argparse,copy,io,json,os,subprocess,sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parent));import driver as d
exp=d.module(d.HERE/'export.py','unit_export');checker=d.module(d.HERE/'check.py','unit_check');adapter=d.module(d.HERE/'cohort_adapter.py','unit_adapter')
ARGS=None;EVENTS=[]
def cli(argv):
 before=d.snapshot(ARGS.repo_root,ARGS.contracts_root);start=d.now();r=subprocess.run(argv,capture_output=True,timeout=30);after=d.snapshot(ARGS.repo_root,ARGS.contracts_root)
 EVENTS.append({'kind':'actual_cli','argv':argv,'started_at':start,'finished_at':d.now(),'source_before':before,'source_after':after,'returncode':r.returncode,'stdout_utf8':r.stdout.decode(),'stderr_utf8':r.stderr.decode()});return r
class Contracts(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.root=Path(ARGS.control_root);cls.root.mkdir(parents=True,exist_ok=False)
  cls.protocol=cls.root/'protocol.json';d.write(cls.protocol,exp.fixture_protocol(ARGS.contracts_root))
  cls.ctx=d.fixture_context(ARGS.repo_root,ARGS.contracts_root);cls.ctx['protocol_sha256']=d.read(cls.protocol)['freeze']['protocol_sha256']
  cls.input=cls.root/'input.json';d.write(cls.input,adapter.fixed_input(cls.ctx['protocol_sha256'],d.sha(d.canonical(cls.ctx['source_sha256']))))
  cls.out=cls.root/'execution';cls.result=d.run_fixture(ARGS.repo_root,ARGS.contracts_root,cls.input,cls.out,cls.protocol)
  cls.bundle,cls.findings=exp.make(cls.protocol,cls.out,ARGS.contracts_root,cls.root/'export')
 def valid(self):
  return checker.check(self.out,self.protocol,self.root/'export/export.json',ARGS.repo_root,ARGS.contracts_root)
 def test_01_actual_full_toy_route(self):
  self.assertEqual(self.result['status'],'complete');self.assertEqual(self.findings,[]);self.assertEqual(self.valid()['operational_status'],'complete')
  pr=[d.read(self.out/a/'process.json') for a in ('candidate','baseline')];self.assertEqual(len({r['pid'] for r in pr}),2)
  v=d.read(self.out/'baseline/result/verification.json');self.assertEqual(v['observed'],{'setups':16,'singles':16,'intents':20,'traces':20,'cells':24})
  rows=d.read(self.out/'baseline/result/bsgs.json')['rows'];self.assertEqual([r['answer']['scalar'] for r in rows],[7,7]);self.assertTrue(all(r['public_equation_verified'] for r in rows))
  EVENTS.append({'kind':'actual_fixed_coverage','pids':[r['pid'] for r in pr],'counts':v['observed'],'decoder_statuses':v['decoder_statuses'],'BSGS_scalars':[7,7],'scientific_runs':0})
 def test_02_unchanged_native_json_and_cli(self):
  sys.path.insert(0,str(Path(ARGS.contracts_root)/'tools'));native=d.module(Path(ARGS.contracts_root)/'tools/experiment_execution.py','unit_native')
  for arm in ('candidate','baseline'):
   out=self.out/arm;body=d.read(out/'manifest.yaml')['run'];launch=d.read(out/'launch.json');plan=d.read(out/'native-plan.json');trial={'id':arm,'run_id':body['id'],'parameters':{'fixture_only':True}};old=(out/'manifest.yaml').read_bytes();before=d.snapshot(ARGS.repo_root,ARGS.contracts_root);start=d.now()
   r=native.complete_manifest(out,plan,'native-plan.json',d.sha_file(out/'native-plan.json'),trial,launch['authority'],launch['argv'],launch['check_argv'],launch['started_at'],body['timing']['finished_at'])
   self.assertEqual(r['action'],'unchanged');self.assertEqual((out/'manifest.yaml').read_bytes(),old)
   EVENTS.append({'kind':'native_complete_manifest','arm':arm,'started_at':start,'finished_at':d.now(),'source_before':before,'source_after':d.snapshot(ARGS.repo_root,ARGS.contracts_root),'result':r,'exact_manifest_bytes_preserved':True})
  for args in (['validate',str(self.protocol)],['check-export',str(self.root/'export/export.json'),'--protocol',str(self.protocol),'--verify-files']):
   r=cli([sys.executable,'-B',str(Path(ARGS.contracts_root)/'tools/experiment_protocol.py')]+args);self.assertEqual(r.returncode,0,r.stdout.decode()+r.stderr.decode())
 def test_03_same_path_isolated_metadata_mutations(self):
  mutations={
   'missing_arm':lambda p,b,r:r['processes'].pop(),
   'cloned_pid':lambda p,b,r:r['processes'][1].update(pid=r['processes'][0]['pid']),
   'row_reuse':lambda p,b,r:b['runs'][1].update(backend_ref=b['runs'][0]['backend_ref']),
   'instance':lambda p,b,r:b['runs'][1].update(instance_id='wrong'),
   'analysis':lambda p,b,r:b['analysis'].pop('script'),
   'physical_count':lambda p,b,r:b['runs'][0]['measurements']['counted'].update(physical_invocations=2),
   'false_completion':lambda p,b,r:b['runs'][0].update(status='infra_error'),
   'instrument_commit':lambda p,b,r:[a['instrument'].update(commit='0'*40) for a in p['arms']]}
  targets=[self.protocol,self.root/'export/export.json',self.out/'registry.json']
  for name,mutate in mutations.items():
   self.valid();p=d.read(targets[0]);b=d.read(targets[1]);reg=d.read(targets[2]);mutate(p,b,reg)
   if name in ('missing_arm','cloned_pid'):
    encoded=d.canonical(reg);b['host']['sha256']=d.sha(encoded)
    for item in b['files']+[f for row in b['runs'] for f in row['artifacts']]:
     if (self.root/'export'/item['path']).resolve()==targets[2].resolve():item.update(sha256=d.sha(encoded),bytes=len(encoded))
   if name=='false_completion':b['flow']=exp.ep_module(ARGS.contracts_root).compute_flow(b['runs']);b['runs'][0]['outcome_class']='not_completed'
   if name=='instrument_commit':
    p['freeze']['protocol_sha256']=exp.ep_module(ARGS.contracts_root).protocol_hash(p)
    b['protocol']['sha256']=p['freeze']['protocol_sha256'];b['source']['commit']='0'*40
    for a in b['arms']:a['commit']='0'*40
   case=self.root/'negative'/name;case.mkdir(parents=True);old=[t.read_bytes() for t in targets]
   for i,(target,obj) in enumerate(zip(targets,[p,b,reg])):
    (case/f'{i}.before').write_bytes(old[i]);bad=d.canonical(obj);(case/f'{i}.mutated').write_bytes(bad);target.write_bytes(bad)
   try:
    try:self.valid()
    except (ValueError,KeyError) as error:message=str(error)
    else:self.fail('accepted '+name)
   finally:
    for t,raw in zip(targets,old):t.write_bytes(raw)
   if name in ('missing_arm','cloned_pid'):self.assertIn('missing or cloned process',message)
   if name=='instrument_commit':self.assertIn('input/source/protocol binding',message)
   EVENTS.append({'kind':'isolated_negative','name':name,'baseline_passed_same_paths':True,'single_logical_mutation':True,'dependent_hashes_recomputed':name in ('missing_arm','cloned_pid','false_completion'),'refused':True,'refusal':message})
 def test_04_bytes_source_native_and_parser_refusals(self):
  for text in ('{"x":0,"x":1}','x: 1','{"x":NaN}','{"x":1e999}','{'):
   with self.assertRaises(ValueError):d.loads(text)
  for name,path,fn in [('member',self.out/'candidate/result/raw/traces.jsonl',lambda b:b+b'{}\n'),('partial',self.out/'candidate/result/raw/traces.jsonl',lambda b:b[:-1]),('seal',self.out/'candidate/seal.json',lambda b:d.canonical({**d.loads(b),'tree_sha256':'0'*64})),('source',self.out/'candidate/process.json',lambda b:d.canonical({**d.loads(b),'source_publication_commit':'0'*40}))]:
   self.valid();old=path.read_bytes();bad=fn(old);case=self.root/'negative'/name;case.mkdir(parents=True);(case/'before').write_bytes(old);(case/'mutated').write_bytes(bad);path.write_bytes(bad)
   try:
    with self.assertRaises((ValueError,KeyError)):self.valid()
   finally:path.write_bytes(old)
   EVENTS.append({'kind':'file_negative','name':name,'baseline_passed_same_paths':True,'refused':True})
  sys.path.insert(0,str(Path(ARGS.contracts_root)/'tools'));native=d.module(Path(ARGS.contracts_root)/'tools/experiment_execution.py','unit_native_bad');out=self.out/'candidate';old=(out/'manifest.yaml').read_bytes();m=d.loads(old);launch=d.read(out/'launch.json');plan=d.read(out/'native-plan.json');trial={'id':'candidate','run_id':m['run']['id'],'parameters':{'fixture_only':True}}
  for name,fn in [('commit',lambda x:x['run']['code'].update(commit='0'*40)),('command',lambda x:x['run']['code'].update(command=['false'])),('boolean',lambda x:x['run'].update(attack_claimed=0))]:
   bad=copy.deepcopy(m);fn(bad);case=self.root/'negative'/('native_'+name);case.mkdir(parents=True);(case/'before').write_bytes(old);(case/'mutated').write_bytes(d.canonical(bad));(out/'manifest.yaml').write_bytes(d.canonical(bad));start=d.now()
   try:
    with self.assertRaises(native.EnvelopeRefused):native.complete_manifest(out,plan,'native-plan.json',d.sha_file(out/'native-plan.json'),trial,launch['authority'],launch['argv'],launch['check_argv'],launch['started_at'],m['run']['timing']['finished_at'])
   finally:(out/'manifest.yaml').write_bytes(old)
   EVENTS.append({'kind':'native_negative','name':name,'started_at':start,'finished_at':d.now(),'refused':True})
 def test_05_real_failed_children_truthful_incomplete(self):
  case=self.root/'failed-children';case.mkdir();out=case/'execution';r=d.execute(ARGS.repo_root,ARGS.contracts_root,self.input,out,self.ctx,self.protocol,{'candidate':'nonzero','baseline':'nonzero'})
  self.assertEqual(r['status'],'incomplete');b,f=exp.make(self.protocol,out,ARGS.contracts_root,case/'export');self.assertEqual(f,[]);self.assertEqual([r['status'] for r in b['runs']],['infra_error','infra_error']);self.assertEqual(checker.check(out,self.protocol,case/'export/export.json',ARGS.repo_root,ARGS.contracts_root)['operational_status'],'incomplete')
  procs=[d.read(out/a/'process.json') for a in ('candidate','baseline')];self.assertTrue(all(r['returncode']!=0 and r['termination_ack']['wait_returned'] for r in procs));EVENTS.append({'kind':'actual_failed_children','pids':[r['pid'] for r in procs],'returncodes':[r['returncode'] for r in procs],'partial_markers_retained':True,'no_zero_filled_completion':True})
 def test_06_real_watchdog_escalation_and_byte_guard(self):
  for name,fault,limits in [('timeout','hang',{'seconds':0.3,'terminate_grace_seconds':0.2}),('escalation','ignore-term',{'seconds':0.3,'terminate_grace_seconds':0.1}),('filecap',None,{'file_bytes':128}),('logcap','flood',{'log_bytes':1024})]:
   ctx=copy.deepcopy(self.ctx);ctx['limits'].update(limits);case=self.root/name;case.mkdir()
   r=d.launch_arm('candidate',ARGS.repo_root,ARGS.contracts_root,self.input,case/'candidate',ctx,fault);self.assertFalse(r['operational_complete']);self.assertTrue(r['termination_ack']['wait_returned']);self.assertTrue((case/'candidate/stdout.log').is_file());self.assertTrue((case/'candidate/stderr.log').is_file())
   try:os.kill(r['pid'],0)
   except ProcessLookupError:pass
   else:self.fail('child remains alive')
   if name=='escalation':self.assertEqual([x['signal'] for x in r['signals']],['SIGTERM','SIGKILL'])
   if name=='filecap':self.assertNotEqual(r['returncode'],0)
   EVENTS.append({'kind':'actual_resource_control','name':name,'pid':r['pid'],'returncode':r['returncode'],'resource_stop':r['resource_stop'],'signals':r['signals'],'wait_returned':True,'all_partial_bytes_retained':True})
 def test_07_job_law_static_full_schedule_and_no_authority_bypass(self):
  plan=adapter.static_schedule(ARGS.repo_root);self.assertEqual(plan['jobs'],382464);self.assertEqual(plan['counts'],adapter.FULL);self.assertEqual(plan['scientific_draws'],0);EVENTS.append({'kind':'actual_static_plan_only','result':plan})
  x=d.read(self.input);bad=copy.deepcopy(x['plan']);bad['jobs'][1]['id']=bad['jobs'][0]['id']
  with self.assertRaisesRegex(ValueError,'duplicate/unfrozen job'):adapter.expected_from_jobs(x['public'],bad)
  bad=copy.deepcopy(x);bad['public']['curves'][0]['model']['r']=31
  with self.assertRaises(ValueError):d.input_check(bad)
  fake=self.root/'no-native-context';fake.mkdir()
  with self.assertRaises((ValueError,OSError,KeyError,TypeError)):d.production_authority(ARGS.repo_root,fake,self.root/'missing-plan.json','fake',self.root/'missing-config.json')
  self.assertFalse((fake/'shared').exists())
 def test_08_lossless_no_duplicate_publication_stream(self):
  path=self.out/'candidate/result/raw/decoder-cells.jsonl';sink=io.BytesIO();r=d.stream_payload(path,sink,257);self.assertEqual(sink.getvalue(),path.read_bytes());self.assertEqual(r,{'sha256':d.sha_file(path),'bytes':path.stat().st_size,'local_duplicate_bytes':0});EVENTS.append({'kind':'actual_lossless_stream','source_sha256':r['sha256'],'bytes':r['bytes'],'chunk_bytes':257,'source_unchanged':True,'network_calls':0,'publication_or_deletion':False})
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--repo-root',required=True);p.add_argument('--contracts-root',required=True);p.add_argument('--control-root',required=True);ARGS=p.parse_args();before=d.snapshot(ARGS.repo_root,ARGS.contracts_root);start=d.now();r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contracts));Path(ARGS.control_root).mkdir(parents=True,exist_ok=True);d.write(Path(ARGS.control_root)/'checks.json',{'schema':'controlled-followup-v4.unit-checks/v1','started_at':start,'finished_at':d.now(),'source_before':before,'source_after':d.snapshot(ARGS.repo_root,ARGS.contracts_root),'events':EVENTS,'returncode':0 if r.wasSuccessful() else 1,'scientific_runs':0,'actual_vms':0,'fresh_entropy_draws':0},64<<20);raise SystemExit(0 if r.wasSuccessful() else 1)

