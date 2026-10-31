"""Prepare a contingent, frozen-input n45 random03 local admission variant."""

from pathlib import Path
import copy
import hashlib
import json


study = Path('analysis/semaev-degree-five-quotient-lift')
source_plan = study / 'panel-local-n45-rand03-plan-001.json'
source_protocol = study / 'panel-local-n45-rand03-protocol-001.json'
new_plan = study / 'panel-local-n45-rand03-lowmem-plan-001.json'
new_protocol = study / 'panel-local-n45-rand03-lowmem-protocol-001.json'
assert not new_plan.exists() and not new_protocol.exists()
old_cap, new_cap = 40 << 30, 24 << 30
plan = json.loads(source_plan.read_text())
assert plan['memory_bytes'] == old_cap and plan['reserve_bytes'] == 2 << 30
assert plan['output_root'].endswith('/panel-local-n45-rand03-001')
plan['memory_bytes'] = new_cap
plan['output_root'] = plan['output_root'].replace('/panel-local-n45-rand03-001', '/panel-local-n45-rand03-lowmem-001')
plan['scope'] = ('Contingent same-input n45 random03 D4 attempt only after the original 40GiB admission-only '
                 'refusal; unchanged pinned worker, request, controls, checker and count; 24GiB child cap, '
                 '2GiB reserve, 900s bounded admission. No timing or population inference.')
new_plan.write_text(json.dumps(plan, indent=2) + '\n')
plan_sha = hashlib.sha256(new_plan.read_bytes()).hexdigest()


def replace(value):
    if isinstance(value, dict):
        return {k: replace(v) for k, v in value.items()}
    if isinstance(value, list):
        return [replace(v) for v in value]
    if isinstance(value, int) and value == old_cap:
        return new_cap
    if isinstance(value, str):
        return (value.replace('40GiB', '24GiB').replace('40 GiB', '24 GiB')
                     .replace('42GiB', '26GiB').replace('42 GiB', '26 GiB')
                     .replace('42949672960', '25769803776')
                     .replace('panel-local-n45-rand03-plan-001.json', new_plan.name)
                     .replace('unchanged24GiB', '24GiB')
                     .replace('cap and admission unchanged', 'cap and admission changed explicitly for this resource variant'))
    return value


protocol = replace(copy.deepcopy(json.loads(source_protocol.read_text())))
protocol['protocol_id'] = 'SEMAEV-PANEL-LOCAL-N45-RAND03-LOWMEM-20261031'
protocol['question'] = ('After an admission-only refusal at the original cap, can the same original '
                        'n45 random03 D4 input be completed under a 24GiB child cap with the unchanged '
                        'qualified worker and independent checker?')
protocol['links']['plan'] = new_plan.name
protocol['links']['plan_sha256'] = plan_sha
protocol['links']['prior_inventory'] = 'runtime/panel-remaining-after-local010.json'
protocol['links']['prior_inventory_sha256'] = hashlib.sha256((study / protocol['links']['prior_inventory']).read_bytes()).hexdigest()
protocol['links']['kind'] = ('Contingent resource variant for the same frozen input, only if the original '
                             '40GiB-cap launcher returns admission refusal before a worker starts; no redraw.')
protocol['stopping_rules'][0]['rule'] = ('One worker attempt on the same original input only after the '
                                         '40GiB-cap launcher has terminal admission refusal and no worker. '
                                         'Acquire both original locks, wait at most 900 seconds for '
                                         'MemAvailable >=26GiB, and rehash pinned bytes. Preserve refusal, '
                                         'timeout, and checker failure without an LFD claim.')
protocol['freeze'] = {'status': 'draft', 'protocol_sha256': None, 'commit': None,
                      'frozen_at': None, 'filed_before_affected_data': False}
protocol.setdefault('amendments', []).append({
    'id': 'RAND03-LOWMEM-CONTINGENCY', 'filed': '2026-10-31', 'filed_before_affected_data': True,
    'reason': 'The original fixed-cap launcher is observing memory pressure before any worker launch.',
    'changes': ['Same original input and pinned worker/checker/count binaries.',
                'Explicit 24GiB child cap and 2GiB reserve; no runtime comparison.',
                'Execute only if the original 40GiB-cap attempt ends with admission-only refusal.']})
new_protocol.write_text(json.dumps(protocol, indent=2) + '\n')
print(json.dumps({'plan_sha256': plan_sha, 'protocol': str(new_protocol), 'output_root': plan['output_root']}))
