#!/usr/bin/env python3
"""Classify exact-main ecbench replay receipts; repair only omitted nested evidence."""
from __future__ import annotations
import collections
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

BASE = Path('/home/ec2-user/scratch/validation-continuation-20261023')
REPO = Path('/home/ec2-user/crypto-sheriff-main-20261024')
HEAD = '172f84c7b0143ff5b4a26d6d21ffed3bf0f0cf3b'
IN = BASE / 'ecbench-earlier-sessions-v2-20261024'
BINARY = REPO / 'target/release/ecbench'
OUT = BASE / 'ecbench-earlier-classification-20261024.json'
FIX = BASE / 'ecbench-earlier-nested-rechecks-20261024'
TEMP = BASE.parent / 'ecbench-earlier-temp-20261024'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nested_recheck(row: dict) -> dict:
    src = REPO / row['session_dir']
    rid = hashlib.sha256(row['session_dir'].encode()).hexdigest()[:20]
    FIX.mkdir(exist_ok=True)
    audit_path = FIX / f'{rid}.ecbench.json'
    receipt_path = FIX / f'{rid}.json'
    if receipt_path.exists():
        cached = json.loads(receipt_path.read_text())
        assert cached['session_dir'] == row['session_dir'] and cached['source_session_sha256'] == sha(src / 'session.json')
        assert cached['audit_sha256'] == sha(audit_path)
        return cached
    with tempfile.TemporaryDirectory(prefix='ecbench-nested-', dir=TEMP) as d:
        tmp = Path(d)
        for item in src.iterdir():
            (tmp / item.name).symlink_to(item, target_is_directory=item.is_dir())
        for item in src.glob('*.gz'):
            plain = tmp / item.name[:-3]
            if not plain.exists():
                with gzip.open(item, 'rb') as inp, plain.open('wb') as out:
                    shutil.copyfileobj(inp, out)
        proc = subprocess.run([str(BINARY), 'verify', '--dir', str(tmp), '--replay', '0',
                               '--allow-interrupted', '--exit-code', '--out', str(audit_path)],
                              cwd=REPO, capture_output=True, text=True, timeout=1200)
    audit = json.loads(audit_path.read_text())
    result = {'schema': 'ecbench.nested-evidence-recheck/v1', 'head': HEAD,
              'session_dir': row['session_dir'], 'source_session_sha256': sha(src / 'session.json'),
              'original_receipt_sha256': sha(IN / row['_filename']), 'audit_sha256': sha(audit_path),
              'binary_sha256': sha(BINARY), 'exit_code': proc.returncode,
              'stderr_tail': proc.stderr[-800:], 'ok': audit.get('ok'),
              'session_status': audit.get('session_status'), 'records_bound': audit.get('records_bound'),
              'problems': audit.get('problems'), 'records': audit.get('records'),
              'verified_records': audit.get('verified_records'),
              'normalization': 'temporary symlinks to all tracked top-level files and nested evidence; gzip expanded only in scratch'}
    receipt_path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    return result


def main() -> int:
    summary = json.loads((IN / 'summary.json').read_text())
    assert summary['head'] == HEAD and summary['selected'] == 449
    rows = []
    for path in IN.glob('*.json'):
        if path.name.endswith('.ecbench.json') or path.name == 'summary.json':
            continue
        row = json.loads(path.read_text())
        if row.get('schema') != 'ecbench.session.integrity.recheck/v1':
            continue
        assert row['head'] == HEAD
        row['_filename'] = path.name
        rows.append(row)
    assert len(rows) == 449 and len({r['session_dir'] for r in rows}) == 449
    cases = []
    for row in sorted(rows, key=lambda r: r['session_dir']):
        kind = None
        detail = None
        if row['status'] == 'pass':
            audit_path = IN / row['result_file']
            assert sha(audit_path) == row['result_sha256']
            audit = json.loads(audit_path.read_text())
            assert audit['ok'] is True and audit['records_bound'] is True and audit['problems'] == []
            kind = 'complete_bound_pass'
        elif row['status'] == 'fail':
            audit = json.loads((IN / row['result_file']).read_text()) if row.get('result_file') else None
            if audit and audit.get('session_status') == 'interrupted' and audit.get('ok') is True and audit.get('records_bound') is False and audit.get('problems') == []:
                kind = 'interrupted_unbound'
            elif audit and audit.get('problems') and all('exec/' in str(x) and 'missing or altered' in str(x) for x in audit['problems'][1:]) and str(audit['problems'][0]).startswith('records:'):
                corrected = nested_recheck(row)
                detail = corrected
                kind = 'complete_bound_pass_after_nested_correction' if corrected['exit_code'] == 0 and corrected['ok'] is True and corrected['records_bound'] is True and corrected['problems'] == [] else 'unresolved_nested_evidence'
            elif not audit:
                src = REPO / row['session_dir']
                missing = [x for x in ('spec.json', 'host.json', 'plan.json', 'records.jsonl') if not (src / x).is_file()]
                status = json.loads((src / 'session.json').read_text()).get('status')
                detail = {'missing_inputs': missing, 'session_status': status}
                kind = 'complete_missing_inputs' if status == 'complete' and missing else 'unclassified_failure'
            else:
                detail = {'problems': audit.get('problems') if audit else None, 'session_status': audit.get('session_status') if audit else None}
                kind = 'unclassified_failure'
        else:
            kind = 'unclassified_status'
        cases.append({'session_dir': row['session_dir'], 'receipt': row['_filename'], 'classification': kind, 'detail': detail})
    counts = dict(collections.Counter(x['classification'] for x in cases))
    doc = {'schema': 'ecbench.session.integrity.classification/v1', 'head': HEAD,
           'source_summary_sha256': sha(IN / 'summary.json'), 'selected': len(cases),
           'counts': counts, 'nonpass_cases': [x for x in cases if x['classification'] != 'complete_bound_pass']}
    OUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'selected': len(cases), 'counts': counts, 'output': str(OUT)}, sort_keys=True))
    return 1 if any(x.startswith('unclassified') or x.startswith('unresolved') for x in counts) else 0


if __name__ == '__main__':
    raise SystemExit(main())
