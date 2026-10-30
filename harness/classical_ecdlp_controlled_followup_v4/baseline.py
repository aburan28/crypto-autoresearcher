#!/usr/bin/env python3
"""Unchanged BSGS and streaming, post-termination host checks in a separate child."""
from pathlib import Path
from collections import Counter
import argparse,json,sys,signal,time
sys.path.insert(0,str(Path(__file__).resolve().parent));import driver as d
def local_seal(candidate,host):
 candidate=Path(candidate);p=d.read(candidate/'process.json');s=d.read(candidate/'seal.json')
 d.need(p['arm']=='candidate' and p['operational_complete'] is True and p['returncode']==0 and p['termination_ack']=={'wait_returned':True,'returncode':0},'candidate incomplete; retain partials')
 d.need(s['process_sha256']==d.sha_file(candidate/'process.json') and s['tree_sha256']==d.sha(d.canonical(s['files'])),'candidate seal contradiction')
 root=candidate/'result';actual={q.relative_to(root).as_posix() for q in root.rglob('*') if q.is_file()}
 d.need(actual=={q['path'] for q in s['files']} and len(actual)==len(s['files']),'candidate member closure')
 files={}
 for row in s['files']:
  path=d.safe(root,row['path']);d.need(path.stat().st_size==row['bytes'] and d.sha_file(path)==row['sha256'],'candidate member hash');files[path.name]=path
 d.need(set(files)==set(host.FILES),'exact seven engine files required')
 return host.SealedInput(files,s['tree_sha256'],{'scope':'Verified actual LOCAL process termination and full closed bytes; no remote UID claim','local_seal':s})
def run(repo,input_path,out,candidate,fixture_fault=None):
 dep=d.dependencies(repo);x=d.input_check(d.read(input_path));out=Path(out);out.mkdir(parents=True,exist_ok=False)
 if fixture_fault:
  d.need(x['fixture_only'],'unit fault denied')
  d.write(out/'partial-marker.json',{'fault':fixture_fault,'fixture_only':True})
  if fixture_fault=='nonzero':raise RuntimeError('disclosed fixed baseline failure')
  if fixture_fault=='ignore-term':signal.signal(signal.SIGTERM,signal.SIG_IGN)
  time.sleep(60)
 d.need(x['generation_status']=='complete','generation incomplete')
 adapter=d.module(d.HERE/'cohort_adapter.py','baseline_schedule');wanted=adapter.expected_from_jobs(x['public'],x['plan'])
 sys.path.insert(0,str(dep/'host'));host=d.module(dep/'host/verify.py','verify');ref=d.module(dep/'host/reference.py','reference')
 seal=local_seal(candidate,host);d.need(d.sha_file(input_path)==d.read(Path(candidate)/'process.json')['input']['sha256'],'same public input')
 curves={c['curve_id']:c for c in x['public']['curves']};rows=[];bsgs_vectors=[]
 # Solver phase sees only public E/G/Q/r; no oracle has been constructed yet.
 for c in x['public']['curves']:
  if not c['targets']:continue
  group=host.Group(c['model']);bsgs=ref.BSGS(seal,group,tuple(c['base']))
  for target in c['targets']:
   answer=bsgs.solve(tuple(target['point']));ok=answer['status']=='success' and group.mul(answer['scalar'],tuple(c['base']))==tuple(target['point'])
   d.need(ok,'BSGS public equation failed')
   rows.append({'curve_id':c['curve_id'],'target_id':target['target_id'],'point':target['point'],'answer':answer,'public_equation_verified':ok})
  bsgs_vectors.append({'curve_id':c['curve_id'],'counts':dict(group.counts),'phase':'BSGS solve plus its own public verification only'})
 d.write(out/'bsgs.json',{'status':'complete','rows':rows,'solver_vectors':bsgs_vectors,'input_scope':'Only public E/G/Q/r. No oracle/log/candidate recovered value was passed to BSGS.','full_cost_qualified':False,'wall_valid':False})
 setupids={(j['curve_id'],j['arm_id']) for j in x['plan']['jobs']};singles=[j for j in x['plan']['jobs'] if j['kind']=='single'];traces=[j for j in x['plan']['jobs'] if j['kind']!='single'];observed=dict.fromkeys(wanted,0);setuprows={}
 for row in host.iter_records(seal,'setups.jsonl'):
  key=(row['curve_id'],row['arm_id']);d.need(key in setupids and key not in setuprows and row['arm']==host.ARMS[row['arm_id']],'setup schedule/arm')
  c=curves[row['curve_id']];d.need(row['model']==c['model'] and row['base']==c['base'],'setup input');setuprows[key]=row;observed['setups']+=1
 d.need(set(setuprows)==setupids,'missing setup')
 diagnostics=[];current=None;oracle=None
 def get_oracle(cid):
  nonlocal current,oracle
  if cid!=current:
   if oracle is not None:diagnostics.append({'curve_id':current,'counts':dict(oracle.group.counts),'phase':'independent diagnostic verification, separate from BSGS'})
   c=curves[cid];oracle=host.Oracle(seal,c['model'],c['base']);current=cid
   for (setup_cid,aid),setup in setuprows.items():
    if setup_cid!=cid:continue
    d.need(host.point(setup['prepared_base'],oracle.group.p)==oracle.group.mul(host.ARMS[aid]['base_multiplier'],oracle.base),'prepared base')
    d.need(setup['setup_reason']==host.engine_answer(oracle,None,host.ARMS[aid])['reason'],'setup reason');host.validate_counter_vector(setup['counts'])
  return oracle
 for job,row in __import__('itertools').zip_longest(singles,host.iter_records(seal,'single-points.jsonl')):
  d.need(job is not None and row is not None and row['single_id']==job['id'] and row['curve_id']==job['curve_id'] and row['arm_id']==job['arm_id'],'single schedule')
  o=get_oracle(row['curve_id']);d.need(row['answer']==host.engine_answer(o,host.point(row['point'],o.group.p),host.ARMS[row['arm_id']]),'single answer');host.validate_counter_vector(row['counts']);observed['singles']+=1
 cell_iter=iter(host.iter_records(seal,'decoder-cells.jsonl'));intent_iter=iter(host.iter_records(seal,'attempt-intents.jsonl'));analytical=[];statuses=Counter()
 for job,row in __import__('itertools').zip_longest(traces,host.iter_records(seal,'traces.jsonl')):
  d.need(job is not None and row is not None and row['trace_id']==job['id'] and row['curve_id']==job['curve_id'] and row['arm_id']==job['arm_id'],'trace schedule')
  intent=next(intent_iter,None);d.need(intent is not None and all(intent[k]==row[k] for k in intent if k!='schema'),'intent/trace')
  paired=job['kind']=='confirmation-trace';d.need((row['incremental'] is not None)==paired,'paired schedule')
  if paired:
   target=next(t['point'] for t in curves[row['curve_id']]['targets'] if t['target_id']==job['target_id']);d.need(row['target']==target and row['target_id']==job['target_id'],'public target binding')
  o=get_oracle(row['curve_id']);bits,_=host.check_engine_trace(o,host.ARMS[row['arm_id']],row)
  if paired:
   for radius,cap in host.CELLS:
    cell=next(cell_iter,None);d.need(cell is not None and (cell['radius'],cell['erasure_cap'])==(radius,cap),'cell order')
    host.check_engine_cell(o,row,bits,cell);observed['cells']+=1;statuses[cell['status']]+=1
    analytical.append({'cell_id':cell['cell_id'],'M':cell['M'],'conditional_fraction':[min(cell['M'],o.group.r-1),o.group.r-1],'physical_invocations':0})
  observed['traces']+=1;observed['intents']+=1
 d.need(next(intent_iter,None) is None and next(cell_iter,None) is None,'extra raw records')
 if oracle is not None:diagnostics.append({'curve_id':current,'counts':dict(oracle.group.counts),'phase':'independent diagnostic verification, separate from BSGS'})
 summary=d.read(seal.files['engine-summary.json']);completion=d.read(seal.files['engine-completion.json'])
 d.need(observed==wanted==summary['expected']==summary['observed'] and summary['status']==completion['status']=='complete' and not summary['errors'],'complete exact workload')
 d.need(summary['provenance']==completion['provenance']==x['provenance'],'source/input provenance')
 for name,obj in completion['files'].items():
  d.need(name in seal.files and obj['bytes']==seal.files[name].stat().st_size and obj['sha256']==d.sha_file(seal.files[name]),'completion byte binding')
 for name,kind in {'setups.jsonl':'setups','single-points.jsonl':'singles','traces.jsonl':'traces','attempt-intents.jsonl':'intents','decoder-cells.jsonl':'cells'}.items():d.need(completion['files'][name]['records']==observed[kind],'completion record counts')
 d.write(out/'verification.json',{'status':'complete','observed':observed,'diagnostic_vectors':diagnostics,'decoder_statuses':dict(statuses),'primitive_counter_replay_qualified':False,'wall_valid':False})
 d.write(out/'analytical-reference.json',{'kind':'analytical_data_not_a_physical_arm','rows':analytical,'wall_valid':False})
 return {'status':'complete','targets':len(rows),'observed':observed,'wall_valid':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--repo-root',required=True);p.add_argument('--input',required=True);p.add_argument('--out',required=True);p.add_argument('--candidate',required=True);p.add_argument('--fixture-fault');a=p.parse_args();print(json.dumps(run(a.repo_root,a.input,a.out,a.candidate,a.fixture_fault)))

