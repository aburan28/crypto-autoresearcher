#!/usr/bin/env python3
"""Prospective one-case execution library; no scientific launch CLI.

A Coordinator-approved trial plan must bind and call execute_case. The public
CLI only describes the frozen cohort and executes no legacy program.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import artifact_store
from certificate_admission import admit, parse
from guest_framing import valid_frame
from qemu_controls import vm, record, WORK, RUNTIME


def digest(data):
    return hashlib.sha256(data).hexdigest()


def inputs():
    cohort = json.loads((HERE / 'cohort-inputs.json').read_bytes())
    bindings = json.loads((HERE / 'runtime-bindings.json').read_bytes())
    rows = cohort['rows']
    assert len(rows) == len({r['curve_uid'] for r in rows}) == 21
    assert sum(r['label'] == 'omitted' for r in rows) == 11
    assert sum(r['label'] == 'published' for r in rows) == 10
    artifacts = {}
    for item in bindings['artifacts']:
        logical = ROOT / item['logical_path']
        raw = artifact_store.read_bytes(logical)
        assert digest(raw) == item['sha256'] and len(raw) == item['bytes']
        artifacts[logical.name] = raw
    return cohort, bindings, artifacts


def execute_case(index, destination):
    """Only for a future approved plan; never called by this file's CLI."""
    cohort, bindings, artifacts = inputs()
    assert isinstance(index, int) and 0 <= index < 21
    row = cohort['rows'][index]
    # Source/data are read-only inputs; no catalog change is accepted here.
    data = WORK / 'ECPP/Ecpp/Data'
    actual = {p.relative_to(data).as_posix(): digest(p.read_bytes())
              for p in sorted(data.rglob('*')) if p.is_file()}
    assert actual == bindings['original_data']
    assert digest((RUNTIME / 'vmlinuz-lts').read_bytes()) == bindings['kernel']['kernel_sha256']
    out = Path(destination)
    out.mkdir(parents=True, exist_ok=False)
    identity = {'curve': row, 'cohort_sha256': digest((HERE / 'cohort-inputs.json').read_bytes()),
                'bindings_sha256': digest((HERE / 'runtime-bindings.json').read_bytes()),
                'launcher_sha256': digest(Path(__file__).read_bytes()), 'fresh_process_rng': 'original ModInitialize: srandom(1)',
                'prover_guest_limit_seconds': 300, 'prover_host_limit_seconds': 390,
                'classification_scope': 'legacy prover/checker behavior on an already-certified prime integer'}
    record(out / 'identity.json', identity)
    result, body = vm(out / 'prover', artifacts['qemu-init'], artifacts['runecpp'],
                      ['-l', '/ecpp/', '-f', '/input', '-Fc', '-C', '/tmp/certificate'],
                      payload=row['n'].encode() + b'\n', data_mode='full',
                      cpu_limit=300, host_limit=390)
    serial = (out / 'prover/serial.raw').read_bytes()
    result['vm_valid'] = valid_frame(result['qemu_exit'], serial, result['reason'])
    labels = [s.decode() for s in re.findall(rb'^(?:% )?This number is (prime|composite)\b.*$', body, re.M)]
    observation = {'curve_uid': row['curve_uid'], 'legacy_labels': labels, 'prover': result,
                   'certificate_admitted': False, 'mathematical_classification': 'INDETERMINATE',
                   'reason': 'no complete admitted certificate', 'checker': None,
                   'trace_coverage': 'complete original stdout; unprinted branches are unobserved',
                   'printed_D': re.findall(rb'^% next D is (-?\d+)$', body, re.M),
                   'printed_recursive_N': re.findall(rb'^% N_\d+=(\d+)$', body, re.M)}
    # Convert trace tokens to text without treating absent branches as attempted.
    for key in ['printed_D', 'printed_recursive_N']:
        observation[key] = [s.decode() for s in observation[key]]
    cert_path = out / 'prover/certificate.cformat'
    if result['vm_valid'] and result['child_exit'] == 0 and labels == ['prime'] and cert_path.exists():
        payload = cert_path.read_bytes()
        try:
            steps = parse(payload, int(row['n']))
        except (ValueError, UnicodeError) as e:
            observation['reason'] = 'certificate grammar/root binding: ' + str(e)
        else:
            checker, stdout = vm(out / 'checker', artifacts['qemu-init'], artifacts['checkcertif'],
                                 ['-f', '/input'], payload=payload, cpu_limit=30, host_limit=90)
            checker['vm_valid'] = valid_frame(checker['qemu_exit'], (out / 'checker/serial.raw').read_bytes(), checker['reason'])
            admitted = admit(checker, stdout, payload, int(row['n']))
            observation.update(checker=checker, certificate_admitted=admitted,
                               certificate_steps=steps, certificate_sha256=digest(payload),
                               reason='legacy certificate admitted' if admitted else 'checker admission failed')
            if admitted:
                # Deliberately separate observed software acceptance from prior primality evidence.
                observation['mathematical_classification'] = 'PRIOR_PRIMALITY_EVIDENCE_REQUIRED'
    record(out / 'observation.json', observation)
    return observation


if __name__ == '__main__':
    if sys.argv[1:] != ['--describe']:
        raise SystemExit('Only --describe is exposed. Scientific execution requires a future approved trial plan.')
    cohort, bindings, artifacts = inputs()
    print(json.dumps({'scope': 'prospective inputs only; no execution', 'named_orders_executed': 0,
                      'cases': len(cohort['rows']), 'omitted': cohort['omitted_count'],
                      'published': cohort['published_count'], 'runtime_payloads_verified': sorted(artifacts)}, indent=2))
