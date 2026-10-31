from pathlib import Path
import hashlib,json,os,subprocess,sys
base=Path(__file__).resolve().parent
seal=json.loads((base/'SEAL.json').read_text())
for name,want in seal['files'].items():
 p=base/name
 assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==want,name
actual={str(p.relative_to(base)) for p in base.rglob('*') if p.is_file() and p.name!='SEAL.json' and '__pycache__' not in p.parts}
assert actual==set(seal['files']),sorted(actual.symmetric_difference(seal['files']))
parent=json.loads((base/'PROTOCOL.json').read_text());assert len(parent['controls'])==9
for job in parent['controls']:
 d=base/'runs'/job['id'];r=json.loads((d/'RESULT.json').read_text())
 assert r['job']==job and r['exit_code']==2 and not r['native_complete']
 assert b'AUDIT TABLE_UNAVAILABLE' in (d/'stdout.raw').read_bytes()
 for kind in ['stdout','stderr']:assert hashlib.sha256((d/(kind+'.raw')).read_bytes()).hexdigest()==r[kind+'_sha256']
assert not list((base/'runs').glob('case-*'))
proc=subprocess.run([sys.executable,'-B',str(base/'attempt-02/audit.py')],capture_output=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert proc.returncode==0,proc.stderr.decode(errors='replace')
observed=json.loads(proc.stdout);expected=json.loads((base/'attempt-02/AUDIT.json').read_text())
assert observed==expected and observed['status']=='PASS'
print(json.dumps({'status':'PASS','sealed_files':len(seal['files']),'initial_missing_table_controls':9,'successful_specializations':observed['successful_specializations'],'rational_modular_roots':observed['rational_modular_roots'],'kernel_profile_checks':observed['kernel_profile_checks'],'atkin_specializations':observed['atkin_specializations'],'native_programs_launched_by_replay':0,'historical_criterion_identified':False},indent=2))
