#!/usr/bin/env python3
"""Exact packaged-worker controls across separate source and restore pods."""
import argparse,hashlib,json,os,shutil,subprocess,time
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):
 with p.open('x') as f:json.dump(d,f,indent=2);f.write('\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--bundle',type=Path,required=True);ap.add_argument('--protocol',type=Path,required=True);ap.add_argument('--mode',choices=['source','restored'],required=True);ap.add_argument('--source-prefix');a=ap.parse_args()
 if a.mode=='restored' and not a.source_prefix:raise ValueError('source prefix required')
 m=json.loads((a.bundle/'manifest.json').read_text());p=json.loads(a.protocol.read_text());assert p['freeze']['status']=='frozen'
 for name,digest in m['files'].items():assert sha(a.bundle/name)==digest,name
 out=Path('/work/results/worker-control');out.mkdir(exist_ok=False);target=os.environ['ISOLAB_RESULTS_URI'].rstrip('/');rows=[]
 def upload(path):subprocess.run(['aws','s3','cp',str(path),target+'/worker-control/'+str(path.relative_to(out)),'--only-show-errors'],check=True,timeout=120)
 save(out/'environment.json',dict(mode=a.mode,source_prefix=a.source_prefix,target=target,protocol_sha256=p['freeze']['protocol_sha256'],manifest_sha256=sha(a.bundle/'manifest.json')));upload(out/'environment.json')
 for i,f in enumerate(m['fixtures']):
  for mode in (['fresh','source'] if a.mode=='source' else ['restored']):
   case=out/(str(i)+'-'+mode);case.mkdir();work=Path('/work/results/lift');assert not work.exists()
   argv=['python3',str(a.bundle/'run_lift_worker_checkpoint.py'),'--bundle',str(a.bundle),'--request',str(a.bundle/f['request']),'--protocol',str(a.protocol),'--out',str(work),'--upload']
   if mode=='source':argv+=['--control-source']
   if mode=='restored':argv+=['--restore-prefix',a.source_prefix.rstrip('/')+f'/worker-controls/{i}/source/lift/checkpoints']
   env=dict(os.environ,ISOLAB_RESULTS_URI=target+f'/worker-controls/{i}/{mode}')
   save(case/'launch.json',dict(argv=argv,unix_time=time.time(),worker_target=env['ISOLAB_RESULTS_URI']));upload(case/'launch.json')
   row=dict(arm=mode,instance_id=str(i),seed=0,passed=False)
   try:
    with (case/'stdout').open('xb') as stdout,(case/'stderr').open('xb') as stderr:child=subprocess.run(argv,env=env,stdout=stdout,stderr=stderr,timeout=900)
    row['returncode']=child.returncode;assert child.returncode==0
    d=json.loads((work/'result.json').read_text());row['status']=d['status'];assert d['exact_solutions']==f['count'];assert d.get('last_fall_degree_lower_bound') is None
    if mode=='source':assert d['status']=='checkpointed_control'
    else:
     assert d['status']=='certificate_verified' and d['certificate_sha256']==f['expected_sha256']
     assert d['certified_codimension_lower_bound']==f['count']
    if mode=='restored':assert json.loads((work/'restore.json').read_text())['status']=='checkpoint_restored'
    row['passed']=True
   except Exception as error:row['error']=repr(error)
   finally:
    if work.exists():shutil.move(str(work),str(case/'work'))
   save(case/'result.json',row);rows.append(row)
   for name in ['stdout','stderr','result.json']:
    if (case/name).exists():upload(case/name)
 result=dict(rows=rows,passed=all(x['passed'] for x in rows),scope='Fixed cloud worker controls; no frontier or new mathematical bound');save(out/'result.json',result);upload(out/'result.json');print(json.dumps(result));return int(not result['passed'])
if __name__=='__main__':raise SystemExit(main())
