from pathlib import Path
import hashlib,json,os,platform,shutil,subprocess,time
REPORT=Path(__file__).resolve().parents[1]; ART=REPORT/'artifacts'
REVIEW=Path('/workspace/review-lean-evidence');SCRATCH=Path('/tmp/TASK-20261018-695548')
REV='aaccd2f5d0a801fd73209e2a51b587efbda3ee5e';runtime=SCRATCH/'runtime-v2'
runtime.mkdir()
env={**os.environ,'PATH':'/workspace/.elan/bin:'+os.environ['PATH'],
     'ELAN_HOME':'/workspace/.elan','XDG_CACHE_HOME':'/workspace/.cache',
     'PYTHONDONTWRITEBYTECODE':'1','GIT_NO_LAZY_FETCH':'1'}
paths=[p.relative_to(REVIEW).as_posix() for p in (REVIEW/'orchestration/formal').glob('*.py')]
paths+=['orchestration/fast_yaml.py','orchestration/__init__.py','formal/AxiomAudit.lean','tests/test_lean_live.py']
paths +=[p.relative_to(REVIEW).as_posix() for p in (REVIEW/'formal/smoke').rglob('*') if p.is_file() and '.lake' not in p.parts]
rows=[]
for rel in paths:
    p=subprocess.run(['git','show',REV+':'+rel],cwd=REVIEW,env=env,capture_output=True,timeout=10)
    assert p.returncode==0,(rel,p.stderr)
    dst=runtime/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(p.stdout)
    saved=ART/'runtime-sources'/rel;saved.parent.mkdir(parents=True,exist_ok=True);saved.write_bytes(p.stdout)
    rows.append({'path':rel,'revision':REV,'sha256':hashlib.sha256(p.stdout).hexdigest()})
(ART/'runtime-input-bindings.json').write_text(json.dumps(rows,indent=2)+'\n')
observed={'python':platform.python_version(),'platform':platform.platform(),'cpu_count':os.cpu_count(),
          'scratch':str(SCRATCH),'runtime':str(runtime),'runtime_revision':REV,
          'plan_commit':'d47080d59f4b5b54ffd29df46d8089c5665689c5',
          'initial_failures':['/usr/local/bin/python3 absent; used handoff venv',
          'git archive hung; interrupted without using its output; direct read-only git show used instead']}
for label,cmd in [('lean_version',['lake','env','lean','--version']),('lake_version',['lake','--version'])]:
    p=subprocess.run(cmd,cwd=runtime/'formal/smoke',env=env,capture_output=True,text=True,timeout=30)
    observed[label]={'command':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
(ART/'environment.json').write_text(json.dumps(observed,indent=2)+'\n')
print(json.dumps(observed))
