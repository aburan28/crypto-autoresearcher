#!/usr/bin/env python3
"""Bind and check fixed positive/negative certificate admission fixtures."""
import hashlib
import json
import re
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def accepted(code, stdout):
    text = stdout.decode(errors='replace')
    rows = re.findall(r'^\s*\d+:\s*(-?\d+)\s+([01])\s+', text, re.M)
    return code == 0 and bool(rows) and all(ok == '1' for _, ok in rows) and '%!%' not in text


def main():
    out = HERE / 'attempts/checker-controls-v1'
    out.mkdir(parents=True, exist_ok=False)
    build = json.loads((HERE / 'attempts/build-v4/result.json').read_text())
    checked = json.loads((HERE / 'attempts/checker-build-v1/result.json').read_text())
    work = Path(build['work_path'])
    assert checked['status'] == 'built_unexecuted'
    assert sha(work / 'checkcertif') == checked['executable_sha256']
    assert not accepted(0, b'')
    assert not accepted(0, b'Total time is 0.00s\n')
    assert not accepted(0, b'0: -1 0 0.00s\n')
    assert not accepted(1, b'0: -1 1 0.00s\n')
    local = HERE / '.work/checker-controls-v1'
    local.mkdir(parents=True, exist_ok=False)
    root = work / 'ECPP/Ecpp/C/Ex'
    prime101 = (HERE / 'attempts/small-v1/prime-101/certificate.cformat').read_bytes()
    sources = [('source-certif1', (root / 'certif1_c').read_bytes(), True), ('source-certif2', (root / 'certif2_c').read_bytes(), True), ('prime101', prime101, True), ('prime65537', (HERE / 'attempts/small-v1/prime-65537/certificate.cformat').read_bytes(), True), ('cm-only101', (HERE / 'attempts/cm-only-v1/cm-only-101/certificate.cformat').read_bytes(), True), ('empty', b'', False), ('truncated', prime101[:8], False), ('mutated-root', prime101.replace(b'101\n', b'105\n', 1), False)]
    assert sources[-1][1] != prime101
    image = json.loads(subprocess.check_output(['docker', 'image', 'inspect', '--platform', 'linux/386', 'alpine:3.20']))[0]
    fixtures = []
    for name, payload, expectation in sources:
        path = local / (name + '.cert')
        path.write_bytes(payload)
        fixtures.append({'name': name, 'expected_accept': expectation, 'sha256': sha(path), 'bytes': len(payload)})
        (out / (name + '.cert')).write_bytes(payload)
    (out / 'started.json').write_text(json.dumps({'recorded_utc': datetime.now(timezone.utc).isoformat(), 'scope': 'fixed compatibility checker controls, no named NIST/ANSI order', 'script_sha256': sha(__file__), 'protocol_sha256': sha(HERE / 'CONTROL_AMENDMENT.md'), 'checker_sha256': checked['executable_sha256'], 'image_digest': image['RepoDigests'][0], 'fixtures': fixtures}, indent=2, sort_keys=True) + '\n')
    records = []
    for fixture in fixtures:
        name = fixture['name']
        target = out / name
        target.mkdir()
        container = 'nist-ecpp-check-' + uuid.uuid4().hex[:10]
        command = ['docker', 'run', '--name', container, '--rm', '--platform', 'linux/386', '--network', 'none', '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', '65534:65534', '--memory', '128m', '--cpus', '1', '--pids-limit', '64', '--mount', 'type=bind,src=' + str(work) + ',dst=/work,readonly', '--mount', 'type=bind,src=' + str(local) + ',dst=/control,readonly', image['RepoDigests'][0], '/work/checkcertif', '-f', '/control/' + name + '.cert']
        begin = time.monotonic()
        reason = None
        try:
            proc = subprocess.run(command, capture_output=True, timeout=15)
            code, stdout, stderr = proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired as e:
            code, stdout, stderr, reason = None, e.stdout or b'', e.stderr or b'', 'watchdog'
            cleanup = subprocess.run(['docker', 'rm', '-f', container], capture_output=True, timeout=15)
            (target / 'cleanup.stdout').write_bytes(cleanup.stdout)
            (target / 'cleanup.stderr').write_bytes(cleanup.stderr)
        (target / 'stdout.txt').write_bytes(stdout)
        (target / 'stderr.txt').write_bytes(stderr)
        verdict = accepted(code, stdout)
        record = {**fixture, 'command': command, 'exit_code': code, 'reason': reason, 'elapsed_seconds': time.monotonic() - begin, 'admission_accept': verdict, 'stdout_sha256': hashlib.sha256(stdout).hexdigest()}
        (target / 'result.json').write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
        records.append(record)
        assert verdict == fixture['expected_accept'], record
    summary = {'status': 'passed', 'scope': 'fixed legacy certificate fixtures and admission negatives only; not independent mathematical review', 'positive': 5, 'negative': 3, 'rows': records, 'script_sha256': sha(__file__)}
    (out / 'CHECKER_CONTROLS_COMPLETE.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': 'passed', 'positive': 5, 'negative': 3}))


if __name__ == '__main__':
    main()
