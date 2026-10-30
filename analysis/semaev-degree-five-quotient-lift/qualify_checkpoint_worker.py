#!/usr/bin/env python3
"""Run all nine frozen worker controls; retain each actual outcome."""
import argparse,hashlib,json,os,shutil,subprocess,time
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):
 with p.open('x') as f:json.dump(d,f,indent=2);f.write('\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--plan',type=Path,required=True);ap.add_argument('--protocol',type=Path,required=True);a=ap.parse_args()
 plan=json.loads(a.plan.read_text());protocol=json.loads(a.protocol.read_text());assert protocol['freeze']['status']=='frozen'
 for name,digest in plan['hashes'].items():assert sha(Path(name))==digest,name
 out=Path(plan['output_root']);out.mkdir(exist_ok=False);root=Path(plan['work_root']);bundle=root/'bundle';bin_dir=root/'bin';bin_dir.mkdir();shutil.copy2(plan['fake_aws'],bin_dir/'aws');(bin_dir/'aws').chmod(0o755)
 env=dict(os.environ,PATH=str(bin_dir)+os.pathsep+os.environ['PATH'],FAKE_CHECKPOINT_STORE=str(out/'store'))
 rows=[]
 for i,fixture in enumerate(plan['fixtures']):
  source_ok=False
  for mode in ['fresh','source','restored']:
   case=out/(str(i)+'-'+mode);case.mkdir();work=root/'work';assert not work.exists()
   prefix=f's3://fake-bucket/worker/{i}/{mode}'
   argv=[plan['python'],str(bundle/'run_lift_worker_checkpoint.py'),'--bundle',str(bundle),'--request',fixture['request'],'--protocol',str(a.protocol.resolve()),'--out',str(work),'--checkpoint-prefix',prefix]
   if mode=='source':argv+=['--control-source']
   if mode=='restored':argv+=['--restore-prefix',f's3://fake-bucket/worker/{i}/source']
   row=dict(arm=mode,instance_id=str(i),seed=0,passed=False)
   save(case/'launch.json',dict(argv=argv,unix_time=time.time()))
   try:
    if mode=='restored' and not source_ok:raise RuntimeError('dependent restore withheld after source failure')
    with (case/'stdout').open('xb') as stdout,(case/'stderr').open('xb') as stderr:
     child=subprocess.run(argv,env=env,stdout=stdout,stderr=stderr,timeout=900)
    row['returncode']=child.returncode;assert child.returncode==0
    result=json.loads((work/'result.json').read_text());row['status']=result['status']
    assert result['exact_solutions']==fixture['count']
    assert result.get('last_fall_degree_lower_bound') is None
    if mode=='source':
     assert result['status']=='checkpointed_control';source_ok=True
    else:
     assert result['status']=='certificate_verified'
     assert result['certificate_sha256']==fixture['expected_sha256']
     assert result['certified_codimension_lower_bound']==fixture['count']
    if mode=='restored':assert json.loads((work/'restore.json').read_text())['status']=='checkpoint_restored'
    row['passed']=True
   except Exception as error:row['error']=repr(error)
   finally:
    if work.exists():shutil.move(str(work),str(case/'work'))
   save(case/'result.json',row);rows.append(row)
 result=dict(rows=rows,passed=all(r['passed'] for r in rows),scope='Local fake-storage worker integration; no new mathematical bound');save(out/'result.json',result);print(json.dumps(result));return int(not result['passed'])
if __name__=='__main__':raise SystemExit(main())
