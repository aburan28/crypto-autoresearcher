#!/usr/bin/env python3
"""Two actual worker paths; binding rejection assertions belong to reuse row."""
import argparse,copy,hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
from verify_seed_acceptance import verify

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):
 with p.open('x') as f:json.dump(d,f,indent=2);f.write('\n')
def negatives(bundle,request,out):
 names=['capsule_hash','seed_bytes','target','checker','failed_step','timeout','stdout','argv','original_request','worker','transfer','evidence_path']
 results=[]
 for name in names:
  root=out/name;shutil.copytree(bundle/'acceptance',root)
  cap=root/'capsule.json';data=json.loads(cap.read_text());req=copy.deepcopy(request)
  seed=root/'seed.bin';import gzip
  seed.write_bytes(gzip.decompress((bundle/'seed-0.gz').read_bytes()));checker=bundle/'cert_check.py'
  key=None
  if name=='seed_bytes':seed.write_bytes(b'x'+seed.read_bytes()[1:])
  elif name=='target':req['record']['z_hex']='3'
  elif name=='checker':checker=root/'wrong.py';checker.write_text('not the checker')
  elif name in ['failed_step','timeout']:
   key='step';p=root/data['evidence'][key]['path'];x=json.loads(p.read_text());x['returncode' if name=='failed_step' else 'timeout']=1 if name=='failed_step' else True;p.write_text(json.dumps(x))
  elif name=='stdout':key='stdout';(root/data['evidence'][key]['path']).write_text('INVALID\n')
  elif name=='argv':
   key='argv';p=root/data['evidence'][key]['path'];x=json.loads(p.read_text());x[-1]='8';p.write_text(json.dumps(x))
  elif name=='original_request':
   key='request';p=root/data['evidence'][key]['path'];x=json.loads(p.read_text());x['worker_manifest_sha256']='0'*64;p.write_text(json.dumps(x))
  elif name=='worker':key='worker';(root/data['evidence'][key]['path']).write_text('changed worker')
  elif name=='transfer':
   key='seed_transfer';p=root/data['evidence'][key]['path'];x=json.loads(p.read_text());x['bytes']+=1;p.write_text(json.dumps(x))
  elif name=='evidence_path':data['evidence']['stdout']['path']='../outside.txt';(out/'outside.txt').write_text('outside')
  if key:
   p=root/data['evidence'][key]['path'];data['evidence'][key].update(bytes=p.stat().st_size,sha256=sha(p))
  cap.write_text(json.dumps(data));req['seed_acceptance']['sha256']=sha(cap) if name!='capsule_hash' else '0'*64
  try:verify(cap,req,checker,seed)
  except (ValueError,KeyError,FileNotFoundError) as error:results.append(dict(case=name,rejected=True,error=str(error)))
  else:results.append(dict(case=name,rejected=False))
 save(out/'results.json',results)
 assert all(x['rejected'] for x in results),results
 return results

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--plan',type=Path,required=True);ap.add_argument('--protocol',type=Path,required=True);a=ap.parse_args()
 plan=json.loads(a.plan.read_text());protocol=json.loads(a.protocol.read_text());assert protocol['freeze']['status']=='frozen'
 for p,h in plan['hashes'].items():assert sha(Path(p))==h,p
 out=Path(plan['output_root']);out.mkdir(exist_ok=False);root=Path(plan['work_root']);bundle=root/'bundle';bin_dir=root/'bin';bin_dir.mkdir();shutil.copy2(plan['fake_aws'],bin_dir/'aws');(bin_dir/'aws').chmod(0o755)
 env=dict(os.environ,PATH=str(bin_dir)+os.pathsep+os.environ['PATH'],FAKE_CHECKPOINT_STORE=str(out/'store'))
 rows=[]
 for mode in ['fresh','reuse']:
  case=out/mode;case.mkdir();work=root/'work';assert not work.exists();request=root/('request-'+mode+'.json')
  argv=[plan['python'],str(bundle/'run_lift_worker_checkpoint_reuse.py'),'--bundle',str(bundle),'--request',str(request),'--protocol',str(a.protocol.resolve()),'--out',str(work),'--checkpoint-prefix','s3://fake-bucket/seed-reuse/'+mode]
  row=dict(arm=mode,instance_id='0',seed=0,passed=False);save(case/'launch.json',{'argv':argv})
  try:
   if mode=='reuse':
    neg=case/'negative-bindings';neg.mkdir();row['binding_controls']=negatives(bundle,json.loads(request.read_text()),neg)
   with (case/'stdout').open('xb') as so,(case/'stderr').open('xb') as se:child=subprocess.run(argv,env=env,stdout=so,stderr=se,timeout=900)
   row['returncode']=child.returncode;assert child.returncode==0
   r=json.loads((work/'result.json').read_text());assert r['status']=='certificate_verified'
   assert r['certificate_sha256']==plan['expected_certificate_sha256'];assert r['exact_solutions']==3;assert r['certified_codimension_lower_bound']==3;assert r.get('last_fall_degree_lower_bound') is None
   assert r['seed_check_origin']==('historical_acceptance_reused' if mode=='reuse' else 'fresh_independent_check')
   assert (work/'check4.finished.json').exists()==(mode=='fresh')
   assert (work/'check5.finished.json').exists() and (work/'count.finished.json').exists()
   row.update(passed=True,certificate_sha256=r['certificate_sha256'],exact_solutions=r['exact_solutions'],seed_check_origin=r['seed_check_origin'])
  except Exception as e:row['error']=repr(e)
  finally:
   if work.exists():shutil.move(str(work),str(case/'work'))
  save(case/'result.json',row);rows.append(row)
 result=dict(rows=rows,passed=all(r['passed'] for r in rows),scope='Local worker evidence reuse qualification only; no frontier or new LFD bound');save(out/'result.json',result);print(json.dumps(result));return int(not result['passed'])
if __name__=='__main__':raise SystemExit(main())
