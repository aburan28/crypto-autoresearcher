#!/usr/bin/env python3
"""Exploratory, source-bound comparison of a public nineteen-curve table."""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EXTERNAL_SHA256 = '9fd4cf9a99482e44e7207b59aa831c58cec15682582a2932b65c04b3c6bc915c'
RAW = ROOT / 'research/nist_seed_1997_selection_extension_20261023/sea_signature/runs/scan-20261023T1840Z/raw.json'
ASS = ROOT / 'research/nist_seed_skipped_curves_20261016/assessed.json'
TRAITS = ROOT / 'research/nist_seed_skipped_curves_20261016/traits.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_external(data):
    assert 'product > 2^(L/2+2)' in data
    rows = {}
    current = None
    for line in data.splitlines():
        match = re.search(r'candidate #(\d+)', line)
        if match:
            current = int(match.group(1))
            assert current not in rows
            rows[current] = {}
        if current is None:
            continue
        for key, pattern in (
            ('reported_cutoff', r'SEA lmax \(Elkies only\):\s*(\d+)'),
            ('listed_elkies', r'Elkies primes < 100:\s*(.*)'),
            ('listed_atkin', r'Atkin primes < 100:\s*(.*)'),
            ('n_hex', r'n = #E \(prime\):\s*(0x[0-9A-Fa-f]+)'),
            ('trace_hex_signed', r't \(trace\):\s*([+-]0x[0-9A-Fa-f]+)'),
            ('b_hex', r'^\s*b:\s*(0x[0-9A-Fa-f]+)'),
            ('seed_hex', r'seed \(20 bytes\):\s*([0-9A-Fa-f]{40})'),
        ):
            match = re.search(pattern, line)
            if match:
                rows[current][key] = (int(match.group(1)) if key == 'reported_cutoff' else
                                      [int(x) for x in match.group(1).split()] if key.startswith('listed_') else match.group(1))
    assert len(rows) == 19 and all(set(v) == {'reported_cutoff', 'listed_elkies', 'listed_atkin', 'n_hex',
                                                'trace_hex_signed', 'b_hex', 'seed_hex'} for v in rows.values())
    return rows


def threshold(primes, signature, predicate):
    product = 1
    for ell, symbol in zip(primes, signature):
        if symbol in '+0':
            product *= ell
        if predicate(product):
            return ell
    raise AssertionError('bound exhausted')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('external', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    assert not args.output.exists()
    assert sha(args.external) == EXTERNAL_SHA256
    ext = parse_external(args.external.read_text())
    raw = json.loads(RAW.read_text())
    source_rows = json.loads(ASS.read_text())['candidate_rows'] + list(json.loads(TRAITS.read_text())['published_controls'].values())
    ordinal = {r['identity']['curve_uid']: r['seed_ordinal_one_based'] for r in source_rows}
    by_uid = {r['identity']['curve_uid']: r for r in source_rows}
    assert len(ordinal) == 21 and len(raw['rows']) == 19
    rows = []
    for r in raw['rows']:
        name = r['name']
        e = ext[ordinal[r['curve_uid']]]
        bound = by_uid[r['curve_uid']]
        p = int(r['p_hex'], 16)
        assert int(e['n_hex'], 16) == int(r['n_hex'], 16)
        assert int(e['trace_hex_signed'], 16) == int(r['trace_hex_signed'], 16)
        source_b, archive_b = int(e['b_hex'], 16), int(bound['b_hex'], 16)
        b_sign_model = 'same' if source_b == archive_b else 'opposite_isomorphic'
        assert source_b == archive_b or (p.bit_length() == 224 and source_b == (-archive_b) % p)
        assert e['seed_hex'].lower() == bound['seed_hex'].lower().removeprefix('0x')
        bits = p.bit_length()
        full = {ell: sign for ell, sign in zip(raw['odd_primes'], r['signature'])}
        listed_plus = set(e['listed_elkies'])
        listed_minus = set(e['listed_atkin'])
        expected_under100 = {ell for ell in raw['odd_primes'] if ell < 100}
        assert listed_plus.isdisjoint(listed_minus)
        assert listed_plus | listed_minus == expected_under100
        assert all(full[ell] in '+0' for ell in listed_plus)
        assert all(full[ell] == '-' for ell in listed_minus)
        ramified_listed_elkies = sorted(ell for ell in listed_plus if full[ell] == '0')
        literal_cutoff = threshold(raw['odd_primes'], r['signature'], lambda m: m*m > (1 << (bits+4)))
        integer_cutoff = threshold(raw['odd_primes'], r['signature'], lambda m: m > (1 << (((bits-1)//2)+2)))
        assert integer_cutoff == e['reported_cutoff'], name
        rows.append({'name': name, 'curve_uid': r['curve_uid'], 'field_bits': bits,
                     'ordinal': ordinal[r['curve_uid']], 'label': r['label'],
                     'b_sign_model': b_sign_model,
                     'ramified_listed_elkies_under100': ramified_listed_elkies,
                     'source_reported_cutoff': e['reported_cutoff'],
                     'replay_literal_formula_with_ramified': literal_cutoff,
                     'replay_integer_rule_with_ramified': integer_cutoff,
                     'strict_exact_elkies_only_cutoff': r['cutoff_ell']})
    assert len(rows) == 19
    answer = {'external_url': 'https://raw.githubusercontent.com/emanjon/share/refs/heads/main/ecdsa_skipped_curves.txt',
              'external_sha256': EXTERNAL_SHA256, 'strict_raw_sha256': sha(RAW),
              'input_sha256': {str(ASS.relative_to(ROOT)): sha(ASS), str(TRAITS.relative_to(ROOT)): sha(TRAITS)},
              'rows': rows,
              'summary': {'curves': len(rows),
                          'ramified_entries_listed_as_elkies_under100': sum(len(r['ramified_listed_elkies_under100']) for r in rows),
                          'curves_with_such_entries': sum(bool(r['ramified_listed_elkies_under100']) for r in rows),
                          'opposite_isomorphic_b_models': sum(r['b_sign_model']=='opposite_isomorphic' for r in rows),
                          'reported_cutoffs_replayed_by_integer_rule': sum(r['source_reported_cutoff']==r['replay_integer_rule_with_ramified'] for r in rows),
                          'reported_cutoffs_replayed_by_literal_formula': sum(r['source_reported_cutoff']==r['replay_literal_formula_with_ramified'] for r in rows),
                          'reported_cutoffs_equal_strict_exact_cutoff': sum(r['source_reported_cutoff']==r['strict_exact_elkies_only_cutoff'] for r in rows)}}
    args.output.write_text(json.dumps(answer, sort_keys=True, indent=2)+'\n')
    print(json.dumps(answer['summary'], sort_keys=True))


if __name__ == '__main__':
    main()
