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
old=yaml.safe_load((original.parent/'manifest.yaml').read_text())
launch=json.loads((original.parent/'launch.json').read_text())
plan=json.loads((ROOT/new['code']['trial_plan']).read_text())
expected=[a.replace('{run_dir}',str(original.parent)) for a in plan['trials'][0]['argv']]
assert launch['argv']==new['code']['command']==expected
assert new['trial_id']==launch['trial_id']==plan['trials'][0]['id']=='full-grid'
assert code['commit']=='aefcb291f54dd1cb1e59487a70c11b910ec28b06'
assert code['producer_observed_repository_head']==old['git_commit']=='74180d9aa1b30d56699152d7a80add600dd4903f'
assert new['environment']['producer_rustc']==old['rustc']
assert new['environment']['producer_gp_version'] is None and old['gp_version'] is None
assert new['result']['independent_points_certified'] is False and new['result']['rank_certified'] is False
raw=json.loads((original.parent/'raw-result.json').read_text());assert len(raw['cells'])==1395
assert new['result']['rank_arm_literals']==sorted({c['rank_arm'] for c in raw['cells']})
assert all(s.startswith('skipped:') for s in new['result']['rank_arm_literals'])
assert not set(code['paths_changed_between_execution_and_producer_head']).intersection(bindings)
checks=json.loads((BASE/'checks.json').read_text());assert checks['original_bundle_unchanged'] and checks['original_bundle_matches_published_archive']
print(json.dumps({'schema_correction_check':'pass','scope':'one immutable G3 bundle and proposed fragment only','scientific_status_preserved':'invalid_output','scientific_review_verified':False,'execution_source_bindings_verified':len(bindings),'original_trial_id_preserved':True,'original_launch_argv_preserved':True,'producer_head_distinguished_from_execution_commit':True,'raw_cells':len(raw['cells']),'rank_arm_skipped':True,'rank_certified':False,'independent_points_certified':False,'negative_controls':negative,'scientific_trials_launched':0,'writes_performed':0},indent=2,sort_keys=True))
