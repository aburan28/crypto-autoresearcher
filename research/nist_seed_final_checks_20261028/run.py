"""One frozen full-cohort invocation; retain stdout/stderr and every certificate."""
import datetime,hashlib,json,platform,subprocess,time
from pathlib import Path
P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for n,h in json.loads((P/'FROZEN.json').read_text())['files'].items():assert sha(P/n)==h,n
W=P/'runs/final-01';W.mkdir(parents=True,exist_ok=False)
cmd=['/opt/homebrew/bin/gp','-q','-f','-s','134217728',str(P/'inputs.gp'),str(P/'check.gp')];start=time.monotonic();stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
try:r=subprocess.run(cmd,cwd=P,capture_output=True,timeout=240);rc=r.returncode;out=r.stdout;err=r.stderr;timed=False
except subprocess.TimeoutExpired as e:rc=None;out=e.stdout or b'';err=e.stderr or b'';timed=True
(W/'stdout.txt').write_bytes(out);(W/'stderr.txt').write_bytes(err)
receipt={'command':cmd,'returncode':rc,'timeout':timed,'started_at':stamp,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'wall_seconds_diagnostic':time.monotonic()-start,'platform':platform.platform(),'gp_version':subprocess.run(['/opt/homebrew/bin/gp','--version-short'],capture_output=True,text=True).stdout.strip(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=P,text=True).strip(),'stdout_sha256':sha(W/'stdout.txt'),'stderr_sha256':sha(W/'stderr.txt')}
(W/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');assert rc==0 and not timed and not err,receipt
lines=out.decode().splitlines();assert lines[0]=='CONTROLS PASS' and lines[-1]=='COMPLETE';data=[json.loads(s) for s in lines[1:-1]];assert len(data)==21 and [x[0] for x in data]==list(range(21))
(W/'raw.json').write_text(json.dumps(data,indent=2)+'\n');print(json.dumps({'status':'COMPLETED','rows':len(data),'full_cohort_invocations':1,'retries':0,'wall_seconds_diagnostic':receipt['wall_seconds_diagnostic']}))
