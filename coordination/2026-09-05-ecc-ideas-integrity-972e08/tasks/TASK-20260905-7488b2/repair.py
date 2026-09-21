#!/usr/bin/env python3
"""Mechanical, write-once schema completion from committed historical inputs.

This script executes no experiment or arithmetic verifier. Run once from repo
root by the Coordinator after authority is committed. --check only validates
products; --preflight checks frozen inputs without writing successors.
"""
from pathlib import Path
import argparse,copy,hashlib,json,subprocess
import yaml

ROOT=Path.cwd()
TASK='TASK-20260905-7488b2'
DEC='DEC-20260905-cfdc8d'
BASE='coordination/2026-09-05-ecc-ideas-integrity-972e08'
MIRROR='ledger/corrections/schema-supersessions/20260905'
SOURCES=[
 'ledger/hypotheses/H-CRYPTO-21e529.yaml',
 'ledger/hypotheses/H-CRYPTO-7dd003.yaml',
 'ledger/handoffs/TASK-20260831-52f3df.yaml',
 'ledger/handoffs/TASK-20260904-a897dc.yaml',
 'ledger/handoffs/TASK-20260904-c616c0.yaml']
PLANS={SOURCES[3]:'ledger/handoffs/TASK-20260904-410404.yaml',
       SOURCES[4]:'ledger/handoffs/TASK-20260904-4f5322.yaml'}
BUDGET='experiments/EXP-MONO-cb905d/specification.yaml'
SNAPSHOT='75794de66e63daef44880da6dc7d9f6e838c6fac'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
class StrictLoader(yaml.SafeLoader):
 pass

def strict_mapping(loader,node,deep=False):
 out={}
 for key_node,value_node in node.value:
  key=loader.construct_object(key_node,deep=deep)
  if key in out:raise ValueError(f'duplicate YAML key {key!r} at line {key_node.start_mark.line+1}')
  out[key]=loader.construct_object(value_node,deep=deep)
 return out
StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,strict_mapping)
def parse(text):return yaml.load(text,Loader=StrictLoader)
def read(p):return parse(Path(p).read_text())
def committed(p):
 data=subprocess.check_output(['git','show','HEAD:'+str(p)])
 assert data==Path(p).read_bytes(),f'uncommitted source: {p}'
 return hashlib.sha256(data).hexdigest()
def write_new(p,data):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 serialized=yaml.safe_dump(data,sort_keys=False,width=100,allow_unicode=True)
 assert parse(serialized)==data,f'strict serialization mismatch: {p}'
 with p.open('x') as f:f.write(serialized)
def mirror(p):return MIRROR+'/'+p.removesuffix('.yaml').replace('/','__')+'.v2.yaml'
def fields_changed(a,b,path=''):
 if type(a) is not type(b):return [path]
 if isinstance(a,dict):
  out=[]
  for k in sorted(a.keys()|b.keys()):
   q=path+'/'+str(k)
   out+=([q] if k not in a or k not in b else fields_changed(a[k],b[k],q))
  return out
 if isinstance(a,list):
  if len(a)!=len(b):return [path]
  return sum((fields_changed(x,y,path+'/'+str(i)) for i,(x,y) in enumerate(zip(a,b))),[])
 return [] if a==b else [path]
def aggregate(raw):
 parts=[]
 for name in ('member_records','null_records'):
  for row in raw[name]:parts.append((name,row['status'],(row.get('certificate') or {}).get('verified')))
 for row in (raw.get('tail_check_1_rerun') or {}).get('rerun_16_seeds',[]):
  parts.append(('tail_check_1_rerun.rerun_16_seeds',row['status'],row.get('certificate_verified')))
 counts={'main_verified':0,'tail_verified':0,'censored':0}
 for name,status,flag in parts:
  if status=='solved':
   assert flag is True,(name,status,flag)
   counts['tail_verified' if name.startswith('tail') else 'main_verified']+=1
  else:
   assert status=='censored' and flag is None,(name,status,flag)
   counts['censored']+=1
 counts['verified']=counts['main_verified']+counts['tail_verified']
 assert counts['verified']>0
 return counts

def main():
 ap=argparse.ArgumentParser();m=ap.add_mutually_exclusive_group();m.add_argument('--check',action='store_true');m.add_argument('--preflight',action='store_true');args=ap.parse_args()
 protocol=read(Path(BASE)/'protocol.json')
 authority=['ledger/decisions/'+DEC+'.yaml','ledger/handoffs/'+TASK+'.yaml',BASE+'/protocol.json']
 for p in authority:committed(p)
 assert protocol['approved_by']=='coordinator' and protocol['approved_by_decision']==DEC
 for rule in protocol['ledger_corrections']+protocol['run_corrections']:
  assert sha(rule['source_path'])==rule['source_sha256']
  if not args.check:assert not Path(rule['target_path']).exists()
  if 'raw_path' in rule:assert sha(rule['raw_path'])==rule['raw_sha256']
  op=rule.get('operation',{})
  if 'copy_from' in op:assert sha(op['copy_from'])==op['source_sha256']
  if 'raw_path' in rule:
   actual=aggregate(json.loads(Path(rule['raw_path']).read_text()))
   frozen=rule['counts']
   assert actual=={'main_verified':frozen['main_solved_verified_true'],
    'tail_verified':frozen['tail_solved_verified_true'],'verified':frozen['all_solved_verified_true'],
    'censored':frozen['censored_unverified']},(rule['id'],actual,frozen)
   run=read(rule['source_path'])['run']
   assert run['status']==rule['preserved_status']
   assert run['result']['valid'] is rule['preserved_result_valid']
   assert run['result']['certificate']['verified'] is None
 for registry in protocol['registry_operations']:
  base_bytes=subprocess.check_output(['git','show',protocol['source_commit']+':'+registry])
  parse(base_bytes.decode())
  if not args.check:assert Path(registry).read_bytes()==base_bytes,'registry drift: '+registry
 if args.preflight:
  print('PASS: authority, frozen hashes, strict YAML, exact main/tail/solved/censored totals and unchanged statuses match; no successors written')
  return
 summary={'task_id':TASK,'decision_id':DEC,'arithmetic_reverified':False,'experiments_run':0,'changes':[],
 'source_commit':protocol['source_commit'],'protocol_sha256':sha(Path(BASE)/'protocol.json'),
 'implementation_script_sha256':sha(__file__),'protocol_deviations':[],
 'execution_role':'coordinator control plane; executor prepared script only'}
 entries=[]
 for source in SOURCES:
  prior_hash=committed(source);d=read(source);root=next(iter(d));b=d[root]
  detail={'scope':'Schema-only correction; historical statements and status unchanged.',
          'recorded_at':'2026-09-05','task_id':TASK,'authorized_by':DEC,
          'prior_path':source,'prior_sha256':prior_hash,'new_evidence_or_execution':False}
  if source in SOURCES[:2]:
   for ingredient in b['structural_ingredients']:
    if ingredient.get('provenance')=='internal' and not ingredient.get('verified_by'):
     ingredient['provenance']='recalled'
   detail['operation']='Classify explicitly unread citations as recalled; do not claim source verification.'
  elif source==SOURCES[2]:
   budget_doc=read(BUDGET);spec=budget_doc.get('experiment',budget_doc)
   b['budget']=copy.deepcopy(spec['budget'])
   detail.update(operation='Materialize the budget already bound by the predecessor constraints.',
                 source_path=BUDGET,source_sha256=committed(BUDGET),source_field='experiment.budget')
  else:
   plan=PLANS[source]
   detail.update(operation='Materialize the pre-existing review plan named by the predecessor.',
                 original_review_plan_pointer=b['review_plan'],source_path=plan,
                 source_sha256=committed(plan),source_field='handoff.review_plan')
   b['review_plan']=copy.deepcopy(read(plan)['handoff']['review_plan'])
  b['schema_supersession']=detail
  dest=mirror(source)
  rule=next(r for r in protocol['ledger_corrections'] if r['source_path']==source)
  assert dest==rule['target_path']
  operation=rule['operation']
  allowed={('/'+root+'/schema_supersession')}
  if 'indices' in operation:
   allowed.update('/hypothesis/structural_ingredients/'+str(i)+'/provenance' for i in operation['indices'])
  else:allowed.add('/'+operation['path'].replace('.','/'))
  deltas=fields_changed(read(source),d)
  assert set(deltas)==allowed,(source,deltas,allowed)
  if not args.check:write_new(dest,d)
  assert read(dest)==d,dest
  entries.append({'kind':'ledger','superseded_path':source,'superseded_sha256':prior_hash,
   'superseding_path':dest,'superseding_sha256':sha(dest),'defect':detail['operation'],
   'registered':'2026-09-05'})
  summary['changes'].append({'source':source,'successor':dest,'source_sha256':prior_hash,
   'successor_sha256':sha(dest),'changed_fields':fields_changed(read(source),d)})
 runs=[]
 expected={'20bit-A':(380,11),'20bit-B':(382,9),'24bit-A':(1027,28),'24bit-B':(1044,27)}
 for suffix,(solved,censored) in expected.items():
  run='RUN-ISOU-'+suffix;folder='experiments/EXP-ISOU-2ac81f/runs/'+run
  source=folder+'/manifest.yaml';raw_path=folder+'/raw-result.json';dest=folder+'/manifest_v2.yaml'
  prior_hash=committed(source);raw_hash=committed(raw_path)
  # The existing snapshot must bind the identical original artifacts.
  for p,h in ((source,prior_hash),(raw_path,raw_hash)):
   assert hashlib.sha256(subprocess.check_output(['git','show',SNAPSHOT+':'+p])).hexdigest()==h
  original=read(source);d=copy.deepcopy(original);b=d['run']
  counts=aggregate(json.loads(Path(raw_path).read_text()))
  assert (counts['verified'],counts['censored'])==(solved,censored)
  b['result']['certificate'].update(verified=True,verification_basis='archived_verifier_outcomes',
   verification_scope='Every solved row in member_records, null_records, and any tail_check_1_rerun.rerun_16_seeds has an archived verification flag equal to true. Censored rows are excluded and assert no solve.',
   raw_result_path=raw_path,raw_result_sha256=raw_hash,
   historical_verified_outcomes=counts['verified'],censored_outcomes_without_certificate=counts['censored'],
   arithmetic_reverified_during_correction=False)
  b['supersedes']={'prior_manifest_path':source,'prior_manifest_sha256':prior_hash,
   'prior_manifest_snapshot_commit':SNAPSHOT,'supersession_kind':'certificate_summary_completion',
   'correction_task_id':TASK,'authorized_by':DEC,'scope':'Summarizes archived verification outcomes only. No arithmetic was rerun, no experiment executed, and no scientific or validity status changed. Historical first-attempt deletion/reuse remains an unresolved integrity limitation, and invalid_measurement control failures remain invalid.'}
  allowed={'/run/supersedes','/run/result/certificate/verified'}
  added_certificate_fields={'verification_basis','verification_scope','raw_result_path',
   'raw_result_sha256','historical_verified_outcomes','censored_outcomes_without_certificate',
   'arithmetic_reverified_during_correction'}
  allowed.update('/run/result/certificate/'+key for key in added_certificate_fields)
  deltas=fields_changed(original,d)
  assert set(deltas)==allowed,(source,deltas,allowed)
  if not args.check:write_new(dest,d)
  assert read(dest)==d
  assert b['status']==original['run']['status'] and b['result']['valid']==original['run']['result']['valid']
  runs.append({'run_id':run,'superseded_path':source,'superseded_sha256':prior_hash,
   'superseding_path':dest,'superseding_sha256':sha(dest),'registered':'2026-09-05',
   'supersession_kind':'certificate_summary_completion',
   'defect':'The producer unconditionally wrote a null summary although all archived solved-row verification outcomes are true. Summary only; arithmetic not reverified; original validity unchanged.'})
  summary['changes'].append({'source':source,'successor':dest,'source_sha256':prior_hash,
   'successor_sha256':sha(dest),'raw_result_sha256':raw_hash,'counts':counts,
   'preserved_status':b['status'],'preserved_result_valid':b['result']['valid'],
   'changed_fields':fields_changed(original,d)})
 for registry,new_entries in [('tools/schema_supersession_registry.yaml',entries),('tools/run_supersession_registry.yaml',runs)]:
  old=read(registry)
  baseline=subprocess.check_output(['git','show',protocol['source_commit']+':'+registry])
  suffix=yaml.safe_dump(new_entries,sort_keys=False,width=100).encode()
  intended=baseline+suffix
  assert parse(intended.decode())['records']==parse(baseline.decode())['records']+new_entries
  if args.check:
   assert Path(registry).read_bytes()==intended,'registry prefix or entries differ: '+registry
   for e in new_entries:assert e in old['records']
  else:
   committed(registry)
   oldpaths={e['superseded_path'] for e in old['records']}
   assert all(e['superseded_path'] not in oldpaths for e in new_entries)
   with Path(registry).open('ab') as f:f.write(suffix)
   assert Path(registry).read_bytes()==intended
   assert read(registry)['records']==old['records']+new_entries
 for rule in protocol['ledger_corrections']+protocol['run_corrections']:
  assert sha(rule['source_path'])==rule['source_sha256']
  if 'raw_path' in rule:assert sha(rule['raw_path'])==rule['raw_sha256']
  operation=rule.get('operation',{})
  if 'copy_from' in operation:assert sha(operation['copy_from'])==operation['source_sha256']
 report=Path(BASE)/'tasks'/TASK/'report.json'
 if args.check:
  assert json.loads(report.read_text())==summary
  print('PASS: nine deterministic successors, original bytes, source bindings, counts and registry entries match')
 else:
  with report.open('x') as f:f.write(json.dumps(summary,indent=2)+'\n')
  print(json.dumps({'successors':len(summary['changes']),'experiments_run':0,'arithmetic_reverified':False}))
if __name__=='__main__':main()
