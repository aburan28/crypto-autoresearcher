#!/usr/bin/env python3
"""Declared fixed tiny controls. Each attempt uses a fresh immutable directory."""
from pathlib import Path
import argparse,copy,json,shutil,sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parent));import driver as d
exp=d.module(Path(__file__).with_name('export.py'),'v3_export');check=d.module(Path(__file__).with_name('check.py'),'v3_check');ARGS=None;EVENTS=[]
class Contracts(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.root=Path(ARGS.control_root);cls.root.mkdir(parents=True,exist_ok=False);cls.input=cls.root/'input.json';d.write(cls.input,d.read(d.HERE/'fixtures.json')['input']);cls.protocol=cls.root/'protocol.json';d.write(cls.protocol,exp.fixture_protocol(ARGS.contracts_root));cls.out=cls.root/'execution';cls.result=d.run(ARGS.repo_root,ARGS.contracts_root,cls.input,cls.out,True);cls.bundle,cls.findings=exp.make(cls.protocol,cls.out,ARGS.contracts_root,cls.root/'export')
 def test_01_real_distinct_processes_and_all_negative_rows(self):
  self.assertEqual(self.result['status'],'complete');self.assertEqual(self.findings,[]);self.assertEqual(check.check(self.out,self.protocol,self.root/'export/export.json',ARGS.repo_root,ARGS.contracts_root)['status'],'pass');procs=[d.read(self.out/a/'process.json') for a in ('candidate','baseline')];self.assertEqual(len({p['pid'] for p in procs}),2)
  cells=[d.loads(line) for line in (self.out/'candidate/result/raw/decoder-cells.jsonl').read_bytes().splitlines()];counts=__import__('collections').Counter(c['status'] for c in cells);self.assertEqual(len(cells),168);self.assertEqual(counts,{'RECOVERED':90,'REJECTED_FINAL_VERIFICATION':38,'EMPTY_INTERVAL':10,'UNDEFINED':10,'CAPPED_ERASURES':20});refs=d.read(self.out/'baseline/result/bsgs.json');self.assertEqual(refs['independent_decoder_cells_checked'],168);self.assertEqual([r['answer']['scalar'] for r in refs['rows']],[7,7]);self.assertTrue(all(r['public_equation_verified'] for r in refs['rows']));EVENTS.append({'kind':'actual_fixed_coverage','cells':168,'statuses':dict(counts),'actual_distinct_pids':[p['pid'] for p in procs],'BSGS_scalars':[7,7],'scientific_runs':0})
 def test_02_native_complete_json_unchanged(self):
  sys.path.insert(0,str(Path(ARGS.contracts_root)/'tools'));native=d.module(Path(ARGS.contracts_root)/'tools/experiment_execution.py','v3_native')
  for arm in ('candidate','baseline'):
   out=self.out/arm;m=d.read(out/'manifest.yaml');l=d.read(out/'launch.json');plan=d.read(out/'native-plan.json');trial={'id':arm,'run_id':m['run']['id'],'parameters':{'fixture_only':True}};before=(out/'manifest.yaml').read_bytes();result=native.complete_manifest(out,plan,'native-plan.json',d.sha((out/'native-plan.json').read_bytes()),trial,l['authority'],l['argv'],l['check_argv'],l['started_at'],m['run']['timing']['finished_at']);self.assertEqual(result['action'],'unchanged');self.assertEqual((out/'manifest.yaml').read_bytes(),before);EVENTS.append({'kind':'native_complete_manifest','arm':arm,'actual_result':result,'exact_bytes_preserved':True})
 def test_03_strict_json_bad_shapes_and_partial(self):
  for text in ('{"x":0,"x":1}','x: 1','{"x":NaN}','{"x":1e999}','{'):
   with self.assertRaises(ValueError):d.loads(text)
  x=d.read(self.input);x['fixture_only']=1
  with self.assertRaises(ValueError):d.input_check(x,True)
 def test_04_known_negative_mutations(self):
  mutations={
   'missing_arm':lambda r,p,b:r['processes'].pop(),
   'cloned_pid':lambda r,p,b:r['processes'][1].update(pid=r['processes'][0]['pid']),
   'row_reuse':lambda r,p,b:b['runs'][1].update(backend_ref=b['runs'][0]['backend_ref']),
   'instrument_commit':lambda r,p,b:p['arms'][0]['instrument'].update(commit='0'*40),
   'instance_identity':lambda r,p,b:b['runs'][1].update(instance_id='different'),
   'missing_analysis':lambda r,p,b:b['analysis'].pop('script'),
   'source_hash':lambda r,p,b:b['analysis']['script'].update(sha256='0'*64),
   'false_success':lambda r,p,b:b['runs'][0].update(status='infra_error'),
   'physical_count':lambda r,p,b:b['runs'][0]['measurements']['counted'].update(physical_invocations=2)}
  for name,mutate in mutations.items():
   r=d.read(self.out/'registry.json');p=d.read(self.protocol);b=copy.deepcopy(self.bundle);mutate(r,p,b)
   if name=='instrument_commit':
    for arm in p['arms']:arm['instrument']['commit']='0'*40
    p['freeze']['protocol_sha256']=exp.ep_module(ARGS.contracts_root).protocol_hash(p)
    for arm in b['arms']:arm['commit']='0'*40
    b['source']['commit']='0'*40;b['protocol']['sha256']=p['freeze']['protocol_sha256']
   if name=='false_success':
    b['runs'][0]['outcome_class']='not_completed';b['flow']=exp.ep_module(ARGS.contracts_root).compute_flow(b['runs'])
   # Recompute dependent file bindings so a registry semantic corruption is
   # tested beyond the generic byte-tampering detector.
   if name in ('missing_arm','cloned_pid'):
    newbytes=d.canonical(r);b['host']['sha256']=d.sha(newbytes)
    for item in b['files']+[a for row in b['runs'] for a in row['artifacts']]:
     if (self.root/'export'/item['path']).resolve()==(self.out/'registry.json').resolve():item.update(sha256=d.sha(newbytes),bytes=len(newbytes))
   case=self.root/'negative'/name;case.mkdir(parents=True);rp=case/'registry.json';pp=case/'protocol.json';bp=case/'export.json';d.write(rp,r);d.write(pp,p);d.write(bp,b)
   # Mutate exactly one field at its original resolution path. A passing
   # unchanged baseline precedes every mutation; otherwise a relocated path
   # could make an unrelated file lookup explain the refusal.
   check.check(self.out,self.protocol,self.root/'export/export.json',ARGS.repo_root,ARGS.contracts_root)
   targets=[(self.out/'registry.json',rp),(self.protocol,pp),(self.root/'export/export.json',bp)];originals=[t.read_bytes() for t,_ in targets]
   for target,mutated in targets:target.write_bytes(mutated.read_bytes())
   try:
    try:check.check(self.out,self.protocol,self.root/'export/export.json',ARGS.repo_root,ARGS.contracts_root)
    except (ValueError,KeyError) as error:message=str(error)
    else:self.fail('Mutation was accepted: '+name)
   finally:
    for (target,_),original in zip(targets,originals):target.write_bytes(original)
   expected={'missing_arm':'missing or cloned process','cloned_pid':'missing or cloned process','instrument_commit':'instrument commit falsely identifies execution source','false_success':'false completion'}
   if name in expected:self.assertIn(expected[name],message)
   EVENTS.append({'kind':'negative_control','name':name,'refused':True,'refusal':message,'baseline_passed_same_resolution_paths':True,'single_logical_mutation':True,'dependent_bindings_recomputed':name in ('missing_arm','cloned_pid','instrument_commit','false_success'),'fresh_scientific_runs':0})
 def test_05_file_member_seal_source_and_falsecomplete(self):
  cases=[('member_bytes',self.out/'candidate/result/raw/traces.jsonl',lambda b:b+b'{}\n'),('seal',self.out/'candidate/seal.json',lambda b:d.canonical({**d.loads(b),'tree_sha256':'0'*64})),('process_source',self.out/'candidate/process.json',lambda b:d.canonical({**d.loads(b),'source_publication_commit':'0'*40})),('falsecomplete',self.out/'candidate/process.json',lambda b:d.canonical({**d.loads(b),'returncode':1})),('partial_jsonl',self.out/'candidate/result/raw/traces.jsonl',lambda b:b[:-1])]
  for name,path,mutate in cases:
   old=path.read_bytes();bad=mutate(old);case=self.root/'negative'/name;case.mkdir(parents=True);(case/'before.bin').write_bytes(old);(case/'mutated.bin').write_bytes(bad);path.write_bytes(bad)
   try:
    with self.assertRaises((ValueError,KeyError)):check.check(self.out,self.protocol,self.root/'export/export.json',ARGS.repo_root,ARGS.contracts_root)
   finally:path.write_bytes(old)
   EVENTS.append({'kind':'negative_control','name':name,'refused':True})
 def test_06_native_contradictions_and_yaml_format(self):
  sys.path.insert(0,str(Path(ARGS.contracts_root)/'tools'));native=d.module(Path(ARGS.contracts_root)/'tools/experiment_execution.py','v3_native_negative');out=self.out/'candidate';old=(out/'manifest.yaml').read_bytes();l=d.read(out/'launch.json');m=d.loads(old);plan=d.read(out/'native-plan.json');trial={'id':'candidate','run_id':m['run']['id'],'parameters':{'fixture_only':True}}
  for name,mutate in [('commit',lambda b:b['run']['code'].update(commit='0'*40)),('false_complete_type',lambda b:b['run'].update(attack_claimed=0)),('command',lambda b:b['run']['code'].update(command=['false']))]:
   bad=copy.deepcopy(m);mutate(bad);case=self.root/'negative'/('native_'+name);case.mkdir(parents=True);(case/'before.bin').write_bytes(old);(case/'mutated.bin').write_bytes(d.canonical(bad));(out/'manifest.yaml').write_bytes(d.canonical(bad))
   try:
    with self.assertRaises(native.EnvelopeRefused):native.complete_manifest(out,plan,'native-plan.json',d.sha((out/'native-plan.json').read_bytes()),trial,l['authority'],l['argv'],l['check_argv'],l['started_at'],m['run']['timing']['finished_at'])
   finally:(out/'manifest.yaml').write_bytes(old)
   EVENTS.append({'kind':'native_negative','name':name,'refused':True})
  yamlfile=self.root/'negative/native_yaml.json';yamlfile.write_text('run:\n  status: completed\n')
  with self.assertRaises(ValueError):d.read(yamlfile)
 def test_07_unchanged_cli_and_source_readiness_limit(self):
  import subprocess
  for args in (['validate',str(self.protocol)],['check-export',str(self.root/'export/export.json'),'--protocol',str(self.protocol),'--verify-files']):
   argv=[sys.executable,'-B',str(Path(ARGS.contracts_root)/'tools/experiment_protocol.py')]+args;start=d.now();r=subprocess.run(argv,capture_output=True);EVENTS.append({'kind':'unchanged_cli','argv':argv,'started_at':start,'finished_at':d.now(),'returncode':r.returncode,'stdout':r.stdout.decode(),'stderr':r.stderr.decode()});self.assertEqual(r.returncode,0,r.stdout.decode()+r.stderr.decode())
 def test_08_actual_nonzero_children_retained_as_infra_error(self):
  case=self.root/'actual-malformed-input-failure';case.mkdir();inp=case/'malformed-input.json';x=d.read(self.input);x['public']['curves'][0]['targets'][0]['point']='SYNTHETIC_INVALID_POINT_TYPE';d.write(inp,x);out=case/'execution';out.mkdir();context=d.read(self.out/'candidate/process.json')['launch_context_commit'];records=[d.launch_arm(a,ARGS.repo_root,ARGS.contracts_root,inp,out/a,context) for a in ('candidate','baseline')];self.assertTrue(all(r['returncode']!=0 for r in records));d.write(out/'registry.json',{'schema':'controlled-followup-v3.physical-registry/v1','instance_id':'shared-public-bundle','processes':[{'arm':r['arm'],'pid':r['pid'],'process_sha256':d.sha((out/r['arm']/'process.json').read_bytes())} for r in records],'input_sha256':d.sha(inp.read_bytes()),'physical_invocations':2,'analytical_reference_is_arm':False});bundle,findings=exp.make(self.protocol,out,ARGS.contracts_root,case/'export');self.assertEqual(findings,[]);self.assertTrue(all(r['status']=='infra_error' for r in bundle['runs']));self.assertEqual(check.check(out,self.protocol,case/'export/export.json',ARGS.repo_root,ARGS.contracts_root)['operational_status'],'incomplete');EVENTS.append({'kind':'actual_malformed_input_child_failures','pids':[r['pid'] for r in records],'returncodes':[r['returncode'] for r in records],'typed_rows':['infra_error','infra_error'],'candidate_partial_files_retained':True,'fabricated_zero_completion':False,'scientific_invocations':0,'fixture':'Fixed F11/F23 with synthetic invalid point TYPE; no replacement target or entropy.'})
 def test_09_actual_timeout_termination_and_closed_nonfixture_launch(self):
  case=self.root/'actual-watchdog';case.mkdir();context=d.read(self.out/'candidate/process.json')['launch_context_commit'];r=d.launch_arm('candidate',ARGS.repo_root,ARGS.contracts_root,self.input,case/'candidate',context,command_seconds=0.000001);self.assertTrue(r['timed_out']);self.assertTrue(r['termination_ack']['wait_returned']);self.assertNotEqual(r['returncode'],0);self.assertTrue(r['signals']);self.assertTrue((case/'candidate/stdout.log').is_file());self.assertTrue((case/'candidate/stderr.log').is_file());self.assertEqual(d.read(case/'candidate/seal.json')['returncode'],r['returncode']);EVENTS.append({'kind':'actual_watchdog_termination','pid':r['pid'],'returncode':r['returncode'],'signals':r['signals'],'wait_returned':True,'partial_files_and_logs_retained':True,'scientific_invocations':0})
  nonfixture=d.read(self.input);nonfixture['fixture_only']=False;np=case/'nonfixture.json';d.write(np,nonfixture)
  with self.assertRaisesRegex(ValueError,'Nonfixture launch unavailable'):d.run(ARGS.repo_root,ARGS.contracts_root,np,case/'must-not-exist',False,{'approved':True})
  self.assertFalse((case/'must-not-exist').exists())
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--repo-root',required=True);p.add_argument('--contracts-root',required=True);p.add_argument('--control-root',required=True);ARGS=p.parse_args();before=d.snapshot(ARGS.repo_root,ARGS.contracts_root);start=d.now();result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contracts));Path(ARGS.control_root).mkdir(parents=True,exist_ok=True);d.write(Path(ARGS.control_root)/'checks.json',{'schema':'controlled-followup-v3.unit-checks/v1','started_at':start,'finished_at':d.now(),'source_before':before,'source_after':d.snapshot(ARGS.repo_root,ARGS.contracts_root),'events':EVENTS,'returncode':0 if result.wasSuccessful() else 1,'scientific_invocations':0,'actual_vms':0,'fresh_entropy_draws':0,'actual_model':None,'policy':'executor-implementation','effort':'high'});raise SystemExit(0 if result.wasSuccessful() else 1)
