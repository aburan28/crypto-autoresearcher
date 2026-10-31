#!/usr/bin/env python3
"""Map each certified D4 panel lower bound to its checked public archive receipt."""
import collections
import datetime
import hashlib
import json
from pathlib import Path
import tarfile
from urllib.parse import urlparse


STUDY = Path('analysis/semaev-degree-five-quotient-lift')
COVERAGE = STUDY / 'validation/panel-coverage-20261031-001/coverage.json'
OUT = STUDY / 'validation/publication-coverage-20261031-001'
RECEIPT_ROOTS = [
    Path('analysis/semaev-m2-last-fall-degree/submission-20261029/archive'),
    STUDY / 'panel-archive',
    STUDY / 'panel-local-archive-001',
]
BUNDLE = STUDY / 'runtime/semaev-panel-worker-20261029.tar.gz'
BUNDLE_PUBLICATION = STUDY / 'runtime/panel-publication.json'
BUNDLE_MEMBERS = {
    'fresh-n42-rand-03': 'requests/fresh-n42-rand-03/retained.bin',
    'fresh-n42-rand-04': 'requests/fresh-n42-rand-04/retained.bin',
}


def digest(path):
    h = hashlib.sha256()
    size = 0
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(block)
            size += len(block)
    return size, h.hexdigest()


def checked_receipts(expected_certificates):
    index = collections.defaultdict(list)
    for root in RECEIPT_ROOTS:
        for path in sorted(root.glob('*.publication.json')):
            receipt = json.loads(path.read_text())
            certificate = receipt.get('certificate_sha256')
            if certificate not in expected_certificates:
                continue
            if receipt.get('schema') == 'semaev.publication-readback/v1':
                checks = receipt['checks']
                assert 'anonymous HTTPS GET and SHA256 for every asset' in checks
                assert 'gzip decompression and original certificate SHA256' in checks
                public = next((f['anonymous_url'] for f in receipt['files'] if f['name'].endswith('.D4.cert.gz')), None)
                assert public
                mode = 'separate_gzip_certificate'
            elif 'anonymous_download_verified' in receipt:
                assert receipt['anonymous_download_verified'] and receipt['downloaded_certificate_hash_verified']
                public = receipt['public_url']
                mode = 'evidence_archive_with_certificate'
            else:
                assert receipt['anonymous_get_verified'] and receipt['anonymous_url']
                public = receipt['anonymous_url']
                archive_path = path.parent / Path(urlparse(public).path).name
                assert digest(archive_path) == (receipt['bytes'], receipt['sha256'])
                with tarfile.open(archive_path, 'r:gz') as archive:
                    member = archive.getmember('./certificate.bin')
                    h = hashlib.sha256()
                    with archive.extractfile(member) as stream:
                        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
                            h.update(block)
                    assert h.hexdigest() == certificate
                mode = 'evidence_archive_with_verified_member'
            index[certificate].append({'mode': mode, 'public_url': public,
                                       'receipt_path': str(path), 'receipt_sha256': digest(path)[1]})
    return index


def bundle_evidence(expected):
    publication = json.loads(BUNDLE_PUBLICATION.read_text())
    assert publication['anonymous_https_get_verified']
    assert digest(BUNDLE) == (publication['bytes'], publication['sha256'])
    result = {}
    with tarfile.open(BUNDLE, 'r:gz') as archive:
        for name, member in BUNDLE_MEMBERS.items():
            item = archive.getmember(member)
            h = hashlib.sha256()
            size = 0
            with archive.extractfile(item) as stream:
                for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
                    h.update(block)
                    size += len(block)
            assert size == 344101184 and h.hexdigest() == expected[name]
            result[name] = {'mode': 'worker_bundle_member', 'public_url': publication['url'],
                            'archive_member': member, 'archive_sha256': publication['sha256'],
                            'receipt_path': str(BUNDLE_PUBLICATION),
                            'receipt_sha256': digest(BUNDLE_PUBLICATION)[1]}
    return result


def main():
    coverage = json.loads(COVERAGE.read_text())
    assert coverage['certified_lfd_at_least5'] == 59
    expected = {}
    for row in coverage['rows']:
        if row['last_fall_degree_lower_bound'] != 5:
            continue
        result = json.loads(Path(row['result_path']).read_text())
        assert result['certificate_sha256']
        expected[row['id']] = result['certificate_sha256']
    assert len(expected) == 59
    receipts = checked_receipts(set(expected.values()))
    embedded = bundle_evidence(expected)
    rows = []
    for name, certificate in sorted(expected.items()):
        hits = receipts.get(certificate, [])
        if name in embedded:
            assert not hits
            location = embedded[name]
        else:
            assert len(hits) == 1, (name, hits)
            location = hits[0]
        rows.append({'id': name, 'certificate_sha256': certificate, **location})
    assert len(rows) == 59
    modes = dict(collections.Counter(row['mode'] for row in rows))
    assert modes.get('worker_bundle_member') == 2
    OUT.mkdir(parents=True, exist_ok=False)
    record = {'schema': 'semaev.publication-coverage/v1',
              'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'scope': 'Receipt and local bundle-content audit of public locations for 59 certified lower-bound certificates. Historical anonymous GET receipts are reused; this run does not redownload every asset.',
              'panel_coverage_path': str(COVERAGE), 'panel_coverage_sha256': digest(COVERAGE)[1],
              'certified_lower_bound_certificates': 59, 'mapped_public_locations': len(rows),
              'modes': modes, 'rows': rows}
    (OUT / 'publication-coverage.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({'mapped_public_locations': len(rows), 'modes': modes}))


if __name__ == '__main__':
    main()
