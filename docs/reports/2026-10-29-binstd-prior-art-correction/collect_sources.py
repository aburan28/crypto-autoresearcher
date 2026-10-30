"""Collect exact existing source bytes; no ledger or routing writes."""
from pathlib import Path
import hashlib,json,subprocess
import yaml
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
COMMIT='7e45528b293fd42049b1486a03135670ab5ac55c'
REVIEW='a14bc266c05c454361639254feee427b87f849e3'
def blob(commit,path):
 return subprocess.check_output(['git','-C',str(ROOT),'show',commit+':'+path])
old=json.loads(blob(REVIEW,'docs/reports/2026-10-28-proposal-prior-art/sources.json'))
registry=blob(COMMIT,'tools/schema_supersession_registry.yaml')
routes=yaml.safe_load(registry)['records']
ids=['43f871','4f41d0','94078e','c9c6c3']
paths=[x['path'] for x in old['records']]
selected=[]
for suffix in ids:
 path='ledger/proposals/IDEA-20261003-'+suffix+'.yaml'
 route=next((x for x in routes if x['superseded_path']==path),None)
 selected.append({'original_path':path,'route':route,'effective_path':route['superseding_path'] if route else path})
 if route and route['superseding_path'] not in paths:paths.append(route['superseding_path'])
records=[]
for path in paths:
 data=blob(COMMIT,path);digest=hashlib.sha256(data).hexdigest();prior=next((x for x in old['records'] if x['path']==path),None)
 if prior:assert digest==prior['sha256'],path
 records.append({'path':path,'sha256':digest,'git_blob':subprocess.check_output(['git','-C',str(ROOT),'rev-parse',COMMIT+':'+path]).decode().strip(),'text':data.decode(),'matches_prior_review':True if prior else None})
for item in selected:
 if item['route']:
  for k,p in [('superseded_sha256','original_path'),('superseding_sha256','effective_path')]:
   assert item['route'][k]==next(x['sha256'] for x in records if x['path']==item[p])
doc={'schema':'crypto.source_bound_attribution_inputs.v1','source_commit':COMMIT,'prior_review_commit':REVIEW,'prior_review_source':'docs/reports/2026-10-28-proposal-prior-art/sources.json','registry_sha256':hashlib.sha256(registry).hexdigest(),'selected':selected,'records':records,'scope':'Read-only source extraction; no replacement applied. Current reader must distinguish repository-card claims from independent full-text literature verification.'}
with (OUT/'sources.json').open('x') as f:json.dump(doc,f,indent=2,ensure_ascii=False);f.write('\n')
print('Sources',len(records),'bytes',(OUT/'sources.json').stat().st_size)
for item in selected:
 body=yaml.safe_load(next(x['text'] for x in records if x['path']==item['effective_path']))['idea']
 print(json.dumps({'path':item['effective_path'],'id':body['id'],'claim':body.get('claim'),'novelty_status':body.get('novelty_status'),'prior_art':body.get('prior_art'),'citations':body.get('citations')},ensure_ascii=False,indent=2))
