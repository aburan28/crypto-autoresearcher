from pathlib import Path
import json, os, subprocess, sys, time
b=Path('/tmp/review-TASK-20261018-63a7cc')
label=sys.argv[1]; args=sys.argv[2:]
env=os.environ.copy(); env.update(json.loads((b/'environment.json').read_text()))
art=b/'artifacts'
if label.startswith('controls-attempt-'):
    (art/(label.replace('controls','Controls')+'.lean')).write_bytes((b/'lean/Controls.lean').read_bytes())
start=time.time()
r=subprocess.run(args,cwd=b/'lean',env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(art/(label+'.log')).write_text(r.stdout)
p=art/'commands.json'; records=json.loads(p.read_text())
records.append({'label':label,'command':args,'cwd':str(b/'lean'),'exit_status':r.returncode,'elapsed_seconds':time.time()-start,'log':label+'.log'})
p.write_text(json.dumps(records,indent=2)+'\n')
print('exit_status',r.returncode,flush=True); print(r.stdout,flush=True)
