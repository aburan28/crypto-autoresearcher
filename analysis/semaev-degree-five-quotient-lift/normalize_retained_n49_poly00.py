"""Make a write-once publication view of the independently checked n49 D4 map."""

from pathlib import Path
import hashlib
import json
import os
import shutil


STUDY = Path('analysis/semaev-degree-five-quotient-lift')
SOURCE = Path('/home/ec2-user/fall-degree-data-20261029/frontier-cascade-001/fresh-n49-poly-00-D5-cascade01/attempt-001')
CHECK = STUDY / 'validation/n49-poly00-retained-check-001'
DEST = Path('/home/ec2-user/fall-degree-data-20261029/n49-retained-publication-001/fresh-n49-poly-00-D4-retained01/attempt-001')


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


checked = json.loads((CHECK / 'result.json').read_text())
assert checked['status'] == 'certificate_verified'
assert checked['last_fall_degree_lower_bound'] == 5
assert checked['certified_codimension_lower_bound'] == 32291
assert checked['exact_solutions'] == 2
assert digest(SOURCE / 'degree4.bin') == checked['certificate_sha256']
assert digest(SOURCE / 'input.sys') == checked['system_sha256']
assert not DEST.exists(), 'publication projection is write-once'
DEST.mkdir(parents=True)
os.link(SOURCE / 'degree4.bin', DEST / 'certificate.bin')
for origin, target in [
    (SOURCE / 'input.sys', 'input.sys'),
    (SOURCE / 'started.json', 'started.json'),
    (SOURCE / 'produce4.stdout.txt', 'produce.stdout.txt'),
    (SOURCE / 'produce4.stderr.txt', 'produce.stderr.txt'),
    (CHECK / 'count.argv.json', 'count.argv.json'),
    (CHECK / 'count.stdout.txt', 'count.stdout.txt'),
    (CHECK / 'count.stderr.txt', 'count.stderr.txt'),
    (CHECK / 'check4.argv.json', 'check.argv.json'),
    (CHECK / 'check4.stdout.txt', 'check.stdout.txt'),
    (CHECK / 'check4.stderr.txt', 'check.stderr.txt'),
    (CHECK / 'result.json', 'verification.json'),
]:
    shutil.copy2(origin, DEST / target)
origin = {
    'schema': 'semaev.retained-publication-origin/v1',
    'original_plan_sha256': checked['original_plan_sha256'],
    'recovery_plan_sha256': checked['recovery_plan_sha256'],
    'recovery_protocol_sha256': checked['protocol_sha256'],
    'original_candidate': str(SOURCE / 'degree4.bin'),
    'original_certificate_sha256': checked['certificate_sha256'],
    'verification': str(CHECK / 'result.json'),
    'verification_sha256': digest(CHECK / 'result.json'),
    'scope': 'Publication-format projection of a retained candidate after fresh original-checker acceptance and exact count.',
}
(DEST / 'origin.json').write_text(json.dumps(origin, indent=2) + '\n')
started = json.loads((SOURCE / 'started.json').read_text())
artifacts = {p.name: {'bytes': p.stat().st_size, 'sha256': digest(p)}
             for p in DEST.iterdir() if p.is_file()}
result = {
    'schema': 'semaev.retained-publication/v1',
    'id': 'fresh-n49-poly-00-D4-retained01',
    'prior_id': started['parameters']['original_id'],
    'status': 'certificate_verified',
    'degree': 4,
    'certificate_sha256': checked['certificate_sha256'],
    'certified_codimension_lower_bound': checked['certified_codimension_lower_bound'],
    'exact_solutions': checked['exact_solutions'],
    'last_fall_degree_lower_bound': checked['last_fall_degree_lower_bound'],
    'parameters': {'record': started['parameters']['record'], 'degree': 4},
    'artifacts': artifacts,
    'provenance': origin,
}
(DEST / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'id': result['id'], 'certificate_sha256': result['certificate_sha256'],
                  'codimension': result['certified_codimension_lower_bound'],
                  'exact_solutions': result['exact_solutions']}))
