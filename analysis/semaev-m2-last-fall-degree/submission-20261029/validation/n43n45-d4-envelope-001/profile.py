#!/usr/bin/env python3
"""Recompute source-derived dense D4 admission for all fixed n43..45 inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dossier', type=Path, required=True)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if sha(args.plan) != '70db416219090b5eeeb4a8a4a1e0f289f65b1cdea5691cbb1ed20218c46a0743':
        raise RuntimeError('original fixed panel plan mismatch')
    sys.path.insert(0, str(args.dossier / 'submission-20261029'))
    from certificate_campaign import memory_admission
    plan = json.loads(args.plan.read_text())
    rows = []
    for item in plan['items']:
        record = item['record']
        n = record['n']
        if item['degree'] != 4 or n not in (43, 44, 45):
            continue
        with tempfile.TemporaryDirectory(prefix='semaev-fixed-envelope-') as directory:
            root = Path(directory)
            (root / 'record.json').write_text(json.dumps([record]))
            subprocess.run([sys.executable, args.dossier / 'code/mksys.py', root / 'record.json',
                            record['name'], root / 'input.sys'], check=True,
                           stdout=subprocess.DEVNULL)
            cap = (14 if n < 45 else 16) * 2**30
            profile = memory_admission(root / 'input.sys', 4, 60000, cap)
            rows.append({'id': item['id'], 'n': n, 'family': record['basis'],
                         'system_sha256': sha(root / 'input.sys'),
                         'columns': profile['columns'], 'initial_rows': profile['initial_rows'],
                         'source_envelope_bytes': profile['conservative_bytes'],
                         'child_cap_bytes': cap, 'admitted_by_source_arithmetic': profile['admitted']})
    if len(rows) != 30 or any(sum(row['n'] == n for row in rows) != 10 for n in (43, 44, 45)):
        raise RuntimeError('fixed panel selection incomplete')
    if any(not row['admitted_by_source_arithmetic'] for row in rows):
        raise RuntimeError('planned cap fails for a fixed input')
    result = {'schema': 'semaev.source-envelope-profile/v1', 'original_plan_sha256': sha(args.plan),
              'method': 'certificate_campaign.memory_admission on freshly regenerated exact systems',
              'method_source_sha256': sha(args.dossier / 'submission-20261029/certificate_campaign.py'),
              'system_generator_sha256': sha(args.dossier / 'code/mksys.py'),
              'rows': rows,
              'scope': 'Source-derived planning envelope only; not RSS, completion, or mathematical acceptance.'}
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'rows': len(rows), 'n43_n44_bytes': rows[0]['source_envelope_bytes'],
                      'n45_bytes': rows[-1]['source_envelope_bytes']}))


if __name__ == '__main__':
    main()
