"""Publish completed retained files via repository policy, then GET/hash them.

This is a transport operation, never a scientific run or a native archive
completion. It leaves the supervisor receipt and hydrated stored forms intact.
"""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('five_artifacts',ROOT/'tools/artifacts/artifacts.py')
artifacts=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=artifacts
spec.loader.exec_module(artifacts)

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1<<20),b''):h.update(block)
    return h.hexdigest()

def publish(directory,out):
    directory=directory.resolve();out=out.resolve()
    if out.exists():raise ValueError('transport receipt already exists')
    if directory not in out.parents and directory!=out:
        pass
    else:raise ValueError('receipt must be outside the sealed run directory')
    receipt_path=directory/'execution-receipt.json'
    before=sha(receipt_path) if receipt_path.exists() else None
    if receipt_path.exists():
        execution=json.loads(receipt_path.read_text())
        if execution['status'] not in ('output_validated','interrupted','invalid_output','infrastructure_error','timed_out'):
            raise ValueError('no terminal execution receipt')
    else:execution=None
    cfg=artifacts.Config.load(ROOT)
    selected=[p for p in sorted(directory.iterdir()) if p.is_file()
              and artifacts.belongs_in_store(str(p.relative_to(ROOT)),p.stat().st_size,cfg.policy)]
    if selected:
        subprocess.run([sys.executable,str(ROOT/'tools/artifacts/artifacts.py'),'push',
                        *map(str,selected),'--jobs','2'],cwd=ROOT,check=True)
    manifest=artifacts.read_manifest(directory)
    remote=artifacts.Remote(cfg)
    rows=[]
    with tempfile.TemporaryDirectory(prefix='prime-five-readback-') as tmp:
        for name,entry in sorted(manifest.items()):
            local=directory/name
            if sha(local)!=entry['sha256'] or local.stat().st_size!=entry['bytes']:
                raise ValueError('hydrated file does not match manifest: '+name)
            if remote.head(entry['sha256'])!=entry['bytes']:
                raise ValueError('remote size mismatch: '+name)
            retrieved=Path(tmp)/entry['sha256']
            remote.get(entry['sha256'],retrieved)
            if sha(retrieved)!=entry['sha256'] or retrieved.stat().st_size!=entry['bytes']:
                raise ValueError('GET hash mismatch: '+name)
            logical=[]
            if execution:
                logical=[{'logical_path':k,'content_sha256':execution['artifact_sha256'][k]}
                         for k,v in execution.get('artifact_storage',{}).items() if v['path']==name]
            rows.append({'stored_path':str(local.relative_to(ROOT)),**entry,'head_and_get_sha256_verified':True,
                         'object_uri':cfg.remote.rstrip('/')+'/'+artifacts.object_key(entry['sha256']),
                         'receipt_logical_bindings':logical})
    if before and sha(receipt_path)!=before:raise ValueError('sealed receipt changed')
    result={'schema':'prime-five-artifact-transport/v1','recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'directory':str(directory.relative_to(ROOT)),'remote':cfg.remote,
            'receipt_sha256_unchanged':before,'files':rows,'file_count':len(rows),
            'stored_bytes':sum(r['bytes'] for r in rows),'hydrated_files_retained':True,
            'native_snapshot_completed':False,
            'native_snapshot_gap':'problems/native-snapshot-artifact-manifest-resolution.md',
            'scope':'Verified storage transport only; no scientific result or native archive transition.'}
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps({'receipt':str(out),'files':len(rows),'bytes':result['stored_bytes'],'all_GET_hashes_verified':True}))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory',type=Path);p.add_argument('--out',required=True,type=Path)
    args=p.parse_args();publish(args.directory,args.out)
