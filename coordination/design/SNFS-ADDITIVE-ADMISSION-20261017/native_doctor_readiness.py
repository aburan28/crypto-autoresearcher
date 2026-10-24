"""Bounded native connectivity/config readiness only; no inference or secret output."""
import hashlib,json,os,re,subprocess
from pathlib import Path
BASE=Path(__file__).resolve().parent
for name in ['runtime-state','runtime-log']:(BASE/name).mkdir(exist_ok=True)
argv=['/opt/codex/bin/codex','--strict-config','-c',f'sqlite_home="{BASE / "runtime-state"}"','-c',f'log_dir="{BASE / "runtime-log"}"','doctor','--summary','--no-color','--ascii']
keys={'config','auth','state','threads','network','websocket','reachability','sandbox','app-server','runtime','install'}
report={'kind':'native_readiness_only','argv':argv,'home_variables_overridden':False,'secret_material_read_or_copied_by_script':False,'inference_invocations':0,'session_probe_performed':False,'configured_model_binding_changed':False,'timeout_seconds':45}
try:
 p=subprocess.run(argv,cwd=BASE.parents[2],capture_output=True,text=True,timeout=45)
 rows=[]
 for line in p.stdout.splitlines():
  m=re.match(r'\s*\[([^]]+)\]\s+(\S+)\s+(.*)',line)
  if m and m[2] in keys:rows.append({'check':m[2],'status':m[1].strip()})
 report.update(exit_code=p.returncode,allowlisted_status_rows=rows,stdout_sha256=hashlib.sha256(p.stdout.encode()).hexdigest(),stderr_sha256=hashlib.sha256(p.stderr.encode()).hexdigest(),stdout_bytes=len(p.stdout.encode()),stderr_bytes=len(p.stderr.encode()),timed_out=False)
except subprocess.TimeoutExpired as exc:
 report.update(exit_code=None,timed_out=True,allowlisted_status_rows=[],stdout_bytes=len(exc.stdout or b''),stderr_bytes=len(exc.stderr or b''))
# No credential-bearing response bodies, raw stdout, raw stderr or env values are persisted.
with (BASE/'native-doctor-readiness.json').open('x') as f:f.write(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps(report,indent=2,sort_keys=True))
