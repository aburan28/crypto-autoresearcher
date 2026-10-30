#!/usr/bin/env python3
"""Write native export from sealed PNEXT artifacts; never invokes scientific code."""
import argparse, hashlib, json, os, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import artifact_store
import experiment_protocol as ep
ENC=('quartic','membership','quadratic','quadratic_aa')
COEFF=('leaf_sat','prefix_univariate_gcd','exhaustive_reference','aa_reverse_prefix')
def ref(path,base,kind='raw'):
 stored=artifact_store.resolve(path)
 if stored is None:raise FileNotFoundError(path)
 return {'path':os.path.relpath(stored,base),'sha256':ep.sha256_file(stored),'bytes':stored.stat().st_size,'kind':kind}
def numeric(obj,prefix=''):
 """Keep primitive names and phases distinct; sum only identical leaf units."""
 out={}
 if isinstance(obj,dict):
  for key,value in obj.items():out.update(numeric(value,prefix+'_'+str(key) if prefix else str(key)))
 elif type(obj) is int:out[prefix]=obj
 return out

def accumulate(total, key, value):
 # Maxima describe reached size/degree; adding them would invent an aggregate.
 if '_max_' in key or '_peak_' in key or key.startswith(('max_', 'peak_')):
  total[key]=max(total.get(key,value),value)
 else:
  total[key]=total.get(key,0)+value

def controls(payload):
 value=payload.get('controls',{})
 if not isinstance(value,dict):raise ValueError('controls must be a named boolean mapping')
 out={}
 for name,item in value.items():
  if isinstance(item,bool):out[name]=item
  elif isinstance(item,dict) and isinstance(item.get('valid'),bool):out[name]=item['valid']
  else:raise ValueError('unrecognized control result '+name)
 return out

def extraction(payloads):
 selected={};counts={}
 for name in ENC:
  rows=[a for c in payloads['encoding']['cells'] for a in c['arms'] if a['arm']==name]
  selected[name]=('encoding',rows)
  counts[name]={'subcells':len(rows),'search_complete':sum(a['search']['status']=='complete' for a in rows),'search_censored':sum(a['search']['status']=='censored' for a in rows),'models_found':sum(len(a['search']['models']) for a in rows),'reference_models':sum(len(c['reference_models']) for c in payloads['encoding']['cells']),'certificate_bytes':sum(a['search']['certificate_bytes'] for a in rows)}
  for cell in payloads['encoding']['cells']:
   for key,n in numeric(cell['reference_cost'],'shared_reference').items():accumulate(counts[name],key,n)
  for a in rows:
   phases={'construction':a['construction_cost'],'search':a['search']['costs'],'verification':a['verification_cost'],'reconstruction':a['reconstruction_cost'],'census':a['census']['costs']}
   for key,n in numeric(phases,'phase').items():accumulate(counts[name],key,n)
 for name in COEFF:
  rows=[c['arms'][name] for c in payloads['coefficients']['cells']];selected[name]=('coefficients',rows)
  counts[name]={'subcells':len(rows),'search_complete':sum(a['status']=='complete' for a in rows),'search_censored':sum(a['status']=='censored' for a in rows),'models_found':sum(len(a['coefficient_models']) for a in rows),'reference_models':sum(len(c['reference']['coefficient_models']) for c in payloads['coefficients']['cells']),'generic_relations':sum(len(a['generic_relations']) for a in rows),'fallback_relations':sum(len(a['fallback']['relations']) for a in rows),'complete_relations':sum(len(a['complete_relations']) for a in rows)}
  for cell in payloads['coefficients']['cells']:
   for key,n in numeric(cell['reference']['costs'],'shared_reference').items():accumulate(counts[name],key,n)
  for a in rows:
   for key,n in numeric(a['costs'],'phase').items():accumulate(counts[name],key,n)
   for key,n in numeric(a.get('search',{}).get('counts',{}),'search_event').items():accumulate(counts[name],key,n)
   for key,n in numeric(a.get('search',{}).get('sat_native',{}),'sat_native').items():accumulate(counts[name],key,n)
 allcontrols={package+':'+key:val for package,payload in payloads.items() for key,val in controls(payload).items()}
 # Explicit labels only, fixed before data; no result-dependent allocation.
 negative=lambda key:any(word in key.lower() for word in ('tamper','corrupt','negative','satisfiable_not_refuted','invalid','no_root','nonroot'))
 for name,want in [('positive_controls',False),('negative_controls',True)]:
  subset={k:v for k,v in allcontrols.items() if negative(k)==want}
  if not subset:raise ValueError('missing '+name)
  selected[name]=('both',subset)
  counts[name]={'subcells':len(subset),'control_pass':sum(subset.values()),'control_fail':sum(not x for x in subset.values()),'search_complete':0,'search_censored':0,'models_found':0}
 return selected,counts

def build(raw_path,protocol_path,out):
 base=out.parent;raw=artifact_store.read_json(raw_path);p=ep.read_json(protocol_path)
 receipt=artifact_store.read_json(raw_path.parent/'execution-receipt.json');env=artifact_store.read_json(raw_path.parent/'environment.json');launch=artifact_store.read_json(raw_path.parent/'launch.json')
 if receipt.get('status')!='output_validated' or receipt.get('returncode')!=0 or receipt.get('check_returncode')!=0:raise ValueError('completed validated native receipt required; partial artifacts must remain explicitly partial')
 for k,v in p['extensions']['source_sha256'].items():
  if env['source_sha256'].get(k)!=v:raise ValueError('source mismatch '+k)
 if raw['config_sha256']!=p['extensions']['input_sha256'][p['study_dir']+'/config.json']:raise ValueError('input mismatch')
 binary=ep.sha256_file(Path(launch['argv'][0]).resolve())
 if any(a['instrument']['binary_sha256']!=binary for a in p['arms']):raise ValueError('interpreter mismatch')
 check={}
 for line in artifact_store.read_text(raw_path.parent/'check.stdout.log').splitlines():
  try:item=json.loads(line)
  except ValueError:continue
  if isinstance(item,dict) and 'valid' in item and 'packages' in item:check=item
 if check.get('valid') is not True or any(check.get('packages',{}).get(n,{}).get('valid') is not True for n in ('encoding','coefficients')):raise ValueError('missing independent package validation')
 payloads={};files={}
 for name in ('encoding','coefficients'):
  meta=raw['packages'][name]
  if meta['status']!='completed':raise ValueError('incomplete '+name)
  logical=raw_path.parent/meta['artifact'];b=artifact_store.read_bytes(logical)
  if hashlib.sha256(b).hexdigest()!=meta['sha256']:raise ValueError('package digest mismatch '+name)
  payloads[name]=json.loads(b);files[name]=ref(logical,base)
  if payloads[name]['config']!=raw['config'][name]:raise ValueError('package config mismatch')
 sets,counts=extraction(payloads)
 if set(sets)!={a['id'] for a in p['arms']}:raise ValueError('arm mismatch')
 e=ep.export_skeleton(p,os.path.relpath(protocol_path,base),'local',p['protocol_id']+'-export')
 e['producer']={'runtime':'native_codex','model':None,'session':'prime-sat-followup-20261029','role':'executor'};e['source']={'repo':p['repository'],'commit':env['commit'],'dirty':None}
 e['arms']=[{'id':a['id'],'role':a['role'],'binary_sha256':binary,'commit':a['instrument']['commit']} for a in p['arms']]
 environment_file=ref(raw_path.parent/'environment.json',base);e['host']['path']=environment_file['path'];e['host']['sha256']=environment_file['sha256']
 for a in p['arms']:
  name=a['id'];package,rows=sets[name];counts[name]['verification_pass']=1
  e['runs'].append(ep.run_row(run_id=raw_path.parent.name+'-'+name,arm=name,instance_id='0',seed=17,replicate=0,status='succeeded',measurements={'counted':counts[name],'wall_valid':False},verification={'status':'verified','verifier':'Frozen native driver independent complete model/certificate/chart checker; search censoring remains separate'},exclusion={'excluded':False,'rule':None},artifacts=list(files.values()) if package=='both' else [files[package]],started_at=launch.get('started_at'),finished_at=receipt.get('finished_at'),backend_ref=raw_path.parent.name,isolation={'tier':'none','contended':None,'blockers':['No timed comparison.']}))
 e['flow']=ep.compute_flow(e['runs']);e['files']=list(files.values())
 for name in ['raw-result.json','manifest.yaml','launch.json','environment.json','execution-receipt.json','check.stdout.log','check.stderr.log','encoding-cells.jsonl','coefficient-cells.jsonl']:e['files'].append(ref(raw_path.parent/name,base))
 e['files'].append(ref(protocol_path,base,'protocol'));e['analysis']['script']=ref(Path(__file__).resolve(),base,'analysis')
 e['notes']=[{'kind':'observation','by':'executor-analysis','text':x} for x in ['Ten aggregate rows retain106 encoding and6coefficient cells. A validated package may contain censored bounded searches; search_complete and search_censored are distinct from exact model equivalence.','Coefficient models, squarefree point relations and coordinate models have different domains and are never pooled. Repeated divisors are outside the coefficient relation completeness claim.','shared_reference counters are computed once per cell, repeated beside each arm for transparency and never added across arms. Counter keys retain phase and primitive units; max/peak keys use maxima, other integer event/arithmetic keys use sums, and missing telemetry remains absent. They cover instrumented work only, not all CPU instructions or end-to-end costs. No timing, intrinsic regularity or attack inference.','Prior public curves/targets and coefficient fixtures were seen before this mechanism comparison; this is exact finite calibration, not held-out performance evidence.']]
 errors=ep.schema_errors(e,'experiment.export/v1') or ep.lint_export(e,p,base,True)
 if errors:raise ValueError('\n'.join(errors))
 ep.write_once(out,e);print(json.dumps({'export':str(out),'flow':e['flow']},indent=2))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--raw',required=True,type=Path);a.add_argument('--protocol',required=True,type=Path);a.add_argument('--out',required=True,type=Path);x=a.parse_args();build(x.raw.resolve(),x.protocol.resolve(),x.out.resolve())
