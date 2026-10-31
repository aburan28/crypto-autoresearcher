import json,hashlib,tarfile,subprocess,sys
from pathlib import Path
s=Path('/home/ec2-user/crypto-autoresearcher-fall-degree-submission-20261029/analysis/semaev-degree-five-quotient-lift');status=json.loads((s/'runs/blocked-worker-cloud-restore-terminal-002.json').read_text());assert status['job']['state']=='succeeded';pod=status['pods'][0]['uid'];assert pod!='bbe03960-0d90-4ef8-805f-4dcc6a21854e'
root=Path('/home/ec2-user/fall-degree-runtime-20261029/blocked-cloud-restore-v2-raw');root.mkdir(exist_ok=False)
prefix=f's3://isolab-results-104186811093-us-east-2/runs/semaev-blocked-worker-restore-v2-20261030-2105/{pod}/';subprocess.run(['aws','s3','cp',prefix,str(root),'--recursive','--only-show-errors'],check=True)
roots={'source':Path('/home/ec2-user/fall-degree-runtime-20261029/blocked-cloud-source-v2-raw'),'restored':root};rows=[];files=[]
for label,path in roots.items():
 d=json.loads((path/'worker-control/result.json').read_text());assert d['passed'];rows+=d['rows']
 files += [{'path':label+'/'+str(f.relative_to(path)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(path.rglob('*')) if f.is_file()]
assert len(rows)==9 and all(x['passed'] for x in rows)
fixtures=json.loads((s/'runtime/blocked-checkpoint-worker-cloud-001/manifest.json').read_text())['fixtures']
for i,f in enumerate(fixtures):
 w=root/f'worker-controls/{i}/restored/lift';d=json.loads((w/'result.json').read_text());assert d['status']=='certificate_verified' and d['exact_solutions']==f['count'] and d['certified_codimension_lower_bound']==f['count'];assert hashlib.sha256((w/'certificate.bin').read_bytes()).hexdigest()==f['expected_sha256'];assert d['steps']['check5']['returncode']==0 and d['steps']['count']['returncode']==0
 r=json.loads((w/'restore.json').read_text());assert r['status']=='checkpoint_restored';assert r['snapshot']['binary_sha256']=='fc0911db6560fe10b49d88d6206f89f8de6494616020a864c82d8be552749613'
v=s/'validation/blocked-checkpoint-worker-cloud-002';v.mkdir()
with tarfile.open(v/'raw-evidence.tar.gz','w:gz') as t:
 for f in files:
  label,rel=f['path'].split('/',1);t.add(roots[label]/rel,arcname=f['path'],recursive=False)
(v/'raw-manifest.json').write_text(json.dumps({'files':files},indent=2)+'\n');(v/'result.json').write_text(json.dumps({'rows':rows,'passed':True,'source_pod':'bbe03960-0d90-4ef8-805f-4dcc6a21854e','restore_pod':pod},indent=2)+'\n');print(len(files),'files;',len(rows),'passed controls')
