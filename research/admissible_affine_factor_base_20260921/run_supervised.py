#!/usr/bin/env python3
"""Root-owned outer telemetry. Launch each pre-admitted phase once; never retry."""
import argparse,datetime,hashlib,json,os,pathlib,subprocess,sys,time
p=argparse.ArgumentParser();p.add_argument('phase',choices=['controls','science','checker']);p.add_argument('commit');a=p.parse_args()
root=pathlib.Path(__file__).resolve().parents[2]
control=root/'research/admissible_affine_factor_base_20260921'
run=root/'experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11'
folder=control/'supervisor';folder.mkdir(exist_ok=True)
marker=folder/(a.phase+'.launch.json');out=folder/(a.phase+'.stdout');err=folder/(a.phase+'.stderr');receipt=folder/(a.phase+'.receipt.json')
argv=[sys.executable,str(root/'experiments/EXP-KIC-3df18c/code/runner.py'),'--phase',a.phase,'--admission',str(control/(a.phase+'_admission.json')),'--admission-commit',a.commit]
record={'phase':a.phase,'argv':argv,'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'cwd':str(root),'admission_commit':a.commit}
with marker.open('x') as f:json.dump(record,f,indent=2);f.write('\n')
with out.open('xb') as fo,err.open('xb') as fe:
 start=time.perf_counter_ns();child=subprocess.Popen(argv,cwd=root,stdout=fo,stderr=fe,stdin=subprocess.DEVNULL)
 pid,status,usage=os.wait4(child.pid,0);end=time.perf_counter_ns();child.returncode=os.waitstatus_to_exitcode(status)
record.update(ended_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),exit_code=child.returncode,wall_seconds=(end-start)/1e9,wait4={'user_seconds':usage.ru_utime,'system_seconds':usage.ru_stime,'maximum_rss_bytes':usage.ru_maxrss,'scope':'wait4 of phase supervisor; OS descendant accounting may include waited native/checker children; do not add to child receipt CPU'},wall_scope='Supervisor launch through wait4 reap including input/source checks, child compute, output promotion, hashing and phase raw archive. This external wrapper receipt serialization is outside that interval.',stdout_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),stderr_sha256=hashlib.sha256(err.read_bytes()).hexdigest())
with receipt.open('x') as f:json.dump(record,f,indent=2);f.write('\n')
print(json.dumps(record,indent=2));raise SystemExit(child.returncode)
