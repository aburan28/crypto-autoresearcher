"""Successor candidates correcting the independently identified provenance defect."""
from copy import deepcopy
from pathlib import Path
import hashlib
import json
import yaml

P = Path(__file__).resolve().parent
sources = json.loads((P / 'sources.json').read_text())
manifest = deepcopy(json.loads((P / 'candidates-v2.json').read_text()))
changed = {'IDEA-20261003-4f41d0': 'KR-IC-5765d2',
           'IDEA-20261003-94078e': 'KR-IC-73db3f',
           'IDEA-20261003-c9c6c3': 'KR-IC-73db3f'}
(P / 'candidates-v3').mkdir(exist_ok=True)
for item in manifest['records']:
    previous = yaml.safe_load((P / item['candidate']).read_text())
    doc = deepcopy(previous)
    if item['id'] in changed:
        ref = changed[item['id']]
        card, = [r for r in sources['records'] if ref in r['path']]
        row, = [r for r in doc['idea']['prior_art']['nearest'] if r['ref'] == ref]
        row['provenance'] = 'retrieved'
        row['verified_by'] = {
            'agent': 'Codex coordinator /root; T-782 / TASK-20261029-8b1359',
            'read_on': '2026-10-29',
            'method': 'Direct reading of the pinned repository card through Git; no retrieval-index resolution asserted.',
            'source_path': card['path'],
            'source_commit': sources['source_commit'],
            'source_sha256': card['sha256'],
            'scope': 'Repository-card attribution and comparison only; no new full-text literature verification or independent verification of the card findings.'
        }
    data = yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=100).encode()
    dest = P / 'candidates-v3' / (item['id'] + '.yaml')
    with dest.open('xb') as f:
        f.write(data)
    item['previous_candidate'] = item['candidate']
    item['previous_candidate_sha256'] = item['candidate_sha256']
    item['candidate'] = dest.relative_to(P).as_posix()
    item['candidate_sha256'] = hashlib.sha256(data).hexdigest()
    item['proposed_registry_entry']['superseding_sha256'] = item['candidate_sha256']
manifest['supersedes_candidate_packet'] = 'candidates-v2.json'
manifest['review_finding'] = 'TASK-20261029-d6606a: three direct Git comparisons were incorrectly labelled kb and lacked explicit verified_by. V3 changes only those provenance fields.'
with (P / 'candidates-v3.json').open('x') as f:
    json.dump(manifest, f, indent=2)
    f.write('\n')
print('Prepared four V3 candidates; live ledger and registry remain unchanged.')
