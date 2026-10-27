#!/usr/bin/env python3
"""Copy recorded summaries and perform labelled sums only; never run a solver."""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('/workspace/classical-ecdlp-validation-ready'))
    parser.add_argument('--postrun', type=Path, default=Path('/workspace/classical-ecdlp-endpoint-reuse/postrun-RUN-ECDLP-b883bf-01'))
    parser.add_argument('--out', type=Path, default=Path(__file__).with_name('data.json'))
    args = parser.parse_args()
    run = args.repo / 'experiments/EXP-ECDLP-2b4ff1/runs/RUN-ECDLP-b883bf'
    raw = run / 'modal/collected/tree/raw'
    analysis = json.loads((args.postrun/'analysis/summary.json').read_bytes())
    verification = json.loads((args.postrun/'public-verification/summary.json').read_bytes())
    aa = json.loads((args.postrun/'aa-recorded-check.json').read_bytes())
    receipt = json.loads((run/'execution-receipt.json').read_bytes())
    manifest = json.loads((raw/'algorithm-raw-manifest.json').read_bytes())
    launch = json.loads((run/'launch.json').read_bytes())
    protocol = json.loads((args.repo/'experiments/EXP-ECDLP-2b4ff1/protocol.modal-vm.v1.json').read_bytes())
    panel = []
    sources = {}
    for path in sorted((args.postrun/'analysis').glob('per-cell-[0-9][0-9][0-9].json')):
        panel.extend(json.loads(path.read_bytes()))
        sources[str(path)] = sha(path)
    assert len(panel) == 768
    totals = defaultdict(lambda: {'children': 0, 'targets': 0, 'group_additions_m64': 0,
                                  'whole_child_cpu_seconds': 0.0, 'maximum_child_maxrss_bytes': 0})
    for row in panel:
        arm = row['arm']
        value = totals[arm]
        value['group_additions_m64'] += row['prefixes']['64']['counters']['group_additions']
        value['targets'] += sum(row['status_counts'].values())
        value['children'] += 1
    for path in sorted((raw/'cells').glob('*/*/execution.json')):
        child = json.loads(path.read_bytes())
        assert child['status'] == 'completed' and child['exitcode'] == 0 and child['clock']['wall_valid'] is False
        value = totals[child['arm']]
        value['whole_child_cpu_seconds'] += child['rusage']['user_seconds'] + child['rusage']['system_seconds']
        value['maximum_child_maxrss_bytes'] = max(value['maximum_child_maxrss_bytes'], child['rusage']['maxrss_bytes'])
        sources[str(path)] = sha(path)
    for path in [args.postrun/'analysis/summary.json', args.postrun/'public-verification/summary.json',
                 args.postrun/'aa-recorded-check.json', run/'execution-receipt.json', run/'manifest.yaml',
                 raw/'algorithm-raw-manifest.json', run/'launch.json',
                 args.repo/'experiments/EXP-ECDLP-2b4ff1/protocol.modal-vm.v1.json']:
        sources[str(path)] = sha(path)
    ver_fields = ('status', 'public_fixtures', 'public_target_ids', 'settings_cells', 'producer_cells',
                  'raw_rows', 'target_arm_cases', 'verified_case_witnesses', 'retained_terminal_equations',
                  'promotions_checked', 'producer_status_counts', 'hidden_scalar_labels_read',
                  'native_cost_counters_verified', 'execution_or_isolation_attested',
                  'total_curve_order_independently_counted', 'scientific_review_or_performance_qualification')
    output = {
        'schema': 'classical.ecdlp.descriptive-run-report-data/v1',
        'recorded_at': datetime.now(timezone.utc).isoformat(),
        'run_id': 'RUN-ECDLP-b883bf', 'experiment_id': 'EXP-ECDLP-2b4ff1',
        'hypothesis_id': 'H-ECDLP-3509c4', 'goal_id': 'GOAL-ECDLP-e70832',
        'source_a': 'fe01ccd832832488c58abeef17548b0a8db6035f',
        'source_b': 'de6ed88850fc8bad17ccbabfad8b66a791e478e5',
        'binary_sha256': manifest['binary_sha256'],
        'protocol_sha256': manifest['protocol_sha256'],
        'inputs_manifest_sha256': manifest['inputs_manifest_sha256'],
        'launch': launch,
        'supervisor': {k: receipt[k] for k in ('status', 'started_at', 'finished_at', 'returncode', 'check_returncode')},
        'flow': manifest['flow'],
        'verification': {k: verification[k] for k in ver_fields},
        'aa': {'passes': aa['passes'], 'cell_pairs': aa['cell_pairs'], 'native_streams': aa['native_streams'],
               'recorded_target_rows': aa['recorded_target_rows'], 'mismatches': aa['mismatches'], 'field_names': aa['field_names']},
        'analysis': {k: analysis[k] for k in ('curves', 'replicates_per_curve', 'bootstrap_replicates',
                                           'bootstrap_seed', 'bootstrap_unit', 'primary_panel_eligible',
                                           'aa_counter_mismatches', 'comparisons')},
        'repeated_query_records': len(analysis['duplicate_public_queries']),
        'arm_diagnostics': dict(totals),
        'diagnostic_arithmetic': {
            'group_additions_m64': 'Sum of the frozen per-cell prefix64 counter, across128 cells per arm. This is not the equal-curve geometric mean comparison.',
            'whole_child_cpu_seconds': 'Sum of wait4 user_seconds+system_seconds over128 children per arm; includes common validation, parsing, solver, output and teardown. Clocks are unqualified operational diagnostics.',
            'maximum_child_maxrss_bytes': 'Maximum of128 recorded whole-child Linux wait4ru_maxrss values, each converted fromKiB tobytes by sourceA. Not an endpoint-arena or physical-host isolation attestation.'},
        'protocol_freeze': protocol['freeze'],
        'sources_sha256': sources,
        'archive': {'uri': 's3://setec-astronomy-artifacts/store/sha256/80/80fe9afc0762b80bfa030c13a6f4df32b358a70fc57bbdcf7e5ff1b0bc06d88c',
                    'bytes': 43223355, 'sha256': '80fe9afc0762b80bfa030c13a6f4df32b358a70fc57bbdcf7e5ff1b0bc06d88c'},
        'observations_only': True, 'official_status_changed': False,
    }
    with args.out.open('x') as stream:
        json.dump(output, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'out': str(args.out), 'bytes': args.out.stat().st_size, 'sources': len(sources)}, indent=2))


if __name__ == '__main__':
    main()
