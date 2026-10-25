#!/usr/bin/env python3
"""Check certified prime-order branches against the dated X9.62 draft."""

import hashlib
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PDF = Path('/private/tmp/x962-11-17-97.pdf')
CROSS = ROOT / 'research/nist_seed_selection_20261016/raw/full_census_crosscheck_v4.json'
CERT = ROOT / 'research/nist_seed_selection_20261016/raw/full_prime_order_certificates.jsonl'
PDF_DIGEST = '0c231d5176fcf0b239b44732213d281b518a0e16cc6f13f7bd4039ec99807b6e'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dated_r(seed, p):
    t = p.bit_length()  # November 1997: ceil(log2 p), for non-powers of 2.
    s, h = divmod(t - 1, 160)
    h += 1
    value = int.from_bytes(hashlib.sha1(seed.to_bytes(20, 'big')).digest(), 'big')
    value &= (1 << (h - 1)) - 1  # take h low bits, then clear their top bit.
    for i in range(1, s + 1):
        nxt = (seed + i) % (1 << 160)
        value = (value << 160) | int.from_bytes(hashlib.sha1(nxt.to_bytes(20, 'big')).digest(), 'big')
    return value


def main():
    assert digest(PDF) == PDF_DIGEST
    cross = json.loads(CROSS.read_text())
    certs = [json.loads(line) for line in CERT.read_text().splitlines()]
    branches = [row for row in certs if row.get('record') == 'certificate']
    assert cross['status'] == 'validated' and len(branches) == 82
    assert certs[-1]['record'] == 'completed' and certs[-1]['certified_branches'] == 82
    by_key = defaultdict(list)
    for row in branches:
        key = (row['target'], row['index'])
        assert row['name'] == f"{key[0]}:{key[1]}:{row['side']}"
        assert row['order_certified'] and row['n_prime_pari']
        assert row['on_curve'] and row['n_times_point_identity']
        assert row['n_in_hasse_interval'] and row['hasse_interval_narrower_than_n']
        p, n, b = int(row['p']), int(row['n']), int(row['b'], 16)
        seed = int(row['seed'], 16)
        assert p.bit_length() in (192, 224, 239, 256, 384, 521)
        assert n > 2**160 and n != p and n > 1
        assert (-108 + 27*b*b) % p != 0
        assert (dated_r(seed, p)*b*b + 27) % p == 0
        assert dated_r(seed ^ 1, p) != dated_r(seed, p)
        assert all(pow(p, k, n) != 1 for k in range(1, 21))
        by_key[key].append(row)
    assert len(by_key) == 69

    streams = {}
    all_published = all_omitted = all_other = 0
    rows = []
    for name, record in sorted(cross['streams'].items()):
        eligible = set(record['broad_family_both_seeded_roots'])
        published = set(record['published'])
        omissions = set(record['screen_skipped'])
        width = set(record['screen_rejected_order_too_wide'])
        opposite = set(record['seeded_opposite_root_only_prime'])
        assert eligible == published | omissions | width | opposite, name
        assert not any((a & b) for i, a in enumerate([published, omissions, width, opposite])
                       for b in [published, omissions, width, opposite][i+1:])
        branch_keys = {index for target, index in by_key if target == name}
        assert branch_keys == eligible, name
        for index in sorted(eligible):
            bs = by_key[(name, index)]
            assert len({x['seed'] for x in bs}) == 1
            assert len({x['n'] for x in bs}) <= 2
            label = ('published' if index in published else
                     'retrospective_omission' if index in omissions else
                     'order_too_wide_only' if index in width else
                     'opposite_root_only')
            rows.append({'stream': name, 'index': index, 'label': label,
                         'seed': bs[0]['seed'], 'branches': [x['side'] for x in bs],
                         'order_bits': [int(x['n']).bit_length() for x in bs]})
        streams[name] = {
            'published': len(published), 'retrospective_omissions': len(omissions),
            'order_too_wide_only': len(width), 'opposite_root_only': len(opposite),
            'all_1997_numerically_eligible': len(eligible),
            'earliest_eligible_index': min(eligible),
            'published_indices': sorted(published),
        }
        all_published += len(published)
        all_omitted += len(omissions)
        all_other += len(width) + len(opposite)
    assert (all_published, all_omitted, all_other) == (10, 11, 48)
    assert cross['totals']['broad_family_both_seeded_roots'] == len(rows)
    assert cross['totals']['broad_family_unpublished'] == len(rows)-all_published
    assert sum(len(by_key[k]) for k in by_key) == 82
    result = {
        'sources_sha256': {'x962_1997_pdf': digest(PDF),
                           str(CROSS.relative_to(ROOT)): digest(CROSS),
                           str(CERT.relative_to(ROOT)): digest(CERT),
                           'protocol': digest(HERE/'PROTOCOL.md')},
        'summary': {'certified_branches': 82, 'seed_level_eligible': 69,
                    'published': 10, 'unpublished': 59,
                    'retrospective_omissions': 11,
                    'additional_unpublished': 48,
                    'order_too_wide_only': 17,
                    'opposite_root_only': 31},
        'streams': streams, 'rows': rows,
    }
    output = json.dumps(result, sort_keys=True, indent=2) + '\n'
    path = HERE/'analysis.json'
    if path.exists():
        assert path.read_text() == output, 'immutable replay mismatch'
    else:
        path.write_text(output)
    print(json.dumps(result['summary'], sort_keys=True))


if __name__ == '__main__':
    main()
