#!/usr/bin/env python3
"""Bind real published snapshot commit and verify normal raw archive task.
No trial, git mutation, scientific review or scientific state transition.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools'))
from research_dispatch import GitRepositoryVerifier,validate_queue
from experiment_execution import coverage
ap=argparse.ArgumentParser();ap.add_argument('snapshot_commit');a=ap.parse_args()
def git(*args):return subprocess.check_output(['git',*args],cwd=R,text=True).strip()
commit=git('rev-parse',a.snapshot_commit+'^{commit}');remote='origin/research/snfs-observation-cards-20261017';tip=git('rev-parse',remote+'^{commit}')
subprocess.run(['git','merge-base','--is-ancestor',commit,tip],cwd=R,check=True)
parent=git('show','-s','--format=%P',commit).split()[0]
qpath=R/'coordination/goals/GOAL-ECDLP-001/batches/BATCH-e7fde0/dispatch_queue.json';q=json.loads(qpath.read_text());p,t=q['tasks'];assert p['state']=='completed' and t['state']=='queued'
assert t['id']=='TASK-20261018-70f7f2'
paths=sorted(set(p['artifact_paths'])|set(t['artifact_paths']));assert len(paths)==25
hashes={s:hashlib.sha256((R/s).read_bytes()).hexdigest() for s in paths}
t['archive'].update(binding_mode='content_at_commit',commit_sha=commit,parent_sha=parent,path_sha256=hashes);t['state']='completed'
verifier=GitRepositoryVerifier(R);validate_queue(q,repository_verifier=verifier)
cov=coverage(R,R/'experiments/EXP-ECDLP-00e491/trial-plan.json');assert cov['measurement_complete'] and cov['scientific_review_verified'] is False
out=R/'coordination/goals/GOAL-ECDLP-001/batches/BATCH-e7fde0/archives/TASK-20261018-70f7f2/publication-verification.json';assert not out.exists()
record={'schema':'crypto.autoresearch.raw_publication_verification.v1','verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'task_id':t['id'],'source_task_id':p['id'],'experiment_id':'EXP-ECDLP-00e491','publication_verified':True,'scientific_review_verified':False,'scientific_conclusion':None,'archive_verifier':'tools.research_dispatch.validate_queue(repository_verifier=GitRepositoryVerifier(repo))','binding_mode':'content_at_commit','snapshot_commit_sha':commit,'snapshot_parent_sha':parent,'remote_tracking_ref':remote,'observed_remote_tracking_commit':tip,'snapshot_is_ancestor_of_observed_published_ref':True,'path_sha256':hashes,'source_artifact_count':24,'archive_artifact_count':1,'measurement_complete':cov['measurement_complete'],'trial_states':cov['trials'],'coverage_implementation_note':'tools/experiment_execution.py coverage() unconditionally reports publication_verified:false; this separate explicit Git-verification record does not rewrite it or any sealed execution receipt. scientific_review_verified remains false.','scientific_effect':'none','operational_task_states':{p['id']:p['state'],t['id']:t['state']}}
out.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n');qpath.write_text(json.dumps(q,indent=2,sort_keys=True)+'\n')
print(json.dumps({'archive_verified':True,'publication_verified':True,'scientific_review_verified':False,'snapshot_commit':commit,'paths_verified':len(paths),'new_record':str(out.relative_to(R)),'queue':str(qpath.relative_to(R))},indent=2))
