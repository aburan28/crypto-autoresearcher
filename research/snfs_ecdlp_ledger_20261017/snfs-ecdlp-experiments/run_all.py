"""Run the bounded pilot modules serially, with measured CPU and resource caps."""
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'vendor'))


def limits():
    resource.setrlimit(resource.RLIMIT_CPU,(240,250))
    # 3 GiB address-space limit per module; tiny pilots should remain far below it.
    resource.setrlimit(resource.RLIMIT_AS,(3*1024**3,3*1024**3))


def main():
    os.environ['OPENBLAS_NUM_THREADS']='1'
    os.environ['OMP_NUM_THREADS']='1'
    runs=[]
    for module in ('transfer_pilots.py','number_pilots.py','algebra_pilots.py','surface_pilots.py'):
        start=time.perf_counter();before=resource.getrusage(resource.RUSAGE_CHILDREN)
        with (ROOT/(module.removesuffix('.py')+'.log')).open('w') as log:
            proc=subprocess.run([sys.executable,str(ROOT/module)],stdout=log,stderr=subprocess.STDOUT,
                timeout=300,preexec_fn=limits(),env=os.environ.copy())
        after=resource.getrusage(resource.RUSAGE_CHILDREN)
        runs.append(dict(module=module,exit_code=proc.returncode,wall_seconds=time.perf_counter()-start,
            cpu_seconds=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
            process_tree_peak_RSS_kib=after.ru_maxrss,
            RSS_note='resource high-water mark over completed children; includes earlier modules, not a module-isolated maximum'))
        print(json.dumps(runs[-1]),flush=True)
        if proc.returncode:raise RuntimeError(f'{module} failed; inspect log')
    packages={}
    for name in ('sympy','numpy','scipy','z3-solver','fpylll','cysignals','matplotlib'):
        packages[name]=importlib.metadata.version(name)
    source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('*.py')}
    metadata=dict(platform=platform.platform(),python=sys.version,packages=packages,
        run_mode='serial, one BLAS thread',runs=runs,source_sha256=source_hashes,
        input_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'inputs').iterdir() if p.is_file()},
        per_module_cpu_soft_cap_seconds=240,per_module_wall_cap_seconds=300,
        per_module_address_space_cap_bytes=3*1024**3,
        network_used_by_pilot_code=False,no_sieving=True,
        canonical_registry_import=False,campaign_seed_reservation=False)
    (ROOT/'run-metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')


if __name__=='__main__':main()
