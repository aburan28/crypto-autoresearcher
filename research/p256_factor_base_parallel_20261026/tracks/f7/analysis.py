"""Frozen analysis of recorded panel files only; no mathematical reruns."""
import argparse
import hashlib
import json
from pathlib import Path


def analyze(directory, output):
    directory, output = Path(directory), Path(output)
    if output.exists():
        raise FileExistsError('Analysis outputs are write-once')
    summary = json.loads((directory/'result.json').read_text())
    checks = json.loads((directory/'checks.json').read_text())
    rows = [json.loads(line) for line in (directory/'rows.jsonl').read_text().splitlines() if line]
    if sorted(row['arm'] for row in rows) != ['candidate', 'reference']:
        raise ValueError('Expected two actual whole-panel arm records')
    if summary['assertions_passed'] != sum(c['passed'] for c in checks):
        raise ValueError('Summary check counts disagree with native records')
    for row in rows:
        expected = sum(c['passed'] and c['arm'] == row['arm'] for c in checks)
        if row['assertions_passed'] != expected:
            raise ValueError('Per-arm check count disagrees')
    files = []
    for path in sorted(directory.rglob('*')):
        if path.is_file() and path != output:
            data = path.read_bytes()
            files.append({'path': str(path.relative_to(directory)), 'bytes': len(data),
                          'sha256': hashlib.sha256(data).hexdigest()})
    result = {'schema': 'p256-pass2-recorded-analysis/v1', 'task': summary['task'],
              'observations_only': True, 'panel_status': summary['status'],
              'execution_unit': 'two actual algorithm arms of one fixed whole panel; shared setup and process',
              'rows': rows, 'case_files': summary['case_files'],
              'failed_checks': [c for c in checks if not c['passed']],
              'error': summary['error'], 'files': files,
              'values_from_raw_summary': summary['values'],
              'analysis_scope': 'recorded flow, exact counts and file custody; no arithmetic rerun, inference or comparative timing',
              'AA_interval': None,
              'AA_not_applicable_reason': 'Exact finite identities, not noisy performance or population inference.'}
    with output.open('x') as handle:
        handle.write(json.dumps(result, indent=2, sort_keys=True)+'\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    result = analyze(args.directory, args.out)
    print(json.dumps({'task': result['task'], 'status': result['panel_status'], 'rows': len(result['rows'])}))
