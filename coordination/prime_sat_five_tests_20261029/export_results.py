#!/usr/bin/env python3
"""Export already-produced five-lead artifacts; never executes a scientific arm.

Package completion is bookkeeping, not acceptance of a mechanism or performance
hypothesis. Missing packages yield explicit not-completed rows. No absent metric
is silently replaced by zero; per-lead model counts retain the raw cell domain.
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import artifact_store
import experiment_protocol as ep

def physical_entry(logical:Path, base:Path, kind='raw'):
 stored=artifact_store.resolve(logical)
 if stored is None: return None
 return {'path':os.path.relpath(stored,base),'sha256':ep.sha256_file(stored),'bytes':stored.stat().st_size,'kind':kind}

def checked(check):
 return isinstance(check,dict) and check.get('valid') is True

def cells_for(arm,payloads):
 geo=payloads.get('geometry',{}); alg=payloads.get('algebra',{}); sat=payloads.get('sat',{})
 if arm=='lead1': return geo.get('graeffe',{}).get('cells',[])
 if arm=='lead5': return geo.get('saturation',{}).get('cells',[])
 if arm=='lead2': return sat.get('rows',[])
 if arm in ('lead3','lead4'):
  return [a for c in alg.get('cells',[]) if c['population']=='s3_residual' for a in c[arm] if not a['arm'].startswith('aa_')]
 if arm=='aa_replay':
  out=[a for c in alg.get('cells',[]) for group in ['lead3','lead4'] for a in c[group] if a['arm'].startswith('aa_')]
  if 'aa' in sat: out.append(sat['aa'])
  return out
 if arm=='positive_controls':
  return [c for c in alg.get('cells',[]) if c['population'] in ('affine_unsat','planted_gate_backdoor')]+[c for c in sat.get('controls',[]) if c['name']=='positive_sat']
 if arm=='negative_controls':
  return [c for c in alg.get('cells',[]) if c['population']=='matched_support_null']+[c for c in sat.get('controls',[]) if c['name']=='negative_unsat']+[c for c in geo.get('graeffe',{}).get('cells',[]) if c['kind']=='empty_squarefree_control']
 raise ValueError(arm)

def exact_metrics(arm,cells,valid):
 # Values aggregate only explicitly emitted metrics for the selected raw records.
 out={'subcells':len(cells),'verification_pass':int(valid)}
 unknown=sum(str(c.get('status','')).lower() in ('unknown','censored','selector_cap','row_cap') for c in cells)
 if arm=='lead4': unknown=sum(sum(str(b.get('status','')).lower()=='unknown' for b in c.get('branches',[])) for c in cells)
 out['unknown_subcells']=unknown
 if arm=='lead2':
  out['model_count']=sum(c['oracle_solution_count'] for c in cells)
  out['oracle_assignments']=sum(c['oracle_assignments'] for c in cells)
  out['learned_clauses']=sum(len(c['learner']['learned']) for c in cells)
  out['early_clauses']=sum(sum(len(x.get('prefix',[]))<2*c['instance']['s'] for x in c['learner']['learned']) for c in cells)
 if arm in ('lead3','lead4'):
  out['algebraic_work']=sum(c.get('metrics',{}).get('all_counted_field_ops',0) for c in cells)
  out['matrix_entries']=sum(c.get('metrics',{}).get('generated_matrix_entries',0) for c in cells)
  complete=[c for c in cells if c.get('models') is not None]
  if complete: out['model_count']=sum(len(c['models']) for c in complete)
  out['model_count_complete_subcells']=len(complete)
  if arm=='lead4': out['strong_backdoors']=sum(c.get('strong_backdoor') is True for c in cells)
 if arm in ('lead1','lead5'):
  out['ineligible_subcells']=sum(c.get('status')!='complete' for c in cells)
  # Geometry intentionally does not supply a complete field-operation count.
  if arm=='lead1':
   inv=[c for c in cells if c.get('kind')=='inverse' and 'inverse' in c]
   out['inverse_cells_executed']=len(inv)
   out['inverse_predicate_agreements']=sum(sum(v is True for v in c.get('inverse_oracle_agreement',{}).values()) for c in inv)
 return out

def build(raw_path,protocol_path,out):
 base=out.parent; raw=artifact_store.read_json(raw_path); p=ep.read_json(protocol_path)
 problems=ep.schema_errors(p,'experiment.protocol/v1') or ep.lint_protocol(p,protocol_path.parent)
 if problems or p['freeze']['status']!='frozen': raise ValueError('invalid/unfrozen protocol: '+str(problems))
 env_path=raw_path.parent/'environment.json'; launch_path=raw_path.parent/'launch.json'
 if not env_path.exists() or not launch_path.exists(): raise ValueError('native launch/environment provenance is required')
 env=json.loads(env_path.read_text()); launch=json.loads(launch_path.read_text())
 for path,digest in p['extensions']['source_sha256'].items():
  if env.get('source_sha256',{}).get(path)!=digest: raise ValueError('observed source binding mismatch: '+path)
 python_path=Path(launch['argv'][0]).resolve(); binary_sha=ep.sha256_file(python_path)
 if any(a['instrument']['binary_sha256']!=binary_sha for a in p['arms']): raise ValueError('launched interpreter digest differs from protocol')
 if raw['config_sha256']!=p['extensions']['input_sha256'][f"{p['study_dir']}/config.json"]: raise ValueError('observed config differs from protocol')
 checklog=raw_path.parent/'check.stdout.log'; verification={}
 if checklog.exists():
  for line in checklog.read_text().splitlines():
   try:
    obj=json.loads(line)
    if isinstance(obj,dict) and 'packages' in obj and 'valid' in obj: verification=obj
   except ValueError: pass
 payloads={}; entries={}; failures=[]
 for name in ['geometry','sat','algebra']:
  meta=raw.get('packages',{}).get(name,{})
  logical=raw_path.parent/meta.get('artifact',name+'.json')
  entry=physical_entry(logical,base)
  if entry: entries[name]=entry
  if meta.get('status')=='completed':
   data=artifact_store.read_bytes(logical)
   if hashlib.sha256(data).hexdigest()!=meta.get('sha256'): raise ValueError('payload digest mismatch: '+name)
   payloads[name]=json.loads(data)
  else: failures.append(name)
 e=ep.export_skeleton(p,os.path.relpath(protocol_path,base),'local',p['protocol_id']+'-export')
 e['producer']={'runtime':'native_codex','model':None,'session':'five-leads-20261029','role':'executor'}
 e['source']={'repo':p['repository'],'commit':env.get('commit'),'dirty':None}
 e['arms']=[{'id':a['id'],'role':a['role'],'binary_sha256':binary_sha,'commit':a['instrument']['commit']} for a in p['arms']]
 e['host']['path']=os.path.relpath(env_path,base); e['host']['sha256']=ep.sha256_file(env_path)
 e['host']['summary']['kernel']=raw.get('environment',{}).get('platform')
 e['host']['summary']['isolation_tier_max']='none'
 needed={'lead1':['geometry'],'lead2':['sat'],'lead3':['algebra'],'lead4':['algebra'],'lead5':['geometry'],'aa_replay':['sat','algebra'],'positive_controls':['sat','algebra'],'negative_controls':['geometry','sat','algebra']}
 receipt_path=raw_path.parent/'execution-receipt.json'; receipt=json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
 for arm in [a['id'] for a in p['arms']]:
  present=all(x in payloads for x in needed[arm]); valid=present and all(checked(verification.get('packages',{}).get(x)) for x in needed[arm])
  vals=cells_for(arm,payloads)
  status='succeeded' if valid else ('failed' if present and verification else 'infra_error')
  row=ep.run_row(run_id=raw_path.parent.name+'-'+arm,arm=arm,instance_id='0',seed=17,replicate=0,status=status,measurements={'counted':exact_metrics(arm,vals,valid),'wall_valid':False},verification={'status':'verified' if valid else ('refuted' if present and verification else 'not_run'),'verifier':'driver.py --verify; package-specific independent polynomial/model checks'},exclusion={'excluded':not valid,'rule':None if valid else 'Missing/incomplete package or checker failure: no decisive inference.'},artifacts=[entries[x] for x in needed[arm] if x in entries],started_at=launch.get('started_at'),finished_at=receipt.get('finished_at'),backend_ref=raw_path.parent.name,isolation={'tier':'none','contended':None,'blockers':['No isolated-clock claim; exact finite computations only.']})
  e['runs'].append(row)
 e['flow']=ep.compute_flow(e['runs'])
 for name in ['raw-result.json','manifest.yaml','launch.json','environment.json','execution-receipt.json','check.stdout.log','check.stderr.log']:
  item=physical_entry(raw_path.parent/name,base,'receipt' if 'receipt' in name else 'raw')
  if item: e['files'].append(item)
 e['files']+=list(entries.values())
 e['files'].append(physical_entry(protocol_path,base,'protocol'))
 e['analysis']['script']=physical_entry(Path(__file__).resolve(),base,'analysis')
 e['notes']=[{'kind':'observation','text':'Eight aggregate package rows summarize one native trial. Completed means package executed and checker returned a result, not that any performance hypothesis was established. Full internal cells, controls, UNKNOWN branches and chart losses remain in raw payloads.'},{'kind':'observation','text':'Metric subcells counts selected raw records; verification_pass is one iff all required package checkers passed; unknown_subcells counts unresolved legal branches for lead4 and unknown/censored records otherwise. Model counts summed over explicitly complete subcells only and carry no yield interpretation. Absent work counters are omitted, not replaced by geometric operation estimates.'},{'kind':'observation','text':'Source launch commit comes from native environment receipt; arm implementation commit is independently pinned by exact source hashes. No model identity or clean-tree state was inferred when absent from provenance.'}]
 for note in e['notes']: note['by']='executor-analysis'
 errors=ep.schema_errors(e,'experiment.export/v1') or ep.lint_export(e,p,base,True)
 if errors: raise ValueError('export refused:\n'+'\n'.join(errors))
 ep.write_once(out,e)
 print(json.dumps({'export':str(out),'flow':e['flow'],'schema_and_protocol_valid':True},indent=2))

if __name__=='__main__':
 a=argparse.ArgumentParser(description=__doc__); a.add_argument('--raw',required=True,type=Path); a.add_argument('--protocol',required=True,type=Path); a.add_argument('--out',required=True,type=Path); x=a.parse_args(); build(x.raw.resolve(),x.protocol.resolve(),x.out.resolve())
