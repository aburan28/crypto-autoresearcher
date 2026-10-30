#!/usr/bin/env python3
"""Local two-process adapter. Source/unit readiness is not scientific admission."""
from pathlib import Path
import argparse,base64,datetime,hashlib,importlib.util,json,math,os,subprocess,sys
HERE=Path(__file__).resolve().parent
PINS={'curve.py':'6ce0b50fcc78287de7091c36383b5ccefb5dbe208ba3d1ab1c80b1ddbc326400','constructor.py':'31e58db07649df4e61ec2cbcaa1969789bc2c7f229c21f8555daaaaad8fdc451','cohort.py':'cd5896f63f52351d499104ea14e36ddf66a4bd586efaba8e651ebce2053a8ff3','engine.py':'22da83d6494ea66c520b0e58eaa4b54e621c822d8f0275deda8822c7179915fb','host/reference.py':'ee58b639fecbed063e74d6e825ca5a6d0e19dc79816c3713092defc8dcfa3ce2','host/verify.py':'e25f80618f65c0ce19a972658dd58eaa80e16848442bdd6293b2970ec42f6fe0'}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def need(v,m):
 if not v:raise ValueError(m)
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode()+b'\n'
def pairs(items):
 d={}
 for k,v in items:
  need(k not in d,'duplicate JSON key');d[k]=v
 return d
def loads(b):
 def number(v):
  x=float(v);need(math.isfinite(x),'nonfinite');return x
 return json.loads(b,object_pairs_hook=pairs,parse_float=number,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('nonfinite')))
def read(p):
 p=Path(p);need(p.is_file() and not p.is_symlink() and p.stat().st_size<=64<<20,'bounded regular JSON');return loads(p.read_bytes())
def write(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(canonical(x))
def module(p,name):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def dependency_root(repo):return Path(repo)/'harness/classical_ecdlp_controlled_followup_v2'
def verify_dependencies(repo):
 root=dependency_root(repo)
 for n,h in PINS.items():need(sha((root/n).read_bytes())==h,'pinned dependency mismatch: '+n)
 return root
def snapshot(repo,contracts):
 paths=list(HERE.glob('*.py'))+list(HERE.glob('*.json'))+[dependency_root(repo)/n for n in PINS]
 paths += [Path(contracts)/n for n in ('tools/experiment_protocol.py','tools/experiment_execution.py','schemas/experiment-protocol.v1.json','schemas/experiment-export.v1.json')]
 out={}
 for p in sorted(set(paths)):
  if p.name=='delivery.json':continue
  b=p.read_bytes();out[str(p)]={'sha256':sha(b),'bytes':len(b),'base64':base64.b64encode(b).decode()}
 return {'captured_at':now(),'files':out}
def source_map(s):return {p:r['sha256'] for p,r in s['files'].items()}
def input_check(x,fixture_only):
 need(type(x) is dict and set(x)=={'schema','fixture_only','public','blindings'},'input fields')
 need(x['schema']=='controlled-followup-v3.public-input/v1' and type(x['fixture_only']) is bool,'input schema')
 need(x['fixture_only']==fixture_only,'fixture flag contradiction')
 pub=x['public'];need(set(pub)=={'curves','nonce'} and pub['nonce']=='00'*32 if fixture_only else set(pub)=={'curves','nonce'},'public fields')
 need(type(pub['curves']) is list and pub['curves'],'curve list')
 seen=set()
 for curve in pub['curves']:
  need(set(curve)=={'curve_id','model','base','targets'} and type(curve['curve_id']) is str and curve['curve_id'] not in seen,'curve identity');seen.add(curve['curve_id'])
  need(set(curve['model'])=={'p','a','b','r'} and all(type(v) is int for v in curve['model'].values()),'model fields')
  need(not fixture_only or curve['model']['r']<=29,'tiny fixture bound')
  need(type(curve['targets']) is list and curve['targets'] and len({t['target_id'] for t in curve['targets']})==len(curve['targets']),'target identity')
  bs=x['blindings'][curve['curve_id']];need(type(bs) is list and bs and all(type(v) is int and 0<v<curve['model']['r'] for v in bs),'fixed explicit blindings')
 need(set(x['blindings'])==seen,'blinding coverage');return x

def launch_arm(arm,repo,contracts,input_path,out,context,source_publication_commit=None,source_publication_pins=None,command_seconds=120):
 need(read(input_path).get('fixture_only') is True,'Source-unit launcher only; nonfixture requires separately frozen production adapter and actual allocated native context')
 need(source_publication_commit is None,'Unpublished source fixture cannot claim a publication commit')
 need(type(command_seconds) in (int,float) and 0<command_seconds<=120,'bounded fixture watchdog')
 out=Path(out);out.mkdir(parents=True,exist_ok=False);before=snapshot(repo,contracts);start=now()
 if source_publication_commit is not None:
  need(source_publication_pins is not None,'published source needs exact committed closure');need(source_publication_pins==source_map(before),'published source closure differs')
 argv=[sys.executable,'-B',str(HERE/(arm+'.py')),'--repo-root',str(repo),'--input',str(input_path),'--out',str(out/'result')]
 if arm=='baseline':argv+=['--candidate',str(out.parent/'candidate')]
 env={'PATH':os.defpath,'PYTHONDONTWRITEBYTECODE':'1','LC_ALL':'C.UTF-8'}
 proc=subprocess.Popen(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,close_fds=True);signals=[];timed_out=False
 try:stdout,stderr=proc.communicate(timeout=command_seconds)
 except subprocess.TimeoutExpired:
  timed_out=True;signals.append({'signal':'SIGTERM','sent_at':now()});proc.terminate()
  try:stdout,stderr=proc.communicate(timeout=5)
  except subprocess.TimeoutExpired:
   signals.append({'signal':'SIGKILL','sent_at':now()});proc.kill();stdout,stderr=proc.communicate()
 finish=now();after=snapshot(repo,contracts)
 (out/'stdout.log').write_bytes(stdout);(out/'stderr.log').write_bytes(stderr)
 need(source_map(before)==source_map(after),'source changed during process')
 record={'schema':'controlled-followup-v3.physical-process/v1','arm':arm,'pid':proc.pid,'parent_pid':os.getpid(),'argv':argv,'started_at':start,'finished_at':finish,'returncode':proc.returncode,'timed_out':timed_out,'watchdog_seconds':command_seconds,'signals':signals,'termination_ack':{'wait_returned':True,'returncode':proc.returncode},'input':{'path':str(input_path),'sha256':sha(Path(input_path).read_bytes())},'source_before':before,'source_after':after,'source_publication_commit':source_publication_commit,'launch_context_commit':context,'interpreter':{'path':sys.executable,'sha256':sha(Path(sys.executable).resolve().read_bytes())},'stdout':{'sha256':sha(stdout),'bytes':len(stdout)},'stderr':{'sha256':sha(stderr),'bytes':len(stderr)},'fixture_only':read(input_path)['fixture_only'],'actual_vms':0,'wall_valid':False,'performance_qualified':False}
 write(out/'process.json',record)
 files=[]
 for p in sorted((out/'result').rglob('*')):
  need(not p.is_symlink(),'output symlink');
  if p.is_file():files.append({'path':p.relative_to(out/'result').as_posix(),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size})
 write(out/'seal.json',{'schema':'controlled-followup-v3.local-seal/v1','arm':arm,'process_sha256':sha((out/'process.json').read_bytes()),'wait_returned':True,'returncode':proc.returncode,'files':files,'tree_sha256':sha(canonical(files)),'scope':'Actual local child termination and file closure, no UID1000/VM/isolation attestation.'})
 native_plan={'experiment_id':'EXP-FIXTURE-89247b','task_id':'TASK-20261030-89247b','approved_by':None}
 trial={'id':arm,'run_id':'RUN-FIXTURE-89247b-'+arm,'parameters':{'fixture_only':record['fixture_only']}}
 write(out/'native-plan.json',native_plan);plan_hash=sha((out/'native-plan.json').read_bytes());environment={'python':sys.version,'platform':sys.platform,'commit':context,'source_sha256':source_map(before),'runtime_lock':None,'runtime_lock_sha256':None};write(out/'environment.json',environment)
 launch={'argv':argv,'check_argv':[sys.executable,str(HERE/'check.py')],'started_at':start,'trial_id':arm,'run_id':trial['run_id'],'authority':{'commit':context},'plan_sha256':plan_hash,'task_id':native_plan['task_id']};write(out/'launch.json',launch);(out/'command.txt').write_text(json.dumps(argv)+'\n')
 write(out/'raw-result.json',{'attack_claimed':False,'status':'completed' if proc.returncode==0 else 'failed','physical_process_sha256':sha((out/'process.json').read_bytes()),'wall_valid':False})
 body={'id':trial['run_id'],'experiment_id':native_plan['experiment_id'],'task_id':native_plan['task_id'],'trial_id':arm,'approved_by':None,'status':'completed' if proc.returncode==0 else 'failed','attack_claimed':False,'code':{'commit':context,'command':argv,'check_command':launch['check_argv'],'command_file':'command.txt','instrument_source_publication_commit':source_publication_commit},'environment':{'file':'environment.json',**environment},'inputs':{'trial_plan':'native-plan.json','plan_sha256':plan_hash,'trial_id':arm,'parameters':trial['parameters']},'timing':{'started_at':start,'finished_at':finish},'result':{'raw_result':'raw-result.json','certificate':{'kind':'none','verified':None}},'metrics':{'physical_invocations':1,'wall_valid':False}}
 write(out/'manifest.yaml',{'run':body})
 return record

def run(repo,contracts,input_path,out,fixture_only=False,admission=None):
 """No entropy/sampling. Nonfixture launches are explicitly unavailable here."""
 verify_dependencies(repo);x=input_check(read(input_path),fixture_only)
 if fixture_only:need(x==read(HERE/'fixtures.json')['input'],'only declared disclosed fixed fixture')
 else:raise ValueError('Nonfixture launch unavailable in source-unit version. Separate frozen production schedule/admission/actual allocated native context and source publication binding are required.')
 out=Path(out);out.mkdir(parents=True,exist_ok=False)
 context=subprocess.check_output(['git','rev-parse','HEAD'],cwd=contracts).decode().strip();pub=None if fixture_only else admission['source_publication_commit'];pins=None if fixture_only else admission['source_sha256']
 records=[launch_arm(a,repo,contracts,Path(input_path).resolve(),out/a,context,pub,pins) for a in ('candidate','baseline')]
 need(len({r['pid'] for r in records})==2,'distinct physical children required')
 write(out/'registry.json',{'schema':'controlled-followup-v3.physical-registry/v1','instance_id':'shared-public-bundle','processes':[{'arm':r['arm'],'pid':r['pid'],'process_sha256':sha((out/r['arm']/'process.json').read_bytes())} for r in records],'input_sha256':sha(Path(input_path).read_bytes()),'physical_invocations':2,'analytical_reference_is_arm':False})
 return {'status':'complete' if all(r['returncode']==0 for r in records) else 'incomplete','physical_invocations':2,'scientific_validity':'not_assessed','wall_valid':False}

def main():
 p=argparse.ArgumentParser();p.add_argument('--repo-root',required=True);p.add_argument('--contracts-root',required=True);p.add_argument('--input',required=True);p.add_argument('--out',required=True);p.add_argument('--fixture-only',action='store_true');a=p.parse_args();print(json.dumps(run(a.repo_root,a.contracts_root,a.input,a.out,a.fixture_only)));return 0
if __name__=='__main__':raise SystemExit(main())
