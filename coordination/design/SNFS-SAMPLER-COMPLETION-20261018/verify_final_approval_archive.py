#!/usr/bin/env python3
"""Verify a real isolated approval snapshot through existing repository verifier.
No commit, status change or inference. stdout is a receipt only after verification.
"""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools'))
from research_dispatch import GitRepositoryVerifier
p=argparse.ArgumentParser();p.add_argument('commit');a=p.parse_args()
task=json.loads((B/'approval-archive-final-template.json').read_text());t=task['task']
commit=subprocess.check_output(['git','rev-parse',a.commit+'^{commit}'],cwd=R,text=True).strip()
parents=subprocess.check_output(['git','show','-s','--format=%P',commit],cwd=R,text=True).split()
t['archive']['commit_sha']=commit;t['archive']['parent_sha']=parents[0] if parents else None
GitRepositoryVerifier(R).verify_archive(t,sorted(t['archive']['path_sha256']))
print(json.dumps({'schema':'crypto.autoresearch.approval_snapshot_verified.v1','verified':True,'task_id':t['id'],'commit_sha':commit,'parent_sha':t['archive']['parent_sha'],'binding_mode':'content_at_commit','path_sha256':t['archive']['path_sha256'],'scientific_effect':'none','scientific_trials_launched_by_verifier':0},indent=2,sort_keys=True))
