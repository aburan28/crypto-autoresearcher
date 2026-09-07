"""Successor adapter for EXP-PFDR-a76b91 (host side; never runs in the container).

Assembles the canonical schema-conforming run record from (a) the
tools/audit_process.py supervisor output (launch.json, receipt.json,
stdout.log, stderr.log) and (b) the frozen driver's final stdout payload.

The driver's own manifest is producer metadata carried inside the stdout
payload; it is NOT the canonical record. This adapter constructs the
canonical manifest (schemas/run-manifest.schema.json) per docs/
first-fall-audit-repair.md: "A successor adapter must construct the canonical
manifest and validate it before measurement." No scientific interpretation;
statuses, statuses and reasons are copied from the frozen driver, never
re-classified here.
"""
import argparse
import hashlib
import json
import pathlib
import shutil
import sys

EXP = 'EXP-PFDR-a76b91'
SCHEMA = 'schemas/run-manifest.schema.json'
NUMERIC_REQUIRED = {'completed_valid', 'completed_invalid'}


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def parse_payload(stdout_path):
    lines = [ln for ln in pathlib.Path(stdout_path).read_text().splitlines() if ln.strip()]
    if not lines:
        raise ValueError('payload stdout is empty')
    payload = json.loads(lines[-1])
    if 'manifest' not in payload or 'group' not in payload:
        raise ValueError('final stdout line is not the driver payload')
    return payload


def structural_check(record, schema):
    """Dependency-free fallback: the constraints this adapter relies on."""
    errs = []
    run = record.get('run', {})
    allowed = set(schema['properties']['run']['properties'].keys())
    extra = set(run) - allowed
    if extra:
        errs.append(f'unexpected run keys: {sorted(extra)}')
    for k in ('id', 'experiment_id', 'status', 'code', 'environment', 'inputs', 'timing', 'resources', 'result', 'artifacts'):
        if k not in run:
            errs.append(f'missing run key: {k}')
    if run.get('status') not in schema['properties']['run']['properties']['status']['enum']:
        errs.append('status not in enum')
    for blk, keys in (('code', {'commit', 'dirty', 'command'}),
                      ('timing', {'started_at', 'finished_at', 'wall_seconds', 'total_wall_seconds'}),
                      ('resources', {'peak_rss_bytes', 'cpu_seconds', 'wrapper_postprocessing', 'unavailable_reason'}),
                      ('result', {'metrics', 'valid', 'invalid_reason', 'certificate'}),
                      ('inputs', {'curve_id', 'seed', 'parameters'})):
        if blk in run and set(run[blk]) - keys:
            errs.append(f'unexpected {blk} keys: {sorted(set(run[blk]) - keys)}')
    cert = run.get('result', {}).get('certificate', {})
    if cert.get('kind') != 'none' and cert.get('verified') is not True:
        errs.append('non-none certificate requires verified true')
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--supervisor-output', required=True)
    ap.add_argument('--group', type=int, required=True)
    ap.add_argument('--run-id', required=True)
    ap.add_argument('--dest', required=True, help='repo runs/ directory (parent of the run dir)')
    ap.add_argument('--prefix', required=True, help='repo-relative experiment path, e.g. experiments/EXP-PFDR-a76b91')
    ap.add_argument('--setup-wall-seconds', type=float, required=True)
    args = ap.parse_args()

    sup = pathlib.Path(args.supervisor_output)
    receipt = json.loads((sup / 'receipt.json').read_text())
    launch = json.loads((sup / 'launch.json').read_text())
    rdir = pathlib.Path(args.dest) / args.run_id
    rdir.mkdir(parents=True, exist_ok=False)  # exclusive: a second attempt cannot replace this one

    def copy(name):
        shutil.copyfile(sup / name, rdir / name)
        return name

    def write(name, obj):
        with (rdir / name).open('x') as f:
            f.write(json.dumps(obj, indent=2) + '\n')
        return name

    env_sup = {
        'backend': receipt.get('backend'),
        'image_id': receipt.get('image_id'),
        'container_id': receipt.get('container_id'),
        'memory_boundary': receipt.get('memory_boundary'),
        'memory_limit_bytes': receipt.get('memory_limit_bytes'),
        'wall_limit_seconds': receipt.get('wall_limit_seconds'),
        'supervisor_wall_seconds': receipt.get('wall_seconds'),
        'payload_exit_code': receipt.get('payload_exit_code'),
        'cleanup_error': receipt.get('cleanup_error'),
        'setup_wall_seconds_charged': args.setup_wall_seconds,
        'note': 'Supervisor receipts are infrastructure records, not payload telemetry; '
                'payload CPU/RSS come from the driver manifest (resource.getrusage/process_time).',
    }

    if receipt.get('status') != 'completed' or receipt.get('payload_exit_code') != 0:
        # Honest terminal record for a non-completed supervisor outcome. The
        # driver produced no payload (or a non-zero exit); nothing measured.
        canon = {'run': {
            'id': args.run_id,
            'experiment_id': EXP,
            'status': receipt.get('status', 'failed_infrastructure'),
            'code': {'commit': None, 'dirty': None,
                     'command': ' '.join(receipt.get('command', [])) or None},
            'environment': {'supervisor': env_sup,
                            'payload_environment': None,
                            'payload_environment_unavailable': 'driver did not reach its environment capture'},
            'inputs': {'curve_id': None, 'seed': 0, 'parameters': {'group': args.group, 'toy_scope': True}},
            'timing': {'started_at': receipt.get('started_at'), 'finished_at': receipt.get('finished_at'),
                       'wall_seconds': receipt.get('wall_seconds'),
                       'total_wall_seconds': receipt.get('wall_seconds')},
            'resources': {'peak_rss_bytes': None, 'cpu_seconds': None,
                          'unavailable_reason': receipt.get('unavailable_reason') or receipt.get('error')},
            'result': {'metrics': {'incorrectly_accepted_claims': None, 'measured_fixture_count': 0,
                                   'attempted': receipt.get('payload_exit_code') is not None,
                                   'group': args.group},
                       'valid': False,
                       'invalid_reason': receipt.get('error') or receipt.get('unavailable_reason'),
                       'certificate': {'kind': 'none', 'verified': None, 'verifier': None}},
        }}
        files = [write('command.txt', (canon['run']['code']['command'] or '') + '\n'),
                 write('environment.json', canon['run']['environment']),
                 write('raw-result.json', {'group': args.group, 'run_id': args.run_id, 'fixtures': [],
                                           'incorrectly_accepted_claims': None, 'native_measurements': 0,
                                           'checker': None,
                                           'reason': 'payload did not complete; no fixture evaluation'}),
                 write('certificates.json', {'native_matrices': [], 'native_certificates': [],
                                             'missing_native_reason': 'payload did not complete'}),
                 copy('stdout.log'), copy('stderr.log')]
        files.append(write('supervisor-launch.json', launch))
        files.append(write('supervisor-receipt.json', receipt))
        canon['run']['artifacts'] = {n: {'path': f'{args.prefix}/runs/{args.run_id}/{n}', 'sha256': sha(rdir / n)} for n in files}
        write('manifest.yaml', canon)
        report = {'validated': None, 'reason': f'supervisor status {receipt.get("status")}: no canonical validation of a completed payload',
                  'receipt_status': receipt.get('status')}
        write('adapter-report.json', report)
        print(json.dumps({'run_id': args.run_id, 'status': receipt.get('status'), 'recorded': True}))
        return 0

    payload = parse_payload(sup / 'stdout.log')
    if payload['group'] != args.group or payload['run_id'] != args.run_id:
        raise ValueError('payload group/run-id mismatch with reserved identity')
    mp = payload['manifest']['run']
    if mp['id'] != args.run_id or mp['experiment_id'] != EXP:
        raise ValueError('manifest identity mismatch')
    frozen = json.loads((pathlib.Path(args.prefix) / 'implementation.md').read_text()
                        .split('```json\n')[1].split('\n```')[0])
    for name, digest in frozen['sha256'].items():
        actual = sha(pathlib.Path(args.prefix) / name)
        if actual != digest:
            raise ValueError(f'frozen hash mismatch for {name}: {actual} != {digest}')
    if not isinstance(mp['resources']['peak_rss_bytes'], int) or not isinstance(mp['resources']['cpu_seconds'], (int, float)):
        raise ValueError('completed run must carry numeric payload resources')
    if mp['timing']['wall_seconds'] > 900:
        raise ValueError('payload wall exceeds the frozen per-run cap')

    fixtures = payload['fixtures']
    measured = sum(1 for f in fixtures if f.get('status') in ('admissible', 'inadmissible'))
    environment = dict(mp['environment'])
    environment['freeze'] = {'frozen_at': mp['code']['freeze_timestamp'], 'sha256': mp['code']['sha256']}
    environment['supervisor'] = env_sup
    environment['inference'] = mp['inference']

    canon = {'run': {
        'id': args.run_id,
        'experiment_id': EXP,
        'status': mp['status'],
        'code': {'commit': mp['code']['commit'], 'dirty': mp['code']['dirty'], 'command': mp['code']['command']},
        'environment': environment,
        'inputs': {'curve_id': None, 'seed': 0,
                   'parameters': {'fixtures': [f for f in json.loads((pathlib.Path(args.prefix) / 'inputs.json').read_text())['fixtures']
                                    if f['group'] == args.group],
                                  'group': args.group, 'toy_scope': True}},
        'timing': {'started_at': mp['timing']['started_at'], 'finished_at': mp['timing']['finished_at'],
                   'wall_seconds': mp['timing']['wall_seconds'],
                   'total_wall_seconds': mp['timing']['total_charged_wall_seconds']},
        'resources': {'peak_rss_bytes': mp['resources']['peak_rss_bytes'], 'cpu_seconds': mp['resources']['cpu_seconds']},
        'result': {'metrics': {'incorrectly_accepted_claims': mp['result']['metrics']['incorrectly_accepted_claims'],
                               'measured_fixture_count': measured, 'group': args.group,
                               'fixture_statuses': {f['id']: f['status'] for f in fixtures}},
                   'valid': mp['result']['valid'], 'invalid_reason': mp['result']['invalid_reason'],
                   'certificate': mp['result']['certificate']},
    }}
    files = [write('command.txt', mp['code']['command'] + '\n'),
             write('environment.json', environment),
             write('raw-result.json', {'group': args.group, 'run_id': args.run_id, 'fixtures': fixtures,
                                       'incorrectly_accepted_claims': 0, 'native_measurements': 0,
                                       'checker': payload['checker']}),
             write('certificates.json', payload['cert']),
             copy('stdout.log'), copy('stderr.log')]
    files.append(write('supervisor-launch.json', launch))
    files.append(write('supervisor-receipt.json', receipt))
    canon['run']['artifacts'] = {n: {'path': f'{args.prefix}/runs/{args.run_id}/{n}', 'sha256': sha(rdir / n)} for n in files}
    write('manifest.yaml', canon)

    schema = json.loads(pathlib.Path(SCHEMA).read_text())
    validated, how = None, None
    try:
        import jsonschema
        jsonschema.validate(canon, schema)
        validated, how = True, 'jsonschema'
    except ImportError:
        errs = structural_check(canon, schema)
        validated, how = (not errs), ('structural_fallback:' + (';'.join(errs) if errs else 'passed'))
    report = {'validated': validated, 'validation': how, 'receipt_status': receipt.get('status'),
              'payload_status': mp['status'],
              'frozen_hashes_verified': sorted(frozen['sha256'].keys()),
              'supervisor': {k: env_sup[k] for k in ('image_id', 'container_id', 'memory_boundary')},
              'note': 'Adapter records only; statuses copied from the frozen driver, not re-classified.'}
    write('adapter-report.json', report)
    print(json.dumps({'run_id': args.run_id, 'status': mp['status'], 'validated': validated, 'validation': how,
                      'fixtures': {f['id']: f['status'] for f in fixtures}}))
    return 0 if validated else 1


if __name__ == '__main__':
    sys.exit(main())
