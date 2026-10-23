#!/usr/bin/env python3
"""Read-only replay of a single schema/accounting correction and refusal controls."""
import copy,hashlib,json,subprocess,sys
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools'))
import validate_ledger as v
fragment=BASE/'run-supersession-registry.fragment.yaml'
entries=v.load_run_supersessions(str(fragment));assert len(entries)==1
key,entry=next(iter(entries.items()));original=Path(entry['superseded_path']);successor=Path(entry['superseding_path'])
ctx=v.Ctx(set());v.check_run_supersessions(ctx,entries);v.check_run(str(original),ctx,entries);assert not ctx.errors,ctx.errors
new=yaml.safe_load(successor.read_text())['run'];receipt=json.loads((original.parent/'execution-receipt.json').read_text())
assert new['status']==receipt['status']=='invalid_output'
assert new['result']['scientific_review_verified'] is False and new['scientific_review_verified'] is False
assert new['result']['output_validated'] is False and new['result']['certificate']['kind']=='none'
assert new['result']['scientific_conclusion'] is None
assert new['result']['producer_returncode']==receipt['returncode']==0
assert new['result']['checker_returncode']==receipt['check_returncode']==0
negative={}
for label in ['altered_original_digest','altered_successor_digest','missing_identity_opt_in','wrong_run_identity']:
 bad=copy.deepcopy(entries)
 if label=='altered_original_digest':bad[key]['superseded_sha256']='0'*64
 elif label=='altered_successor_digest':bad[key]['superseding_sha256']='0'*64
 elif label=='missing_identity_opt_in':bad[key]['superseded_id_null']=None
 else:bad[key]['run_id']='RUN-ECDLP-000000'
 check=v.Ctx(set());v.check_run_supersessions(check,bad)
 assert check.errors,(label,'incorrectly accepted')
 negative[label]={'refused':True,'error_count':len(check.errors)}
code=new['code'];bindings={**code['source_sha256'],**code['input_sha256']}
for path,digest in bindings.items():
 blob=subprocess.check_output(['git','show',f"{code['commit']}:{path}"],cwd=ROOT)
 assert hashlib.sha256(blob).hexdigest()==digest,path
checks=json.loads((BASE/'checks.json').read_text());assert checks['original_bundle_unchanged'] and checks['original_bundle_matches_published_archive']
print(json.dumps({'schema_correction_check':'pass','scope':'one immutable G2 bundle and proposed fragment only','scientific_status_preserved':'invalid_output','scientific_review_verified':False,'execution_source_bindings_verified':len(bindings),'negative_controls':negative,'scientific_trials_launched':0,'writes_performed':0},indent=2,sort_keys=True))
