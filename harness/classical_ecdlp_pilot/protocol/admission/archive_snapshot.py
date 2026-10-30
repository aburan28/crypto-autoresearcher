#!/usr/bin/env python3
"""Prepare or verify an actual post-execution snapshot; never mutate a queue.

prepare requires a completed producer release and a live, published archive
claim. It writes only under this tool's admission directory. The Coordinator
copies the receipt to its declared path and commits exactly the emitted pathspec.
verify binds a real commit using the unchanged repository Git verifier.
"""
from __future__ import annotations
import argparse
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()


def published(root, relative):
    local = (root/relative).read_bytes()
    for ref in git(root, 'for-each-ref', '--format=%(refname)', 'refs/remotes/origin/').splitlines():
        result = subprocess.run(['git','-C',str(root),'show',ref+':'+relative],capture_output=True)
        if result.returncode == 0 and result.stdout == local:
            return ref
    raise ValueError('claim/release is not present with these exact bytes in an origin ref: '+relative)


def run(args):
    root = args.repo_root.resolve()
    out = args.out.resolve()
    require(out.is_relative_to(Path(__file__).resolve().parent), 'output must remain under admission task scope')
    sys.path.insert(0,str(root/'tools'))
    import experiment_execution
    import goal_lanes
    from research_dispatch import GitRepositoryVerifier
    queue = json.loads((root/args.queue).read_text())
    source = next(t for t in queue['tasks'] if t['id'] == args.producer)
    archive = copy.deepcopy(next(t for t in queue['tasks'] if t['id'] == args.archive))
    require(source['archived_by'] == archive['id'] and source['id'] in archive['archive']['source_task_ids'], 'archive ownership mismatch')
    require(archive['archive'].get('binding_mode','commit') == 'commit', 'this helper is specifically for the frozen default commit binding')
    receipt_relative = archive['artifact_paths'][0]
    require(len(archive['artifact_paths']) == 1, 'exactly one declared snapshot receipt required')
    if args.command == 'prepare':
        claims = goal_lanes.claim_summary(root, root/args.queue, include_refs=True)
        producer = claims[source['id']]
        coordinator = claims[archive['id']]
        require(producer['status'] == 'released' and producer['release']['outcome'] == 'completed', 'producer must have an actual completed release')
        require(coordinator['status'] == 'live' and coordinator['owner'] == args.owner and coordinator['epoch'] == args.epoch, 'archive must hold its actual live claim')
        claim_prefix = (Path(args.queue).parent/'claims').as_posix()
        release_rel = claim_prefix+'/'+source['id']+'.'+str(producer['epoch'])+'.release.json'
        claim_rel = claim_prefix+'/'+archive['id']+'.'+str(coordinator['epoch'])+'.claim.json'
        release_ref = published(root,release_rel)
        claim_ref = published(root,claim_rel)
        plan_relative = source['handoff']['execution']['trial_plan']
        progress = experiment_execution.coverage(root,root/plan_relative)
        require(progress['measurement_complete'] and progress['output_validated'] == 1 and progress['remaining'] == 0, 'supervisor batch is not complete')
        paths = source['artifact_paths']
        require(len(paths) == len(set(paths)) == 110, 'expected exact 110-file sealed source')
        source_hashes = {path:sha(root/path) for path in sorted(paths)}
        release_hashes = producer['release'].get('artifact_sha256')
        require(release_hashes == source_hashes, 'completed release does not bind these exact 110 bytes')
        run_base = Path(plan_relative).parent/'runs'
        execution_files = [p for p in paths if p.endswith('/execution-receipt.json')]
        require(len(execution_files) == 1,'one supervisor execution receipt expected')
        execution = json.loads((root/execution_files[0]).read_text())
        require(execution['status'] == 'output_validated' and execution['returncode'] == 0 and execution['check_returncode'] == 0, 'supervisor output-integrity result is not complete')
        require(not execution.get('artifact_storage'),'unexpected compacted storage requires a separately explicit physical-path archive')
        base = (root/execution_files[0]).parent
        actual_files = {p.relative_to(root).as_posix() for p in base.rglob('*') if p.is_file()}
        require(actual_files == set(paths), 'sealed run has unexpected or missing files outside the declared 110-file envelope')
        for name,digest in execution['artifact_sha256'].items():
            require(sha(base/name)==digest,'sealed supervisor artifact changed: '+name)
        parent = git(root,'rev-parse','HEAD')
        receipt = {'schema':'classical.ecdlp.actual-snapshot.v1','prepared_at':dt.datetime.now(dt.timezone.utc).isoformat(),
             'archive_task_id':archive['id'],'source_task_ids':[source['id']], 'goal_id':queue['goal_id'],
             'record_ids':archive['archive']['record_ids'],'precommit_parent_sha':parent,
             'source_artifact_sha256':source_hashes,'source_artifact_count':len(paths),
             'execution_receipt':{'path':execution_files[0],'sha256':sha(root/execution_files[0]),'status':execution['status']},
             'supervisor_progress':progress,
             'producer_release':{'path':release_rel,'sha256':sha(root/release_rel),'published_ref':release_ref},
             'archive_claim':{'path':claim_rel,'sha256':sha(root/claim_rel),'published_ref':claim_ref,'owner':args.owner,'epoch':args.epoch},
             'meaning':'Actual source-byte snapshot before its isolated commit; the Coordinator binds the resulting commit and receipt hash in the queue afterwards.',
             'scientific_review_verified':False,'scientific_conclusion':None}
        out.mkdir(parents=True,exist_ok=False)
        receipt_path=out/'snapshot-receipt.json'
        write(receipt_path,receipt)
        all_hashes={**source_hashes,receipt_relative:sha(receipt_path)}
        binding={**archive['archive'],'commit_sha':None,'parent_sha':parent,'path_sha256':all_hashes}
        write(out/'archive-binding-candidate.json',binding)
        expected=sorted(all_hashes)
        (out/'git-pathspec.nul').write_bytes(b'\0'.join(p.encode() for p in expected)+b'\0')
        message='snapshot('+archive['id']+'): preserve '+', '.join(archive['archive']['record_ids'])
        write(out/'commit-instructions.json',{'receipt_copy_to':receipt_relative,'expected_parent':parent,'exact_changed_paths':expected,'commit_message':message,
            'publication_order':'This isolated raw-records-plus-snapshot commit precedes derived reports. No earlier separate raw-record commit is compatible with this frozen default binding.'})
        print(json.dumps({'prepared':True,'source_files':110,'commit_files':111,'receipt':str(receipt_path),'copy_to':receipt_relative,'expected_parent':parent,'commit_message':message},indent=2))
    else:
        require(args.commit is not None,'--commit is required for actual verification')
        binding=json.loads((out/'archive-binding-candidate.json').read_text())
        binding['commit_sha']=git(root,'rev-parse',args.commit+'^{commit}')
        require(binding['parent_sha']==git(root,'rev-parse',args.commit+'^'),'archive parent changed after snapshot preparation')
        archive['archive']=binding
        archive['state']='completed'
        expected=sorted(binding['path_sha256'])
        GitRepositoryVerifier(root).verify_archive(archive,expected)
        record={'verified_by':'unmodified tools.research_dispatch.GitRepositoryVerifier','archive_task_id':archive['id'],
                'commit_sha':binding['commit_sha'],'parent_sha':binding['parent_sha'],'paths_verified':len(expected),'archive_binding':binding,
                'scientific_review_verified':False,'scientific_conclusion':None}
        write(out/'actual-archive-verification.json',record)
        print(json.dumps({'actual_archive_commit_verified':True,'commit':binding['commit_sha'],'paths_verified':len(expected),'binding_file':str(out/'actual-archive-verification.json')},indent=2))


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=('prepare','verify'))
    p.add_argument('--repo-root',type=Path,required=True)
    p.add_argument('--queue',required=True)
    p.add_argument('--producer',default='TASK-20261025-640fa7')
    p.add_argument('--archive',default='TASK-20261025-4c4ea5')
    p.add_argument('--owner',default='coordinator-classical-pilot')
    p.add_argument('--epoch',type=int,default=1)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--commit')
    try:
        run(p.parse_args())
    except (OSError,ValueError,KeyError,subprocess.CalledProcessError) as e:
        print('archive snapshot refused: '+str(e),file=sys.stderr)
        raise SystemExit(2)
