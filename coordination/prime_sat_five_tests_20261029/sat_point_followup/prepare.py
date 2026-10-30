#!/usr/bin/env python3
"""Corrective point-SAT and complete algebra admission; never runs an experiment."""
import argparse,copy,hashlib,importlib.util,json,subprocess,sys
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[3]
BASE='coordination/prime_sat_five_tests_20261029'
COORD=BASE+'/sat_point_followup'
OLD='experiments/EXP-PFIVE-3ca920'; EXP='EXP-PFIVE-e26798'; EX='experiments/'+EXP
HYP='H-PFIVE-6510c2'; DEC='DEC-20261029-7994d5'; EXEC='TASK-20261029-7998da'; SNAP='TASK-20261029-d2ad88'
REVIEW='TASK-20261029-aaf28b'; LEDGER='TASK-20261029-da658d'; RDEC='DEC-20261029-af9601'; RUN='RUN-PFIVE-e793f3'
DRIVER='research/prime_sat_five_tests_20261029/sat/corrective_driver.py'
QUEUE='coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-449a28/dispatch_queue.json'

def read(path): return json.loads((ROOT/path).read_text())
def dump(path,obj,kind='json'):
 p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(obj,indent=2)+'\n' if kind=='json' else yaml.safe_dump(obj,sort_keys=False,width=100))
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def helper():
 path=ROOT/BASE/'prepare_admission.py'; spec=importlib.util.spec_from_file_location('original_admission_helper',path); m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 for k,v in dict(COORD=COORD,EXP=EXP,EX=EX,HYP=HYP,DEC=DEC,EXEC=EXEC,SNAP=SNAP,REVIEW=REVIEW,LEDGER=LEDGER,RDEC=RDEC,RUN=RUN,DRIVER=DRIVER,HANDOFF=f'ledger/handoffs/{EXEC}.yaml').items():setattr(m,k,v)
 native_dump=m.dump
 def scoped_dump(path,obj,kind='json',exclusive=False):
  if path.startswith('ledger/'): path=f'{COORD}/records/'+path
  native_dump(path,obj,kind,exclusive)
 m.dump=scoped_dump
 original_binding=m.binding
 def bound_with_originals():
  sources,inputs=original_binding()
  sys.path.insert(0,str(ROOT/'tools'))
  import artifact_store
  cfg=read(EX+'/config.json')
  for key in ('geometry','sat'):
   stored=artifact_store.resolve(ROOT/cfg['original_artifacts'][key])
   if stored is None: raise SystemExit('missing original '+key)
   relative=str(stored.relative_to(ROOT));inputs[relative]=sha(relative)
  for name in ('raw-result.json','execution-receipt.json'):
   logical=Path(cfg['original_artifacts']['geometry']).parent/name
   stored=artifact_store.resolve(ROOT/logical)
   if stored is None: raise SystemExit('missing original '+name)
   relative=str(stored.relative_to(ROOT));inputs[relative]=sha(relative)
  return sources,inputs
 m.binding=bound_with_originals
 return m

def draft():
 raise SystemExit('The complete corrective draft is already checked in; inspect config/protocol/specification instead of regenerating an obsolete precursor.')

def bind():
 p=read(EX+'/protocol.json')
 if p['freeze']['status']!='draft':raise SystemExit('already frozen')
 m=helper(); sources,inputs=m.binding(); commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 for path,digest in sources.items():
  try: b=subprocess.check_output(['git','show',f'{commit}:{path}'],cwd=ROOT,stderr=subprocess.DEVNULL)
  except subprocess.CalledProcessError:raise SystemExit('uncommitted source '+path)
  if hashlib.sha256(b).hexdigest()!=digest:raise SystemExit('dirty source '+path)
 p['extensions']['source_sha256']=sources;p['extensions']['input_sha256']=inputs;p['extensions']['config']=read(EX+'/config.json')
 for arm in p['arms']:arm['instrument']['flags']={'driver':DRIVER}
 p['analysis_plan']['script']['sha256']=sha(COORD+'/export_results.py')
 for arm in p['arms']:arm['instrument']['commit']=commit
 dump(EX+'/protocol.json',p)
 s=yaml.safe_load((ROOT/EX/'specification.yaml').read_text())['experiment'];s['input_bindings']={'source':[{'path':k,'sha256':v} for k,v in sources.items()],'fixtures':[{'path':k,'sha256':v} for k,v in inputs.items()]};dump(EX+'/specification.yaml',{'experiment':s},'yaml')
 print('Bound committed implementation and fixed inputs; native validate/freeze then bind-frozen.')

def preview():
 m=helper();m.preview()
 q=read(COORD+'/preview/queue.json'); original=read(QUEUE)
 q['tasks'][0]['depends_on']=[]  # Original failed attempt is retained via immutable input hashes, not a false completion dependency.
 q['tasks']=original['tasks']+q['tasks'];q['objective']=original['objective']+' Corrective full algebra completion and all-target point validation after preserved terminal original attempt, serial.'
 dump(COORD+'/preview/queue.json',q)
 plan=read(COORD+'/preview/trial-plan.json');plan['trials'][0]['id']='corrective-completion';cfg=read(EX+'/config.json')
 checkpoints=[f'{pop}-p{prime}-s{digits}-r{target}.json' for prime in cfg['algebra']['primes'] for digits in cfg['algebra']['digits'] for target in cfg['algebra']['targets'] for pop in cfg['algebra']['populations']]
 checkpoints += [f'{kind}-p{prime}.json' for prime in cfg['algebra']['primes'] for kind in ('affine-unsat','gate-backdoor')]
 assert len(checkpoints)==78 and len(set(checkpoints))==78
 plan['trials'][0]['artifacts']=['manifest.yaml','raw-result.json','point.json','algebra.json',*checkpoints]
 dump(COORD+'/preview/trial-plan.json',plan)
 digest=sha(COORD+'/preview/trial-plan.json')
 for task in q['tasks']:
  if task['id']==EXEC:
   task['handoff']['execution']['trial_plan_sha256']=digest
   # The generic reusable builder declared original geometry package filenames.
   task['artifact_paths']=[f'{EX}/runs/{RUN}/{name}' for name in [*m.GENERATED,*plan['trials'][0]['artifacts']]]
   task['handoff']['artifact_paths']=task['artifact_paths'];task['handoff']['deliverables']=task['artifact_paths']
   dump(COORD+'/preview/handoff.yaml',{'handoff':task['handoff']},'yaml')
 dump(COORD+'/preview/queue.json',q)
 print('Prospective additive queue only; no canonical queue mutation. Promote only after original run terminal and snapshot archived.')

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('stage',choices=['draft','bind-source','bind-frozen','preview','promote']);x=a.parse_args()
 if x.stage=='draft':draft()
 elif x.stage=='bind-source':bind()
 elif x.stage=='bind-frozen':helper().bind_frozen()
 elif x.stage=='promote':helper().promote()
 else:preview()
