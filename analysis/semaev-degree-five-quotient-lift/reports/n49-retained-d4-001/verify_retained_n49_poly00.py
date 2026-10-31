"""Recheck the interrupted n49 D4 candidate against the original verifier."""

from pathlib import Path
import hashlib
import json
import re
import subprocess
import time


STUDY = Path('analysis/semaev-degree-five-quotient-lift')
PLAN = STUDY / 'highmem-recovery-plan-001.json'
PROTOCOL = STUDY / 'highmem-recovery-protocol-001.json'
SOURCE = Path('/home/ec2-user/fall-degree-data-20261029/frontier-cascade-001/fresh-n49-poly-00-D5-cascade01/attempt-001')
OUT = STUDY / 'validation/n49-poly00-retained-check-001'
ID = 'fresh-n49-poly-00-D5-cascade01-highmem01-recovery01'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


protocol = json.loads(PROTOCOL.read_text())
assert digest(PLAN) == protocol['links']['plan_sha256']
plan = json.loads(PLAN.read_text())
entry = next(row for row in plan['items'] if row['id'] == ID)
seed = entry['seed']
assert seed['degree'] == 4
assert digest(SOURCE / 'started.json') == seed['origin_sha256']
assert digest(SOURCE / 'input.sys') == seed['system_sha256']
assert digest(SOURCE / 'degree4.bin') == seed['sha256']
assert digest(Path('/home/ec2-user/fall-degree-runtime-20261029/bin/count_by_sum')) == protocol['arms'][1]['instrument']['binary_sha256']
OUT.mkdir(parents=True, exist_ok=True)

check = json.loads((SOURCE / 'check3.argv.json').read_text())
check[check.index(str(SOURCE / 'degree3.bin'))] = str(SOURCE / 'degree4.bin')
count = json.loads((SOURCE / 'count.argv.json').read_text())


def run(name, argv):
    started = time.monotonic()
    proc = subprocess.run(argv, text=True, capture_output=True, timeout=3600)
    (OUT / f'{name}.stdout.txt').write_text(proc.stdout)
    (OUT / f'{name}.stderr.txt').write_text(proc.stderr)
    (OUT / f'{name}.argv.json').write_text(json.dumps(argv, indent=2) + '\n')
    return {'returncode': proc.returncode, 'elapsed_seconds': time.monotonic() - started,
            'stdout_sha256': digest(OUT / f'{name}.stdout.txt'),
            'stderr_sha256': digest(OUT / f'{name}.stderr.txt')}


steps = {'count': run('count', count), 'check4': run('check4', check)}
stdout = (OUT / 'check4.stdout.txt').read_text()
match = re.search(r'VALID: 1 is not in W_4\(F\), and codim W_4\(F\) >= (\d+)', stdout)
exact = (OUT / 'count.stdout.txt').read_text().strip()
certified = steps['count']['returncode'] == 0 and steps['check4']['returncode'] == 0 and match and exact.isdecimal()
result = {'schema': 'semaev.retained-candidate-check/v1', 'id': ID,
          'status': 'certificate_verified' if certified else 'check_failed',
          'certificate_sha256': seed['sha256'], 'system_sha256': seed['system_sha256'],
          'original_plan_sha256': digest(STUDY / 'cascade-plan.json'),
          'recovery_plan_sha256': digest(PLAN), 'protocol_sha256': protocol['freeze']['protocol_sha256'],
          'steps': steps, 'exact_solutions': int(exact) if steps['count']['returncode'] == 0 and exact.isdecimal() else None,
          'certified_codimension_lower_bound': int(match.group(1)) if certified else None}
result['last_fall_degree_lower_bound'] = 5 if certified and result['certified_codimension_lower_bound'] > result['exact_solutions'] else None
(OUT / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2), flush=True)
