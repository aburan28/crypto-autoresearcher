#!/usr/bin/env python3
"""Run only four newly needed matched cubic control descents."""
import concurrent.futures
import hashlib
import importlib.util
import json
import platform
import resource
import subprocess
import time
from pathlib import Path

RUN = Path(__file__).resolve().parent.parent
REPO = RUN.parents[3]
spec = importlib.util.spec_from_file_location('prior_rank_runner', RUN / 'source/run_rank.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def main():
    plan = json.loads((RUN / 'plan.json').read_text())
    launch = {'started_at_utc': module.stamp(),
              'command_argv': ['python3', str(Path(__file__).resolve())],
              'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
              'git_dirty_before_run': subprocess.check_output(['git', 'status', '--porcelain'], cwd=REPO, text=True).strip(),
              'platform': platform.platform(), 'python': platform.python_version(), 'pari_version': '2.17.2',
              'model': 'GPT-6 (system identity; no provider probe)', 'requested_policy': 'executor-implementation',
              'fallback_used': False, 'degraded_requirements': [], 'independent_review_performed': False,
              'rank_source_reused': 'RUN-ECDLP-7cfef7; identical checked source, no mandatory control rerun',
              'source_hashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in (RUN / 'source').iterdir() if p.is_file()}}
    module.write_json(RUN / 'rank-preparation-launch.json', launch)
    t0 = time.monotonic()
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(module.execute, j, area='matched-ranks') for j in plan['jobs']]
        for f in concurrent.futures.as_completed(futures):
            r = f.result()
            results.append(r)
            print(r['job']['field'], r['job']['A'], r['job']['B'], r['status'], r['nf_bounds'],
                  r['elapsed_seconds'], flush=True)
    u = resource.getrusage(resource.RUSAGE_CHILDREN)
    module.write_json(RUN / 'matched-ranks-result.json', {'nf': results,
                      'process': {'elapsed_seconds': time.monotonic() - t0, 'user_cpu_seconds': u.ru_utime,
                                  'system_cpu_seconds': u.ru_stime, 'peak_child_rss_kib': u.ru_maxrss,
                                  'finished_at_utc': module.stamp()}})

if __name__ == '__main__':
    main()
