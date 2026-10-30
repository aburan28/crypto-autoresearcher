"""Build experiment.export/v1 from observed F3 files, never planned identities."""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
METRICS = ('cases_completed', 'natural_cases_completed', 'natural_dependencies',
           'natural_useful', 'constructed_useful', 'constructed_zero_Q',
           'oracle_signed_quadruples', 'mitm_pair_evaluations', 'refusal_and_premise_checks')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--analysis', type=Path, required=True)
    parser.add_argument('--protocol', type=Path, default=HERE/'protocol.json')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise SystemExit('Refusing to overwrite an existing export')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(REPO))
    from tools import experiment_protocol as ep
    protocol = ep.read_json(args.protocol)
    execution = ep.read_json(args.run/'execution.json')
    raw_rows = [json.loads(line) for line in (args.run/'rows.jsonl').read_text().splitlines() if line]
    if len(raw_rows) != 2 or {row['arm'] for row in raw_rows} != {'mitm', 'exhaustive'}:
        raise ValueError('two algorithm arms over the same fixed full-panel unit required')
    observed = raw_rows[0]
    base = args.out.parent.resolve()

    def entry(path, kind):
        path = path.resolve()
        data = path.read_bytes()
        return {'path': os.path.relpath(path, base), 'sha256': sha256(data).hexdigest(),
                'bytes': len(data), 'kind': kind}

    e = ep.export_skeleton(protocol, os.path.relpath(args.protocol.resolve(), base),
                           'local', 'F3-pass2-'+args.run.name)
    e['producer'] = execution['producer']
    source = observed['source']
    if execution['protocol_sha256'] != protocol['freeze']['protocol_sha256']:
        raise ValueError('observed execution used a different frozen protocol')
    e['source'] = {'repo': 'crypto-autoresearcher', 'commit': source['observed_git_head'],
                   'dirty': source['global_dirty_before_outputs']}
    # A pinned implementation commit is observed through byte-for-byte Git
    # equivalence checks before execution; runtime HEAD is recorded separately.
    commit = source['instrument_commit'] if source['instrument_commit_byte_equivalence_checked'] else source['observed_git_head']
    e['arms'] = [{'id': arm['id'], 'role': arm['role'],
                  'binary_sha256': source['interpreter_sha256'], 'commit': commit}
                 for arm in protocol['arms']]
    host = ep.read_json(args.run/'host.json')
    host_file = entry(args.run/'host.json', 'host')
    e['host'] = {'path': host_file['path'], 'sha256': host_file['sha256'], 'class_id': None,
                 'summary': {key: host.get(key) for key in ('cpu_model', 'logical_cpus', 'memory_bytes',
                                                           'kernel', 'hypervisor', 'isolation_tier_max')}}
    raw_files = [entry(path, 'host' if path.name == 'host.json' else 'log' if path.suffix == '.log' else 'raw')
                 for path in sorted(args.run.iterdir()) if path.is_file()]
    e['files'] = raw_files
    e['runs'] = []
    for observed in raw_rows:
        failure = observed['status'] != 'succeeded'
        exported_row = ep.run_row(
        run_id=observed['run_id'], arm=observed['arm'], instance_id=observed['instance_id'],
        seed=observed['seed'], replicate=observed['replicate'], warmup=observed['warmup'],
        status=observed['status'], attempts=observed['attempts'], resumed=observed['resumed'],
        checkpoint={'policy': 'none', 'generations_written': 0,
                    'restored_from_generation': None},
        measurements={'counted': {key: observed[key] for key in METRICS},
                      'wall_seconds': observed['wall_seconds'], 'wall_valid': False,
                      'cpu_user_seconds': observed['cpu_user_seconds'],
                      'cpu_sys_seconds': observed['cpu_sys_seconds'],
                      'max_rss_bytes': observed['max_rss_bytes'], 'counters': observed['native_counters']},
        isolation=observed['isolation'],
        verification={'status': observed['verification'], 'verifier': observed['verification_detail']},
        exclusion={'excluded': failure, 'rule': 'panel not completely verified; partial counts are not complete-domain observations' if failure else None},
        artifacts=raw_files, started_at=observed['started_at'], finished_at=observed['finished_at'],
        worker=host['hostname'])
        e['runs'].append(exported_row)
    e['flow'] = ep.compute_flow(e['runs'])
    e['analysis'] = {'script': entry(HERE/'analysis.py', 'analysis'), 'blinded': False,
                      'blinding_key_sha256': None,
                      'outputs': [entry(path, 'analysis') for path in sorted(args.analysis.iterdir()) if path.is_file()],
                      'unmasked_at': None}
    e['notes'] = [{'kind': 'observation', 'by': '/root/pass2_labelled',
                   'text': f"Native status {observed['status']}; {observed['cases_completed']} of10 fixed internal cases completed. Exact counters are retained; wall_valid=false. Native model binding is unprobed."}]
    e['backend_record'] = {'execution': entry(args.run/'execution.json', 'receipt'),
                           'source_byte_equivalence': source,
                           'export_unit': execution['export_unit'],
                           'shared_diagnostic_interval_and_setup': 'The two algorithm arms share construction/postprocessing and one process diagnostic interval. Mirrored native counters describe that joint process, not independently attributable method costs. No clock or cost comparison.'}
    errors = ep.schema_errors(e, 'experiment.export/v1') or ep.lint_export(e, protocol, base, True)
    if errors:
        # Preserve the failed conversion without replacing any prior attempt.
        rejected = args.out.with_name(args.out.stem+'-rejected.json')
        ep.write_once(rejected, {'candidate_export': e, 'findings': errors})
        raise ValueError('export rejected: '+'; '.join(errors))
    ep.write_once(args.out, e)
    print(ep.render_flow(e))


if __name__ == '__main__':
    main()
