"""Pin a matching request for the admission-only low-memory contingency."""

from pathlib import Path
import hashlib
import json
import shutil


study = Path('analysis/semaev-degree-five-quotient-lift')
source_plan = study / 'panel-local-n45-rand03-lowmem-plan-001.json'
source_protocol = study / 'panel-local-n45-rand03-lowmem-protocol-001.json'
plan_path = study / 'panel-local-n45-rand03-lowmem-plan-002.json'
protocol_path = study / 'panel-local-n45-rand03-lowmem-protocol-002.json'
source_request_dir = study / 'runtime/panel-local-n45-rand03-001'
request_dir = study / 'runtime/panel-local-n45-rand03-lowmem-002'
old_root = Path('/home/ec2-user/fall-degree-data-20261029/panel-local-n45-rand03-lowmem-001')
assert not old_root.exists(), 'the first contingency must have failed before worker admission'
assert not request_dir.exists() and not plan_path.exists() and not protocol_path.exists()
request_dir.mkdir(parents=True)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


request = json.loads((source_request_dir / 'request.json').read_text())
assert request['memory_bytes'] == 40 << 30
request['memory_bytes'] = 24 << 30
request['id'] = 'fresh-n45-rand-03-rref-lowmem01'
(request_dir / 'request.json').write_text(json.dumps(request, indent=2) + '\n')
shutil.copy2(source_request_dir / 'input.sys', request_dir / 'input.sys')
assert digest(request_dir / 'input.sys') == request['system_sha256']

plan = json.loads(source_plan.read_text())
assert plan['memory_bytes'] == request['memory_bytes']
plan['request'] = str((request_dir / 'request.json').resolve())
plan['output_root'] = plan['output_root'].replace('-lowmem-001', '-lowmem-002')
plan['hashes'][str((request_dir / 'request.json').resolve())] = digest(request_dir / 'request.json')
plan['hashes'][str((request_dir / 'input.sys').resolve())] = digest(request_dir / 'input.sys')
plan['scope'] += ' Version 002 pins a matching 24GiB request after the first variant failed a preflight assertion without output.'
plan_path.write_text(json.dumps(plan, indent=2) + '\n')

protocol = json.loads(source_protocol.read_text())
protocol['protocol_id'] = 'SEMAEV-PANEL-LOCAL-N45-RAND03-LOWMEM-V2-20261031'
protocol['links']['plan'] = plan_path.name
protocol['links']['plan_sha256'] = digest(plan_path)
protocol['links']['kind'] += ' Version 002 pins a matching request; version 001 failed preflight before worker launch.'
protocol['analysis_plan']['inputs'] = [value.replace(source_plan.name, plan_path.name) for value in protocol['analysis_plan']['inputs']]
protocol['analysis_plan']['inputs'].extend([
    'runtime/panel-local-n45-rand03-lowmem-002/request.json',
    'runtime/panel-local-n45-rand03-lowmem-002/input.sys'])
protocol.setdefault('amendments', []).append({
    'id': 'RAND03-LOWMEM-REQUEST-REPAIR', 'filed': '2026-10-31', 'filed_before_affected_data': True,
    'reason': 'Version 001 stopped at the launcher request-cap equality assertion before output creation.',
    'changes': ['Pin a separate request with the same input and a 24GiB memory cap.',
                'Keep the exact worker, three controls, counter, checker, and 2GiB reserve.',
                'Use a fresh output root. No version-001 worker ran.']})
protocol['freeze'] = {'status': 'draft', 'protocol_sha256': None, 'commit': None,
                      'frozen_at': None, 'filed_before_affected_data': False}
protocol_path.write_text(json.dumps(protocol, indent=2) + '\n')
print(json.dumps({'plan_sha256': digest(plan_path), 'request_sha256': digest(request_dir / 'request.json'),
                  'protocol': str(protocol_path)}))
