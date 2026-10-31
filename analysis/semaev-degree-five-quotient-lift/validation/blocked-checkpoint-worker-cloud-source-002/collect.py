import json,hashlib,sys,tarfile,subprocess
from pathlib import Path
s=Path('/home/ec2-user/crypto-autoresearcher-fall-degree-submission-20261029/analysis/semaev-degree-five-quotient-lift')
sys.path.insert(0,str(s));from publish_lift_checkpoint import inspect_snapshot
root=Path('/home/ec2-user/fall-degree-runtime-20261029/blocked-cloud-source-v2-raw');root.mkdir(exist_ok=False)
prefix='s3://isolab-results-104186811093-us-east-2/runs/semaev-blocked-worker-source-v2-20261030-2055/bbe03960-0d90-4ef8-805f-4dcc6a21854e/'
subprocess.run(['aws','s3','cp',prefix,str(root),'--recursive','--only-show-errors'],check=True)
d=json.loads((root/'worker-control/result.json').read_text());assert d['passed'] and len(d['rows'])==6 and all(x['passed'] for x in d['rows'])
p=json.loads((s/'blocked-checkpoint-worker-cloud-protocol-002.json').read_text());fixtures=json.loads((s/'runtime/blocked-checkpoint-worker-cloud-001/manifest.json').read_text())['fixtures']
verified=[]
for i,f in enumerate(fixtures):
 for mode in ['fresh','source']:
  w=root/f'worker-controls/{i}/{mode}/lift';r=json.loads((w/'result.json').read_text());assert r['exact_solutions']==f['count']
  assert r['steps']['count']['returncode']==0 and r['steps']['check4']['returncode']==0
  if mode=='fresh':
   assert r['status']=='certificate_verified' and r['certificate_sha256']==f['expected_sha256'] and r['steps']['check5']['returncode']==0
   cert=w/'certificate.bin';assert hashlib.sha256(cert.read_bytes()).hexdigest()==f['expected_sha256']
  else:
   assert r['status']=='checkpointed_control';context=json.loads((w/'environment.json').read_text())['context'];assert context['protocol_sha256']==p['freeze']['protocol_sha256']
   mans=sorted((w/'checkpoints/manifests').glob('*.json'));assert mans
   for m in mans:
    assert hashlib.sha256(m.read_bytes()).hexdigest()==m.stem.split('-')[1]
    md=json.loads(m.read_text());assert md['context']==context
    obj=w/'checkpoints/objects'/Path(md['snapshot_uri']).name;assert inspect_snapshot(obj)==md['snapshot']
   verified.append({'fixture':i,'manifests_verified':len(mans),'last_sequence':json.loads(mans[-1].read_text())['snapshot']['sequence']})
v=s/'validation/blocked-checkpoint-worker-cloud-source-002';v.mkdir()
files=[{'path':str(f.relative_to(root)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(root.rglob('*')) if f.is_file()]
with tarfile.open(v/'raw-evidence.tar.gz','w:gz') as t:
 for f in files:t.add(root/f['path'],arcname=f['path'],recursive=False)
(v/'raw-manifest.json').write_text(json.dumps({'prefix':prefix,'files':files},indent=2)+'\n');(v/'result.json').write_text(json.dumps(d,indent=2)+'\n');(v/'checkpoint-verification.json').write_text(json.dumps(verified,indent=2)+'\n');print(len(files),'files; all six source controls and checkpoint object hashes verified')
