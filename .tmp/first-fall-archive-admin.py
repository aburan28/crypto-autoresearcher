from pathlib import Path
import sys, json, hashlib, subprocess, datetime
root=Path('/Volumes/SSD990/crypto-autoresearcher/.tmp/first-fall-designs-20260905')
batch=root/'coordination/goals/GOAL-ECDLP-001/batches/BATCH-ae9150'
qpath=batch/'dispatch_queue.json'
q=json.loads(qpath.read_text())
mode=sys.argv[1]; j=int(sys.argv[2])
producer=q['tasks'][j]; archive=q['tasks'][j+1]
if mode=='prepare':
    paths=producer['artifact_paths']
    missing=[p for p in paths if not (root/p).is_file()]
    if missing: raise SystemExit('Missing: '+str(missing))
    parent=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    manifest={'schema':'crypto.autoresearch.design_snapshot.v1',
      'archive_task_id':archive['id'],'source_task_ids':[producer['id']],
      'record_ids':archive['archive']['record_ids'],'parent_sha':parent,
      'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'source_path_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths},
      'claim_boundary':'Design artifacts only. No experiment execution, result validation, or scientific promotion.',
      'commit_binding':'The containing snapshot commit is recorded after creation in dispatch_queue.json; this manifest does not assert its own commit hash.'}
    target=root/archive['artifact_paths'][0];target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists(): raise SystemExit('Refusing to overwrite manifest')
    target.write_text(json.dumps(manifest,indent=2)+'\n')
    producer['state']='completed'; producer['state_note']='Declared design artifacts produced; no experiment runs.'
    archive['state']='queued'
    qpath.write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({'archive_task_id':archive['id'],'paths':paths+archive['artifact_paths'],'parent_sha':parent},indent=2))
elif mode=='bind':
    commit=sys.argv[3]
    parent=subprocess.check_output(['git','show','-s','--format=%P',commit],cwd=root,text=True).strip().split()[0]
    paths=producer['artifact_paths']+archive['artifact_paths']
    archive['archive'].update(commit_sha=commit,parent_sha=parent,path_sha256={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths})
    archive['state']='completed';archive['state_note']='Exact source and manifest commit bound; dispatcher verification required before downstream work.'
    qpath.write_text(json.dumps(q,indent=2)+'\n')
    print(commit)
else: raise SystemExit('Unknown mode')
