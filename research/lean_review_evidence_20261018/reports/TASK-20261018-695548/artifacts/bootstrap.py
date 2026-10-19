from pathlib import Path
import hashlib, io, json, os, platform, shutil, subprocess, tarfile

REPORT = Path(__file__).resolve().parents[1]
ART = REPORT/'artifacts'
REVIEW = Path('/workspace/review-lean-evidence')
FROZEN = Path('/workspace/lean-review-repairs')
SCRATCH = Path('/tmp/TASK-20261018-695548')
REV = 'aaccd2f5d0a801fd73209e2a51b587efbda3ee5e'
assert not SCRATCH.exists(), 'preserve previous attempts; choose a new scratch path'
SCRATCH.mkdir()
manifest = json.loads((REVIEW/'research/lean_review_evidence_20261018/repair-inputs.json').read_text())
observations=[]
for f in manifest['files']:
    src=FROZEN/f['repository']/f['path']
    content=src.read_bytes()
    row={**f, 'snapshot_sha256': hashlib.sha256(content).hexdigest()}
    assert row['snapshot_sha256']==f['sha256'], row
    dst=ART/'bound-sources'/f['repository']/f['path']
    dst.parent.mkdir(parents=True,exist_ok=True); dst.write_bytes(content)
    repo=REVIEW if f['repository']=='review' else Path('/workspace')/f['repository']
    blob=subprocess.run(['git','show',f"{f['revision']}:{f['path']}"],cwd=repo,capture_output=True)
    row['git_blob_returncode']=blob.returncode
    row['git_blob_sha256']=hashlib.sha256(blob.stdout).hexdigest() if blob.returncode==0 else None
    row['matches_bound_git']=row['git_blob_sha256']==f['sha256']
    observations.append(row)
(ART/'input-bindings.json').write_text(json.dumps(observations,indent=2)+'\n')
assert all(r['matches_bound_git'] for r in observations)
paths=['orchestration/formal','orchestration/fast_yaml.py','orchestration/__init__.py',
       'formal/smoke','formal/AxiomAudit.lean','tests/test_lean_live.py','tools/check_review_independence.py']
archive=subprocess.run(['git','archive',REV,*paths],cwd=REVIEW,capture_output=True,check=True).stdout
runtime=SCRATCH/'runtime'; runtime.mkdir()
with tarfile.open(fileobj=io.BytesIO(archive)) as t:t.extractall(runtime,filter='data')
for p in (FROZEN/'crypto-autoresearcher/orchestration/formal').glob('*.py'):
    shutil.copy2(p,runtime/'orchestration/formal'/p.name)
shutil.copy2(FROZEN/'crypto-autoresearcher/tests/test_lean_live.py',runtime/'tests/test_lean_live.py')
for p in runtime.rglob('*'):
    if p.is_file():
        dst=ART/'runtime-sources'/p.relative_to(runtime)
        dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
env={**os.environ,'PATH':'/workspace/.elan/bin:'+os.environ['PATH'],
     'ELAN_HOME':'/workspace/.elan','XDG_CACHE_HOME':'/workspace/.cache',
     'PYTHONDONTWRITEBYTECODE':'1'}
observed={'python':platform.python_version(),'platform':platform.platform(),
          'cpu_count':os.cpu_count(),'scratch':str(SCRATCH),'runtime_revision':REV,
          'plan_commit':'d47080d59f4b5b54ffd29df46d8089c5665689c5'}
for label,cmd in [('lean_version',['lake','env','lean','--version']),('lake_version',['lake','--version'])]:
    p=subprocess.run(cmd,cwd=runtime/'formal/smoke',env=env,capture_output=True,text=True)
    observed[label]={'command':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
(ART/'environment.json').write_text(json.dumps(observed,indent=2)+'\n')
print(json.dumps({'files_bound':len(observations),'all_match':True,'scratch':str(SCRATCH),'environment':observed}))
