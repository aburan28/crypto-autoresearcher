#!/usr/bin/env python3
"""Two-worker S3 recovery controls on fixed Semaev fixtures; no frontier claim."""
import argparse
import hashlib
import json
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
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def save(path, obj):
    with path.open('x') as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.write('\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bundle', type=Path, required=True)
    ap.add_argument('--request', type=Path, required=True)
    ap.add_argument('--protocol', type=Path, required=True)
    ap.add_argument('--role', choices=['reference', 'restored'], required=True)
    ap.add_argument('--source-prefix')
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    req = json.loads(a.request.read_text())
    protocol = json.loads(a.protocol.read_text())
    assert protocol['freeze']['status'] == 'frozen'
    assert sha(a.request) == protocol['links']['request_sha256']
    assert sha(a.bundle/'manifest.json') == req['manifest_sha256']
    manifest = json.loads((a.bundle/'manifest.json').read_text())
    for name, expected in manifest['files'].items():
        assert sha(a.bundle/name) == expected, name
    if a.role == 'restored':
        assert a.source_prefix and a.source_prefix.startswith('s3://')
    target = os.environ['ISOLAB_RESULTS_URI'].rstrip('/') + '/checkpoint-control/'
    source = a.source_prefix.rstrip('/') if a.source_prefix else target.rstrip('/')
    a.out.mkdir(parents=True, exist_ok=False)
    env = {k:v for k,v in os.environ.items() if not k.startswith('SEMAEV_CHECKPOINT_')}
    env.update(OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1',
               LD_LIBRARY_PATH=str(a.bundle/'lib')+os.pathsep+env.get('LD_LIBRARY_PATH',''))
    save(a.out/'environment.json', dict(role=a.role, source_prefix=source,
         destination=target, hostname=platform.node(), uname=list(platform.uname()),
         request_sha256=sha(a.request), protocol_sha256=protocol['freeze']['protocol_sha256'],
         manifest_sha256=sha(a.bundle/'manifest.json'), prlimit_path=shutil.which('prlimit'), wall_valid=False))
    rows = []
    uploaded = set()

    def upload():
        # Only closed immutable files. Snapshot objects have their own synchronous hook.
        for path in sorted(a.out.rglob('*')):
            if not path.is_file() or path in uploaded:
                continue
            if 'snapshots' in path.relative_to(a.out).parts or 'restore-files' in path.relative_to(a.out).parts:
                continue
            subprocess.run(['aws','s3','cp',str(path),target+str(path.relative_to(a.out)),
                            '--only-show-errors'], check=True, timeout=120)
            uploaded.add(path)

    upload()
    for i, fixture in enumerate(manifest['fixtures']):
        root = a.out/str(i); root.mkdir()
        row = dict(instance_id=str(i), seed=0, arm=a.role, passed=False, steps=[])
        record = fixture['record']
        seed = a.bundle/fixture['seed']
        certificate = root/'certificate.bin'
        context = root/'context.json'
        save(context, dict(request_sha256=sha(a.request), protocol_sha256=protocol['freeze']['protocol_sha256'],
             seed_sha256=sha(seed), binary_sha256=manifest['files']['bin/quotient_lift_checkpoint']))

        def run(label, argv, extra=None, expected=0):
            argv = list(map(str,argv))
            def limits():
                resource.setrlimit(resource.RLIMIT_AS, (req['child_memory_bytes'],req['child_memory_bytes']))
            start = time.monotonic()
            with (root/(label+'.stdout')).open('xb') as out, (root/(label+'.stderr')).open('xb') as err:
                try:
                    p = subprocess.Popen(argv, env=dict(env, **(extra or {})), stdout=out,
                                         stderr=err, preexec_fn=limits, start_new_session=True)
                    rc = p.wait(timeout=req['child_timeout_seconds'])
                except subprocess.TimeoutExpired:
                    os.killpg(p.pid,signal.SIGKILL)
                    p.wait()
                    rc = 'timeout'
            step = dict(label=label, argv=argv, returncode=rc, expected=expected,
                        elapsed_seconds=time.monotonic()-start, memory_bytes=req['child_memory_bytes'], wall_valid=False)
            save(root/(label+'.step.json'),step); row['steps'].append(step)
            upload()
            assert rc == expected, (label, rc, expected)
            return (root/(label+'.stdout')).read_text()

        try:
            if a.role == 'reference':
                run('reference',[a.bundle/'bin/quotient_lift_reference',seed,certificate,req['chunk_rows'],req['child_memory_bytes']])
            else:
                receipt = root/'restore.json'
                run('download',[sys.executable,a.bundle/'restore_lift_checkpoint.py','--prefix',
                    source+'/snapshots/'+str(i),'--context',context,'--out',root/'restore-files','--receipt',receipt])
                restored = json.loads(receipt.read_text())
                assert restored['snapshot']['sequence'] == req['stop_after']
                run('resume',[a.bundle/'bin/quotient_lift_checkpoint',seed,certificate,req['chunk_rows'],req['child_memory_bytes']],
                    dict(SEMAEV_CHECKPOINT_RESTORE=restored['local_path'],SEMAEV_CHECKPOINT_DIR=str(root/'snapshots')))
            assert sha(certificate) == fixture['expected_sha256'], 'certificate differs from frozen reference'
            text = run('independent-check',[sys.executable,a.bundle/'cert_check.py',certificate,
                record['n'],record['modulus_hex'],record['a2'],record['a6_hex'],record['z_hex'],*record['V_basis_hex']])
            match = re.search(r'VALID: 1 is not in W_5\(F\), and codim W_5\(F\) >= (\d+)',text)
            assert match, 'independent checker did not accept'
            row['codimension'] = int(match[1])
            counted = run('exact-count',[a.bundle/'bin/count_by_sum',record['n'],record['modulus_hex'],
                record['z_hex'],record['a6_hex'],len(record['V_basis_hex']),*record['V_basis_hex']])
            row['solutions'] = int(counted.strip())
            if a.role == 'reference':
                run('checkpoint-stop',[a.bundle/'bin/quotient_lift_checkpoint',seed,root/'unfinished.bin',req['chunk_rows'],req['child_memory_bytes']],
                    dict(SEMAEV_CHECKPOINT_DIR=str(root/'snapshots'),SEMAEV_CHECKPOINT_STOP_AFTER=str(req['stop_after']),
                         SEMAEV_CHECKPOINT_PUBLISH=str(a.bundle/'publish_lift_checkpoint.py'),
                         SEMAEV_CHECKPOINT_CONTEXT=str(context),SEMAEV_CHECKPOINT_PRUNE_LOCAL='1',
                         SEMAEV_CHECKPOINT_S3_PREFIX=source+'/snapshots/'+str(i)),expected=75)
                assert not (root/'unfinished.bin').exists()
                assert not list((root/'snapshots').glob('checkpoint-*.bin'))
            row.update(passed=True, certificate_sha256=sha(certificate))
        except Exception as error:
            row['error'] = repr(error)
            row['error_filename'] = getattr(error,'filename',None)
        save(root/'result.json',row); rows.append(row); upload()
    result = dict(role=a.role, rows=rows, passed=all(r['passed'] for r in rows),
                  request_sha256=sha(a.request), protocol_sha256=protocol['freeze']['protocol_sha256'],
                  scope='Fixed small-fixture cloud recovery controls only; no frontier LFD inference')
    save(a.out/'result.json',result); upload(); print(json.dumps(result))
    return int(not result['passed'])


if __name__ == '__main__':
    raise SystemExit(main())
