import json,hashlib,shutil,tarfile
from pathlib import Path
s=Path('analysis/semaev-degree-five-quotient-lift').resolve();old=Path('/home/ec2-user/fall-degree-runtime-20261029/blocked-checkpoint-worker-001');root=old.with_name('blocked-checkpoint-worker-cloud-001');root.mkdir();b=root/'bundle';b.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
om=json.loads((old/'bundle/manifest.json').read_text())
for name in om['files']:
 dst=b/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/'bundle'/name,dst)
shutil.copy2(s/'qualify_checkpoint_worker_cloud.py',b/'qualify_checkpoint_worker_cloud.py')
plan=json.loads((s/'blocked-checkpoint-worker-plan-001.json').read_text());fixtures=[dict(request=f'request-{i}.json',count=f['count'],expected_sha256=f['expected_sha256']) for i,f in enumerate(plan['fixtures'])]
manifest=dict(files={str(p.relative_to(b)):sha(p) for p in b.rglob('*') if p.is_file()},fixtures=fixtures);save(b/'manifest.json',manifest)
requests=[]
for i in range(3):
 d=json.loads((old/f'request-{i}.json').read_text());d['id']=f'blocked-checkpoint-worker-cloud001-fixture{i}';d['seed_url']=f'file:///work/bundle/seed-{i}.gz';d['worker_manifest_sha256']=sha(b/'manifest.json');d['disk_policy'].update(work_root='/work',certificate_relative_path='results/lift/certificate.bin');save(b/f'request-{i}.json',d);requests.append(sha(b/f'request-{i}.json'))
archive=root.parent/'semaev-blocked-checkpoint-worker-cloud-001.tar.gz'
with tarfile.open(archive,'w:gz') as t:
 for p in sorted(b.rglob('*')):
  if p.is_file():t.add(p,arcname='bundle/'+str(p.relative_to(b)),recursive=False)
meta=dict(archive_path=str(archive),archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,request_sha256s=requests,manifest_sha256=sha(b/'manifest.json'),url='https://github.com/isogeny-labs/crypto-autoresearcher/releases/download/semaev-closure-certificates-20261029/'+archive.name)
r=s/'runtime/blocked-checkpoint-worker-cloud-001';r.mkdir();save(r/'publication-candidate.json',meta);shutil.copy2(b/'manifest.json',r/'manifest.json')
for i in range(3):shutil.copy2(b/f'request-{i}.json',r/f'request-{i}.json')
print(json.dumps(meta))
