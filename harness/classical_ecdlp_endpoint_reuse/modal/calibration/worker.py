"""Reuse the source-pinned native wait4 helper for six development calls."""
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path('/work/calibration')
OUT = ROOT / 'result'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write(name, value):
    with (OUT / name).open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')

def main():
    assert os.getuid() == 1000 and os.getgid() == 1000
    plan = json.loads((ROOT / 'plan.json').read_text())
    assert sha('/usr/local/bin/endpoint_reuse') == plan['binary_sha256']
    assert sha('/opt/study/execution/run_experiment.py') == plan['native_helper_sha256']
    assert sha('/opt/study/build-info.json') == plan['build_info_sha256']
    for item in plan['inputs']:
        assert sha(ROOT / item['path']) == item['sha256']
    sys.path.insert(0, '/opt/study')
    spec = importlib.util.spec_from_file_location('source_a_native_helpers', '/opt/study/execution/run_experiment.py')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    OUT.mkdir()
    receipt = {'schema': 'classical.ecdlp.runtime-calibration-worker/v1',
               'started_at': helper.utc(), 'plan_sha256': sha(ROOT / 'plan.json'),
               'purpose': plan['purpose'], 'scientific_confirmation_measurement': False,
               'uid': os.getuid(), 'gid': os.getgid(), 'wall_valid': False,
               'host': helper.host_facts(), 'arms': [], 'completed': False}
    deadline = time.monotonic() + plan['native_global_timeout_seconds']
    with (ROOT / 'targets.tsv').open() as stream:
        targets = list(csv.DictReader(stream, delimiter='\t'))
    for arm in plan['arms']:
        if time.monotonic() >= deadline:
            receipt['stop_reason'] = 'native_global_timeout_before_next_child'
            break
        raw = OUT / (arm + '.jsonl')
        argv = ['/usr/local/bin/endpoint_reuse', '--run', str(ROOT/'fixtures.tsv'),
                str(ROOT/'targets.tsv'), str(ROOT/'settings.tsv'), arm, str(raw)]
        observation = helper.wait_child(argv, OUT/(arm+'.stdout.txt'), OUT/(arm+'.stderr.txt'),
                                        plan['native_child_timeout_seconds'], deadline=deadline)
        observation.update({'arm': arm, 'argv': argv, 'raw_path': raw.name,
                            'scientific_confirmation_measurement': False})
        if raw.exists():
            observation['raw_sha256'] = sha(raw)
        if observation['exitcode'] == 0:
            observation['shape'] = helper.shape_check(raw, plan['setting']['cell_id'], plan['setting'], arm, targets)
        receipt['arms'].append(observation)
        write(arm+'.command.json', observation)
        # Every native outcome is preserved; there is no automatic retry.
    receipt['completed'] = (len(receipt['arms']) == 6 and
                            all(r['exitcode'] == 0 and r.get('shape',{}).get('output_shape_complete') for r in receipt['arms']))
    receipt['finished_at'] = helper.utc()
    if receipt['completed']:
        per_cell = sum(r['clock']['wall_seconds'] for r in receipt['arms'])
        receipt['runtime_estimate'] = {'fixed_seconds': None, 'per_sample_seconds': per_cell,
            'threads': 1, 'estimated_total_seconds': 128*per_cell,
            'measured_on': 'Actual Modal VM; image '+plan['image_id']+'; reused public18-bit fixture '+plan['fixture_id']+'; sixteen existing Q repeated four times; one64Qnative child per each of six arms; parent wait4/perf-monotonic clocks unqualified wall_valid=false; estimate128cells times sum six child intervals; provider/startup/staging/collection overhead excluded; planning proxy, not an upper bound or algorithm comparison.'}
    write('receipt.json', receipt)
    manifest = {'schema': 'classical.ecdlp.runtime-calibration-output-manifest/v1',
                'files': [{'path': p.name, 'bytes': p.stat().st_size, 'sha256': sha(p)}
                          for p in sorted(OUT.iterdir()) if p.is_file()]}
    write('output-manifest.json', manifest)
    print(json.dumps({'completed': receipt['completed'], 'actual_children': len(receipt['arms']),
                      'runtime_estimate': receipt.get('runtime_estimate')}), flush=True)
    return 0 if receipt['completed'] else 1

if __name__ == '__main__':
    sys.exit(main())
