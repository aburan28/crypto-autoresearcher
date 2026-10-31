"""Read-only replay; --fibers also requires python-flint0.9.0."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent
def main():
    manifest=json.loads((P/'MANIFEST.json').read_text())
    actual={str(f.relative_to(P)) for f in P.rglob('*') if f.is_file() and f.name not in ['MANIFEST.json','SEAL.json']}
    assert actual==set(manifest),(actual-set(manifest),set(manifest)-actual)
    for name,h in manifest.items():assert hashlib.sha256((P/name).read_bytes()).hexdigest()==h,name
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
    scripts=['canonical-equations-01/audit.py','ccr-recovery/audit_formula.py']
    if '--fibers' in sys.argv:scripts+=['canonical-equations-01/audit_fibers.py']
    for name in scripts:subprocess.run([sys.executable,'-B',str(P/name),'--check'],check=True,env=env)
    print(json.dumps({'status':'PASS','sealed_files':len(manifest),'fiber_root_completeness_replayed':'--fibers' in sys.argv,'external_producer_processes':0,'in_process_native_extension':'python-flint0.9.0 when --fibers is requested'},sort_keys=True))
if __name__=='__main__':main()
