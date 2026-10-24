#!/usr/bin/env python3
"""Independent bit-string and partition replay for analysis.json."""

import hashlib
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
output = json.loads((HERE / 'analysis.json').read_text())
cert_path = ROOT / 'research/nist_seed_selection_20261016/raw/full_prime_order_certificates.jsonl'
certs = [item for item in
         (json.loads(line) for line in cert_path.read_text().splitlines())
         if item.get('record') == 'certificate']
by_key = defaultdict(list)
for item in certs:
    by_key[(item['target'], item['index'])].append(item)

assert len(certs) == 82 and len(by_key) == 69
seen = set()
for row in output['rows']:
    key = row['stream'], row['index']
    assert key not in seen and key in by_key
    seen.add(key)
    for branch in by_key[key]:
        p = int(branch['p'])
        t = p.bit_length()
        count = (t - 1) // 160
        first_width = t - 160*count
        seed = int(branch['seed'], 16)
        pieces = []
        for i in range(count + 1):
            value = (seed+i) % 2**160
            pieces.append(format(int(hashlib.sha1(value.to_bytes(20, 'big')).hexdigest(), 16), '0160b'))
        first = pieces[0][-first_width:]
        bits = '0' + first[1:] + ''.join(pieces[1:])
        r = int(bits, 2)
        b = int(branch['b'], 16)
        assert len(bits) == t
        assert (r*b*b + 27) % p == 0
        assert branch['side'] in row['branches']
assert seen == set(by_key)
summary = output['summary']
assert summary['seed_level_eligible'] == 69
assert summary['published'] + summary['unpublished'] == 69
assert summary['retrospective_omissions'] + summary['additional_unpublished'] == 59
assert summary['order_too_wide_only'] + summary['opposite_root_only'] == 48
assert sum(v['all_1997_numerically_eligible'] for v in output['streams'].values()) == 69
print('verified 82 dated SHA-1 branch equations and 69 disjoint seed-level classes')
