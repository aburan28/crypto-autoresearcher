import json,hashlib,gzip,shutil,struct
from pathlib import Path
s=Path('analysis/semaev-degree-five-quotient-lift').resolve();root=Path('/home/ec2-user/fall-degree-runtime-20261029/checkpoint-worker-001');root.mkdir();b=root/'bundle';b.mkdir();old=Path('/home/ec2-user/fall-degree-runtime-20261029/checkpoint-cloud-002');m=json.loads((old/'manifest.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
for name in ['bin/count_by_sum','bin/quotient_lift_checkpoint','cert_check.py','lib/libcrypto.so.3','lib/libz.so.1']:
 p=b/name;p.parent.mkdir(exist_ok=True);shutil.copy2(old/name,p)
for name in ['run_lift_worker_checkpoint.py','run_lift_worker_durable.py','publish_lift_checkpoint.py','restore_lift_checkpoint.py','checkpoint_export_guard.py']:shutil.copy2(s/name,b/name)
for i in range(3):(b/f'seed-{i}.gz').write_bytes(gzip.compress((old/f'seed-{i}.bin').read_bytes(),mtime=0))
manifest={'files':{str(p.relative_to(b)):sha(p) for p in b.rglob('*') if p.is_file()}};save(b/'manifest.json',manifest)
fixtures=[]
for i,f in enumerate(m['fixtures']):
 seed=old/f['seed'];n,d,cols,q=struct.unpack('<4Q',seed.read_bytes()[:32]);gz=b/f'seed-{i}.gz';request=root/f'request-{i}.json'
 req=dict(id=f'checkpoint-worker001-fixture{i}',record=f['record'],seed_url=gz.as_uri(),seed_gzip_sha256=sha(gz),seed_gzip_bytes=gz.stat().st_size,seed_sha256=sha(seed),seed_bytes=seed.stat().st_size,seed_codimension=q,expected_exact_solutions=q,memory_bytes=1<<30,pod_memory_bytes=4<<30,chunk_rows=31,stage_timeout_seconds=120,worker_manifest_sha256=sha(b/'manifest.json'),checkpoint_stop_after=2,disk_policy=dict(N=n,degree=5,working_coordinates=q,capacity_bytes=1<<30,reserve_bytes=16<<20,work_root=str(root),certificate_relative_path='work/certificate.bin'))
 save(request,req);fixtures.append(dict(request=str(request),count=q,expected_sha256=f['expected_sha256']))
plan=dict(schema='semaev.checkpoint-worker-controls/v1',work_root=str(root),output_root='/home/ec2-user/fall-degree-data-20261029/checkpoint-worker-001',python='/home/ec2-user/fall-degree-runtime-20261029/venv/bin/python',fake_aws=str(s/'fake_checkpoint_aws.py'),fixtures=fixtures,hashes={str(p):sha(p) for p in root.rglob('*') if p.is_file()})
for name in ['qualify_checkpoint_worker.py','fake_checkpoint_aws.py']:plan['hashes'][str(s/name)]=sha(s/name)
save(s/'checkpoint-worker-plan-001.json',plan)
print('Prepared runtime and three requests; no trials launched')
