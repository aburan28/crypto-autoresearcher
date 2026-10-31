#!/usr/bin/env python3
"""Finish two interrupted n42 attempts from retained D4 certificates, without rerunning closure."""
import argparse
import fcntl
import hashlib
import json
from pathlib import Path
import re
import sys

from certificate_campaign import command, digest, memory_admission, save


IDS = ('fresh-n42-rand-03', 'fresh-n42-rand-04')


def available_bytes():
    for line in Path('/proc/meminfo').read_text().splitlines():
        if line.startswith('MemAvailable:'):
            return int(line.split()[1]) * 1024
    raise RuntimeError('MemAvailable missing')


def recover(item, args, plan_hash):
    name = item['id']
    record = item['record']
    root = args.data / 'expansion' / name
    attempt = root / 'attempt-001'
    cert = attempt / 'certificate.bin'
    with (root / 'lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if (attempt / 'result.json').exists() or (attempt / 'check.argv.json').exists():
            raise RuntimeError(f'{name}: result or checker already started; reconcile')
        if json.loads((attempt / 'instance.json').read_text()) != [record]:
            raise RuntimeError(f'{name}: retained presentation differs from frozen plan')
        closure = (attempt / 'closure.stdout.txt').read_text()
        if not re.search(r'W4_one 0\b', closure) or not cert.is_file():
            raise RuntimeError(f'{name}: no complete candidate transcript and certificate')
        before = digest(cert)
        old_count = json.loads((args.data / 'expansion/counts' / name / 'attempt-001/result.json').read_text())
        if old_count['status'] != 'completed' or old_count['ordered_solutions'] != 0:
            raise RuntimeError(f'{name}: retained exact count not zero')
        if old_count['binary_sha256'] != digest(args.count_binary) or old_count['plan_sha256'] != plan_hash:
            raise RuntimeError(f'{name}: retained count instrument or plan mismatch')
        free = available_bytes()
        if free < args.check_memory + args.reserve:
            raise RuntimeError(f'{name}: host memory gate refused ({free} bytes)')
        count_step = command([args.count_binary, record['n'], record['modulus_hex'],
                              record['z_hex'], record['a6_hex'], record['k'],
                              *record['V_basis_hex']], attempt, 'recheck_count', 600, 1 << 30)
        count_text = (attempt / 'recheck_count.stdout.txt').read_text().strip()
        if count_step['returncode'] or count_text != '0':
            raise RuntimeError(f'{name}: fresh counter failed or disagreed')
        check_step = command([sys.executable, args.dossier / 'verify/cert_check.py', cert,
                              record['n'], record['modulus_hex'], record['a2'],
                              record['a6_hex'], record['z_hex'], *record['V_basis_hex']],
                             attempt, 'check', args.timeout, args.check_memory)
        checked = (attempt / 'check.stdout.txt').read_text()
        match = re.search(r'VALID: 1 is not in W_4\(F\), and codim W_4\(F\) >= (\d+)', checked)
        if check_step['returncode'] or not match or digest(cert) != before:
            raise RuntimeError(f'{name}: independent checker failed or certificate changed')
        codim = int(match[1])
        if codim <= 0:
            raise RuntimeError(f'{name}: checked codimension not above exact count')
        result = dict(id=name, plan_sha256=plan_hash, source_commit=args.source_commit,
                      binary_sha256=digest(args.binary), parameters=item,
                      status='certificate_verified', system_sha256=digest(attempt / 'input.sys'),
                      memory_admission=memory_admission(attempt / 'input.sys', 4, 60000, 40 * 2**30),
                      certificate_sha256=before, certificate_bytes=cert.stat().st_size,
                      certified_codimension_lower_bound=codim,
                      steps={'closure': {'status': 'candidate_retained',
                                         'producer_exit_code': None,
                                         'note': 'Original process ended before terminal receipt; no exit code inferred.'},
                             'recheck_count': count_step, 'check': check_step},
                      recovery={'kind': 'retained-certificate-after-interrupted-producer',
                                'original_producer_exit_code_known': False,
                                'closure_stdout_sha256': digest(attempt / 'closure.stdout.txt'),
                                'closure_stderr_sha256': digest(attempt / 'closure.stderr.txt'),
                                'retained_count_result_sha256': digest(args.data / 'expansion/counts' / name / 'attempt-001/result.json'),
                                'fresh_recheck_exact_solutions': 0,
                                'certificate_sha256_before_and_after_checker': before},
                      claim='Checker accepts W4 nonmembership; exact zero count implies named-input LFD >= 5.')
        result['artifacts'] = {p.name: {'sha256': digest(p), 'bytes': p.stat().st_size}
                               for p in attempt.iterdir() if p.is_file()}
        save(attempt / 'result.json', result)
        canonical = hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()
        save(root / f'inference-{canonical}.json', dict(
            id=name, last_fall_degree_lower_bound=5,
            justification='Dossier Proposition 1.4: fresh exhaustive count 0 < independently certified D4 codimension',
            count=old_count, fresh_recheck_exact_solutions=0,
            closure_result_canonical_sha256=canonical,
            scope='Exact named Boolean presentation only; no asymptotic or solver-runtime inference.'))
        return dict(id=name, certificate_sha256=before, checked_codimension=codim,
                    exact_solutions=0, last_fall_degree_lower_bound=5,
                    result_sha256=digest(attempt / 'result.json'))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', type=Path, required=True)
    p.add_argument('--dossier', type=Path, required=True)
    p.add_argument('--binary', type=Path, required=True)
    p.add_argument('--count-binary', type=Path, required=True)
    p.add_argument('--receipt', type=Path, required=True)
    p.add_argument('--source-commit', default='fdd9cb0b73')
    p.add_argument('--check-memory', type=int, default=12 * 2**30)
    p.add_argument('--reserve', type=int, default=2 * 2**30)
    p.add_argument('--timeout', type=int, default=21600)
    args = p.parse_args()
    if args.check_memory != 12 * 2**30 or args.reserve != 2 * 2**30:
        p.error('this recovery uses the fixed 12 GiB checker cap and 2 GiB host reserve')
    if digest(args.binary) != 'f7f920e697b263129e91b44814e18c32b228392496770c29869ab4d00a9e6f04':
        raise RuntimeError('original closure binary hash mismatch')
    if digest(args.count_binary) != 'b2d16d8a27b6133443671af1bcc297af225827af1bbd192aa1cb09a2644f6638':
        raise RuntimeError('original counter binary hash mismatch')
    if digest(args.dossier / 'verify/cert_check.py') != '13d926240a99de4b3eede374932fe245d62e7de65102a4fdf2cccfb0e4463877':
        raise RuntimeError('independent checker source hash mismatch')
    if digest(args.dossier / 'submission-20261029/certificate_campaign.py') != 'd00fb15692709a1450c9a16c06ca36f51afb18158b16ffbeb2527b2cf52c08eb':
        raise RuntimeError('campaign helper source hash mismatch')
    plan_path = args.data / 'expansion/plan.json'
    plan_hash = digest(plan_path)
    if plan_hash != '70db416219090b5eeeb4a8a4a1e0f289f65b1cdea5691cbb1ed20218c46a0743':
        raise RuntimeError('original frozen panel plan hash mismatch')
    plan = json.loads(plan_path.read_text())
    by_id = {item['id']: item for item in plan['items']}
    if any(by_id[name]['degree'] != 4 or by_id[name]['record']['n'] != 42 for name in IDS):
        raise RuntimeError('frozen plan selection mismatch')
    args.receipt.mkdir(parents=True, exist_ok=False)
    rows = []
    terminal = {'schema': 'semaev.n42-retained-recovery/v1',
                'original_plan_sha256': plan_hash, 'rows': rows,
                'status': 'started', 'producer_reruns': 0}
    try:
        with (args.data / 'expansion/expansion.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            for name in IDS:
                row = recover(by_id[name], args, plan_hash)
                rows.append(row)
                save(args.receipt / f'{name}.closed.json', row)
        terminal['status'] = 'complete'
    except BaseException as exc:
        terminal.update(status='failed', error=repr(exc))
        raise
    finally:
        save(args.receipt / 'terminal.json', terminal)
    print(json.dumps(rows), flush=True)


if __name__ == '__main__':
    raise SystemExit(main())
