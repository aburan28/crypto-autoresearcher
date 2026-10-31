"""Seal public metadata in two bounded components; omit third-party bodies."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile

P = Path(__file__).resolve().parent
FILES = sorted(p.name for p in P.glob('*-ACCESS.json')) + [
    'ACCESS.json', 'PLAN.md', 'recover.py', 'fetch.py', 'inspect_package.py',
    'document_source.py', 'source_crosswalk.py', 'SOURCE-REVIEW.json',
    'PACKAGE-INSPECTION.json', 'PACKAGE-VERSION-NOTE.json', 'CROSSWALK.json',
    'cohort-crosswalk.csv', 'package-members.csv.gz',
    'package-check.stdout', 'package-check.stderr',
    'crosswalk-check.stdout', 'crosswalk-check.stderr',
    'MERGE-HYGIENE.json', 'merge-tree.stdout.gz', 'merge-tree.stderr.gz',
    'merge-hygiene.stdout.gz', 'merge-hygiene.stderr.gz',
]
assert len(FILES) == len(set(FILES))


def binding(raw):
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


manifest = {n: binding((P/n).read_bytes()) for n in FILES}
buffer = io.BytesIO()
with tarfile.open(fileobj=buffer, mode='w') as tar:
    for n in FILES:
        body = (P/n).read_bytes()
        m = tarfile.TarInfo('evidence/'+n)
        m.size, m.mtime, m.mode = len(body), 0, 0o644
        tar.addfile(m, io.BytesIO(body))
raw = gzip.compress(buffer.getvalue(),mtime=0)
assert len(raw) < 65536
assert not (P/'public-evidence.tar.gz').exists()
(P/'public-evidence.tar.gz').write_bytes(raw)
catalog = (P/'package-file-hashes.json.gz').read_bytes()
assert len(catalog) < 65536
record = {
    'kind': 'source recovery metadata; not a scientific execution export',
    'files': manifest, 'sealed_files': len(FILES),
    'archive': {'path': 'public-evidence.tar.gz', **binding(raw)},
    'external_components': {'package-file-hashes.json.gz': binding(catalog)},
    'excluded': 'All third-party HTML, PS, PDF, OCR, original package bytes and page renderings; prior scientific inputs remain in their hash-bound studies.',
    'new_scientific_trials': 0, 'historical_criterion_identified': False,
}
assert not (P/'BUNDLE.json').exists()
(P/'BUNDLE.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
print(json.dumps({'status': 'SEALED', 'files': len(FILES),
                  'archive': record['archive'], 'external_components': record['external_components']}))
