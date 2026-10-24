#!/usr/bin/env python3
"""Frozen 19-curve two-proxy Pareto comparison; no fitting."""
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INPUTS = {
    'sea': (ROOT / 'research/nist_seed_1997_selection_extension_20261023/sea_signature/runs/scan-20261023T1840Z/raw.json',
            '4a0df1de260e4533253ef591f7b084b73e86fac5e03558ec3609081c750f48fe'),
    'certificate': (ROOT / 'research/nist_seed_order_certificate_20261023/analysis.json',
                    'a86f488c3481519269725c1acf76e614b27f53b25f6fe23fd3b1e4fb7196c69c'),
    'omitted': (ROOT / 'research/nist_seed_skipped_curves_20261016/assessed.json',
                '370e79ce0bff8f26bb437fe37d1756f3f8261a5c00e9062ba41cf70f272e8841'),
    'published': (ROOT / 'research/nist_seed_skipped_curves_20261016/traits.json',
                  'a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67'),
}


def dominates(a, b):
    return a[0] <= b[0] and a[1] <= b[1] and a != b


def main():
    loaded = {}
    for name, (path, expected) in INPUTS.items():
        raw = path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected, name
        loaded[name] = json.loads(raw)
    sea = loaded['sea']['rows']
    assert len(sea) == 19 and len({r['curve_uid'] for r in sea}) == 19
    cert_rows = loaded['certificate']['rows']
    cert = {(r['curve_uid'], r['direction']): r for r in cert_rows}
    assert len(cert) == 38 and set(r['direction'] for r in cert_rows) == {'minus', 'plus'}
    source = loaded['omitted']['candidate_rows'] + list(loaded['published']['published_controls'].values())
    by_uid = {r['identity']['curve_uid']: r for r in source}
    assert len(by_uid) == 21
    by_field = {}
    for r in sea:
        uid = r['curve_uid']
        meta = by_uid[uid]
        field = (int(r['p_hex'], 16), meta['timestamp'])
        by_field.setdefault(field, []).append({**r, 'ordinal': meta['seed_ordinal_one_based']})
    assert sum(len(v) for v in by_field.values()) == 19
    assert sum(r['label'] == 'omitted' for r in sea) == 11
    assert sum(r['label'] == 'published' for r in sea) == 8
    output_pairs = []
    for field, rows in by_field.items():
        omitted = [r for r in rows if r['label'] == 'omitted']
        published = [r for r in rows if r['label'] == 'published']
        for o, p in itertools.product(omitted, published):
            entry = {'field_bits': field[0].bit_length(), 'timestamp': field[1],
                     'omitted_uid': o['curve_uid'], 'omitted_name': o['name'],
                     'omitted_ordinal': o['ordinal'], 'published_uid': p['curve_uid'],
                     'published_name': p['name'], 'published_ordinal': p['ordinal'],
                     'earlier_omission': o['ordinal'] < p['ordinal'],
                     'sea_cutoff_omitted': o['cutoff_ell'], 'sea_cutoff_published': p['cutoff_ell']}
            for direction in ('minus', 'plus'):
                oc = cert[o['curve_uid'], direction]
                pc = cert[p['curve_uid'], direction]
                for metric in ('largest_prime_at_crossing_bits', 'minimum_prime_power_components'):
                    key = direction + '_' + metric
                    a = (o['cutoff_ell'], oc[metric])
                    b = (p['cutoff_ell'], pc[metric])
                    entry[key] = {'omitted': list(a), 'published': list(b),
                                  'omission_dominates_published': dominates(a, b),
                                  'published_dominates_omission': dominates(b, a)}
            output_pairs.append(entry)
    assert len(output_pairs) == 25
    assert sum(r['earlier_omission'] for r in output_pairs) == 16
    summary = {'all_same_field_pairs': 25, 'earlier_omission_pairs': 16}
    for direction in ('minus', 'plus'):
        for metric in ('largest_prime_at_crossing_bits', 'minimum_prime_power_components'):
            key = direction + '_' + metric
            summary[key] = {
                'earlier_omission_dominates_published': sum(r['earlier_omission'] and r[key]['omission_dominates_published'] for r in output_pairs),
                'all_omission_dominates_published': sum(r[key]['omission_dominates_published'] for r in output_pairs),
                'earlier_published_dominates_omission': sum(r['earlier_omission'] and r[key]['published_dominates_omission'] for r in output_pairs),
            }
    output = {'protocol_sha256': hashlib.sha256((HERE/'PROTOCOL.md').read_bytes()).hexdigest(),
              'input_sha256': {name: expected for name, (_, expected) in INPUTS.items()},
              'pairs': output_pairs, 'summary': summary}
    target = HERE / 'analysis.json'
    assert not target.exists()
    target.write_text(json.dumps(output, sort_keys=True, indent=2) + '\n')
    print(json.dumps(summary, sort_keys=True))


if __name__ == '__main__':
    main()
