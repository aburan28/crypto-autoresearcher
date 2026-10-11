#!/usr/bin/env python3
"""Supervise the existing G3 binary without changing its scientific inputs."""
import argparse
import json
import os
import platform
import resource
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--run-id", required=True)
a = p.parse_args()
root = Path('/workspace/solinas-run')
out = root / 'experiments/EXP-ECDLP-4c6a09/runs' / a.run_id
out.mkdir(parents=True, exist_ok=False)
cmd = [str(root / 'experiments/EXP-ECDLP-4c6a09/implementation/target/release/g3'),
       '--kmin', '4', '--kmax', '12', '--min-bits', '12', '--max-primes-per-shape', '3',
       '--random-g', '20', '--curves', '5', '--ladder', '300', '1000', '3000', '10000', '30000', '100000',
       '--seeds', '1', '2', '3', '--aux-primes', '8', '--out', str(out.relative_to(root))]
env = os.environ.copy()
env.update({'CARGO_HOME':'/workspace/solinas-toolchain/cargo', 'RUSTUP_HOME':'/workspace/solinas-toolchain/rustup',
            'LD_LIBRARY_PATH':'/workspace/solinas-runtime/pari/usr/lib/x86_64-linux-gnu'})
env['PATH'] = '/workspace/solinas-toolchain/cargo/bin:' + env['PATH']
start = datetime.now(timezone.utc).isoformat()
meta = {'run_id': out.name, 'command_argv': cmd, 'started_at_utc': start,
        'git_commit': subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
        'git_dirty_before_run': subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True).strip(),
        'platform': platform.platform(), 'memory_limit_bytes': 4 * 1024**3, 'requested_seeds':[1,2,3],
        'requested_random_fields_per_shape_per_seed':20, 'requested_curves_per_field':5,
        'rustc': subprocess.check_output(['rustc','--version'],env=env,text=True).strip(), 'pari_package_version':'2.17.2-1',
        'model':'GPT-6 (system identity; no provider probe)', 'fallback_used':False, 'degraded_requirements':[],
        'inference_usage':None, 'validity_status':'observations; separate research review not performed',
        'purpose':'CTRL-REPLAY; same complete scientific inputs as RUN-ECDLP-24c35a',
        'concurrency':'Replay overlaps the primary run; each binary is single-threaded, host quota four CPUs.'}
(out / 'launch.json').write_text(json.dumps(meta,indent=2)+'\n')
print('START',out.name,start,flush=True)
resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3))
t0=time.monotonic()
with (out/'stdout.log').open('xb') as stdout, (out/'stderr.log').open('xb') as stderr:
    completed = subprocess.run(cmd,env=env,cwd=root,stdout=stdout,stderr=stderr)
usage=resource.getrusage(resource.RUSAGE_CHILDREN)
result={'run_id':out.name,'exit_code':completed.returncode,'finished_at_utc':datetime.now(timezone.utc).isoformat(),
        'elapsed_seconds_supervised':time.monotonic()-t0,'child_user_cpu_seconds':usage.ru_utime,
        'child_system_cpu_seconds':usage.ru_stime,'child_peak_rss_kib':usage.ru_maxrss}
Path('/workspace/solinas-runtime',a.run_id+'-process.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result),flush=True)
raise SystemExit(completed.returncode)
