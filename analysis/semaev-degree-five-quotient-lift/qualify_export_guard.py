#!/usr/bin/env python3
"""Frozen local guard controls; fake storage, unchanged native producer."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from checkpoint_export_guard import certificate_size, work_bytes
from publish_lift_checkpoint import inspect_snapshot


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p,obj):
    with p.open('x') as f:
        json.dump(obj,f,indent=2,sort_keys=True);f.write('\n')


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--plan',type=Path,required=True)
    ap.add_argument('--protocol',type=Path,required=True)
    ap.add_argument('--mode',choices=['fresh','restored'],required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();plan=json.loads(a.plan.read_text());protocol=json.loads(a.protocol.read_text())
    assert protocol['freeze']['status']=='frozen'
    assert a.out.resolve()==Path(plan['output_root'])/a.mode
    for name,digest in plan['hashes'].items():assert sha(Path(name))==digest,name
    a.out.mkdir(parents=True,exist_ok=False)
    bin_dir=a.out/'bin';bin_dir.mkdir();shutil.copy2(plan['fake_aws'],bin_dir/'aws');(bin_dir/'aws').chmod(0o755)
    rows=[]
    for index,name in enumerate(plan['cases']):
        case=a.out/name;case.mkdir();work=case/'work';work.mkdir();snapshots=work/'snapshots';snapshots.mkdir()
        source=Path(plan['phase1'] if name=='phase1' or name.startswith('native_') and a.mode=='fresh' else plan['phase2'])
        snapshot=snapshots/source.name;shutil.copy2(source,snapshot)
        meta=inspect_snapshot(snapshot);output=work/'certificate.bin'
        context=dict(request_sha256='0'*64,protocol_sha256=protocol['freeze']['protocol_sha256'],
                     seed_sha256=meta['seed_sha256'],binary_sha256=meta['binary_sha256'])
        policy=dict(N=7,degree=4,working_coordinates=75,capacity_bytes=1<<30,reserve_bytes=4096,
                    work_root=str(work.resolve()),certificate_relative_path='certificate.bin')
        if name=='native_refuse':policy['capacity_bytes']=policy['reserve_bytes']+1
        if name in ('boundary_exact','boundary_short'):
            # Common direct prelaunch boundary check in both configurations;
            # native hook integration is exercised by native_allow/refuse.
            policy['capacity_bytes']=work_bytes(work)+policy['reserve_bytes']+65536+1616-(name=='boundary_short')
        if name=='wrong_dimensions':policy['N']=8
        request=case/'request.json';save(request,dict(disk_policy=policy));context['request_sha256']=sha(request)
        context_path=case/'context.json';save(context_path,context)
        if name=='wrong_request':request.write_text(request.read_text()+' ')
        if name=='corrupt_snapshot':
            b=bytearray(snapshot.read_bytes());b[-1]^=1;snapshot.write_bytes(b)
        if name=='output_exists':output.write_bytes(b'preserve existing output')
        env={k:v for k,v in os.environ.items() if not k.startswith(('SEMAEV_CHECKPOINT_','FAKE_CHECKPOINT_'))}
        env.update(PATH=str(bin_dir.resolve())+os.pathsep+env['PATH'],FAKE_CHECKPOINT_STORE=str((case/'store').resolve()),
                   SEMAEV_CHECKPOINT_REQUEST=str(request.resolve()),SEMAEV_CHECKPOINT_CONTEXT=str(context_path.resolve()),
                   SEMAEV_CHECKPOINT_DIR=str(snapshots.resolve()),SEMAEV_CHECKPOINT_S3_PREFIX='s3://fake-bucket/guard',
                   SEMAEV_CHECKPOINT_PRUNE_LOCAL='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
        steps=[]
        def run(label,argv,extra=None,expected=0):
            cmd=['prlimit','--as=1073741824','--',*map(str,argv)];started=time.time()
            p=subprocess.run(cmd,env=dict(env,**(extra or {})),capture_output=True,timeout=120)
            (case/(label+'.stdout')).write_bytes(p.stdout);(case/(label+'.stderr')).write_bytes(p.stderr)
            record=dict(argv=cmd,returncode=p.returncode,expected=expected,elapsed_seconds=time.time()-started,wall_valid=False)
            save(case/(label+'.step.json'),record);steps.append(record);assert p.returncode==expected,(label,p.returncode,expected)
            return p
        row=dict(instance_id=str(index),seed=0,case=name,arm=a.mode,native_started=False)
        try:
            if name=='word_counts':
                assert certificate_size(7,4,64,0)==1616
                assert certificate_size(7,4,65,0)==2408
                assert certificate_size(48,5,187583,0)==45161173824
            elif name.startswith('native_'):
                refused=name=='native_refuse'
                if a.mode=='restored':
                    run('prelaunch',[sys.executable,plan['guard'],'--restore',snapshot],expected=73 if refused else 0)
                if a.mode=='fresh' or not refused:
                    row['native_started']=True
                    run('native',[plan['producer'],plan['seed'],output,'31','1073741824'],
                        dict(SEMAEV_CHECKPOINT_RESTORE=str(snapshot.resolve()),SEMAEV_CHECKPOINT_PUBLISH=plan['guard']),
                        expected=2 if refused else 0)
                assert (not output.exists()) if refused else sha(output)==plan['expected_certificate_sha256']
                decisions=list(work.glob('export-admission-*.json'));assert len(decisions)==1
                decision=json.loads(decisions[0].read_text());assert decision['status']==('export_deferred' if refused else 'allowed')
                assert decision['certificate_bytes']==1616
                if a.mode=='fresh':
                    manifests=list((case/'store').glob('**/manifests/*.json'));assert len(manifests)==1
                    published=json.loads(manifests[0].read_text());assert published['snapshot']['phase']==2
                    obj=case/'store/fake-bucket/guard/objects'/(published['snapshot']['sha256']+'.bin')
                    assert sha(obj)==sha(Path(plan['phase2']))
                else:assert snapshot.exists()
            else:
                boundary=name.startswith('boundary_');restore=a.mode=='restored' or boundary
                args=[sys.executable,plan['guard'],*(['--restore'] if restore else []),snapshot]
                expected=73 if name=='boundary_short' else (1 if name in ('wrong_request','wrong_dimensions','corrupt_snapshot','output_exists') else 0)
                run('guard',args,expected=expected)
                if expected==1:
                    assert not (case/'store').exists() and snapshot.exists()
                    if name=='output_exists':assert output.read_bytes()==b'preserve existing output'
                elif name=='phase1':assert not list(work.glob('export-admission-*.json'))
                elif boundary:
                    d=json.loads(next(work.glob('export-admission-*.json')).read_text())
                    assert d['admitted_output_limit_bytes']==1616-(name=='boundary_short')
            row['passed']=True
        except Exception as error:
            row.update(passed=False,error=repr(error))
        row['steps']=len(steps);save(case/'result.json',row);rows.append(row)
    result=dict(scope='Local software controls with fake storage; no frontier or mathematical inference',
                plan_sha256=sha(a.plan),protocol_sha256=protocol['freeze']['protocol_sha256'],mode=a.mode,
                rows=rows,passed=all(r['passed'] for r in rows))
    save(a.out/'result.json',result);print(json.dumps(result));return int(not result['passed'])


if __name__=='__main__':
    raise SystemExit(main())
