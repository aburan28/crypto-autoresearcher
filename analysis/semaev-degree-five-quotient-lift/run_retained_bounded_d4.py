#!/usr/bin/env python3
"""One-attempt D3-to-D4 continuation using pinned retained certificates."""
import argparse
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'semaev-m2-last-fall-degree/submission-20261029'))
from certificate_campaign import command, digest, save


def check_text(text, degree):
    pattern = rf'VALID: 1 is not in W_{degree}\(F\), and codim W_{degree}\(F\) >= (\d+)'
    match = re.search(pattern, text)
    if not match:
        raise ValueError(f'original checker did not accept degree {degree}')
    return int(match[1])


def attempt(item, args, plan_hash):
    root = args.out / item['id']
    root.mkdir(exist_ok=False)
    out = root / 'attempt-001'
    out.mkdir()
    result = dict(schema='semaev.retained-bounded-d4/v1', id=item['id'],
                  plan_sha256=plan_hash, status='started', steps={},
                  stages=[], last_fall_degree_lower_bound=None)
    save(out / 'started.json', result)
    record = item['record']
    seed = Path(item['seed_path'])

    def run(label, argv, cap=args.memory):
        step = command(argv, out, label, args.timeout, cap)
        result['steps'][label] = step
        return step, (out / f'{label}.stdout.txt').read_text()

    try:
        if digest(seed) != item['seed_sha256']:
            raise ValueError('retained seed hash mismatch')
        step, text = run('check3', [sys.executable, args.dossier / 'verify/cert_check.py',
                                   seed, record['n'], record['modulus_hex'], record['a2'],
                                   record['a6_hex'], record['z_hex'], *record['V_basis_hex']])
        if step['returncode'] or check_text(text, 3) != item['seed_codimension']:
            raise ValueError('retained D3 checker/codimension mismatch')
        step, text = run('count', [args.runtime / 'bin/count_by_sum', record['n'],
                                   record['modulus_hex'], record['z_hex'], record['a6_hex'],
                                   len(record['V_basis_hex']), *record['V_basis_hex']], 1 << 30)
        if step['returncode'] or not text.strip().isdigit():
            raise ValueError('fresh exact counter failed')
        count = int(text.strip())
        if count != item['expected_exact_solutions']:
            raise ValueError('fresh exact count disagrees with retained result')
        result['exact_solutions'] = count
        result['stages'].append(dict(degree=3, certified_codimension=item['seed_codimension'],
                                     certificate_sha256=item['seed_sha256']))
        if item['seed_codimension'] > count:
            result['last_fall_degree_lower_bound'] = 4
        cert = out / 'degree4.bin'
        step, text = run('produce4', [args.binary, seed, cert, args.chunk, args.memory])
        if step['status'] == 'timeout':
            result['status'] = 'timeout'
        elif step['returncode']:
            stderr = (out / 'produce4.stderr.txt').read_text()
            result['status'] = 'resource_capped' if 'allocation gate refused' in stderr else 'failed'
            if result['status'] == 'failed':
                result['error'] = f'producer returncode {step["returncode"]}'
        else:
            observed = json.loads(text)
            if observed['status'] == 'projection_kills_one':
                result['status'] = 'projection_kills_one'
            elif observed['status'] == 'candidate_certificate':
                if not cert.is_file():
                    raise ValueError('candidate status without certificate')
                step, text = run('check4', [sys.executable, args.dossier / 'verify/cert_check.py',
                                           cert, record['n'], record['modulus_hex'], record['a2'],
                                           record['a6_hex'], record['z_hex'], *record['V_basis_hex']])
                if step['returncode']:
                    raise ValueError('D4 checker failed')
                codim = check_text(text, 4)
                result['stages'].append(dict(degree=4, certified_codimension=codim,
                                             certificate_sha256=digest(cert)))
                if codim > count:
                    result['last_fall_degree_lower_bound'] = 5
                result['status'] = 'certificate_verified'
            else:
                raise ValueError('unknown producer status')
    except Exception as error:
        result.update(status='failed', error=str(error))
    result['artifacts'] = {p.name: dict(bytes=p.stat().st_size, sha256=digest(p))
                           for p in out.iterdir() if p.is_file()}
    save(out / 'result.json', result)
    print(json.dumps({k: result[k] for k in ('id', 'status', 'last_fall_degree_lower_bound')}), flush=True)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('plan', 'runtime', 'dossier', 'binary', 'out'):
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--memory', type=int, required=True)
    p.add_argument('--chunk', type=int, default=60000)
    p.add_argument('--timeout', type=int, default=21600)
    args = p.parse_args()
    if not (0 < args.memory <= 32 * 2**30 and 0 < args.chunk <= 60000):
        p.error('invalid resource bounds')
    plan = json.loads(args.plan.read_text())
    if plan['memory_bytes'] != args.memory or plan['chunk_rows'] != args.chunk:
        raise ValueError('plan/resource arguments mismatch')
    for path, expected in plan['source_sha256'].items():
        if digest(HERE / path) != expected:
            raise ValueError('source hash mismatch: ' + path)
    if digest(args.binary) != plan['binary_sha256']:
        raise ValueError('native binary hash mismatch')
    if digest(args.runtime / 'bin/count_by_sum') != plan['counter_sha256']:
        raise ValueError('counter binary hash mismatch')
    args.out.mkdir(parents=True, exist_ok=False)
    rows = [attempt(item, args, digest(args.plan)) for item in plan['items']]
    return int(any(row['status'] == 'failed' for row in rows))


if __name__ == '__main__':
    raise SystemExit(main())
