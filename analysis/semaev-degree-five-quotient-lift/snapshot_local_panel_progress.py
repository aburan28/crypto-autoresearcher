#!/usr/bin/env python3
"""Copy only closed local panel startup stages into a write-once snapshot.

The native producer's stdout/stderr and certificate are intentionally excluded
while that stage is running. This is a custody record, not a certificate result.
"""
import argparse
import json
from pathlib import Path
import shutil

from collect_panel_result import digest, read, require


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--protocol', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    plan, protocol = read(args.plan), read(args.protocol)
    require(protocol['freeze']['status'] == 'frozen' and
            digest(args.plan) == protocol['links']['plan_sha256'],
            'Frozen plan binding failed')
    root = Path(plan['output_root'])
    attempt = root / 'attempt-001'
    request = read(attempt / 'request.json')
    require(digest(attempt / 'request.json') == plan['hashes'][plan['request']],
            'Request hash mismatch')
    require(digest(attempt / 'input.sys') == request['system_sha256'],
            'Input system mismatch')
    controls = read(attempt / 'controls/result.json')
    require(controls['status'] == 'passed' and len(controls['fixtures']) == 3,
            'Controls incomplete')
    for fixture in controls['fixtures']:
        require(fixture['independent_checker'] and fixture['reference_byte_identity'] and
                fixture['count'] == fixture['exhaustive_count'], 'Control failed')
    for stage in ('controls', 'count'):
        receipt = read(attempt / (stage + '.step.json'))
        require(receipt['returncode'] == 0 and receipt['timeout'] is False,
                'Stage incomplete: ' + stage)
    count = int((attempt / 'count.stdout.txt').read_text().strip())
    require(count >= 0, 'Invalid exact count')
    files = [root / name for name in ('admission.json', 'launch.json', 'child.json')]
    files += sorted((root / 'admission-samples').glob('*.json'))
    files += [attempt / name for name in ('request.json', 'input.sys', 'environment.json')]
    files += sorted(attempt.glob('controls.*')) + sorted(attempt.glob('count.*'))
    files += sorted(path for path in (attempt / 'controls').rglob('*') if path.is_file())
    require(all(path.is_file() for path in files), 'Startup file missing')
    require(not args.out.resolve().is_relative_to(root.resolve()),
            'Snapshot output must be outside the raw run')
    args.out.mkdir(parents=True, exist_ok=False)
    manifest = []
    for source in files:
        relative = source.relative_to(root)
        target = args.out / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        require(digest(target) == digest(source), 'Snapshot copy changed')
        manifest.append({'path': str(relative), 'bytes': target.stat().st_size,
                         'sha256': digest(target)})
    save(args.out / 'manifest.json', {
        'schema': 'semaev.local-panel-startup-snapshot/v1',
        'id': request['id'], 'prior_id': request['prior_id'],
        'source_output_root': str(root),
        'plan_sha256': digest(args.plan),
        'protocol_file_sha256': digest(args.protocol),
        'closed_stages': ['controls', 'count'],
        'fresh_exact_solutions': count,
        'files': manifest,
        'scope': 'Closed startup stages only; producer, checker, terminal and LFD outcome are not inferred',
    })
    print(json.dumps({'id': request['id'], 'closed_stages': ['controls', 'count'],
                      'fresh_exact_solutions': count, 'files': len(manifest)}))


if __name__ == '__main__':
    main()
