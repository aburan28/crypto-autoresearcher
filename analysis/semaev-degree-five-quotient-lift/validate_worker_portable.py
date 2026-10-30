#!/usr/bin/env python3
"""Software-only worker qualification, with optional durable result upload."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--bundle',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--upload',action='store_true')
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    manifest=json.loads((args.bundle/'manifest.json').read_text())
    for name,digest in manifest['files'].items():
        if sha(args.bundle/name)!=digest:raise ValueError('Bundle hash mismatch: '+name)
    records=[]
    try:
        for fixture in manifest['fixtures']:
            root=args.out/str(fixture['index']);root.mkdir()
            system=(args.bundle/fixture['system']).read_text()
            lines=system.splitlines();n,_=map(int,lines[0].split())
            polys=[list(map(lambda x:int(x,16),line.split()[1:])) for line in lines[1:]]
            exhaustive=sum(all(sum((a&m)==m for m in poly)%2==0 for poly in polys) for a in range(1<<n))
            cert=root/'certificate.bin';steps=[]
            def run(name,argv,stdin=None):
                argv=list(map(str,argv));r=subprocess.run(argv,input=stdin,text=True,capture_output=True,timeout=90,env={**os.environ,'OMP_NUM_THREADS':'1'})
                (root/(name+'.stdout.txt')).write_text(r.stdout);(root/(name+'.stderr.txt')).write_text(r.stderr)
                steps.append(dict(name=name,argv=argv,returncode=r.returncode))
                (root/'steps.json').write_text(json.dumps(steps,indent=2)+'\n')
                if r.returncode:raise RuntimeError(name+' failed, returncode='+str(r.returncode)+': '+r.stderr)
                return r.stdout
            run('producer',[args.bundle/'bin/lfdclose2_worker',4,0,20,cert],system)
            if sha(cert)!=fixture['expected_certificate_sha256']:raise ValueError('Worker output differs from original local reference')
            output=run('checker',[sys.executable,args.bundle/'cert_check.py',cert,fixture['n'],fixture['modulus'],0,3,2,*fixture['basis']])
            if 'VALID: 1 is not in W_4(F)' not in output:raise ValueError('Checker did not accept')
            count=int(run('count',[args.bundle/'bin/count_by_sum_worker',fixture['n'],fixture['modulus'],2,3,len(fixture['basis']),*fixture['basis']]).strip())
            if count!=exhaustive:raise ValueError('Count differs from full Boolean enumeration')
            (root/'steps.json').write_text(json.dumps(steps,indent=2)+'\n')
            records.append(dict(index=fixture['index'],certificate_sha256=sha(cert),count=count,exhaustive_count=exhaustive,independent_checker=True,reference_byte_identity=True))
        result=dict(scope='Software qualification only; no frontier trial or timing claim',status='passed',python=platform.python_version(),machine=platform.machine(),manifest_sha256=sha(args.bundle/'manifest.json'),fixtures=records)
    except Exception as e:
        result=dict(scope='Software qualification only',status='failed',error=str(e),fixtures=records)
    (args.out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    checks={str(p.relative_to(args.out)):sha(p) for p in args.out.rglob('*') if p.is_file()}
    (args.out/'hashes.json').write_text(json.dumps(checks,indent=2,sort_keys=True)+'\n')
    if args.upload:
        target=os.environ['ISOLAB_RESULTS_URI'].rstrip('/')+'/worker-control/'
        subprocess.run(['aws','s3','cp',str(args.out),target,'--recursive','--only-show-errors'],check=True)
    print(json.dumps(result,sort_keys=True),flush=True)
    return 0 if result['status']=='passed' else 1


if __name__=='__main__':
    sys.exit(main())
