"""Frozen sequential launcher: retain stdout/stderr/receipts on failure."""
import datetime,hashlib,json,pathlib,platform,resource,subprocess,sys,time
D=pathlib.Path(__file__).resolve().parent

def main():
 manifest=json.loads((D/'FROZEN-FILES.json').read_text())
 for name,digest in manifest.items():assert hashlib.sha256((D/name).read_bytes()).hexdigest()==digest,name
 for method in ('bitset','rowwise'):
  before=resource.getrusage(resource.RUSAGE_CHILDREN);start=time.monotonic();stamp=datetime.datetime.now(datetime.timezone.utc).isoformat();cmd=[sys.executable,str(D/'search.py'),method]
  try:
   p=subprocess.run(cmd,cwd=D,capture_output=True,text=True,timeout=1800);rc=p.returncode;out=p.stdout;err=p.stderr;timeout=False
  except subprocess.TimeoutExpired as e:
   rc=None;out=e.stdout or b'';err=e.stderr or b'';out=out.decode() if isinstance(out,bytes) else out;err=err.decode() if isinstance(err,bytes) else err;timeout=True
  (D/(method+'.stdout')).write_text(out);(D/(method+'.stderr')).write_text(err)
  after=resource.getrusage(resource.RUSAGE_CHILDREN)
  receipt={'command':cmd,'started_at':stamp,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'returncode':rc,'timeout':timeout,'elapsed_seconds_diagnostic':time.monotonic()-start,'cpu_user_seconds':after.ru_utime-before.ru_utime,'cpu_sys_seconds':after.ru_stime-before.ru_stime,'host':platform.platform(),'python':sys.version,'stdout_sha256':hashlib.sha256(out.encode()).hexdigest(),'stderr_sha256':hashlib.sha256(err.encode()).hexdigest()}
  (D/(method+'-receipt.json')).write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(method,'returncode',rc,'timeout',timeout,flush=True)
  if rc!=0 or timeout:raise SystemExit(1)
 p=subprocess.run([sys.executable,str(D/'audit.py')],cwd=D,capture_output=True,text=True,timeout=120)
 (D/'audit.stdout').write_text(p.stdout);(D/'audit.stderr').write_text(p.stderr)
 if p.returncode:raise SystemExit(p.returncode)
 print(p.stdout,flush=True)
if __name__=='__main__':main()
