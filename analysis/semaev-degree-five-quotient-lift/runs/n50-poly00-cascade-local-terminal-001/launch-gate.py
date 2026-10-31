#!/usr/bin/env python3
"""One-shot admission for the frozen n50 poly00 cascade."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
from datetime import datetime, timezone

study = Path('/home/ec2-user/crypto-autoresearcher-fall-degree-submission-20261029/analysis/semaev-degree-five-quotient-lift')
plan_path = study / 'n50-poly00-cascade-local-plan-001.json'
protocol_path = study / 'n50-poly00-cascade-local-protocol-001.json'
source_plan_path = study / 'cascade-plan.json'
n49 = Path('/home/ec2-user/fall-degree-data-20261029/n49-poly00-d5-local-002')
gate_path = Path('/home/ec2-user/fall-degree-data-20261029/n50-poly00-cascade-local-001.launch-gate.json')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def file_sha(path):
    return sha(Path(path).read_bytes())

plan = json.loads(plan_path.read_text())
protocol = json.loads(protocol_path.read_text())
if protocol['freeze']['status'] != 'frozen' or file_sha(plan_path) != protocol['links']['plan_sha256']:
    raise RuntimeError('frozen n50 plan mismatch')
if file_sha(source_plan_path) != plan['selection']['original_plan_sha256']:
    raise RuntimeError('source plan mismatch')
source_plan = json.loads(source_plan_path.read_text())
matches = [item for item in source_plan['items'] if item['id'] == plan['items'][0]['id']]
if len(matches) != 1 or matches[0]['record'] != plan['items'][0]['record']:
    raise RuntimeError('selected original item mismatch')
for name, expected in plan['source_sha256'].items():
    if file_sha(study / name) != expected:
        raise RuntimeError('source hash mismatch: ' + name)
for name, expected in plan['binary_sha256'].items():
    if file_sha(Path('/home/ec2-user/fall-degree-runtime-20261029/bin') / name) != expected:
        raise RuntimeError('binary hash mismatch: ' + name)
if not (n49 / 'terminal.json').exists() or not (n49 / 'attempt-001/result.json').exists():
    raise RuntimeError('n49 is not terminal')
prior = json.loads((n49 / 'attempt-001/result.json').read_text())
if prior['id'] != 'n49-poly00-D5-local-002' or prior['steps']['produce5']['timeout'] is not True:
    raise RuntimeError('unexpected n49 terminal record')
publication = json.loads((n49 / 'attempt-001/snapshots/checkpoint-9.publication.json').read_text())
manifest = subprocess.run(['aws', 's3', 'cp', publication['manifest_uri'], '-'],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          check=True, timeout=90).stdout
if sha(manifest) != publication['manifest_sha256']:
    raise RuntimeError('n49 durable checkpoint manifest mismatch')

handles = []
for name in plan['selection']['locks']:
    handle = Path(name).open('a')
    fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    os.set_inheritable(handle.fileno(), True)
    handles.append(handle)
available = next(int(line.split()[1]) * 1024 for line in Path('/proc/meminfo').read_text().splitlines()
                 if line.startswith('MemAvailable:'))
required = plan['selection']['memory_bytes'] + plan['selection']['reserve_bytes']
if available < required:
    raise RuntimeError(f'memory admission refused: {available} < {required}')
if Path(plan['selection']['output_root']).exists() or gate_path.exists():
    raise RuntimeError('n50 output or gate record already exists')
argv = plan['selection']['launch_argv']
if argv[:6] != ['flock', '-n', plan['selection']['locks'][0], 'flock', '-n', plan['selection']['locks'][1]]:
    raise RuntimeError('unexpected frozen launch argv')
record = {
    'schema': 'semaev.n50-local-launch-gate/v1',
    'captured_at': datetime.now(timezone.utc).isoformat(),
    'plan_sha256': file_sha(plan_path),
    'protocol_file_sha256': file_sha(protocol_path),
    'source_plan_sha256': file_sha(source_plan_path),
    'n49_terminal_sha256': file_sha(n49 / 'attempt-001/result.json'),
    'n49_checkpoint_manifest_sha256': publication['manifest_sha256'],
    'available_bytes': available,
    'required_bytes': required,
    'locks': plan['selection']['locks'],
    'output_root_absent': True,
    'argv': argv[6:],
    'pid': os.getpid(),
    'scope': 'Prelaunch admission only; no n50 scientific outcome.'
}
with gate_path.open('x') as out:
    json.dump(record, out, indent=2)
    out.write('\n')
print(json.dumps({'gate': str(gate_path), 'pid': os.getpid(), 'available_bytes': available}), flush=True)
os.execv(argv[6], argv[6:])
