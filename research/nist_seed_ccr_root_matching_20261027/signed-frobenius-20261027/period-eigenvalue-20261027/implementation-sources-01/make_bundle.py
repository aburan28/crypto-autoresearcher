"""Seal explicit public source-recovery metadata; exclude third-party bodies."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile

P = Path(__file__).resolve().parent
FILES = [
    'PLAN.md', 'recover.py', 'recover_followup.py', 'recover_exact.py', 'recover_thesis.py',
    'build_crosswalk.py', 'GET-RECEIPTS.json', 'FOLLOWUP-GET-RECEIPTS.json',
    'EXACT-GET-RECEIPTS.json', 'THESIS-GET-RECEIPTS.json', 'LEHMANN-ALLSTATUS.json',
    'DISTRIBUTED-SOURCE.json', 'SOURCE-REVIEW.json', 'CROSSWALK.json',
    'cohort-crosswalk.csv', 'crosswalk-check.stdout', 'MERGE-HYGIENE.json',
    'merge-tree.stdout.gz', 'merge-tree.stderr.gz',
    'merge-hygiene.stdout.gz', 'merge-hygiene.stderr.gz',
]
assert not (P/'public-evidence.tar.gz').exists()
manifest = {name: {'bytes': (P/name).stat().st_size,
                   'sha256': hashlib.sha256((P/name).read_bytes()).hexdigest()} for name in FILES}
buffer = io.BytesIO()
with tarfile.open(fileobj=buffer, mode='w', format=tarfile.PAX_FORMAT) as tar:
    for name in FILES:
        payload = (P/name).read_bytes()
        info = tarfile.TarInfo('evidence/'+name)
        info.size = len(payload)
        info.mtime = 0
        info.mode = 0o644
        tar.addfile(info, io.BytesIO(payload))
raw = gzip.compress(buffer.getvalue(), mtime=0)
(P/'public-evidence.tar.gz').write_bytes(raw)
record = {
    'kind': 'source-recovery metadata archive; not a scientific execution export',
    'files': manifest, 'sealed_files': len(FILES), 'archive_bytes': len(raw),
    'archive_sha256': hashlib.sha256(raw).hexdigest(),
    'excluded': 'All third-party PDF, PS, OCR, HTML bodies, page images and installed software; old scientific records remain in their original hash-pinned bundles.',
    'new_scientific_trials': 0, 'historical_criterion_identified': False,
}
(P/'BUNDLE.json').write_text(json.dumps(record, indent=2, sort_keys=True)+'\n')
print(json.dumps({k: v for k, v in record.items() if k != 'files'}))
