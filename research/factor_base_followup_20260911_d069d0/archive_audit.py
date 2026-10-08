#!/usr/bin/env python3
"""Read-only digest audit of already-finalized public synthetic archives."""
import datetime as dt
import hashlib
import json
from pathlib import Path

SOURCE = Path('/Volumes/SSD990/crypto-hybrid-rank-wt/research/sat_factor_base_review_20260908')
RUNS = [
    ('autolab_n19_k4_balanced_two_swap', '20260911T161257Z-5f6d70e3c8'),
    ('autolab_n19_k4_balanced_two_swap_exhaustive', '20260911T163951Z-5494cdd3cb'),
    ('autolab_n19_k4_two_swap_retained_fresh', '20260911T180242Z-0753387f23'),
    ('autolab_n19_k4_two_swap_retained', '20260911T182124Z-f107bbb0d9'),
]


def digest(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def main():
    output = Path(__file__).with_name('archive_audit.json')
    if output.exists():
        raise FileExistsError(output)
    report = {'started_at': dt.datetime.now(dt.timezone.utc).isoformat(),
              'scope': 'Stored-file integrity and readback of existing verdicts; no scientific rerun or new acceptance decision.',
              'script_sha256': digest(Path(__file__)), 'runs': []}
    for campaign, run_id in RUNS:
        run = SOURCE / campaign / 'runs' / run_id
        manifest = run / 'artifacts/final_manifest.json'
        items = json.loads(manifest.read_text())['files']
        mismatches = []
        total_bytes = 0
        for rel, expected in items.items():
            path = run / rel
            if not path.resolve().is_relative_to(run.resolve()):
                mismatches.append({'path': rel, 'reason': 'outside run'})
                continue
            if not path.is_file():
                mismatches.append({'path': rel, 'reason': 'missing'})
                continue
            total_bytes += path.stat().st_size
            actual = digest(path)
            if actual != expected:
                mismatches.append({'path': rel, 'expected': expected, 'actual': actual})
        verdict = json.loads((run / 'artifacts/verdict.json').read_text())
        validation = json.loads((run / 'artifacts/independent_validation.json').read_text())
        entry = {'run': str(run), 'manifest_sha256': digest(manifest),
                 'file_count': len(items), 'total_bytes': total_bytes,
                 'mismatches': mismatches, 'stored_verdict': verdict['verdict'],
                 'stored_completed_at': verdict.get('completed_at'),
                 'stored_validation_accepted': validation.get('accepted'),
                 'verdict_sha256': digest(run / 'artifacts/verdict.json')}
        distribution = run / 'artifacts/distributions.json'
        if distribution.exists():
            data = json.loads(distribution.read_text())
            entry['stored_paired_ratios'] = {
                contrast: {metric: {k: v for k, v in row[metric].items() if k != 'raw'}
                           for metric in ('complete_primary_per_target_ms', 'process_wall_per_target_ms')}
                for contrast, row in data['paired_contrasts'].items() if contrast.startswith('two_swap')}
        report['runs'].append(entry)
        print(f'{campaign}: {len(items)} files, {len(mismatches)} mismatches', flush=True)
    report['completed_at'] = dt.datetime.now(dt.timezone.utc).isoformat()
    report['all_hashes_match'] = all(not run['mismatches'] for run in report['runs'])
    with output.open('x') as handle:
        json.dump(report, handle, indent=2)
        handle.write('\n')
    if not report['all_hashes_match']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
