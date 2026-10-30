#!/usr/bin/env python3
"""Collect a terminal panel attempt, preserving failures and exact claim gates.

No trial is launched and no inventory or scientific status is changed. The main
certificate remains at its original path; the archive includes small controls.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import tarfile


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def verify(plan_path, protocol_path):
    plan, protocol = read(plan_path), read(protocol_path)
    require(protocol['freeze']['status'] == 'frozen', 'Protocol is not frozen')
    require(digest(plan_path) == protocol['links']['plan_sha256'], 'Plan hash mismatch')
    root = Path(plan['output_root'])
    # A running process is never collected as a terminal result.
    terminal = read(root / 'terminal.json')
    attempt = root / 'attempt-001'
    result, request = read(attempt / 'result.json'), read(attempt / 'request.json')
    require(result['status'] in {'certificate_verified', 'producer_contains_one', 'resource_capped', 'failed'},
            'Nonterminal or unknown result status')
    expected_request = plan['hashes'][plan['request']]
    require(digest(attempt / 'request.json') == expected_request, 'Request hash mismatch')
    require(result['id'] == request['id'] and result['prior_id'] == request['prior_id'],
            'Result identity mismatch')
    require(result['degree'] == request['degree'] == 4, 'Wrong degree')
    require(digest(attempt / 'input.sys') == request['system_sha256'], 'System hash mismatch')
    environment = read(attempt / 'environment.json')
    require(environment['request_sha256'] == expected_request, 'Environment request mismatch')
    require(environment['worker_manifest_sha256'] == plan['hashes'][str(Path(plan['bundle']) / 'manifest.json')],
            'Worker manifest mismatch')
    require(environment['driver_sha256'] == plan['hashes'][plan['driver']], 'Driver mismatch')
    needed = {'request.json', 'input.sys', 'environment.json'}
    if result['status'] == 'certificate_verified':
        needed.update({'certificate.bin', 'check.argv.json', 'check.stdout.txt',
                       'count.argv.json', 'count.stdout.txt', 'controls/result.json'})
        needed.update(label + '.step.json' for label in ['controls', 'count', 'check'])
        if result['certificate_origin'] == 'newly produced':
            needed.add('produce.step.json')
    require(needed <= set(result['artifacts']), 'Required evidence omitted from artifact hashes')
    for name, expected in result['artifacts'].items():
        path = attempt / name
        require(path.resolve().is_relative_to(attempt.resolve()), 'Artifact escapes attempt')
        require(digest(path) == expected, 'Artifact hash mismatch: ' + name)
    require(terminal['returncode'] == (1 if result['status'] == 'failed' else 0),
            'Wrapper status disagrees with result')
    bound = None
    if result['status'] == 'certificate_verified':
        stages = ['controls', 'count', 'check']
        if result['certificate_origin'] == 'newly produced':
            stages.append('produce')
        for label in stages:
            stage = result['steps'][label]
            require(stage['returncode'] == 0 and stage['timeout'] is False, 'Failed stage: ' + label)
            require(read(attempt / (label + '.step.json')) == stage, 'Stage receipt mismatch: ' + label)
        controls = read(attempt / 'controls/result.json')
        require(controls['status'] == 'passed' and len(controls['fixtures']) == 3, 'Controls incomplete')
        for fixture in controls['fixtures']:
            require(fixture['independent_checker'] and fixture['reference_byte_identity'] and
                    fixture['count'] == fixture['exhaustive_count'], 'Control failed')
        r = request['record']
        argv = read(attempt / 'check.argv.json')
        require(argv[1] == str(Path(plan['bundle']) / 'cert_check.py') and
                argv[2] == str(attempt / 'certificate.bin'), 'Checker paths mismatch')
        counter = read(attempt / 'count.argv.json')
        require(counter == list(map(str, [Path(plan['bundle']) / 'bin/count_by_sum_worker',
                r['n'], r['modulus_hex'], r['z_hex'], r['a6_hex'],
                len(r['V_basis_hex']), *r['V_basis_hex']])), 'Counter arguments mismatch')
        require(argv[3:] == list(map(str, [r['n'], r['modulus_hex'], r['a2'],
                r['a6_hex'], r['z_hex'], *r['V_basis_hex']])), 'Checker arguments mismatch')
        accepted = re.search(r'VALID: 1 is not in W_4\(F\), and codim W_4\(F\) >= (\d+)',
                             (attempt / 'check.stdout.txt').read_text())
        require(accepted is not None, 'Independent checker acceptance absent')
        q = int(accepted[1])
        count = int((attempt / 'count.stdout.txt').read_text())
        require(q == result['certified_codimension_lower_bound'], 'Codimension mismatch')
        require(count == result['exact_solutions'], 'Exact count mismatch')
        require(digest(attempt / 'certificate.bin') == result['certificate_sha256'], 'Certificate mismatch')
        bound = 5 if q > count else None
    require(result.get('last_fall_degree_lower_bound') == bound, 'Unsupported bound in result')
    return root, result, {'schema': 'semaev.panel-collection/v1', 'id': result['id'],
        'prior_id': result['prior_id'], 'status': result['status'],
        'last_fall_degree_lower_bound': bound, 'verified_artifact_count': len(result['artifacts']),
        'plan_sha256': digest(plan_path), 'protocol_file_sha256': digest(protocol_path),
        'source_output_root': str(root), 'result_sha256': digest(attempt / 'result.json')}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--plan', type=Path, required=True)
    ap.add_argument('--protocol', type=Path, required=True)
    ap.add_argument('--out', type=Path)
    args = ap.parse_args()
    root, result, record = verify(args.plan, args.protocol)
    if args.out:
        require(not args.out.resolve().is_relative_to(root.resolve()), 'Output must be outside raw attempt')
        args.out.mkdir(parents=True, exist_ok=False)
        manifest = []
        with tarfile.open(args.out / 'raw-evidence.tar.gz', 'w:gz') as archive:
            for path in sorted(root.rglob('*')):
                if not path.is_file():
                    continue
                relative = str(path.relative_to(root))
                included = relative != 'attempt-001/certificate.bin'
                manifest.append(dict(path=relative, bytes=path.stat().st_size,
                                     sha256=digest(path), in_raw_archive=included))
                if included:
                    archive.add(path, arcname=relative, recursive=False)
        record['files'] = manifest
        record['raw_archive_sha256'] = digest(args.out / 'raw-evidence.tar.gz')
        for source, name in [(root / 'attempt-001/result.json', 'result.json'),
                             (root / 'terminal.json', 'terminal.json')]:
            shutil.copyfile(source, args.out / name)
        (args.out / 'manifest.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({k: v for k, v in record.items() if k != 'files'}, indent=2))


if __name__ == '__main__':
    main()
