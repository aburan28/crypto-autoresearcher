#!/usr/bin/env python3
"""Prepare immutable G1 retry draft. No claim, launch, commit or approval."""
import copy,hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent/'G1-retry';BASE.mkdir()
sys.path.insert(0,str(ROOT/'tools'))
from experiment_execution import GENERATED,load_plan
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def alloc(kind):
 args=['python3','tools/allocate_id.py','--next',kind]+(['--area','ECDLP'] if kind=='run' else ['--date','20261017'])
 out=subprocess.check_output(args,cwd=ROOT,text=True);ident=re.search(r'(?:RUN-ECDLP|TASK-20261017|CORR-20261017)-[0-9a-f]{6}',out).group()
 p=subprocess.run(['python3','tools/allocate_id.py','--check',ident],cwd=ROOT,capture_output=True,text=True)
 if p.returncode:raise ValueError(p.stdout+p.stderr)
 return ident
rid,tid,cid=alloc('run'),alloc('handoff'),alloc('correction')
exp='EXP-ECDLP-84af7b';oldpath=ROOT/'experiments'/exp/'trial-plan.json';failed=ROOT/'experiments'/exp/'runs/RUN-ECDLP-18d26b/execution-receipt.json'
plan=json.loads(oldpath.read_text());oldtrials=copy.deepcopy(plan['trials']);plan['task_id']=tid;plan['queue']=str((BASE/'dispatch-queue.pending.json').relative_to(ROOT))
plan['trials'][0]['run_id']=rid;plan['raw_archive_contract']['run_ids']=[rid]
plan['retry_of']={'trial_id':oldtrials[0]['id'],'run_id':oldtrials[0]['run_id'],'execution_receipt':str(failed.relative_to(ROOT)),'execution_receipt_sha256':sha(failed),'reason':'cargo executable missing before scientific program launch; explicit immutable retry pending','original_plan_sha256':sha(oldpath),'new_replication':False,'status':'review_required','additional_execution_authorized':False}
planpath=BASE/'trial-plan.retry.preview.json';planpath.write_text(json.dumps(plan,indent=2,sort_keys=True)+'\n')
q=json.loads((ROOT/'coordination/goals/GOAL-ECDLP-001/batches/BATCH-769f82/dispatch_queue.json').read_text());old=next(t for t in q['tasks'] if t['id']=='TASK-20261017-2cc75e');h=copy.deepcopy(old['handoff']);paths=[f'experiments/{exp}/runs/{rid}/{n}' for n in (*GENERATED,*plan['trials'][0]['artifacts'])]
h.update(id=tid,artifact_paths=paths,deliverables=paths);h['execution'].update(trial_plan=str(planpath.relative_to(ROOT)),trial_plan_sha256=sha(planpath));h['constraints']+=['Draft only: no launch before explicit additive retry approval, released original claim, new published claim and lawful corrected review/archive queue.']
(BASE/'executor-handoff.retry.preview.json').write_text(json.dumps({'handoff':h,'status':'review_required','archive_owner_unresolved':True},indent=2,sort_keys=True)+'\n')
checks={'load_plan_valid':False,'scientific_argv_unchanged':plan['trials'][0]['argv']==oldtrials[0]['argv'],'scientific_trial_id_unchanged':plan['trials'][0]['id']==oldtrials[0]['id'],'new_run_id':rid,'prior_run_untouched':True,'prior_worker_confirmed_dead':False,'cargo_installation_confirmed':False,'queue_prepared':False,'claim_created':False,'scientific_trials_launched':0}
try:load_plan(ROOT,planpath);checks['load_plan_valid']=True
except Exception as e:checks['load_plan_error']=str(e)
obligation={'id':cid,'status':'review_required','experiment_id':exp,'new_task_id':tid,'new_run_id':rid,'old_run_id':'RUN-ECDLP-18d26b','approved_by':None,'scientific_parameters_changed':False,'observed_failure':json.loads(failed.read_text())['detail'],'unblocking_requirements':['Preserve/publish the failed receipt and all existing prior run bytes.','Verify prior worker no longer active and original claim released.','Verify local cargo/rustc and required libpari/build inputs; bind any new runtime lock truthfully.','Construct a lawful new retry queue with isolated snapshot and independent validator/red-team dependencies; never mutate BATCH-769f82. The copied executor handoff archive owner is intentionally unresolved and must be rebound.','Record explicit additive retry authorization under a truthful Coordinator model binding, then commit/push new plan, handoff and queue and publish a fresh claim.','Launch only via /run with the new RUN ID; retain full-grid scientific trial identity, seeds, parameters, checker, source hashes and stopping rules.'],'limitations':['No queue, claim, independent review, or execution approval is represented as complete.','This packet is a retry proposal, not a fresh replication or a scientific result.']}
(BASE/'retry-obligation.json').write_text(json.dumps(obligation,indent=2,sort_keys=True)+'\n');(BASE/'checks.json').write_text(json.dumps(checks,indent=2,sort_keys=True)+'\n')
print(json.dumps(checks,indent=2))
