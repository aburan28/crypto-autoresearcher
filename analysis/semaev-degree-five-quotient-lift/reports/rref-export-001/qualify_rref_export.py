"""Frozen exact software controls for the separate D4 RREF exporter."""
import argparse, hashlib, json, os, struct, subprocess
from pathlib import Path
from test_quotient_lift import independent_conditions

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):
 with Path(p).open('x') as f:json.dump(d,f,indent=2);f.write('\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--plan',type=Path,required=True);ap.add_argument('--protocol',type=Path,required=True);a=ap.parse_args()
 p=json.loads(a.plan.read_text());protocol=json.loads(a.protocol.read_text());assert protocol['freeze']['status']=='frozen' and protocol['links']['plan_sha256']==sha(a.plan)
 for file,digest in p['hashes'].items():assert sha(file)==digest,file
 out=Path(p['output_root']);out.mkdir(exist_ok=False);rows=[]
 for i,fixture in enumerate(p['fixtures']):
  expected=None
  for arm in ['reference','candidate']:
   root=out/f'{i}-{arm}';root.mkdir();row=dict(instance_id=str(i),arm=arm,seed=0,passed=False)
   cert=root/'certificate.bin';argv=['prlimit','--as=1073741824','--',p[arm],str(fixture['degree']),'1','20',str(cert)]
   save(root/'launch.json',{'argv':argv,'input_sha256':sha(fixture['input'])})
   try:
    with open(fixture['input'],'rb') as inp,(root/'stdout.txt').open('xb') as so,(root/'stderr.txt').open('xb') as se:
     run=subprocess.run(argv,stdin=inp,stdout=so,stderr=se,timeout=180,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
    row['returncode']=run.returncode;assert run.returncode==0
    if fixture.get('contains_one'):
     assert f"W{fixture['degree']}_one 1" in (root/'stdout.txt').read_text() and not cert.exists();row['contains_one']=True
    else:
     data=cert.read_bytes();digest=sha(cert)
     if arm=='reference':expected=data
     else:assert data==expected,'certificate bytes differ'
     if fixture.get('expected_sha256'):assert digest==fixture['expected_sha256']
     n,d,cols,q=struct.unpack_from('<4q',data);assert d==fixture['degree'];masks=struct.unpack_from('<'+'Q'*cols,data,32);width=8*((q+63)//64);offset=32+8*cols
     assert len(data)==offset+cols*width
     images={m:int.from_bytes(data[offset+j*width:offset+(j+1)*width],'little') for j,m in enumerate(masks)}
     independent_conditions(n,d,images,q,[set(x) for x in fixture['polys']])
     if fixture.get('checker_argv'):
      cmd=fixture['checker_argv'].copy();cmd[2]=str(cert)
      with (root/'checker.stdout.txt').open('xb') as so,(root/'checker.stderr.txt').open('xb') as se:checked=subprocess.run(['prlimit','--as=1073741824','--']+cmd,stdout=so,stderr=se,timeout=180)
      assert checked.returncode==0 and 'VALID' in (root/'checker.stdout.txt').read_text()
     row.update(certificate_sha256=digest,codimension=q,independent_check=True,reference_byte_identity=True)
    row['passed']=True
   except Exception as error:row['error']=repr(error)
   save(root/'result.json',row);rows.append(row);print(json.dumps(row),flush=True)
 result={'rows':rows,'passed':all(x['passed'] for x in rows),'scope':'Exact exporter equivalence controls; no measured speed comparison'};save(out/'result.json',result);return int(not result['passed'])
if __name__=='__main__':raise SystemExit(main())
