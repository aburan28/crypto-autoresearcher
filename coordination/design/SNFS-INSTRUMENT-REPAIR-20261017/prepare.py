#!/usr/bin/env python3
"""One-shot prospective transport correction preparation; never launches trials."""
import ast, copy, hashlib, json, re, subprocess, sys
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools'))
from experiment_execution import GENERATED, load_plan
from research_dispatch import validate_queue
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,obj,kind='json'):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:f.write((json.dumps(obj,indent=2,sort_keys=True)+'\n') if kind=='json' else yaml.safe_dump(obj,sort_keys=False))
def alloc(kind):
 text=subprocess.check_output(['python3','tools/allocate_id.py','--next',kind,'--date','20261017'],cwd=ROOT,text=True)
 ident=re.search(r'(?:TASK|DEC|CORR)-20261017-[0-9a-f]{6}',text).group()
 check=subprocess.run(['python3','tools/allocate_id.py','--check',ident],cwd=ROOT,text=True,capture_output=True)
 if check.returncode:raise RuntimeError(check.stdout+check.stderr)
 return ident
records=[]
for exp,oldtask,olddec,label in [('EXP-ECDLP-f34097','TASK-20261012-087dbe','DEC-20261012-a99281','E3'),('EXP-ECDLP-903c48','TASK-20261012-ef8523','DEC-20261012-e7075a','D4')]:
 ids={k:alloc(t) for k,t in [('executor','handoff'),('archive','handoff'),('correction','correction'),('prospective_decision','coordinator_decision')]}
 expdir=ROOT/'experiments'/exp
 oldplan=expdir/'trial-plan.json';oldqueue=ROOT/'coordination/design'/oldtask/'dispatch_queue.json'
 d=BASE/label;d.mkdir()
 plandir=expdir/'amendments'/ids['correction'];plandir.mkdir()
 planpath=plandir/'trial-plan.transport-v2.json'
 qpath=d/'dispatch-queue.preview.json';hpath=d/'executor-handoff.preview.yaml'
 plan=json.loads(oldplan.read_text());plan.update(task_id=ids['executor'],queue=str(qpath.relative_to(ROOT)))
 plan['input_sha256']={str(oldplan.relative_to(ROOT)):sha(oldplan),plan['specification']:sha(expdir/'specification.yaml')}
 plan['transport_correction']={'id':ids['correction'],'status':'review_required','original_trial_plan':str(oldplan.relative_to(ROOT)),'original_trial_plan_sha256':sha(oldplan),'scientific_parameters_changed':False,'execution_authorized_by_this_correction':False}
 write(planpath,plan)
 oldq=json.loads(oldqueue.read_text());task=copy.deepcopy(oldq['tasks'][0]);archive=copy.deepcopy(oldq['tasks'][1])
 paths=[f"experiments/{exp}/runs/{t['run_id']}/{n}" for t in plan['trials'] for n in (*GENERATED,*t['artifacts'])]
 h=task['handoff'];h.update(id=ids['executor'],role='executor',archived_by=ids['archive'],artifact_paths=paths,deliverables=paths)
 h['inputs']+=[str(planpath.relative_to(ROOT))]
 h['inference'].update(policy='executor-implementation',reasoning_effort='high',delivery='interactive')
 h['execution'].update(trial_plan=str(planpath.relative_to(ROOT)),trial_plan_sha256=sha(planpath))
 h['completion_gate']+=['Every GENERATED supervisor artifact is retained; logs may be empty as documented by the supervisor.','manifest.yaml passes experiment_execution.manifest_schema_errors; no scientific status transition.']
 h['constraints']+=['REVIEW_REQUIRED: this prospective card conveys no new launch authorization. Existing claim stays attached to the original queue and is not transferred.']
 task.update(id=ids['executor'],state='blocked',archived_by=ids['archive'],artifact_paths=paths,handoff=h)
 task['read_scope']+=[str(d.relative_to(ROOT)),str(plandir.relative_to(ROOT))]
 task['blocked_reason']='Prospective correction pending lawful Coordinator approval, manifest implementation repair, preapproval support and lane admission.'
 ap=str((d/'archive-receipt.json').relative_to(ROOT))
 archive.update(id=ids['archive'],state='blocked',depends_on=[ids['executor']],artifact_paths=[ap],write_scope=[str(d.relative_to(ROOT))])
 archive['archive'].update(source_task_ids=[ids['executor']],record_ids=[exp,plan['hypothesis_id'],ids['executor'],ids['archive'],ids['correction']])
 archive['read_scope']+=paths+[str(planpath.relative_to(ROOT))]
 archive['handoff'].update(id=ids['archive'],role='coordinator',objective='Archive the complete corrected stage-0 execution package only after the prospective correction is approved and execution completes.',inputs=[str(hpath.relative_to(ROOT)),str(planpath.relative_to(ROOT))],artifact_paths=[ap],deliverables=[ap])
 archive['handoff']['inference']={'policy':'coordinator-orchestration-code','reasoning_effort':'high','fallback_allowed':False,'degraded_allowed':False,'independent_session_required':False,'delivery':'interactive'}
 q={k:v for k,v in oldq.items() if k!='tasks'};q.update(task_id=ids['executor'],tasks=[task,archive],status='review_required',transport_correction=ids['correction'])
 write(qpath,q);write(hpath,{'handoff':h},'yaml');write(d/'archive-handoff.preview.yaml',{'handoff':archive['handoff']},'yaml')
 amendment={'protocol_amendment':{'id':ids['correction'],'experiment_id':exp,'version_from':1,'version_to':2,'version_scope':'execution transport only; scientific protocol remains version 1','status':'review_required','reason':'Original queue archives three producer artifacts but current supervisor requires eight additional artifacts; original manifests also lack current run-schema provenance.','changes':['Declare exact eight GENERATED artifacts alongside original three outputs.','Assign a new executor handoff exactly once to an isolated snapshot archive.','Use an additive plan and prospective queue; original frozen bytes and scientific trial/run identities remain unchanged.','Add explicit original specification/plan input SHA-256 bindings.'],'affected_runs':[],'confirmatory_status':'preserved','approved_by':None,'standing_authorization':'AGENTS.md standing user authorization dated 2026-09-06; permission does not waive runnable-contract or inference requirements.','original_plan_sha256':sha(oldplan),'prospective_plan':str(planpath.relative_to(ROOT)),'prospective_queue':str(qpath.relative_to(ROOT)),'prospective_approval_decision_id':ids['prospective_decision'],'implementation_obligation':'A separately dispatched design/implementation task must add a versioned provenance wrapper or driver, preserve original source, write schema-complete manifest from actual launch/environment/timing, retain original producer manifest separately, and bind the new source hashes. No fabricated run metadata or replacement of frozen source.','authorization_effect':'none'}}
 write(plandir/'amendment.review-required.yaml',amendment,'yaml')
 decision={'coordinator_decision':{'id':ids['prospective_decision'],'status':'review_required','decision':'revise','target_ids':[exp,plan['hypothesis_id'],ids['correction']],'context':'Prospective repair packet only; no serving-model substitution is silently authorized.','rationale':['Eight missing archive paths can be prepared additively.','Current preapproval tool cannot certify an already-approved contract at an additive plan path.','Legacy producer manifests cannot pass the current supervisor run-schema check.'],'evidence_refs':[],'limitations':['This is a draft, not a committed Coordinator approval. No official scientific state changes.'],'next_actions':['Finish versioned manifest transport implementation, add supported additive preapproval/routing, resolve truthful runtime policy authority, then rerun exact prospective checks before approval and publication.'],'knowledge_promotion':{'promoted':[],'not_warranted':'No scientific run or scientific conclusion.'},'decided_by':None,'provenance':{'actual_runtime':'Codex','actual_model':'GPT-6 (system-reported family; exact serving model identifier unavailable)','requested_policy':'coordinator-orchestration-code','adapter_resolved_model':'anthropic:claude-opus-5-5','adapter_model_verified':False,'inference_probe_performed':False,'claimed_to_have_run_as_adapter_model':False}}}
 write(d/'decision.review-required.yaml',decision,'yaml')
 packet={'schema':'crypto.autoresearch.preapproval_packet.v1','experiment_id':exp,'approval_decision_id':olddec,'specification':plan['specification'],'trial_plan':f'experiments/{exp}/trial-plan.json','queue':str(qpath.relative_to(ROOT)),'handoff':str(hpath.relative_to(ROOT)),'preview':{'specification':plan['specification'],'trial_plan':str(planpath.relative_to(ROOT)),'queue':str(qpath.relative_to(ROOT)),'handoff':str(hpath.relative_to(ROOT))},'source_ref':'origin/research/snfs-ecdlp-ledger-tracking-20261017','lane_id':None,'execution_route':{'kind':'implementation','reason':'Versioned transport correction and provenance wrapper require implementation-tier judgment; no mechanical runbook is claimed.'},'note':'Read-only diagnostic only; tool currently hardcodes canonical plan path and unapproved canonical state. Original scientific approval remains a historical record, not approval of this correction.'}
 write(d/'preapproval-packet.json',packet)
 result=subprocess.run(['python3','tools/experiment_preapproval.py','--packet',str((d/'preapproval-packet.json').relative_to(ROOT))],cwd=ROOT,text=True,capture_output=True)
 (d/'preapproval.stdout.json').write_text(result.stdout);(d/'preapproval.stderr.txt').write_text(result.stderr)
 structural={'queue_valid':False,'load_plan_valid':False,'all_generated_artifacts_archived':set(paths)==set(task['artifact_paths']),'trial_identity_and_argv_unchanged':plan['trials']==json.loads(oldplan.read_text())['trials'],'original_plan_sha256':sha(oldplan),'original_queue_sha256':sha(oldqueue),'preapproval_exit_code':result.returncode,'original_claim_reused':False,'scientific_trials_launched':0}
 try:validate_queue(copy.deepcopy(q));structural['queue_valid']=True
 except Exception as e:structural['queue_error']=str(e)
 try:load_plan(ROOT,planpath);structural['load_plan_valid']=True
 except Exception as e:structural['load_plan_error']=str(e)
 # Static extraction of the literal manifest f-string list, without importing or executing driver code.
 tree=ast.parse((expdir/'implementation/run.py').read_text());literals=[]
 for node in ast.walk(tree):
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='manifest' for t in node.targets):
   literals=[x.value for x in ast.walk(node.value) if isinstance(x,ast.Constant) and isinstance(x.value,str)]
 missing=[k for k in ['code','environment','inputs','timing','result'] if not any(re.match(r'^  '+k+r':',x) for x in literals)]
 structural['static_manifest_missing_required_fields']=missing
 write(d/'checks.json',structural)
 records.append({'lead':label,'experiment_id':exp,'ids':ids,'plan':str(planpath.relative_to(ROOT)),'packet':str((d/'preapproval-packet.json').relative_to(ROOT)),'checks':structural})
write(BASE/'manifest.json',{'status':'review_required','execution_authorized':False,'scientific_trials_launched':0,'records':records,'untouched_active_batch':'BATCH-769f82','provenance':'Drafting and read-only structural checks only; no model probe, official decision, scientific run, commit or push.'})
print(json.dumps(records,indent=2))
