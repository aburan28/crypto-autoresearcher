#!/usr/bin/env python3
"""Export completed corrective artifacts; no solver or scientific rerun occurs."""
from __future__ import annotations
import argparse,hashlib,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
import artifact_store
import experiment_protocol as ep

def file(path,base,kind='raw'):
 stored=artifact_store.resolve(path)
 if stored is None: raise FileNotFoundError(path)
 return {'path':os.path.relpath(stored,base),'sha256':ep.sha256_file(stored),'bytes':stored.stat().st_size,'kind':kind}

def build(raw_path,protocol_path,out):
 base=out.parent; data=artifact_store.read_json(raw_path); p=ep.read_json(protocol_path)
 receipt=artifact_store.read_json(raw_path.parent/'execution-receipt.json')
 environment=artifact_store.read_json(raw_path.parent/'environment.json')
 launch=artifact_store.read_json(raw_path.parent/'launch.json')
 for k,v in p['extensions']['source_sha256'].items():
  if environment['source_sha256'].get(k)!=v: raise ValueError('source mismatch '+k)
 if data['config_sha256']!=p['extensions']['input_sha256'][p['study_dir']+'/config.json']: raise ValueError('input mismatch')
 binary=ep.sha256_file(Path(launch['argv'][0]).resolve())
 if any(a['instrument']['binary_sha256']!=binary for a in p['arms']): raise ValueError('interpreter mismatch')
 checked={}
 for line in artifact_store.read_text(raw_path.parent/'check.stdout.log').splitlines():
  try:
   item=json.loads(line)
   if isinstance(item,dict) and 'valid' in item and 'packages' in item: checked=item
  except ValueError: pass
 payloads={};files={}
 for name in ('point','algebra'):
  meta=data['packages'][name];logical=raw_path.parent/meta.get('artifact',name+'.json')
  if artifact_store.resolve(logical): files[name]=file(logical,base)
  if meta['status']=='completed':
   b=artifact_store.read_bytes(logical)
   if hashlib.sha256(b).hexdigest()!=meta['sha256']:raise ValueError('payload mismatch '+name)
   payloads[name]=json.loads(b)
 points=payloads.get('point',{}).get('curve_packages',[]);algebra=payloads.get('algebra',{})
 point_rows=[row for c in points for row in c.get('sat_payload',{}).get('rows',[])]
 point_controls=[row for c in points for row in c.get('sat_payload',{}).get('controls',[])]
 alg_cells=algebra.get('cells',[])
 sets={'residual':[r for r in point_rows if not r['instance']['curve_membership']], 'membership':[r for r in point_rows if r['instance']['curve_membership']], 'algebra_degree':[a for c in alg_cells if c['population']=='s3_residual' for a in c['lead3'] if not a['arm'].startswith('aa_')], 'algebra_backdoor':[a for c in alg_cells if c['population']=='s3_residual' for a in c['lead4'] if not a['arm'].startswith('aa_')], 'aa':[a for c in alg_cells for key in ('lead3','lead4') for a in c[key] if a['arm'].startswith('aa_')]+[c['sat_payload']['aa'] for c in points if 'aa' in c.get('sat_payload',{})], 'positive':[c for c in alg_cells if c['population'] in ('affine_unsat','planted_gate_backdoor')]+[c for c in point_controls if c['name']=='positive_sat'], 'negative':[c for c in alg_cells if c['population']=='matched_support_null']+[c for c in point_controls if c['name']=='negative_unsat']}
 needed={'residual':['point'],'membership':['point'],'algebra_degree':['algebra'],'algebra_backdoor':['algebra'],'aa':['point','algebra'],'positive':['point','algebra'],'negative':['point','algebra']}
 e=ep.export_skeleton(p,os.path.relpath(protocol_path,base),'local',p['protocol_id']+'-export')
 e['producer']={'runtime':'native_codex','model':None,'session':'five-leads-corrective-20261029','role':'executor'}
 e['source']={'repo':p['repository'],'commit':environment['commit'],'dirty':None}
 e['arms']=[{'id':a['id'],'role':a['role'],'binary_sha256':binary,'commit':a['instrument']['commit']} for a in p['arms']]
 e['host']['path']=os.path.relpath(raw_path.parent/'environment.json',base);e['host']['sha256']=ep.sha256_file(raw_path.parent/'environment.json')
 for arm in [a['id'] for a in p['arms']]:
  rows=sets[arm];complete=all(n in payloads for n in needed[arm]);valid=complete and all(checked.get('packages',{}).get(n,{}).get('valid') is True for n in needed[arm])
  # Reused original checks are a separate obligation, not counted as new trials.
  valid=valid and receipt.get('status') == 'output_validated' and receipt.get('check_returncode') == 0 and checked.get('valid') is True and all(checked.get('packages',{}).get(n,{}).get('valid') is True for n in ('original_geometry','original_sat'))
  counts={'subcells':len(rows),'verification_pass':int(valid)}
  if arm in ('residual','membership'):
   counts.update(sat=sum(r['learner']['status']=='sat' for r in rows),unsat=sum(r['learner']['status']=='unsat' for r in rows),actual_point_models=sum(r['learner']['status']=='sat' and bool((r.get('lift') or {}).get('point_decomposition')) for r in rows),learned_clauses=sum(len(r['learner']['learned']) for r in rows))
  if arm in ('algebra_degree','algebra_backdoor'):
   counts['algebraic_work_subset']=sum(r.get('metrics',{}).get('all_counted_field_ops',0) for r in rows)
   counts['matrix_entries']=sum(r.get('metrics',{}).get('generated_matrix_entries',0) for r in rows)
   counts['unknown_subcells']=sum(str(r.get('status','')).upper() in ('UNKNOWN','ROW_CAP') for r in rows)
  if arm=='algebra_backdoor':
   counts['unknown_branches']=sum(sum(b['status']=='UNKNOWN' for b in r['branches']) for r in rows)
   counts['strong_backdoors']=sum(r['strong_backdoor'] for r in rows)
  e['runs'].append(ep.run_row(run_id=raw_path.parent.name+'-'+arm,arm=arm,instance_id='0',seed=17,replicate=0,status='succeeded' if valid else ('failed' if complete and checked else 'infra_error'),measurements={'counted':counts,'wall_valid':False},verification={'status':'verified' if valid else ('refuted' if complete and checked else 'not_run'),'verifier':'corrective_driver.py --verify, original artifact checks, complete point oracle and independent algebra certificates'},exclusion={'excluded':not valid,'rule':None if valid else 'Incomplete package or checker failure; no decisive inference.'},artifacts=[files[n] for n in needed[arm] if n in files],started_at=launch.get('started_at'),finished_at=receipt.get('finished_at'),backend_ref=raw_path.parent.name,isolation={'tier':'none','contended':None,'blockers':['No timed comparison.']}))
 e['flow']=ep.compute_flow(e['runs'])
 for name in ['raw-result.json','manifest.yaml','launch.json','environment.json','execution-receipt.json','check.stdout.log','check.stderr.log']:
  e['files'].append(file(raw_path.parent/name,base))
 e['files']+=list(files.values())
 for cell in alg_cells:e['files'].append(file(raw_path.parent/(cell['id']+'.json'),base))
 for name in p['extensions']['input_sha256']:
  if name.startswith('experiments/EXP-PFIVE-3ca920/runs/'):
   e['files'].append(file(ROOT/name,base,'receipt' if 'receipt' in name else 'raw'))
 e['files'].append(file(protocol_path,base,'protocol'));e['analysis']['script']=file(Path(__file__).resolve(),base,'analysis')
 e['notes']=[{'kind':'observation','by':'executor-analysis','text':'One additional serial native run, seven aggregate arm rows. All78 original algebra fixtures and all-target actual-point SAT are retained. Reverified original geometry/SAT are inputs, not new producer executions.'},{'kind':'observation','by':'executor-analysis','text':'The original native attempt was interrupted before completing algebra. Its receipt and completed geometry/SAT remain immutable. This corrective run adds exact monomial-order lookup, per-cell durability, and an independently corrected source-rank checker with six pre-data integrity regressions. Original algebra fixture scope and producer arithmetic are unchanged. No speed comparison is exported.'},{'kind':'observation','by':'executor-analysis','text':'Algebra arithmetic counts are the declared instrumented subset. UNKNOWN branches remain explicit; one UNKNOWN defeats the corresponding strong-backdoor certificate. Exact point witnesses do not imply an ECDLP attack or intrinsic regularity reduction.'}]
 errors=ep.schema_errors(e,'experiment.export/v1') or ep.lint_export(e,p,base,True)
 if errors:raise ValueError('\n'.join(errors))
 ep.write_once(out,e);print(json.dumps({'export':str(out),'flow':e['flow']},indent=2))

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--raw',required=True,type=Path);a.add_argument('--protocol',required=True,type=Path);a.add_argument('--out',required=True,type=Path);x=a.parse_args();build(x.raw.resolve(),x.protocol.resolve(),x.out.resolve())
