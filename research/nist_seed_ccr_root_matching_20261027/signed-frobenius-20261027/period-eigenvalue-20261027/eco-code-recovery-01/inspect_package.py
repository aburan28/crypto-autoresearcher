"""Static inventory of exact archived bytes, without executing package code."""
import collections
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import tarfile

P = Path(__file__).resolve().parent
SOURCE = P/'.work/th-lidia13-tgz.bin'
EXPECTED = '0189dcbb3daab55cb39f213bf612d025b71aac6bd4ca7a5c09b687f47c98d387'
PATTERNS = ['buildLlist', 'choose_relations', 'compute_klist', 'verify_order',
            'simple_verify', 'eco', 'eco_prime', 'eco_gfp', 'Elkies',
            'Schoof', 'Atkin', 'elliptic', 'Fp_polynomial', 'power_mod']
R = {s: re.compile(rb'(?i)(?<![a-z0-9_])'+re.escape(s.encode())+rb'(?![a-z0-9_])')
     for s in PATTERNS}
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
members, hashes, hits, text_sources = [], [], collections.defaultdict(list), {}
with tarfile.open(SOURCE, 'r:gz') as tar:
    for member in tar.getmembers():
        members.append({'name': member.name, 'type': member.type.decode('ascii', errors='replace'),
                        'bytes': member.size, 'mtime': member.mtime, 'link': member.linkname})
        if not member.isfile():
            continue
        body = tar.extractfile(member).read()
        assert len(body) == member.size
        hashes.append({'name': member.name, 'bytes': len(body),
                       'sha256': hashlib.sha256(body).hexdigest()})
        for s, pattern in R.items():
            matches = list(pattern.finditer(body))
            if matches:
                hits[s].append({'name': member.name, 'occurrences': len(matches),
                                'lines': sorted(set(body[:m.start()].count(b'\n')+1 for m in matches))})
        if member.name in ['LiDIA/Readme', 'LiDIA/include/LiDIA/version.h']:
            text_sources[member.name] = body

assert len(members) == 1461 and len(hashes) == 1285
assert hits['Fp_polynomial'] and hits['power_mod']
code_suffixes = {'.c', '.cc', '.C', '.cpp', '.h', '.H', '.hpp'}
code_hits = {s: [r for r in hits[s] if Path(r['name']).suffix in code_suffixes] for s in PATTERNS}
out = io.StringIO(newline='')
w = csv.DictWriter(out, fieldnames=list(members[0]), lineterminator='\n')
w.writeheader()
w.writerows(members)
digest_text = json.dumps(hashes, indent=2, sort_keys=True)+'\n'
summary = {
    'status': 'STATIC_INSPECTION_COMPLETED', 'package_sha256': EXPECTED,
    'package_bytes': SOURCE.stat().st_size, 'archive_capture': '19970517195215',
    'declared_version': '1.3', 'members': len(members), 'regular_files': len(hashes),
    'member_types': dict(collections.Counter(m['type'] for m in members)),
    'source_code_execution': False, 'new_curve_trials': 0,
    'symbol_match_policy': 'Case-insensitive ASCII token boundaries; every regular member scanned. Code subset identified by explicit suffix list.',
    'symbol_file_counts_all': {s: len(hits[s]) for s in PATTERNS},
    'symbol_file_counts_code': {s: len(code_hits[s]) for s in PATTERNS},
    'symbol_hits': dict(hits),
    'version_header_sha256': hashlib.sha256(text_sources['LiDIA/include/LiDIA/version.h']).hexdigest(),
    'readme_sha256': hashlib.sha256(text_sources['LiDIA/Readme']).hexdigest(),
    'historical_nist_caller_authenticated': False,
}
files = {'PACKAGE-INSPECTION.json': json.dumps(summary, indent=2, sort_keys=True)+'\n',
         'package-members.csv': out.getvalue()}
for name, content in files.items():
    if '--check' in sys.argv:
        assert (P/name).read_text() == content
    else:
        assert not (P/name).exists()
        (P/name).write_text(content)
if '--check' in sys.argv:
    assert gzip.decompress((P/'package-file-hashes.json.gz').read_bytes()).decode() == digest_text
else:
    (P/'package-file-hashes.json.gz').write_bytes(gzip.compress(digest_text.encode(), mtime=0))
    for name, data in text_sources.items():
        (P/'.work'/Path(name).name).write_bytes(data)
print(json.dumps({k: v for k,v in summary.items() if k not in ['symbol_hits']}))
