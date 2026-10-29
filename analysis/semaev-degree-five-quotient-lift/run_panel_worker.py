#!/usr/bin/env python3
"""One immutable panel attempt, with stage-by-stage durable uploads.

The input request pins the system and optional retained certificate. The worker
bundle pins the original checker and qualified native binaries. Upload failure
stops execution; pod success alone is never a mathematical result.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import resource
import signal
import shutil
import subprocess
import sys
import time


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def save(path, obj):
    with path.open('x') as stream:
        json.dump(obj, stream, indent=2, sort_keys=True)
        stream.write('\n')


def admission(system, degree, chunk, limit):
    lines = system.read_text().splitlines()
    n, _ = map(int, lines[0].split())
    columns = sum(math.comb(n, d) for d in range(min(n, degree)+1))
    low = sum(math.comb(n, d) for d in range(min(n, degree-1)+1))
    rows = 0
    for line in lines[1:]:
        fields = line.split()
        if int(fields[0]):
            dg = max(bin(int(x, 16)).count('1') for x in fields[1:])
            if dg <= degree:
                rows += sum(math.comb(n, j) for j in range(min(n, degree-dg)+1))
    stride = 8*((columns+63)//64)
    replacement = stride*(max(rows, columns+chunk)+columns+chunk+low)
    export = stride*max(rows, columns+chunk)+columns*stride
    envelope = math.ceil(max(rows*stride, replacement, export)*1.35)+2**30
    return {'conservative_bytes': envelope, 'limit_bytes': limit,
            'admitted': envelope <= limit, 'measured_rss': False}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--bundle', type=Path, required=True)
    ap.add_argument('--request', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--upload', action='store_true')
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    request = json.loads(args.request.read_text())
    manifest = json.loads((args.bundle/'manifest.json').read_text())
    for name, digest in manifest['files'].items():
        if sha(args.bundle/name) != digest:
            raise ValueError('Worker bundle hash mismatch: ' + name)
    system = args.request.parent/request['system']
    if sha(system) != request['system_sha256']:
        raise ValueError('System hash mismatch')
    record = request['record']
    degree = request['degree']
    if degree != 4:
        raise ValueError('This continuation is only the original D4 panel')
    if record['a2'] != 0:
        raise ValueError('Counter is qualified here only for a2=0')
    target = None
    if args.upload:
        target = os.environ['ISOLAB_RESULTS_URI'].rstrip('/')+'/panel/'
    uploaded = set()

    def checkpoint():
        if target:
            # Never copy an actively written file. Called only between stages.
            for path in sorted(args.out.rglob('*')):
                if path.is_file() and str(path) not in uploaded:
                    relative = str(path.relative_to(args.out))
                    subprocess.run(['aws', 's3', 'cp', str(path), target+relative,
                                    '--only-show-errors'], check=True, timeout=600)
                    uploaded.add(str(path))

    save(args.out/'request.json', request)
    shutil.copyfile(system, args.out/'input.sys')
    save(args.out/'environment.json', {
        'uname': list(platform.uname()), 'python': platform.python_version(),
        'cpuinfo': Path('/proc/cpuinfo').read_text(),
        'request_sha256': sha(args.request),
        'worker_manifest_sha256': sha(args.bundle/'manifest.json'),
        'driver_sha256': sha(Path(__file__)), 'wall_valid': False,
        'scope': 'Exact algebra only; shared Spot host, no timing inference'})
    result = {'id': request['id'], 'prior_id': request['prior_id'],
              'degree': degree, 'status': 'started', 'steps': {}}

    def run(label, argv, stdin=None, memory=None):
        limit = memory or request['memory_bytes']
        def limits():
            resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
        argv = list(map(str, argv))
        save(args.out/(label+'.argv.json'), argv)
        started = time.time()
        with (args.out/(label+'.stdout.txt')).open('xb') as out, (args.out/(label+'.stderr.txt')).open('xb') as err:
            process = subprocess.Popen(argv, stdin=stdin, stdout=out, stderr=err,
                start_new_session=True, preexec_fn=limits,
                env={**os.environ, 'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1'})
            timed_out = False
            try:
                process.wait(timeout=request['timeout_seconds'])
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
        result['steps'][label] = {'returncode': process.returncode,
            'timeout': timed_out, 'elapsed_seconds': time.time()-started,
            'wall_valid': False}
        save(args.out/(label+'.step.json'), result['steps'][label])
        checkpoint()
        if process.returncode or timed_out:
            raise RuntimeError(label+' failed or timed out')
        return (args.out/(label+'.stdout.txt')).read_text()

    try:
        checkpoint()
        run('controls', [sys.executable, args.bundle/'validate_worker.py',
            '--bundle', args.bundle, '--out', args.out/'controls'], memory=2**30)
        count = run('count', [args.bundle/'bin/count_by_sum_worker', record['n'],
            record['modulus_hex'], record['z_hex'], record['a6_hex'],
            len(record['V_basis_hex']), *record['V_basis_hex']], memory=2**30)
        result['exact_solutions'] = int(count.strip())
        cert = args.out/'certificate.bin'
        if request.get('retained_certificate'):
            source = args.request.parent/request['retained_certificate']
            if sha(source) != request['retained_certificate_sha256']:
                raise ValueError('Retained candidate hash mismatch')
            # Copy into this attempt so its durable output is self-contained.
            shutil.copyfile(source, cert)
            result['certificate_origin'] = 'retained candidate; rechecked in this attempt'
        else:
            decision = admission(system, degree, request['chunk'], request['memory_bytes'])
            save(args.out/'admission.json', decision)
            if not decision['admitted']:
                result['status'] = 'resource_capped'
                raise StopIteration()
            with system.open('rb') as stream:
                output = run('produce', [args.bundle/'bin/lfdclose2_worker', degree,
                    1, request['chunk'], cert], stdin=stream)
            marker = re.search(r'W4_one ([01])', output)
            if not marker:
                raise ValueError('Missing producer completion marker')
            if marker[1] == '1':
                result['status'] = 'producer_contains_one'
                # No certificate inference, even if the native trace claims one.
                raise StopIteration()
            result['certificate_origin'] = 'newly produced'
        checked = run('check', [sys.executable, args.bundle/'cert_check.py', cert,
            record['n'], record['modulus_hex'], record['a2'], record['a6_hex'],
            record['z_hex'], *record['V_basis_hex']])
        accepted = re.search(r'VALID: 1 is not in W_4\(F\), and codim W_4\(F\) >= (\d+)', checked)
        if not accepted:
            raise ValueError('Original independent checker did not accept')
        result['certified_codimension_lower_bound'] = int(accepted[1])
        result['certificate_sha256'] = sha(cert)
        result['status'] = 'certificate_verified'
        if int(accepted[1]) > result['exact_solutions']:
            result['last_fall_degree_lower_bound'] = 5
    except StopIteration:
        pass
    except Exception as error:
        result['status'] = 'failed'
        result['error'] = str(error)
    result['artifacts'] = {str(p.relative_to(args.out)): sha(p)
                           for p in args.out.rglob('*') if p.is_file()}
    save(args.out/'result.json', result)
    checkpoint()
    print(json.dumps(result, sort_keys=True), flush=True)
    return 1 if result['status'] == 'failed' else 0


if __name__ == '__main__':
    sys.exit(main())
