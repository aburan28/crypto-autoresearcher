import datetime,hashlib,json,pathlib,resource,subprocess,sys,time
D=pathlib.Path(__file__).resolve().parent
for n,h in json.loads((D/'FROZEN-FILES.json').read_text()).items():assert hashlib.sha256((D/n).read_bytes()).hexdigest()==h,n
for arm,script in [('matrix','arithmetic.py'),('eigen','independent.py')]:
 start=time.monotonic();before=resource.getrusage(resource.RUSAGE_CHILDREN);stamp=datetime.datetime.now(datetime.timezone.utc).isoformat();cmd=[sys.executable,str(D/script)]
 try:r=subprocess.run(cmd,cwd=D,capture_output=True,text=True,timeout=600);rc=r.returncode;out=r.stdout;err=r.stderr;timedout=False
 except subprocess.TimeoutExpired as e:rc=None;out=e.stdout or b'';err=e.stderr or b'';out=out.decode() if isinstance(out,bytes) else out;err=err.decode() if isinstance(err,bytes) else err;timedout=True
 (D/(arm+'.stdout')).write_text(out);(D/(arm+'.stderr')).write_text(err);after=resource.getrusage(resource.RUSAGE_CHILDREN);record={'command':cmd,'returncode':rc,'timeout':timedout,'started_at':stamp,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds_diagnostic':time.monotonic()-start,'cpu_user_seconds':after.ru_utime-before.ru_utime,'cpu_sys_seconds':after.ru_stime-before.ru_stime};(D/(arm+'-receipt.json')).write_text(json.dumps(record,indent=2)+'\n');print(arm,'rc',rc,flush=True)
 if rc!=0 or timedout:raise SystemExit(1)
r=subprocess.run([sys.executable,str(D/'audit.py')],cwd=D,capture_output=True,text=True,timeout=900);(D/'audit.stdout').write_text(r.stdout);(D/'audit.stderr').write_text(r.stderr);print('audit rc',r.returncode,flush=True)
if r.returncode:raise SystemExit(r.returncode)
print(r.stdout,flush=True)
