#!/usr/bin/env python3
"""Prepare exact checked seed sets and exact-K/reduction benchmark tables."""
import concurrent.futures
import hashlib
import json
import platform
import resource
import shutil
import time
from pathlib import Path

from finite_math import self_controls
from gp_tables import export_seeds, exact_grid, write

RUN = Path(__file__).resolve().parent.parent

def main():
    stage = RUN / 'point-preparation-attempt-01'
    stage.mkdir(exist_ok=False)
    (stage / 'source').mkdir()
    for filename in ['prepare_tables.py', 'finite_math.py', 'gp_tables.py']:
        shutil.copy2(RUN / 'source' / filename, stage / 'source' / filename)
    write(stage / 'launch.json', {'command_argv': ['python3', str(Path(__file__).resolve())],
                                'python': platform.python_version(), 'pari': '2.17.2',
                                'source_hashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                                  for p in (stage / 'source').iterdir()},
                                'plan_sha256': hashlib.sha256((RUN / 'plan.json').read_bytes()).hexdigest()})
    write(stage / 'controls-result.json', self_controls())
    start = time.monotonic()
    specs = export_seeds(RUN, stage)
    print('SEEDS_EXPORTED', len(specs), flush=True)
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for future in concurrent.futures.as_completed([pool.submit(exact_grid, stage, s) for s in specs]):
            results.append(future.result())
    u = resource.getrusage(resource.RUSAGE_CHILDREN)
    write(stage / 'result.json', {'exact_grid_ids': [r['spec_id'] for r in results],
                                'elapsed_seconds': time.monotonic() - start, 'user_cpu_seconds': u.ru_utime,
                                'system_cpu_seconds': u.ru_stime, 'peak_child_rss_kib': u.ru_maxrss})

if __name__ == '__main__':
    main()
