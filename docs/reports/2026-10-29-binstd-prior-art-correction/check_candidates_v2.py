"""Check exact source bindings, metadata-only edits, and real prior-art rules."""
from pathlib import Path
from copy import deepcopy
import hashlib,importlib.util,json,subprocess,sys
import yaml
P=Path(__file__).resolve().parent
ROOT=P.parents[2]
inputs=json.loads((P/'sources.json').read_text());candidates=json.loads((P/'candidates-v2.json').read_text())
sys.path.insert(0,str(ROOT))
base=inputs['source_commit'];records={r['path']:r for r in inputs['records']}
def raw(path):return subprocess.check_output(['git','-C',str(ROOT),'show',base+':'+path])
def equal_except_attribution(old,new):
 a=deepcopy(old);b=deepcopy(new);a['idea'].pop('prior_art',None);b['idea'].pop('prior_art',None);return a==b
for path,r in records.items():
 assert hashlib.sha256(r['text'].encode()).hexdigest()==r['sha256']
 assert raw(path)==r['text'].encode(),path
assert hashlib.sha256(raw('tools/schema_supersession_registry.yaml')).hexdigest()==inputs['registry_sha256']
verifier=ROOT/'tools/validate_ledger.py';assert verifier.read_bytes()==raw('tools/validate_ledger.py')
spec=importlib.util.spec_from_file_location('checked_validate_ledger',verifier);v=importlib.util.module_from_spec(spec);sys.modules[spec.name]=v;spec.loader.exec_module(v)
def errors(doc,path):
 ctx=v.Ctx(set());v.check_prior_art(str(ROOT/path),doc['idea'],ctx);return ctx.errors
results=[];controls=[]
for item in candidates['records']:
 old=yaml.safe_load(records[item['effective_path']]['text']);data=(P/item['candidate']).read_bytes();assert hashlib.sha256(data).hexdigest()==item['candidate_sha256'];new=yaml.safe_load(data)
 assert equal_except_attribution(old,new),item['id']
 prior=new['idea']['prior_art'];review=prior['retrospective_review'];assert review['read_on']=='2026-10-29' and review['kind']=='retrospective_repository_card_comparison'
 if old['idea'].get('prior_art'):
  expected=deepcopy(old['idea']['prior_art']);internal=[x for x in expected['nearest'] if x['ref'].startswith('IDEA-')];expected['nearest']=[x for x in expected['nearest'] if not x['ref'].startswith('IDEA-')]
  if item['id'].endswith('4f41d0'):
   row=next(r for r in expected['nearest'] if r['ref']=='KR-IC-5765d2');row['provenance']='kb';row['delta']='The committed card concerns SAT and XOR-aware solvers for binary point decomposition. This proposal changes rank-diverse catalogs, seeds and admission floors; it does not establish a new solver method or an end-to-end cost improvement. This comparison is retrospective, dated2026-10-29.'
  actual=deepcopy(prior);assert actual.pop('internal_lineage')==internal;actual.pop('retrospective_review');assert actual==expected
 before=errors(old,item['original_path']);after=errors(new,item['original_path']);assert len(before)==1,(item['id'],before);assert not after,(item['id'],after)
 results.append({'id':item['id'],'before':before,'after':after,'non_attribution_fields_equal':True})
 bad=deepcopy(new);bad['idea']['claim']='UNAUTHORIZED SCIENTIFIC CHANGE';assert not equal_except_attribution(old,bad);controls.append({'id':item['id'],'control':'claim mutation detected','passed':True})
 bad=deepcopy(new);bad['idea']['prior_art']['nearest'][0]['ref']='IDEA-20261003-f20e41';assert errors(bad,item['original_path']);controls.append({'id':item['id'],'control':'internal idea still rejected as typed nearest reference','passed':True})
 bad=deepcopy(new);bad['idea'].pop('prior_art');assert errors(bad,item['original_path']);controls.append({'id':item['id'],'control':'missing prior-art block still rejected','passed':True})
 # Nothing was applied to either ledger or registry, including prior v2 bytes.
 assert raw(item['original_path'])==records[item['original_path']]['text'].encode()
 assert raw(item['effective_path'])==records[item['effective_path']]['text'].encode()
result={'status':'candidate_checks_passed_not_applied','source_commit':base,'verifier_sha256':hashlib.sha256(verifier.read_bytes()).hexdigest(),'source_records_hash_verified':len(records),'candidate_records':4,'prior_art_errors_before':4,'prior_art_errors_after':0,'results':results,'controls':controls,'full_ledger_validation':'not_run; targeted attribution check only','registry_validation':'not_applied; routing and full-corpus gates remain required','execution_or_scientific_validation':False}
if len(sys.argv)!=2:raise SystemExit('usage: check_candidates.py FRESH_OUTPUT_JSON')
with Path(sys.argv[1]).open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('results','controls')},indent=2));print('Negative controls:',len(controls),'passed')
