#!/usr/bin/env python3
"""Exact integration controls; actual reference/fresh/source/restored rows."""
import argparse, hashlib, json, os, struct, subprocess
from pathlib import Path
from test_quotient_lift import independent_conditions

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p, x):
    with Path(p).open('x') as f: json.dump(x, f, indent=2); f.write('\n')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--plan',type=Path,required=True); ap.add_argument('--protocol',type=Path,required=True); a=ap.parse_args()
    plan=json.loads(a.plan.read_text()); protocol=json.loads(a.protocol.read_text())
    assert protocol['freeze']['status']=='frozen'
    assert protocol['links']['plan_sha256']==sha(a.plan)
    for p,h in plan['hashes'].items(): assert sha(p)==h,p
    out=Path(plan['output_root']); out.mkdir(exist_ok=False)
    rows=[]; ranks=[]
    for i, fixture in enumerate(plan['fixtures']):
        latest=None
        for mode in ['reference','fresh','source','restored']:
            case=out/f'{i}-{mode}'; case.mkdir()
            row=dict(instance_id=str(i),arm=mode,seed=0,passed=False)
            env={k:v for k,v in os.environ.items() if not k.startswith('SEMAEV_')}
            env.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
            binary=plan['reference'] if mode=='reference' else plan['candidate']
            argv=['prlimit','--as=1073741824','--',binary,fixture['seed'],str(case/'certificate.bin'),'4096',str(2**30)]
            try:
                if mode in ['source','restored']:
                    env['SEMAEV_CHECKPOINT_DIR']=str(case/'snapshots')
                    if mode=='source': env['SEMAEV_CHECKPOINT_STOP_AFTER']='2'
                    else:
                        assert latest is not None,'source did not complete'
                        env['SEMAEV_CHECKPOINT_RESTORE']=str(latest)
                save(case/'launch.json',dict(argv=argv,checkpoint_env={k:v for k,v in env.items() if k.startswith('SEMAEV_')}))
                with (case/'stdout.txt').open('xb') as so,(case/'stderr.txt').open('xb') as se:
                    run=subprocess.run(argv,env=env,stdout=so,stderr=se,timeout=900)
                row['returncode']=run.returncode
                if mode=='source':
                    assert run.returncode==75
                    snaps=sorted((case/'snapshots').glob('checkpoint-*.bin'),key=lambda p:int(p.stem.split('-')[1]))
                    assert len(snaps)==2
                    latest=snaps[-1]; h=struct.unpack('<14Q',latest.read_bytes()[:112])
                    row.update(checkpoint_sha256=sha(latest),checkpoint_rank=h[12],checkpoint_generation=h[13])
                    ranks.append(h[12]); assert not (case/'certificate.bin').exists()
                else:
                    assert run.returncode==0
                    cert=case/'certificate.bin'; assert sha(cert)==fixture['expected_sha256']
                    row['certificate_sha256']=sha(cert)
                    if mode=='restored': assert 'restored checkpoint 2 ' in (case/'stderr.txt').read_text()
                    if fixture['kind']=='generic':
                        data=cert.read_bytes(); n,d,cols,q=struct.unpack_from('<4q',data)
                        masks=struct.unpack_from('<'+'Q'*cols,data,32); width=8*((q+63)//64); offset=32+8*cols
                        images={m:int.from_bytes(data[offset+j*width:offset+(j+1)*width],'little') for j,m in enumerate(masks)}
                        independent_conditions(n,d,images,q,[set(p) for p in fixture['polys']])
                    else:
                        check=fixture['checker_argv'].copy(); check[2]=str(cert)
                        with (case/'checker.stdout.txt').open('xb') as so,(case/'checker.stderr.txt').open('xb') as se:
                            checked=subprocess.run(['prlimit','--as=1073741824','--']+check,stdout=so,stderr=se,timeout=900)
                        assert checked.returncode==0
                        assert 'VALID' in (case/'checker.stdout.txt').read_text()
                    row['independent_check']=True
                row['passed']=True
            except Exception as error: row['error']=repr(error)
            save(case/'result.json',row); rows.append(row); print(json.dumps(row),flush=True)
    result=dict(rows=rows,passed=all(r['passed'] for r in rows) and any(ranks),nonempty_checkpoint_covered=any(ranks),scope='Native integration only; no new bound, cloud qualification or speed claim')
    save(out/'result.json',result); return int(not result['passed'])
if __name__=='__main__': raise SystemExit(main())
