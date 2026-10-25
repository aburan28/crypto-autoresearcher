#!/usr/bin/env python3
"""Run the predeclared compatibility controls, never a named curve order."""
import base64
import hashlib
import json
import re
import shutil
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = HERE / 'attempts/small-v2'
    out.mkdir(parents=True, exist_ok=False)
    build_receipt = HERE / 'attempts/build-v4/result.json'
    build = json.loads(build_receipt.read_text())
    admission = HERE / 'attempts/arithmetic-v3/ARITHMETIC_COMPLETE.json'
    assert json.loads(admission.read_text())['status'] == 'passed'
    work = Path(build['work_path'])
    exe = work / 'runecpp'
    assert sha(exe) == build['artifacts'][str(exe)]
    image = json.loads(subprocess.check_output(['docker', 'image', 'inspect', '--platform', 'linux/386', 'alpine:3.20']))[0]
    assert image['Architecture'] == '386'
    local = HERE / '.work/small-v2'
    local.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(HERE / 'control_guest.sh', local / 'control_guest.sh')
    for n in (101, 65537, 15, 341):
        (local / ('input-' + str(n))).write_text(str(n) + '\n')
    for mode in ('empty', 'missing'):
        data = local / mode / 'Data'
        data.mkdir(parents=True)
        for name in ('spmax.data', 'difnp5e6.data'):
            shutil.copyfile(work / 'ECPP/Ecpp/Data' / name, data / name)
        if mode == 'empty':
            (data / 'ecpp.DfD').write_text('')
    cases = [('composite-341', 341, 'composite', 'original'), ('empty-catalog-101', 101, None, 'empty'), ('missing-catalog-101', 101, None, 'missing')]
    started = {'recorded_utc': datetime.now(timezone.utc).isoformat(), 'scope': 'frozen small compatibility controls and induced failures; no named NIST/ANSI order', 'build_receipt_sha256': sha(build_receipt), 'arithmetic_admission_sha256': sha(admission), 'script_sha256': sha(__file__), 'guest_sha256': sha(HERE / 'control_guest.sh'), 'protocol_sha256': sha(HERE / 'CONTROL_PROTOCOL.md'), 'executable_sha256': sha(exe), 'image_id': image['Id'], 'image_digest': image['RepoDigests'][0], 'cases': cases}
    (out / 'started.json').write_text(json.dumps(started, indent=2, sort_keys=True) + '\n')
    records = []
    for label, n, expected, mode in cases:
        target = out / label
        target.mkdir()
        name = 'nist-ecpp-control-' + uuid.uuid4().hex[:10]
        args = ['-l', '/work/ECPP/Ecpp/' if mode == 'original' else '/control/' + mode + '/', '-f', '/control/input-' + str(n), '-Fc', '-C', '/tmp/certificate']
        if mode != 'original':
            args += ['-nm', '-np']
        cmd = ['docker', 'run', '--name', name, '--rm', '--platform', 'linux/386', '--network', 'none', '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', '65534:65534', '--memory', '128m', '--cpus', '1', '--pids-limit', '64', '--tmpfs', '/tmp:rw,noexec,nosuid,size=16m,mode=1777', '--mount', 'type=bind,src=' + str(work) + ',dst=/work,readonly', '--mount', 'type=bind,src=' + str(local) + ',dst=/control,readonly', image['RepoDigests'][0], 'sh', '/control/control_guest.sh'] + args
        begin = time.monotonic()
        reason = None
        try:
            proc = subprocess.run(cmd, capture_output=True, timeout=30)
            code, stdout, stderr = proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired as e:
            code, stdout, stderr, reason = None, e.stdout or b'', e.stderr or b'', 'watchdog'
            cleanup = subprocess.run(['docker', 'rm', '-f', name], capture_output=True, timeout=15)
            (target / 'cleanup.stdout').write_bytes(cleanup.stdout)
            (target / 'cleanup.stderr').write_bytes(cleanup.stderr)
        (target / 'stdout.txt').write_bytes(stdout)
        (target / 'stderr.txt').write_bytes(stderr)
        text = stdout.decode(errors='replace')
        labels = re.findall(r'^(?:% )?This number is (prime|composite)\b.*$', text, re.M)
        encoded = re.search(r'CERTIFICATE_BEGIN\n(.*?)CERTIFICATE_END', text, re.S)
        certificate = base64.b64decode(encoded.group(1)) if encoded else None
        if certificate is not None:
            (target / 'certificate.cformat').write_bytes(certificate)
        record = {'label': label, 'input': n, 'data_mode': mode, 'expected_label': expected, 'observed_labels': labels, 'command': cmd, 'exit_code': code, 'reason': reason, 'elapsed_seconds': time.monotonic() - begin, 'no_next_D_messages': text.count('No next D'), 'retry_messages': text.count('Forced to retry'), 'certificate_sha256': hashlib.sha256(certificate).hexdigest() if certificate else None, 'certificate_verification': 'not yet run'}
        (target / 'result.json').write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
        records.append(record)
        if expected is not None:
            assert code == 0 and labels == [expected], record
    result = {'status': 'observed', 'scope': 'one remaining small classification checked; two induced failure outcomes retained; prior three raw outputs retained in small-v1; certificate verification pending', 'cases': records, 'started_sha256': sha(out / 'started.json')}
    (out / 'results.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'small_correct': 1, 'induced': [{k: c[k] for k in ('label', 'exit_code', 'observed_labels', 'no_next_D_messages', 'retry_messages')} for c in records[1:]], 'certificate_verification': 'pending'}, sort_keys=True))


if __name__ == '__main__':
    main()
