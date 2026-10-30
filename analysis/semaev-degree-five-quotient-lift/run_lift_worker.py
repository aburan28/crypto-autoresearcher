#!/usr/bin/env python3
"""One checked retained-seed lift; immutable stages, capped children, durable uploads."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import resource
import shutil
import signal
import subprocess
import sys
import time
import urllib.request


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def save(path, value):
    with Path(path).open('x') as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write('\n')


def placement(request, upload):
    limit = request['memory_bytes']
    if not (0 < limit <= 96 << 30):
        raise ValueError('invalid child memory cap')
    if not (1 <= request['chunk_rows'] <= 60000):
        raise ValueError('invalid chunk')
    if not (0 < request['stage_timeout_seconds'] <= 21600):
        raise ValueError('invalid watchdog')
    values = {}
    for name in ('memory.max', 'memory.current'):
        path = Path('/sys/fs/cgroup') / name
        values[name] = path.read_text().strip() if path.exists() else None
    if upload:
        maximum = values['memory.max']
        if maximum in (None, 'max') or int(maximum) < request['pod_memory_bytes']:
            raise ValueError('finite declared pod memory not observed')
        if request['pod_memory_bytes'] < limit + (2 << 30):
            raise ValueError('insufficient supervisor headroom')
        if int(maximum) - int(values['memory.current']) < limit:
            raise ValueError('insufficient current cgroup headroom')
    else:
        available = int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines()
                             if x.startswith('MemAvailable:'))) * 1024
        if available < limit + (2 << 30):
            raise ValueError('insufficient local headroom')
    return values


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--bundle', type=Path, required=True)
    ap.add_argument('--request', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--upload', action='store_true')
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=False)
    req = json.loads(a.request.read_text())
    if sha(a.bundle/'manifest.json') != req['worker_manifest_sha256']:
        raise ValueError('request does not bind this worker manifest')
    manifest = json.loads((a.bundle/'manifest.json').read_text())
    for name, expected in manifest['files'].items():
        if sha(a.bundle/name) != expected:
            raise ValueError('bundle hash mismatch: ' + name)
    save(a.out/'request.json', req)
    target = os.environ['ISOLAB_RESULTS_URI'].rstrip('/')+'/lift/' if a.upload else None
    uploaded = set()
    result = dict(id=req['id'], prior_id=req['prior_id'], status='started', steps={},
                  scope='Exact algebra; no timing or LFD upper-bound inference')

    def checkpoint():
        if target:
            for path in sorted(a.out.rglob('*')):
                if path.is_file() and str(path) not in uploaded:
                    subprocess.run(['aws','s3','cp',str(path),target+str(path.relative_to(a.out)),
                                    '--only-show-errors'], check=True, timeout=1200)
                    uploaded.add(str(path))

    def run(label, argv, cap):
        def limits():
            resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
        argv = list(map(str, argv))
        save(a.out/(label+'.argv.json'), argv)
        started = time.monotonic()
        with (a.out/(label+'.stdout.txt')).open('xb') as out, (a.out/(label+'.stderr.txt')).open('xb') as err:
            child = subprocess.Popen(argv, stdout=out, stderr=err, preexec_fn=limits,
                start_new_session=True, env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
            timeout = False
            try:
                child.wait(timeout=req['stage_timeout_seconds'])
            except subprocess.TimeoutExpired:
                timeout = True
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait()
        step = dict(returncode=child.returncode, timeout=timeout, memory_bytes=cap,
                    elapsed_seconds=time.monotonic()-started, wall_valid=False)
        result['steps'][label] = step
        save(a.out/(label+'.step.json'), step)
        checkpoint()
        if child.returncode or timeout:
            raise RuntimeError(label+' failed or timed out')
        return (a.out/(label+'.stdout.txt')).read_text()

    def check(label, certificate, record, degree, cap):
        text = run(label, [sys.executable,a.bundle/'cert_check.py',certificate,
            record['n'],record['modulus_hex'],record['a2'],record['a6_hex'],
            record['z_hex'],*record['V_basis_hex']], cap)
        match = re.search(r'VALID: 1 is not in W_'+str(degree)+r'\(F\), and codim W_'+str(degree)+r'\(F\) >= (\d+)', text)
        if not match:
            raise ValueError('original checker acceptance missing')
        return int(match[1])

    try:
        observed = placement(req, a.upload)
        save(a.out/'environment.json', dict(cgroup=observed, uname=list(platform.uname()),
            python=platform.python_version(), request_sha256=sha(a.request),
            manifest_sha256=sha(a.bundle/'manifest.json'), driver_sha256=sha(Path(__file__)),wall_valid=False))
        checkpoint()
        for i, fixture in enumerate(manifest['lift_fixtures']):
            cert = a.out/('control-'+str(i)+'.bin')
            run('control-produce-'+str(i),[a.bundle/'bin/quotient_lift',a.bundle/fixture['seed'],cert,4096,1<<30],1<<30)
            if sha(cert) != fixture['expected_sha256']:
                raise ValueError('runtime candidate byte mismatch')
            check('control-check-'+str(i),cert,fixture['record'],5,1<<30)
        seed = a.out/'seed.bin'
        if 'seed_file' in req:
            shutil.copyfile(a.bundle/req['seed_file'],seed)
        else:
            compressed = a.out/'seed.gz'
            with urllib.request.urlopen(req['seed_url'],timeout=120) as source, compressed.open('xb') as dest:
                shutil.copyfileobj(source,dest,1<<20)
            if sha(compressed) != req['seed_gzip_sha256']:
                raise ValueError('compressed seed hash mismatch')
            with gzip.open(compressed,'rb') as source, seed.open('xb') as dest:
                shutil.copyfileobj(source,dest,1<<20)
        if sha(seed) != req['seed_sha256']:
            raise ValueError('seed hash mismatch')
        record = req['record']
        result['seed_codimension'] = check('check4',seed,record,4,req['memory_bytes'])
        counted = run('count',[a.bundle/'bin/count_by_sum',record['n'],record['modulus_hex'],
            record['z_hex'],record['a6_hex'],len(record['V_basis_hex']),*record['V_basis_hex']],1<<30)
        count = int(counted.strip())
        if count != req['expected_exact_solutions']:
            raise ValueError('exact count disagrees with frozen request')
        result['exact_solutions'] = count
        cert = a.out/'certificate.bin'
        produced = json.loads(run('produce5',[a.bundle/'bin/quotient_lift',seed,cert,
            req['chunk_rows'],req['memory_bytes']],req['memory_bytes']))
        if produced['status'] == 'projection_kills_one':
            result['status'] = 'projection_kills_one'
        elif produced['status'] == 'candidate_certificate':
            codim = check('check5',cert,record,5,req['memory_bytes'])
            result.update(status='certificate_verified',certified_codimension_lower_bound=codim,
                          certificate_sha256=sha(cert))
            if codim > count:
                result['last_fall_degree_lower_bound'] = 6
        else:
            raise ValueError('unknown producer result')
    except Exception as error:
        result.update(status='failed',error=str(error))
    result['artifacts'] = {str(p.relative_to(a.out)):sha(p) for p in a.out.rglob('*') if p.is_file()}
    save(a.out/'result.json',result)
    checkpoint()
    print(json.dumps(result),flush=True)
    return 1 if result['status']=='failed' else 0


if __name__ == '__main__':
    sys.exit(main())
