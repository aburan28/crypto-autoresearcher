#!/usr/bin/env python3
"""Local fake-S3 controls for publication and restore; never cloud evidence."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from publish_lift_checkpoint import inspect_snapshot


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p, obj):
    with p.open('x') as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.write('\n')


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--plan',type=Path,required=True)
    ap.add_argument('--protocol',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();plan=json.loads(a.plan.read_text());protocol=json.loads(a.protocol.read_text())
    assert protocol['freeze']['status']=='frozen'
    for path,digest in plan['hashes'].items():assert sha(Path(path))==digest,path
    a.out.mkdir(parents=True,exist_ok=False)
    bin_dir=a.out/'bin';bin_dir.mkdir()
    shutil.copyfile(plan['fake_aws'],bin_dir/'aws');(bin_dir/'aws').chmod(0o755)
    rows=[]
    for name in plan['cases']:
        root=a.out/name;root.mkdir();snapshots=root/'snapshots';snapshots.mkdir()
        local=[]
        for source in plan['snapshots']:
            dest=snapshots/Path(source).name;shutil.copyfile(source,dest);local.append(dest)
        metadata=inspect_snapshot(local[0])
        context=dict(request_sha256=sha(a.plan),protocol_sha256=protocol['freeze']['protocol_sha256'],
                     seed_sha256=metadata['seed_sha256'],binary_sha256=metadata['binary_sha256'])
        context_path=root/'context.json';save(context_path,context)
        env={k:v for k,v in os.environ.items() if not k.startswith(('SEMAEV_CHECKPOINT_','FAKE_CHECKPOINT_'))}
        env.update(PATH=str(bin_dir.resolve())+os.pathsep+env['PATH'],FAKE_CHECKPOINT_STORE=str((root/'store').resolve()),
                   SEMAEV_CHECKPOINT_DIR=str(snapshots.resolve()),SEMAEV_CHECKPOINT_CONTEXT=str(context_path.resolve()),
                   SEMAEV_CHECKPOINT_S3_PREFIX='s3://fake-bucket/task',OMP_NUM_THREADS='1')
        steps=[]
        def run(label,argv,extra=None,expected=0):
            child_env=dict(env,**(extra or {}));start=time.time()
            cmd=['prlimit','--as=1073741824','--',*map(str,argv)]
            p=subprocess.run(cmd,env=child_env,capture_output=True,timeout=120)
            (root/(label+'.stdout')).write_bytes(p.stdout);(root/(label+'.stderr')).write_bytes(p.stderr)
            record=dict(label=label,argv=cmd,returncode=p.returncode,elapsed_seconds=time.time()-start,wall_valid=False,isolation='L0',fault=(extra or {}).get('FAKE_CHECKPOINT_FAULT'))
            save(root/(label+'.step.json'),record);steps.append(record)
            assert p.returncode==expected,(label,p.returncode,expected)
            return p
        def publish(i,label,extra=None,expected=0):
            p=run(label,[sys.executable,plan['publisher'],local[i]],extra,expected)
            if expected==0:assert p.stdout==b'', 'hook contaminates producer stdout'
            return p
        def restore(label,extra=None,expected=0):
            receipt=root/(label+'.receipt.json')
            run(label,[sys.executable,plan['restorer'],'--prefix','s3://fake-bucket/task',
                       '--context',context_path,'--out',root/(label+'-files'),'--receipt',receipt],extra,expected)
            return json.loads(receipt.read_text()) if receipt.exists() else None
        row=dict(case=name)
        try:
            if name in ('object_put','object_get','object_corrupt_get','manifest_put','manifest_get','manifest_corrupt_get'):
                publish(0,'fault',{'FAKE_CHECKPOINT_FAULT':name},expected=1)
                assert local[0].exists()
                assert not local[0].with_suffix('.publication.json').exists()
                manifests=list((root/'store').glob('**/manifests/*.json'))
                if name in ('object_put','object_get','object_corrupt_get','manifest_put'):assert not manifests
                # Retrying the same immutable snapshot must complete correctly.
                publish(0,'retry')
                r=restore('restore-after-retry');assert r['snapshot']['sequence']==1
            elif name=='wrong_snapshot_context':
                context['seed_sha256']='0'*64;context_path.write_text(json.dumps(context))
                publish(0,'wrong-context',expected=1)
                assert not (root/'store').exists() and local[0].exists()
            elif name=='idempotent_publication':
                publish(0,'first');before={str(p):sha(p) for p in (root/'store').rglob('*') if p.is_file()}
                publish(0,'again');after={str(p):sha(p) for p in (root/'store').rglob('*') if p.is_file()}
                assert before==after
            elif name=='prune_after_readback':
                publish(0,'prune',{'SEMAEV_CHECKPOINT_PRUNE_LOCAL':'1'});assert not local[0].exists()
                r=restore('restore-pruned');assert sha(Path(r['local_path']))==metadata['sha256']
            else:
                publish(0,'older');publish(1,'newer')
                if name=='fallback_corrupt_object':
                    meta=inspect_snapshot(local[1]);p=root/'store/fake-bucket/task/objects'/f'{meta["sha256"]}.bin'
                    p.write_bytes(p.read_bytes()[:-1])
                elif name=='fallback_corrupt_manifest':
                    p=next((root/'store/fake-bucket/task/manifests').glob('00000000000000000002-*.json'))
                    p.write_bytes(p.read_bytes()[:-1])
                elif name=='wrong_restore_context':
                    context['request_sha256']='0'*64;context_path.write_text(json.dumps(context))
                    r=restore('wrong-context',expected=3);assert r['status']=='no_compatible_checkpoint' and len(r['rejected'])==2
                elif name=='truncated_listing':
                    assert restore('truncated',{'FAKE_CHECKPOINT_FAULT':'truncated_listing'},expected=1) is None
                if name not in ('wrong_restore_context','truncated_listing'):
                    r=restore('selected');expected_sequence=1 if name.startswith('fallback_') else 2
                    assert r['snapshot']['sequence']==expected_sequence
                    if name.startswith('fallback_'):assert len(r['rejected'])==1
                    if name=='restore_newest_and_replay':
                        output=root/'restored-certificate.bin'
                        # Remove hook variables; enable only local producer snapshots.
                        replay_env={k:'' for k in env if k.startswith('SEMAEV_CHECKPOINT_')}
                        replay_env.update(SEMAEV_CHECKPOINT_DIR=str(root/'replay-checkpoints'),SEMAEV_CHECKPOINT_RESTORE=r['local_path'])
                        run('native-replay',[plan['producer'],plan['seed'],output,'31','1073741824'],replay_env)
                        assert sha(output)==plan['expected_certificate_sha256']
            row.update(passed=True,steps=len(steps))
        except Exception as error:
            row.update(passed=False,error=repr(error),steps=len(steps))
        save(root/'result.json',row);rows.append(row)
    result=dict(scope='Local fake-S3 software controls only; no actual cloud permission/durability claim',
                plan_sha256=sha(a.plan),protocol_sha256=protocol['freeze']['protocol_sha256'],
                cases=rows,passed=all(r['passed'] for r in rows))
    save(a.out/'result.json',result);print(json.dumps(result))
    return int(not result['passed'])


if __name__=='__main__':
    raise SystemExit(main())
