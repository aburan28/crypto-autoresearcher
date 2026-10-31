"""Prepare the pinned polynomial00 D5 attempt; submission has a separate owner gate."""

import ast
import hashlib
import json
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


s = Path(__file__).resolve().parent.parent
request = s / 'runtime/poly00-blocked-frontier-request-001.json'
protocol = s / 'poly00-blocked-frontier-protocol-001.json'
p = json.loads(protocol.read_text())
r = json.loads(request.read_text())
assert p['freeze']['status'] == 'frozen'
assert sha(request) == p['links']['request_sha256s'][0]
assert r['worker_manifest_sha256'] == p['links']['worker_manifest_sha256']
assert r['seed_sha256'] == json.loads((s / p['links']['accepted_seed_publication']).read_text())['certificate_sha256']
assert sha(s / p['links']['dimension_profile']) == p['links']['dimension_profile_sha256']
assert sha(s / p['links']['corrected_envelope']) == p['links']['corrected_envelope_sha256']
resource = json.loads((s / p['links']['corrected_envelope']).read_text())
assert resource['corrected_envelope_bytes'] < r['memory_bytes']
assert resource['ephemeral_headroom_before_runtime_bytes'] > 0
assert resource['working_coordinates'] == r['disk_policy']['working_coordinates']
assert resource['child_limit_bytes'] == r['memory_bytes']
assert resource['pod_limit_bytes'] == r['pod_memory_bytes']
qualification = s / p['links']['qualification_export']
assert sha(qualification) == p['links']['qualification_export_sha256']
e = json.loads(qualification.read_text())
assert e['flow']['completed'] == 9 and e['flow']['not_completed'] == 0

job = json.loads((s / 'runtime/checkpoint-frontier-job-001.json').read_text())
code = ''.join(job['command'][3:])
values = {
    'URL': p['links']['worker_url'],
    'ARCHIVE_SHA': p['links']['worker_archive_sha256'],
    'REQUEST': request.read_text(),
    'REQUEST_SHA': sha(request),
    'PROTOCOL': protocol.read_text(),
    'PROTOCOL_BYTES_SHA': sha(protocol),
}
lines = code.splitlines(keepends=True)
for key, value in values.items():
    indices = [i for i, line in enumerate(lines) if line.startswith(key + '=')]
    assert len(indices) == 1, key
    lines[indices[0]] = key + '=' + repr(value) + '\n'
code = ''.join(lines)
compile(code, 'poly00-frontier-command', 'exec')
for key, value in values.items():
    parsed = next(ast.literal_eval(line.split('=', 1)[1]) for line in code.splitlines() if line.startswith(key + '='))
    assert parsed == value, key
job['command'] = job['command'][:3] + [code[i:i + 6000] for i in range(0, len(code), 6000)]
assert all(len(x.encode()) <= 8192 for x in job['command'])
job['job_name'] = 'semaev-n47-poly00-d5-blocked-20261031'
job['memory'] = '24Gi'
output = s / 'runtime/poly00-blocked-frontier-job-001.json'
with output.open('x') as f:
    json.dump(job, f, indent=2)
    f.write('\n')
print(output, sha(output))
