import os, subprocess, sys, time, hashlib
from pathlib import Path
source=Path(sys.argv[1])
logpath=Path(sys.argv[2])
env=dict(os.environ, PATH='/workspace/.elan/bin:'+os.environ['PATH'], ELAN_HOME='/workspace/.elan', XDG_CACHE_HOME='/workspace/.cache')
cmd=['lake','env','lean',str(source)]
started=time.time()
p=subprocess.run(cmd,cwd='/workspace/lean-blind-review',env=env,capture_output=True,text=True)
log=f'command: {cmd!r}\ncwd: /workspace/lean-blind-review\nsource_sha256: {hashlib.sha256(source.read_bytes()).hexdigest()}\nstarted_unix: {started}\nelapsed_seconds: {time.time()-started:.6f}\nexit_code: {p.returncode}\nstdout:\n{p.stdout}\nstderr:\n{p.stderr}'
logpath.write_text(log)
print(log)
raise SystemExit(p.returncode)
