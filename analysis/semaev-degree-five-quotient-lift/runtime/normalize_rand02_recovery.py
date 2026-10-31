#!/usr/bin/env python3
"""Project accepted recovery evidence for publication, without changing the run."""
import hashlib
import json
import os
from pathlib import Path
import shutil


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    study = Path(__file__).resolve().parent.parent
    source = study / 'runs/highmem-rand02-check-recovery-001'
    result = json.loads((source / 'result.json').read_text())
    started = json.loads((source / 'started.json').read_text())
    plan = study / 'runtime/highmem-rand02-check-recovery-001.json'
    assert digest(plan) == started['plan_sha256']
    assert json.loads(plan.read_text()) == started['plan']
    for name, entry in result['artifacts'].items():
        p = source / name
        assert p.stat().st_size == entry['bytes'] and digest(p) == entry['sha256']
    assert result['status'] == 'certificate_verified'
    for label in ('count', 'check4'):
        step = result['steps'][label]
        assert step['returncode'] == 0 and step['status'] == 'completed'
        assert step['argv'][3:] == started['plan'][label.replace('check4', 'check') + '_argv']
    cert = Path(started['plan']['check_argv'][2])
    assert digest(cert) == result['certificate_sha256'] == started['plan']['candidate_sha256']
    assert cert.stat().st_size == started['plan']['candidate_bytes']
    assert int((source / 'count.stdout.txt').read_text()) == result['exact_solutions']
    verdict = f"VALID: 1 is not in W_4(F), and codim W_4(F) >= {result['certified_codimension']}"
    assert verdict in (source / 'check4.stdout.txt').read_text()
    assert result['certified_codimension'] > result['exact_solutions']
    original_plan = study / 'highmem-plan.json'
    item = next(x for x in json.loads(original_plan.read_text())['items']
                if x['id'] == 'fresh-n47-rand-02-D5-cascade01-highmem01')
    record = item['record']
    expected = [str(record['n']), record['modulus_hex'], str(record['a2']),
                record['a6_hex'], record['z_hex']] + record['V_basis_hex']
    assert started['plan']['check_argv'][3:] == expected
    name = item['id'] + '-D4-recovery01'
    root = Path('/home/ec2-user/fall-degree-data-20261029/highmem-rand02-recovery-publication')
    target = root / name / 'attempt-001'
    target.mkdir(parents=True, exist_ok=True)
    files = {p.name: p for p in source.iterdir() if p.is_file() and p.name != 'result.json'}
    files.update({'recovery-result.json': source / 'result.json',
                  'recovery-plan.json': plan, 'original-plan.json': original_plan,
                  'check.stdout.txt': source / 'check4.stdout.txt',
                  'check.stderr.txt': source / 'check4.stderr.txt', 'certificate.bin': cert})
    for name_, p in files.items():
        dest = target / name_
        if dest.exists():
            assert digest(dest) == digest(p)
        elif name_ == 'certificate.bin':
            os.link(p, dest)
        else:
            shutil.copyfile(p, dest)
    launch = json.loads((study / 'runs/highmem-rand02-check-recovery-001.launch.json').read_text())
    projected = dict(schema='semaev.recovery-stage-publication/v1', id=name,
        status='certificate_verified', parameters=dict(chain=False, degree=4, record=dict(record, name=name)),
        certificate_sha256=result['certificate_sha256'],
        certified_codimension_lower_bound=result['certified_codimension'],
        exact_solutions=result['exact_solutions'], last_fall_degree_lower_bound=5,
        source_commit=launch['source_commit'], plan_sha256=digest(plan),
        provenance=dict(original_result=str(source / 'result.json'),
            original_result_sha256=digest(source / 'result.json'),
            original_plan_sha256=digest(original_plan),
            note='Publication projection of independent D4 recovery; original cascade remains unfinished. No new draw, D5 result, or upper bound.'),
        artifacts={p.name: dict(bytes=p.stat().st_size, sha256=digest(p))
                   for p in target.iterdir() if p.is_file() and p.name != 'result.json'})
    out = target / 'result.json'
    if out.exists():
        assert json.loads(out.read_text()) == projected
    else:
        out.write_text(json.dumps(projected, indent=2, sort_keys=True) + '\n')
    print(out)


if __name__ == '__main__':
    main()
