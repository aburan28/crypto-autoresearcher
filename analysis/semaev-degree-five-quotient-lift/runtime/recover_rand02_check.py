#!/usr/bin/env python3
"""Recheck a retained candidate without overwriting its interrupted attempt."""
import fcntl
import json
from pathlib import Path
import re
import sys

study = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(study.parent/'semaev-m2-last-fall-degree/submission-20261029'))
from certificate_campaign import command, digest, save

plan_path = study/'runtime/highmem-rand02-check-recovery-001.json'
plan = json.loads(plan_path.read_text())
old_plan = json.loads((study/'highmem-plan.json').read_text())
assert digest(Path(plan['count_argv'][0])) == old_plan['binary_sha256']['count_by_sum']
assert digest(Path(plan['check_argv'][1])) == plan['checker_sha256']
assert digest(Path(plan['check_argv'][2])) == plan['candidate_sha256']
available = int(next(line.split()[1] for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemAvailable:'))) * 1024
assert available >= plan['memory_bytes'] + (2 << 30), 'insufficient recovery headroom'
with open(plan['owner_lock'], 'a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    out = Path(plan['out']); out.mkdir(exist_ok=False)
    save(out/'started.json', dict(plan=plan, plan_sha256=digest(plan_path), available_bytes=available))
    steps = {}
    result = dict(status='failed', scope='D4 validation recovery only; no D5 bound or upper bound')
    for label, cap in [('count', plan['count_memory_bytes']), ('check4', plan['memory_bytes'])]:
        steps[label] = command(plan['count_argv' if label == 'count' else 'check_argv'], out, label, plan['timeout_seconds'], cap, lock.fileno())
        save(out/(label+'.step.json'), steps[label])
        if steps[label]['returncode'] != 0:
            break
    else:
        count = int((out/'count.stdout.txt').read_text().strip())
        match = re.search(r'VALID: 1 is not in W_4\(F\), and codim W_4\(F\) >= (\d+)', (out/'check4.stdout.txt').read_text())
        assert match, 'checker acceptance absent'
        assert digest(Path(plan['check_argv'][2])) == plan['candidate_sha256']
        result.update(status='certificate_verified', exact_solutions=count, certified_codimension=int(match[1]), certificate_sha256=plan['candidate_sha256'])
        if int(match[1]) > count:
            result['last_fall_degree_lower_bound'] = 5
    result.update(steps=steps, artifacts={p.name:dict(sha256=digest(p),bytes=p.stat().st_size) for p in out.iterdir() if p.is_file()})
    save(out/'result.json', result)
    print(json.dumps(result), flush=True)
