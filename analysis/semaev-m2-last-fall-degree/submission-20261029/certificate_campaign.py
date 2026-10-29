#!/usr/bin/env python3
"""Retain, replay and archive exact closure certificates; never delete evidence.

Run a frozen plan of named inputs. Existing results are immutable; resumption
skips completed entries and puts interrupted attempts in a new directory.
No solver trace is promoted to a certified lower bound. This driver reuses the
historical C producer and the separate Python checker without changing either.
"""
import argparse
import concurrent.futures
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def save(path, value):
    with open(path, 'x') as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


def memory_admission(system, degree, chunk, limit):
    lines = system.read_text().splitlines()
    n, _ = map(int, lines[0].split())
    columns = sum(math.comb(n, d) for d in range(min(n, degree) + 1))
    low = sum(math.comb(n, d) for d in range(min(n, degree - 1) + 1))
    rows = 0
    for line in lines[1:]:
        fields = line.split()
        if int(fields[0]):
            dg = max(bin(int(x, 16)).count('1') for x in fields[1:])
            if dg <= degree:
                rows += sum(math.comb(n, j) for j in range(min(n, degree - dg) + 1))
    # A can retain its allocation after elimination; include old A, B and Lw.
    stride = 8 * ((columns + 63) // 64)
    replacement = stride * (max(rows, columns + chunk) + columns + chunk + low)
    export = stride * max(rows, columns + chunk) + columns * stride
    envelope = math.ceil(max(rows * stride, replacement, export) * 1.35) + 2**30
    return dict(nvariables=n, columns=columns, initial_rows=rows,
                conservative_bytes=envelope, limit_bytes=limit,
                admitted=envelope <= limit,
                note='Planning bound plus 35% workspace allowance and 1 GiB; RLIMIT_AS also enforced. Not measured RSS.')


def command(argv, directory, label, timeout, memory, held_lock=None):
    argv = ['prlimit', f'--as={memory}', '--'] + [str(x) for x in argv]
    save(directory / f'{label}.argv.json', argv)
    start = time.time()
    with open(directory / f'{label}.stdout.txt', 'x') as out, open(directory / f'{label}.stderr.txt', 'x') as err:
        p = subprocess.Popen(argv, stdout=out, stderr=err, start_new_session=True,
                             pass_fds=() if held_lock is None else (held_lock,),
                             env={**os.environ, 'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1'})
        try:
            rc = p.wait(timeout=timeout)
            state = 'completed' if rc == 0 else 'failed'
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, signal.SIGTERM)
            try:
                p.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid, signal.SIGKILL)
                p.wait()
            rc, state = p.returncode, 'timeout'
    return dict(argv=argv, returncode=rc, status=state, elapsed_seconds=time.time()-start,
                wall_valid=False, isolation='L0')


def run_item(item, args, plan_hash):
    root = args.out / item['id']
    root.mkdir(parents=True, exist_ok=True)
    with open(root / 'lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for old in sorted(root.glob('attempt-*/result.json')):
            prior = json.loads(old.read_text())
            if prior['plan_sha256'] != plan_hash:
                raise ValueError('output belongs to another plan')
            if prior['status'] in ('certificate_verified', 'closure_contains_one', 'resource_capped'):
                if prior.get('certificate_sha256') and digest(old.parent/'certificate.bin') != prior['certificate_sha256']:
                    raise ValueError('retained certificate hash mismatch')
                return prior
        attempt = root / f'attempt-{len(list(root.glob("attempt-*")))+1:03d}'
        attempt.mkdir()
        result = dict(id=item['id'], plan_sha256=plan_hash, source_commit=args.source_commit,
                      binary_sha256=digest(args.binary), parameters=item, status='started', steps={})
        save(attempt/'started.json', result)
        record_path = attempt/'instance.json'
        record = item['record']
        save(record_path, [record])
        sysfile = attempt/'input.sys'
        maker = args.dossier/'code'/('mksys3.py' if item.get('chain') else 'mksys.py')
        steps = result['steps']
        def execute(argv, label, timeout):
            return command(argv, attempt, label, timeout, args.memory, lock.fileno())
        try:
            steps['descent'] = execute([sys.executable, maker, record_path, record['name'], sysfile], 'descent', 300)
            if steps['descent']['returncode']:
                raise RuntimeError('descent failed')
            result['system_sha256'] = digest(sysfile)
            admission = memory_admission(sysfile, item['degree'], args.chunk, args.memory)
            result['memory_admission'] = admission
            if not admission['admitted']:
                result['status'] = 'resource_capped'
            else:
                cert = attempt/'certificate.bin'
                # stdin is passed without a shell, through this driver's worker mode.
                steps['closure'] = execute([sys.executable, Path(__file__).resolve(), 'producer',
                    '--binary', args.binary, '--system', sysfile, '--degree', item['degree'],
                    '--chunk', args.chunk, '--certificate', cert], 'closure', args.timeout)
                if steps['closure']['returncode']:
                    raise RuntimeError('closure failed or timed out')
                output = (attempt/'closure.stdout.txt').read_text()
                m = re.search(rf'W{item["degree"]}_one ([01])', output)
                if not m:
                    raise RuntimeError('missing closure completion marker')
                result['producer_contains_one'] = int(m[1])
                if int(m[1]):
                    if cert.exists():
                        raise RuntimeError('unexpected certificate for a refutation')
                    result['status'] = 'closure_contains_one'
                else:
                    sha = digest(cert)
                    result['certificate_sha256'] = sha
                    result['certificate_bytes'] = cert.stat().st_size
                    if item.get('expected_sha256') and sha != item['expected_sha256']:
                        raise RuntimeError('historical certificate digest mismatch')
                    argv = [sys.executable, args.dossier/'verify/cert_check.py']
                    if item.get('chain'):
                        argv.append('--t3')
                    argv += [cert, record['n'], record['modulus_hex'], record['a2'], record['a6_hex'], record['z_hex'], *record['V_basis_hex']]
                    steps['check'] = execute(argv, 'check', args.timeout)
                    checked = (attempt/'check.stdout.txt').read_text()
                    valid = re.search(rf'VALID: 1 is not in W_{item["degree"]}\(F\), and codim W_{item["degree"]}\(F\) >= (\d+)', checked)
                    if steps['check']['returncode'] or not valid:
                        raise RuntimeError('independent checker rejected or did not finish')
                    result['certified_codimension_lower_bound'] = int(valid[1])
                    result['status'] = 'certificate_verified'
                    result['claim'] = '1 not in W_D; LFD inference additionally requires independently justified unsatisfiability or a sufficient solution-count bound'
        except Exception as error:
            result['status'] = 'failed'
            result['error'] = str(error)
        result['artifacts'] = {p.name: {'sha256': digest(p), 'bytes': p.stat().st_size}
                               for p in attempt.iterdir() if p.is_file()}
        save(attempt/'result.json', result)
        print(json.dumps({k:result[k] for k in ('id','status')}), flush=True)
        return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='action', required=True)
    run = sub.add_parser('run')
    run.add_argument('--plan', type=Path, required=True)
    run.add_argument('--out', type=Path, required=True)
    run.add_argument('--binary', type=Path, required=True)
    run.add_argument('--dossier', type=Path, required=True)
    run.add_argument('--source-commit', required=True)
    run.add_argument('--workers', type=int, default=2)
    run.add_argument('--memory', type=int, default=40*2**30)
    run.add_argument('--timeout', type=int, default=21600)
    run.add_argument('--chunk', type=int, default=60000)
    prod = sub.add_parser('producer')
    for name in ('binary','system','certificate'):
        prod.add_argument('--'+name, required=True, type=Path)
    for name in ('degree','chunk'):
        prod.add_argument('--'+name, required=True, type=int)
    args = p.parse_args()
    if args.action == 'producer':
        with args.system.open('rb') as stream:
            return subprocess.run([str(args.binary),str(args.degree),'1',str(args.chunk),str(args.certificate)], stdin=stream).returncode
    if args.workers not in (1,2) or args.memory > 40*2**30:
        p.error('shared-host envelope: at most two workers and 40 GiB per worker')
    args.out = args.out.resolve()
    args.out.mkdir(parents=True, exist_ok=True)
    plan = json.loads(args.plan.read_text())
    ids = [x['id'] for x in plan['items']]
    if len(ids) != len(set(ids)) or any(not re.fullmatch('[A-Za-z0-9_-]+', x) for x in ids):
        p.error('plan identities must be unique safe path components')
    with open(args.out/'campaign.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with concurrent.futures.ThreadPoolExecutor(args.workers) as pool:
            results = list(pool.map(lambda x: run_item(x,args,digest(args.plan)), plan['items']))
        print(json.dumps({'completed':len(results), 'statuses':{s:sum(x['status']==s for x in results) for s in sorted({x['status'] for x in results})}}),flush=True)
    return int(any(x['status']=='failed' for x in results))


if __name__ == '__main__':
    sys.exit(main())
