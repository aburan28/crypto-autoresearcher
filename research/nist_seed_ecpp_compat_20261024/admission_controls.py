#!/usr/bin/env python3
"""Replay saved checker output and inject launcher failures; no legacy execution."""
import hashlib
import json
from pathlib import Path
from certificate_admission import admit, parse

HERE = Path(__file__).resolve().parent


def main():
    source = HERE / 'attempts/qemu-v3'
    out = HERE / 'attempts/admission-v1'
    out.mkdir(exist_ok=False)
    rows = []
    controls = [('source-certif1', 100000000000000000039, True),
                ('source-certif2', 3167, False), ('source-certif2-variant', 3167, True),
                ('prime101-cert', 101, True), ('prime65537-cert', 65537, True),
                ('cm-only101-cert', 101, True), ('empty-cert', 101, False),
                ('truncated-cert', 101, False), ('mutated-root-cert', 101, False)]
    for name, root, expectation in controls:
        path = source / name
        result = json.loads((path / 'result.json').read_text())
        stdout, payload = (path / 'program.stdout').read_bytes(), (path / 'input.cformat').read_bytes()
        observed = admit(result, stdout, payload, root)
        rows.append({'name': name, 'expected': expectation, 'observed': observed,
                     'payload_sha256': hashlib.sha256(payload).hexdigest(), 'root': str(root)})
        assert observed == expectation, rows[-1]
    fixture = source / 'prime101-cert'
    result = json.loads((fixture / 'result.json').read_text())
    stdout, payload = (fixture / 'program.stdout').read_bytes(), (fixture / 'input.cformat').read_bytes()
    injected = [('wrong-requested-root', result, stdout, payload, 65537),
                ('missing-completion', {**result, 'vm_valid': False}, stdout, payload, 101),
                ('exception', {**result, 'child_exit': 1}, stdout, payload, 101),
                ('missing-step', result, stdout.splitlines()[0], payload, 101),
                ('duplicate-output', result, stdout + stdout, payload, 101),
                ('extra-certificate', result, stdout, payload + payload, 101),
                ('incomplete-final-sentinel', result, stdout, payload.rstrip()[:-1], 101)]
    for name, r, s, p, n in injected:
        observed = admit(r, s, p, n)
        rows.append({'name': name, 'expected': False, 'observed': observed, 'synthetic_launcher_control': True})
        assert not observed, name
    summary = {'status': 'passed', 'scope': 'strict root/grammar/step binding and fail-closed launcher controls; not independent mathematical certificate verification',
               'cases': len(rows), 'positive': sum(r['expected'] for r in rows), 'rows': rows,
               'source_complete_sha256': hashlib.sha256((source / 'COMPLETE.json').read_bytes()).hexdigest()}
    (out / 'COMPLETE.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': 'passed', 'cases': len(rows)}))


if __name__ == '__main__': main()
