#!/usr/bin/env python3
"""Prepare an additive, observation-only manifest correction from frozen bytes."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools'))
import validate_ledger as ledger
RUN='RUN-ECDLP-2ac930';EXP='EXP-ECDLP-8cc60d';OLD=ROOT/'experiments'/EXP/'runs'/RUN
ARCHIVE='fba584bdc8540f2f552e4ec86e221f99dd191dc6'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(path,value,kind='json'):
 with path.open('x') as f:f.write(json.dumps(value,indent=2,sort_keys=True)+'\n' if kind=='json' else yaml.safe_dump(value,sort_keys=False,allow_unicode=True))
def readj(name):return json.loads((OLD/name).read_text())
def blob(ref,path):return subprocess.check_output(['git','show',f'{ref}:{path}'],cwd=ROOT)
allocated=subprocess.check_output(['python3','tools/allocate_id.py','--next','correction','--date','20261017'],cwd=ROOT,text=True)
cid=re.search(r'CORR-20261017-[0-9a-f]{6}',allocated).group()
checked=subprocess.run(['python3','tools/allocate_id.py','--check',cid],cwd=ROOT,text=True,capture_output=True)
if checked.returncode:raise ValueError(checked.stdout+checked.stderr)
original_hashes={str(p.relative_to(ROOT)):sha(p) for p in sorted(OLD.iterdir()) if p.is_file()}
archival_agreement={p:hashlib.sha256(blob(ARCHIVE,p)).hexdigest()==h for p,h in original_hashes.items()}
assert all(archival_agreement.values())
flat=yaml.safe_load((OLD/'manifest.yaml').read_text());launch=readj('launch.json');env=readj('environment.json');receipt=readj('execution-receipt.json');raw=readj('raw-result.json');checker=readj('check.stdout.log')
assert receipt['status']=='invalid_output' and receipt['returncode']==receipt['check_returncode']==0
assert launch['run_id']==receipt['run_id']==RUN and raw['experiment_id']==flat['experiment_id']==EXP
assert receipt['scientific_conclusion'] is None
assert env['commit']==flat['git_commit']==launch['authority']['commit']==receipt['authority']['commit']
assert flat['raw_result_sha256']==sha(OLD/'raw-result.json')==receipt['artifact_sha256']['raw-result.json']
assert 'id' not in flat and 'run_id' not in flat
specpath=ROOT/'experiments'/EXP/'specification.yaml';spec=yaml.safe_load(specpath.read_text())['experiment']
assert sha(specpath)==env['specification_sha256']
planpath=ROOT/'experiments'/EXP/'trial-plan.json';plan=json.loads(planpath.read_text());assert sha(planpath)==launch['plan_sha256']==receipt['plan_sha256']
parameters={'parts':['A','B','C','D'],'c':[13,17,19,31],'curves':64,'seeds':[1,2,3],'cap':1000000,'boxes':[20,30,40],'norm_samples':100000,'out':str(OLD)}
manifest={
 'run':{
  'id':RUN,'experiment_id':EXP,'hypothesis_id':raw['hypothesis_id'],'status':'invalid_output',
  'status_note':'Immutable supervisor outcome retained. Producer and checker exited 0; original flat manifest failed the required top-level run schema. This additive metadata correction neither changes the execution receipt nor establishes output_validated.',
  'code':{'commit':env['commit'],'commit_meaning':'execution_source_commit_literal_from_supervisor_launch_environment_receipt_and_producer_manifest','command':launch['argv'],'check_command':launch['check_argv'],'source_sha256':env['source_sha256'],'input_sha256':plan['input_sha256'],'producer_source_sha256':flat['source_sha256'],'trial_plan':str(planpath.relative_to(ROOT)),'trial_plan_sha256':launch['plan_sha256']},
  'environment':{'supervisor_record':env,'producer_python':flat['python'],'producer_platform':flat['platform'],'source':str((OLD/'environment.json').relative_to(ROOT))},
  'inputs':{'parameters':parameters,'controls':spec['controls'],'specification':str(specpath.relative_to(ROOT)),'specification_sha256':env['specification_sha256'],'identity_sources':[str((OLD/'launch.json').relative_to(ROOT)),str((OLD/'execution-receipt.json').relative_to(ROOT))],'identity_note':'Original flat manifest has neither id nor run_id. Identity is explicit in the hash-pinned supervisor launch and receipt and agrees with its immutable run-directory basename.'},
  'timing':{'producer_started_unix':flat['started_unix'],'producer_finished_unix':flat['finished_unix'],'producer_wall_clock_seconds':flat['wall_clock_seconds'],'producer_part_c_seconds':flat['part_c_seconds'],'supervisor_started_at':receipt['started_at'],'supervisor_finished_at':receipt['finished_at'],'accounting_note':'Producer wall time is the original rounded literal and excludes supervisor/checker overhead. Supervisor timestamps delimit that larger scope. Neither is presented as a speedup or attack-cost bound.'},
  'result':{'raw_result':str((OLD/'raw-result.json').relative_to(ROOT)),'raw_result_sha256':sha(OLD/'raw-result.json'),'outcome':None,'certificate':{'kind':'none'},'supervisor_status':'invalid_output','producer_returncode':receipt['returncode'],'checker_returncode':receipt['check_returncode'],'supervisor_detail':receipt['detail'],'scientific_conclusion':None,'scientific_review_verified':False,'output_validated':False,'checker_report_literal':checker,'checker_report_scope':'Existing execution-time checker output only; not an independent evidence-review decision.','outcome_note':'Schema/accounting completion only. The original invalid_output receipt remains authoritative. No attack certificate, complexity claim, measured-bound claim, hypothesis transition, or scientific promotion follows.'},
  'scientific_review_verified':False,'publication_verified':False,
  'publication_note':'The immutable original run bundle was archived at the separately named archive commit. This additive correction has not been committed or published by its preparer. The original receipt published:false is unchanged.',
  'supersedes':{'relation':'additive_schema_completion_only','original_manifest':str((OLD/'manifest.yaml').relative_to(ROOT)),'original_manifest_sha256':sha(OLD/'manifest.yaml'),'correction_id':cid,'preserves_original_receipt_status':True,'scientific_observations_reclassified':False},
  'claim_boundary':'Original observations only; no scalar recovery, deployed-key attack, ECDLP advantage, scientific approval, or validation-status promotion.'
 }
}
newpath=BASE/'RUN-ECDLP-2ac930.manifest.schema-v2.yaml';write(newpath,manifest,'yaml')
provenance={'correction':{'id':cid,'kind':'additive_schema_accounting_completion','status':'prepared_not_published','authority_effect':'none; does not approve an experiment, rerun, certificate, or scientific transition','run_id':RUN,'experiment_id':EXP,'original_archive_commit':ARCHIVE,'execution_source_commit':env['commit'],'original_artifacts_sha256':original_hashes,'original_artifacts_match_archive_commit':archival_agreement,'successor_manifest':str(newpath.relative_to(ROOT)),'successor_manifest_sha256':sha(newpath),'evidence_identity':'Original flat manifest lacks id/run_id; launch and receipt explicitly identify RUN-ECDLP-2ac930 and agree with its directory. superseded_id_null opt-in is used for that missing identity, not a claim that id:null appeared in the original.','preserved_supervisor_outcome':receipt['status'],'preserved_producer_returncode':receipt['returncode'],'preserved_checker_returncode':receipt['check_returncode'],'scientific_review_verified':False,'new_scientific_trials':0,'new_independent_review':False,'official_status_changes':[],'shared_registry_modified':False,'model_provenance':{'runtime':'Codex','system_reported_family':'GPT-6','exact_serving_model_identifier':'unavailable','adapter_resolved_coordinator_binding':'anthropic:claude-opus-5-5','adapter_model_verified':False,'probe_performed':False,'substitution_approval_claimed':False},'remaining_authority':'Primary controls review/publication and shared registry merge. No inference approval or scientific authority is asserted by preparing this metadata.'}}
write(BASE/f'{cid}.json',provenance)
entry={'run_id':RUN,'superseded_path':str((OLD/'manifest.yaml').relative_to(ROOT)),'superseded_sha256':sha(OLD/'manifest.yaml'),'superseding_path':str(newpath.relative_to(ROOT)),'superseding_sha256':sha(newpath),'registered':'2026-10-17','supersession_kind':'additive_schema_completion','superseded_id_null':True,'superseded_id_null_provenance':f'Original hash-pinned flat manifest omits id/run_id. Identity is explicit in launch.json (sha256 {sha(OLD/"launch.json")}) and execution-receipt.json (sha256 {sha(OLD/"execution-receipt.json")}) and agrees with the run-directory basename. See {cid}.json; original missing fields are not edited.','defect':'Original flat manifest has no top-level run object and omits its run ID.','notes':'Proposed registry fragment only. Routes schema reading to additive metadata; preserves original invalid_output supervisor status, returncode 0, check_returncode 0, scientific_review_verified:false, all original bytes, and no certificate. Does not authorize any trial or scientific status change.'}
fragmentpath=BASE/'run-supersession-registry.fragment.yaml';write(fragmentpath,{'schema':'run-supersession-registry-v1','records':[entry]},'yaml')
supersessions=ledger.load_run_supersessions(str(fragmentpath))
ctx=ledger.Ctx(set());ledger.check_run_supersessions(ctx,supersessions)
identity_errors=list(ctx.errors)
ledger.check_run(str(OLD/'manifest.yaml'),ctx,supersessions)
schema_errors=ctx.errors[len(identity_errors):]
assert not ctx.errors,ctx.errors
assert original_hashes=={str(p.relative_to(ROOT)):sha(p) for p in sorted(OLD.iterdir()) if p.is_file()}
write(BASE/'checks.json',{'scope':'Only the proposed one-record registry fragment and original G2 source bundle; no repository-wide ledger validation.','registry_fragment_load_passed':True,'check_run_supersessions_errors':identity_errors,'check_run_errors':schema_errors,'registered_run_id':RUN,'original_bundle_unchanged':True,'original_bundle_matches_published_archive':all(archival_agreement.values()),'original_receipt_status':receipt['status'],'successor_status':manifest['run']['status'],'scientific_review_verified':False,'output_validated':False,'scientific_trials_launched':0,'shared_registry_modified':False,'correction_id':cid,'superseded_manifest_sha256':entry['superseded_sha256'],'superseding_manifest_sha256':entry['superseding_sha256']})
print(json.dumps({'correction_id':cid,'fragment_checks':'pass','original_status':receipt['status'],'new_status':manifest['run']['status'],'output_validated':False},indent=2))
