#!/usr/bin/env python3
"""Launch one unchanged panel worker after frozen-input, lock and headroom checks."""
import argparse,fcntl,hashlib,json,os,platform,subprocess,time
from pathlib import Path

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):
 with p.open('x') as f:json.dump(d,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--plan',type=Path,required=True);ap.add_argument('--protocol',type=Path,required=True);a=ap.parse_args()
 plan=json.loads(a.plan.read_text());protocol=json.loads(a.protocol.read_text())
 assert protocol['freeze']['status']=='frozen' and sha(a.plan)==protocol['links']['plan_sha256']
 for name,digest in plan['hashes'].items():assert sha(name)==digest,name
 req=json.loads(Path(plan['request']).read_text());assert req['memory_bytes']==plan['memory_bytes']
 root=Path(plan['output_root']);root.mkdir(parents=True,exist_ok=False)
 locks=[]
 try:
  for name in plan['locks']:
   f=Path(name).open('a');locks.append(f);fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  available=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
  admission=dict(available_bytes=available,process_cap_bytes=plan['memory_bytes'],reserve_bytes=plan['reserve_bytes'],admitted=available>=plan['memory_bytes']+plan['reserve_bytes'],pid=os.getpid(),hostname=platform.node(),locks=plan['locks'],wall_valid=False)
  save(root/'admission.json',admission)
  if not admission['admitted']:return 73
  argv=[plan['python'],plan['driver'],'--bundle',plan['bundle'],'--request',plan['request'],'--out',str(root/'attempt-001')]
  save(root/'launch.json',dict(argv=argv,unix_time=time.time(),protocol_sha256=protocol['freeze']['protocol_sha256'],plan_sha256=sha(a.plan)))
  with (root/'stdout').open('xb') as out,(root/'stderr').open('xb') as err:
   child=subprocess.Popen(argv,stdout=out,stderr=err,start_new_session=True,pass_fds=tuple(f.fileno() for f in locks))
   save(root/'child.json',dict(pid=child.pid,argv=argv));code=child.wait()
  save(root/'terminal.json',dict(returncode=code,unix_time=time.time()));return code
 finally:
  for f in reversed(locks):f.close()
if __name__=='__main__':raise SystemExit(main())
