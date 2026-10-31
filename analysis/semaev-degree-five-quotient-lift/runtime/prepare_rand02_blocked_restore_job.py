"""Build a restore-only continuation for the original random02 blocked job.

Preparation is safe while the original Job runs. Submission requires a fresh
terminal-state and owner check; this script never submits a Job.
"""

import ast
import hashlib
import json
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


s = Path(__file__).resolve().parent.parent
source = s / 'runtime/rand02-blocked-frontier-job-001.json'
request = s / 'runtime/rand02-blocked-frontier-request-001.json'
protocol = s / 'rand02-blocked-frontier-protocol-001.json'
job = json.loads(source.read_text())
p = json.loads(protocol.read_text())
assert job['job_name'] == 'semaev-n47-rand02-d5-blocked-20261030-2120'
assert p['freeze']['status'] == 'frozen'
assert sha(request) == p['links']['request_sha256s'][0]
assert job['retries'] == 0 and job['seconds'] == 21600

prefix = ('s3://isolab-results-104186811093-us-east-2/runs/'
          'semaev-n47-rand02-d5-blocked-20261030-2120/'
          '4c6e513f-b5f2-41c2-bf62-880ea7e8ea28/lift/checkpoints')
code = ''.join(job['command'][3:])
needle = "'--out','/work/results/lift','--upload']"
assert code.count(needle) == 1
replacement = "'--out','/work/results/lift','--upload','--restore-prefix'," + repr(prefix) + "]"
code = code.replace(needle, replacement)
compile(code, 'rand02-restore-command', 'exec')
for key, path in [('REQUEST', request), ('PROTOCOL', protocol)]:
    value = next(ast.literal_eval(line.split('=', 1)[1]) for line in code.splitlines()
                 if line.startswith(key + '='))
    assert value == path.read_text(), key
assert code.count('--restore-prefix') == 1
job['command'] = job['command'][:3] + [code[i:i + 6000] for i in range(0, len(code), 6000)]
assert all(len(x.encode()) <= 8192 for x in job['command'])
job['job_name'] = 'semaev-n47-rand02-d5-blocked-restore01-20261031'
output = s / 'runtime/rand02-blocked-restore-job-001.json'
with output.open('x') as f:
    json.dump(job, f, indent=2)
    f.write('\n')
print(output, sha(output))
