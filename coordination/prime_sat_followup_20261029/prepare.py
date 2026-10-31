#!/usr/bin/env python3
"""Prospective native admission adapter. No scientific execution or git mutation."""
import argparse, hashlib, importlib.util, json, subprocess, sys
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[2]
COORD='coordination/prime_sat_followup_20261029'
IDS=json.loads((ROOT/COORD/'ids.json').read_text())
EXP=IDS['experiment']; EX='experiments/'+EXP
DRIVER='research/prime_sat_followup_20261029/driver.py'
SOURCE='research/prime_sat_followup_20261029'
OLD='research/prime_sat_five_tests_20261029'
GENERATED=['launch.json','execution-receipt.json','command.txt','environment.json','stdout.log','stderr.log','check.stdout.log','check.stderr.log']
ARTIFACTS=['manifest.yaml','raw-result.json','encoding.json','coefficients.json','encoding-cells.jsonl','coefficient-cells.jsonl']
def read(p):return json.loads((ROOT/p).read_text())
def dump(p,v,kind='json'):
 path=ROOT/p;path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(v,indent=2)+'\n' if kind=='json' else yaml.safe_dump(v,sort_keys=False,width=100))
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def binding():
 paths=[str(p.relative_to(ROOT)) for p in sorted((ROOT/SOURCE).rglob('*.py'))]
 paths += [OLD+'/core.py',OLD+'/geometry/geometry.py',OLD+'/sat/solver.py',COORD+'/export_results.py',COORD+'/render_report.py']
 for required in [SOURCE+'/coefficients.py',SOURCE+'/check_coefficients.py',DRIVER]:
  if required not in paths:raise SystemExit('source not ready: '+required)
 return {p:sha(p) for p in sorted(set(paths))},{EX+'/config.json':sha(EX+'/config.json')}
def helper():
 path=ROOT/'coordination/prime_sat_five_tests_20261029/prepare_admission.py'
 sp=importlib.util.spec_from_file_location('native_admission_base',path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 values=dict(COORD=COORD,EXP=EXP,EX=EX,HYP=IDS['hypothesis'],DEC=IDS['approval_decision'],GOAL=IDS['goal'],LANE=IDS['batch'],QUEUE=IDS['queue'],EXEC=IDS['executor'],SNAP=IDS['snapshot'],REVIEW=IDS['reviewer'],LEDGER=IDS['review_archive'],RDEC=IDS['review_decision'],RUN=IDS['run'],SOURCE=SOURCE,DRIVER=DRIVER,HANDOFF='ledger/handoffs/'+IDS['executor']+'.yaml')
 for k,v in values.items():setattr(m,k,v)
 m.binding=binding
 olddump=m.dump
 def scoped_dump(path,obj,kind='json',exclusive=False):
  if path.startswith('ledger/'):path=COORD+'/records/'+path
  olddump(path,obj,kind,exclusive)
 m.dump=scoped_dump
 return m

def bind():
 p=read(EX+'/protocol.json')
 if p['freeze']['status']!='draft':raise SystemExit('frozen protocol cannot be rebound')
 sources,inputs=binding();commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 for path,digest in sources.items():
  try:stored=subprocess.check_output(['git','show',commit+':'+path],cwd=ROOT,stderr=subprocess.DEVNULL)
  except subprocess.CalledProcessError:raise SystemExit('uncommitted source '+path)
  if hashlib.sha256(stored).hexdigest()!=digest:raise SystemExit('dirty source '+path)
 p['extensions'].update(source_sha256=sources,input_sha256=inputs,config=read(EX+'/config.json'))
 p['analysis_plan']['script']['sha256']=sha(COORD+'/export_results.py')
 for arm in p['arms']:arm['instrument']['commit']=commit
 dump(EX+'/protocol.json',p)
 s=yaml.safe_load((ROOT/EX/'specification.yaml').read_text())['experiment'];s['input_bindings']={'source':[{'path':k,'sha256':v} for k,v in sources.items()],'fixtures':[{'path':k,'sha256':v} for k,v in inputs.items()]};dump(EX+'/specification.yaml',{'experiment':s},'yaml')
 print('Bound committed sources and config; validate/freeze then bind-frozen.')

def preview():
 m=helper();m.preview()
 q=read(COORD+'/preview/queue.json');original=read(IDS['queue'])
 if any(t['id']==IDS['executor'] for t in original['tasks']):raise SystemExit('prospective executor already present; do not duplicate')
 q['tasks'][0]['depends_on']=[IDS['design_archive']]
 q['objective']='Equivalent finite point encodings and coefficient-SAT pruning: design/archive precedes one serial frozen scientific run.'
 for task in q['tasks']:
  task['title']=task['title'].replace('five-lead','PNEXT').replace('five exact finite lead packages','two finite follow-up packages').replace('five finite packages','two finite follow-up packages')
  task['handoff']['uncertainty_reduced']='Exact finite equivalence, certified pruning and phase-specific counters; no claim promotion.'
  task['handoff']['objective']=task['handoff']['objective'].replace('five-lead','PNEXT').replace('five-lead','PNEXT')
 plan=read(COORD+'/preview/trial-plan.json');plan['trials'][0]['id']='encoding-and-coefficient-stage1';plan['trials'][0]['artifacts']=ARTIFACTS;dump(COORD+'/preview/trial-plan.json',plan)
 ex=q['tasks'][0];ex['artifact_paths']=[f'{EX}/runs/{IDS["run"]}/{name}' for name in [*GENERATED,*ARTIFACTS]]
 ex['handoff'].update(artifact_paths=ex['artifact_paths'],deliverables=ex['artifact_paths']);ex['handoff']['execution']['trial_plan_sha256']=sha(COORD+'/preview/trial-plan.json');ex['handoff']['objective']='Execute exactly the frozen encoding and coefficient packages with native independent checker; retain every cap and cell.'
 dump(COORD+'/preview/handoff.yaml',{'handoff':ex['handoff']},'yaml')
 q['tasks']=original['tasks']+q['tasks'];q['max_concurrent']=1;dump(COORD+'/preview/queue.json',q)
 for task in q['tasks']:
  if task['id'] in (IDS['snapshot'],IDS['reviewer'],IDS['review_archive']):dump(COORD+'/records/ledger/handoffs/'+task['id']+'.yaml',{'handoff':task['handoff']},'yaml')
 packet=read(COORD+'/preapproval-packet.json');packet['execution_route']['reason']='New implementation needs artifact and census inspection; explicit executor-implementation route, no unlinted runbook.';dump(COORD+'/preapproval-packet.json',packet)
 print('Exact previews prepared; canonical queue untouched. Root must publish design archive and probe before promotion.')

def promote():
 sys.path.insert(0,str(ROOT/'tools'));from experiment_preapproval import assess
 p=read(COORD+'/preapproval-packet.json');result=assess(ROOT,p);dump(COORD+'/preapproval-result.json',result)
 if not result['approvable']:raise SystemExit('Native preapproval refused; canonical experiment remains review_required.')
 # Scope only: root copies these exact accepted bytes to canonical destinations.
 d={'id':IDS['approval_decision'],'date':'2026-10-29','actor':'coordinator','decided_by':'coordinator','decision':'approve_experiment','target_ids':[EXP,IDS['hypothesis'],IDS['executor']],'rationale':'User accepted the selected equivalent-encoding and coefficient-SAT followups. Complete frozen exact finite contract and native prospective packet passed approvable gate. No result or scientific status promotion.','approved_by':'coordinator','user_approval_basis':'Explicit follow-up acceptance and AGENTS standing authorization.','experiment_id':EXP,'protocol_sha256':read(EX+'/protocol.json')['freeze']['protocol_sha256'],'preapproval':result,'knowledge_promotion':{'promoted':[],'not_warranted':'Prospective experiment admission contains no new scientific evidence.'},'constraints':['Exact canonical promotion, archive publication, ready selector, live ownership and checkpoint gates remain mandatory before launch.']}
 dest=COORD+'/records/ledger/decisions/'+IDS['approval_decision']+'.yaml'
 if (ROOT/dest).exists():raise SystemExit('approval already exists; do not overwrite')
 dump(dest,{'coordinator_decision':d},'yaml');print('Approvable exact preview and approval decision prepared; root performs canonical copy/archive/publication.')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('stage',choices=['bind-source','bind-frozen','preview','promote']);x=a.parse_args()
 {'bind-source':bind,'bind-frozen':lambda:helper().bind_frozen(),'preview':preview,'promote':promote}[x.stage]()
