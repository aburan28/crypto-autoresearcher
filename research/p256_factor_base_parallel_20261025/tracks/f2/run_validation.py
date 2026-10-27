#!/usr/bin/env python3
"""Fail-closed exact-check launcher; each attempt has a fresh receipt directory."""
import argparse,contextlib,hashlib,json,os,subprocess,sys,time,traceback
from datetime import datetime,timezone
from pathlib import Path

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--label',required=True)
    parser.add_argument('--inject',choices=['exception','early_return'])
    args=parser.parse_args()
    root=Path(__file__).resolve().parent
    if not args.label.replace('-','').replace('_','').isalnum():
        parser.error('label must contain only letters, digits, hyphens and underscores')
    out=root/'receipts'/args.label
    out.mkdir(exist_ok=False)
    start=datetime.now(timezone.utc).isoformat();t0=time.monotonic()
    source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.glob('*.py')}
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=root,capture_output=True,text=True)
    dirty=subprocess.run(['git','status','--porcelain','--untracked-files=no'],cwd=root,capture_output=True,text=True)
    record=dict(command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),
       started=start,source_sha256=source_hashes,git_commit=git.stdout.strip(),
       dirty_tree=bool(dirty.stdout),dirty_tracked_paths=dirty.stdout.splitlines(),
       scope='software validation; no scientific trial',injection=args.inject,
       inference=dict(policy='executor-implementation',runtime='native Codex inherited model',
                      binding_probe_status='unprobed per instruction',fallback_used=False,degraded=False))
    result=None;error=None
    with (out/'stdout.txt').open('w') as stdout,(out/'stderr.txt').open('w') as stderr:
        with contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):
            try:
                from check_impl import run
                result=run(out,args.inject)
                if not isinstance(result,dict) or result.get('completion_sentinel')!='F2_EXACT_CHECKS_COMPLETE':
                    raise RuntimeError('completion sentinel missing')
                print(json.dumps({'status':result['status'],'checks':result['checks'],'case_count':result['complete_enumerated_cases']}))
            except BaseException as exception:
                error=type(exception).__name__+': '+str(exception)
                traceback.print_exc()
    record.update(finished=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-t0,
                  outcome='PASS' if error is None else 'FAIL',error=error)
    record['artifact_sha256']={str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in sorted(out.rglob('*')) if p.is_file()}
    (out/'receipt.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'attempt':args.label,'outcome':record['outcome'],'error':error,'receipt':str(out/'receipt.json')}))
    return 0 if error is None else 1

if __name__=='__main__': sys.exit(main())
